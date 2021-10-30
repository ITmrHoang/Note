from django.shortcuts import render
# chat/consumers.py
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json
import glob
import os
import time
from tqdm import tqdm
from queue import Queue
import threading
import yaml
import copy
import imutils
from multiprocessing.pool import ThreadPool
import numpy as np
import cv2
import base64
import logging
import os
import shutil
from datetime import datetime
from src.face_detector import FaceDetector, no_accent
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

root_logger= logging.getLogger()
root_logger.setLevel(logging.INFO) # or whatever
if not os.path.exists('logger'):
    os.makedirs('logger')
log_path = os.path.join('logger', datetime.today().strftime('%Y-%m-%d') + '.log')
handler = logging.FileHandler(log_path, mode='a', encoding='utf-8', delay=False) # or whatever
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')) # or whatever
root_logger.addHandler(handler)

# Create your views here.
def index(request):
    return render(request, 'index.html', {'room_name': 'main'})

def camerahr(request):
    return render(request, 'camerahr.html', {'room_name': 'camerahr'})
    
# general config
flagFaceDetect = 0
RESET_FLAG_FACE_DETECT = 6
IOU_THRESHOLD = 0.5
WIDTH_FRAME=640
IP_WEB_SERVER = None
PORT_WEB_SERVER = None

def create_logger():
    root_logger= logging.getLogger()
    root_logger.setLevel(logging.INFO) # or whatever
    if not os.path.exists('logger'):
        os.makedirs('logger')
    log_path = os.path.join('logger', datetime.today().strftime('%Y-%m-%d') + '.log')
    if not os.path.exists(log_path):
        handler = logging.FileHandler(log_path, mode='a', encoding='utf-8', delay=False) # or whatever
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')) # or whatever
        root_logger.addHandler(handler)

def remove_old_data():
    cur_day = datetime.today()
    for file_path in glob.glob('./logger/*.log'):
        file_name = os.path.basename(file_path)
        file_name = os.path.splitext(file_name)[0]
        old_date = datetime.strptime(file_name, '%Y-%m-%d')
        elapsed = (cur_day - old_date).days
        if elapsed > 7:
            logging.info('remove file: ' + file_path)
            os.remove(file_path)

def get_configs():
    global IP_WEB_SERVER
    global PORT_WEB_SERVER
    stream = open("app.yml", 'r')
    try:
        result = yaml.safe_load(stream)
        IP_WEB_SERVER = result['IP_WEB_SERVER']
        PORT_WEB_SERVER = result['PORT_WEB_SERVER']
    except yaml.YAMLError as exc:
        msg = 'config file not exist'
        logging.error(msg)

def get_config(key):
    stream = open("app.yml", 'r')
    try:
        result = yaml.safe_load(stream)
        val = result[key]
        return val
    except yaml.YAMLError as exc:
        msg = 'config file not exist'
        logging.error(msg)
    return None

def set_config(key, val):
    try:
        with open('app.yml') as f:
            doc = yaml.safe_load(f)
        doc[key] = val
        with open('app.yml', 'w') as f:
            yaml.safe_dump(doc, f, default_flow_style=False)
    except yaml.YAMLError as exc:
        msg = 'config file not exist'
        logging.error(msg)

def IoU(boxA, boxB):  # (x, y, w, h) format
    ymin = max(boxA[0], boxB[0])
    xmin = max(boxA[1], boxB[1])
    ymax = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
    xmax = min(boxA[1] + boxA[3], boxB[1] + boxB[3])
    interArea = max(0, xmax - xmin + 1) * max(0, ymax - ymin + 1)
    boxAArea = (boxA[2] + 1) * (boxA[3] + 1)
    boxBArea = (boxB[2] + 1) * (boxB[3] + 1)
    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

def get_cam_url(cam_id):
    try:
        url = "http://{}:{}/get_cam_url/".format(IP_WEB_SERVER, PORT_WEB_SERVER)
        context = {'cam_id' : cam_id}
        r = requests.post(url, data=context, timeout=1.5)
        if not r.ok:
            return
        data=r.json()
        if data['success']:
            return data['cam_url']
        else:
            return ''
    except requests.exceptions.HTTPError as errh:
        logging.error('get_cam_url() Http Error: ' + str(errh))
    except requests.exceptions.ConnectionError as errc:
        logging.error('get_cam_url() Error Connecting: ' + str(errc))
    except requests.exceptions.Timeout as errt:
        logging.error('get_cam_url() Timeout Error: ' + str(errt))
    except requests.exceptions.RequestException as e:
        logging.error('get_cam_url() OOps: Something Else ' + str(e))
    return ''


def checking(cam_id, face_id, face_img, license_plate, lp_img, state):
    try:
        url = "http://{}:{}/checking/".format(IP_WEB_SERVER, PORT_WEB_SERVER)
        context = {'cam_id' : cam_id, 'face_id': face_id, 'license_plate': license_plate, 'state': state}
        _, img_encoded = cv2.imencode('.jpg', face_img)
        _, lp_img_encoded = cv2.imencode('.jpg', lp_img)
        files = {'img': img_encoded, 'lp_img': lp_img_encoded}
        r = requests.post(url, files=files, data=context, timeout=1.5)
        if not r.ok:
            return 0
        data=r.json()
    except requests.exceptions.HTTPError as errh:
        logging.error('checking() Http Error: ' + str(errh))
    except requests.exceptions.ConnectionError as errc:
        logging.error('checking() Error Connecting: ' + str(errc))
    except requests.exceptions.Timeout as errt:
        logging.error('checking() Timeout Error: ' + str(errt))
    except requests.exceptions.RequestException as e:
        logging.error('checking() OOps: Something Else ' + str(e))
    return 0

def search_face(face_imgs, cam_id, stime, is_write=True):
    is_ok=True
    try:
        url = "http://{}:{}/search_face/".format(IP_WEB_SERVER, PORT_WEB_SERVER)
        context = {'cam_id' : cam_id, 'img_num' : len(face_imgs)}
        files = {}
        for idx, face_img in enumerate(face_imgs):
            _, img_encoded = cv2.imencode('.jpg', face_img)
            files['img' + str(idx)] = img_encoded
        lp_img = cv2.imread("D:/test/biensoxe.jpg")
        _, img_encoded = cv2.imencode('.jpg', lp_img)
        files['lp_img'] = img_encoded.tobytes()
        r = requests.post(url, files=files, data=context, timeout=1.5)
        if not r.ok:
           return
        data=r.json()
        if not data['success']:
           return data['success'], data['message']
        # save image and display
        return data['success'], data['face_id']
    except requests.exceptions.HTTPError as errh:
        is_ok = False
        logging.error('search_face() Http Error: ' + str(errh))
    except requests.exceptions.ConnectionError as errc:
        is_ok = False
        logging.error('search_face() Error Connecting: ' + str(errc))
    except requests.exceptions.Timeout as errt:
        is_ok = False
        logging.error('search_face() Timeout Error: ' + str(errt))
    except requests.exceptions.RequestException as e:
        is_ok = False
        logging.error('search_face() OOps: Something Else ' + str(e))
    # write face images if face recognize api failed
    if not is_ok:
        if is_write:
            # save image and display
            fld = os.path.join('static/faces/crop', stime)
            if not os.path.isdir(fld):
                os.mkdir(fld)
            for idx, face_img in enumerate(face_imgs):
                file_name=os.path.join(fld, str(idx) + ".jpg")
                logging.error('write file: ' + file_name)
                cv2.imwrite(file_name, face_img)
        return False, 'no network'
    # end func
    return False, 'unknown'

modelFile = "./src/iwanna_lp.pb"
configFile = "./src/iwanna_lp.pbtxt"
cvNet = cv2.dnn.readNetFromTensorflow(modelFile, configFile)

def get_license_plate(cur_frame):
    global cvNet

    cur_frame = cv2.imread('D:/python/cur_frame.jpg')

    license_plate = ''
    extend = 0.4
    _h = cur_frame.shape[0] 
    _w = cur_frame.shape[1]

    cvNet.setInput(cv2.dnn.blobFromImage(cur_frame, size=(300, 300), swapRB=True, crop=False))

    detections = cvNet.forward()

    bbox = None
    for i in np.arange(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.4:
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([_w, _h, _w, _h])
            (startX, startY, endX, endY) = box.astype("int")

            w = abs(endX - startX)
            h = abs(endY - startY)
            x = startX
            y = startY
            d = 0

            if w > h:
                d = abs(w - h)
                y -= 0.5 * d
                h += d
            else:
                d = abs(h - w)
                x -= 0.5 * d
                w += d

            x -= extend * w
            y -= extend * h
            w += extend * 2 * w
            h += extend * 2 * h
            x = int(x)
            y = int(y)
            w = int(w)
            h = int(h)

            x = max(x, 0)
            y = max(y, 0)
            w = min(w, _w - x - 2)
            h = min(h, _h - y - 2)
            bbox = (x, y, w, h)

    if bbox is not None:
        x, y, w, h = bbox
        lp_img = cur_frame[y:(y+h), x:(x+w)]
        _, img_encoded = cv2.imencode('.jpg', lp_img)
        files = {'img': img_encoded}
        url = "http://{}:{}/anpr_api/".format(IP_WEB_SERVER, PORT_WEB_SERVER)
        r = requests.post(url, files=files, timeout=1.5)
        if r.ok:
            license_plate = r.json()['license_plate']
    else:
        lp_img = cv2.resize(cur_frame, (360, 180), interpolation = cv2.INTER_AREA)

    return (license_plate, lp_img)


class Object():     # faceBox in (x, y , w, h) format
    def __init__(self, cam_id):
        self.faceHist = []
        self.state = False
        self.nFrame = 0
        self.tracker = None
        self.cam_id = cam_id
        self.face_id = 'unknown'
        self.async_result = None
        self.face_img = None
        self.is_show = False

    def createTraker(self, img, bbox):
        del(self.tracker)
        self.tracker = cv2.TrackerMedianFlow_create()
        self.tracker.init(img, tuple((int(i) for i in bbox)))
        self.state = True

    def updateTracker(self, frame, bbox=None, orginFrame=None):
        if bbox is None:
            if self.state and (frame is not None):
                exist, box = self.tracker.update(frame)
                if exist:
                    self.faceBox = tuple((int(i) for i in box))
                    self.nFrame += 1
                if (not exist) or self.nFrame > 8:
                    self.state = False

            if self.face_id == 'unknown':
                if self.state and (orginFrame is not None):
                    x, y, w, h = self.faceBox
                    hf, wf, _ = orginFrame.shape
                    scale = float(wf) / float(frame.shape[1])
                    x *= scale
                    y *= scale
                    w *= scale
                    h *= scale
                    ratio = 0.15
                    max_size = max(h, w)
                    h = w = max_size
                    y = max(y - ratio * max_size, 0)
                    x = max(x - ratio * max_size, 0)
                    h = min(h + 2 * max_size * ratio, hf - y - 1)
                    w = min(w + 2 * max_size * ratio, wf - w - 1)
                    if h > 20 and w > 20:
                        crop = orginFrame[int(y):int(y + h), int(x):int(x + w), :]
                        crop = cv2.resize(crop, (112, 112))
                        self.faceHist.append(crop)

                if (self.async_result is None):
                    if len(self.faceHist) > 0:
                        imgs = []
                        imgs.append(self.faceHist.pop())
                        now = datetime.now()
                        stime = now.strftime('%Y-%m-%d %H:%M:%S.%f')
                        pool = ThreadPool(processes=1)
                        self.async_result = pool.apply_async(search_face, (imgs, self.cam_id, stime))
                else:
                    try:
                        retval, self.face_id = self.async_result.get(timeout=0.0)
                        if not retval:
                            self.async_result = None
                        else:
                            self.face_img = self.faceHist[0]
                            self.is_show = True
                        self.faceHist.clear()
                    except:
                        pass

        else:
            x, y, w, h = [int(i) for i in bbox]
            self.nFrame = 0
            self.createTraker(frame, (x, y, w, h))
            self.faceBox = tuple((x, y, w, h))

    def deleteTracker(self):
        self.state = False
        del(self.tracker)
        self.tracker = None

class VideoStreamWidget():
    def __init__(self, *args):
        self.capture = None
        self.status = None
        self.CAM_URL = None
        self.cur_frame = None
        self.region = None
        self.cam_state = "in"
        self.is_start_cam = False
        self.queue_frame = Queue(maxsize=10)
        self.queue_face = Queue(maxsize=10)
        if not len(args) == 0:
            self.newStrSource(args[0])

    def newStrSource(self, src):
        del(self.capture)
        self.status = None
        self.CAM_URL = src
        self.capture = cv2.VideoCapture(src)
        self.capture.set(3, 1280)
        self.capture.set(4, 720)

    def display(self):
        if self.queue_frame.empty():
            return False, None
        return self.status, self.queue_frame.get()

    def get_faces(self):
        lface = []
        if not self.queue_face.empty():
            lface = list(self.queue_face.queue)
        if self.queue_face.full():
            self.queue_face.get()
        return lface

get_configs()
create_logger()
remove_old_data()
# ====================== JETSON build version ======================
MFD_PATH = 'src/iwanna.pb'
face_detector = FaceDetector(MFD_PATH, gpu_memory_fraction=0.3)
img = np.ones((1280,720,3), dtype=np.uint8)
for i in tqdm(range(3)):
    face_detector(img, WIDTH_FRAME)
del(img)
# ==================================================================
cap = VideoStreamWidget()
cap2 = VideoStreamWidget()
cap3 = VideoStreamWidget()
cap4 = VideoStreamWidget()


def process_camera(camref, camlpref, cam_id):
    objects = []
    global flagFaceDetect
    async_result = None
    start_time = time.time()
    nFrame = 0

    while True:
        if camref.is_start_cam == False:
            camref.status = False
            camref.capture.release()
            break
        if not camref.capture.isOpened():
            logging.error('open rtsp is failed: {}'.format(camref.CAM_URL))
            break
        (camref.status, frame) = camref.capture.read()
        if not camref.status:
            logging.error('camera is disconnect: {}'.format(camref.CAM_URL))
            break

        if nFrame >= 1:
            nFrame = 0
            continue
        nFrame += 1

        src = copy.copy(frame)
        camref.cur_frame = copy.copy(frame)[camref.region[1]:camref.region[3], camref.region[0]:camref.region[2]]
        frame = cv2.rectangle(frame, (camref.region[0], camref.region[1]),  (camref.region[2], camref.region[3]), (255, 0, 0), 4)
        dscale = WIDTH_FRAME / float(frame.shape[1])
        frame = cv2.resize(frame, (int(frame.shape[1] * dscale), int(frame.shape[0] * dscale)), interpolation=cv2.INTER_NEAREST)

        boxesDetect = []
        if flagFaceDetect == 0:
            boxesDetect = face_detector(src, WIDTH_FRAME)
            flagFaceDetect = RESET_FLAG_FACE_DETECT
        else:
            flagFaceDetect -= 1

        if len(boxesDetect) > 0:
            overlap2 = [False] * len(boxesDetect)
            # for idx, obj in enumerate(objects):
            for idx in range(len(objects)):
                overlap = False
                objects[idx].updateTracker(frame)
                for jdx, box in enumerate(boxesDetect):
                    if objects[idx].state:
                        iou = IoU(objects[idx].faceBox, box)
                        if iou > IOU_THRESHOLD:
                            objects[idx].updateTracker(frame, box, src)
                            overlap = True
                            overlap2[jdx] = True
                            break

            # create new tracker
            for idx, ov in enumerate(overlap2):
                if not ov:
                    _obj = Object(cam_id)
                    _obj.updateTracker(frame, boxesDetect[idx], src)
                    objects.append(_obj)
        else:
            for idx, obj in enumerate(objects):
                if obj.state:
                    obj.updateTracker(frame, None, src)

        for idx, obj in enumerate(objects):
            if obj.state:
                # add face info to display html
                if obj.is_show and (not camref.queue_face.full()):
                    obj.is_show = False
                    lp_view = copy.copy(camlpref.cur_frame)
                    lp_text, lp_img = get_license_plate(lp_view)
                    checking(cam_id, obj.face_id, obj.face_img, lp_text, lp_img, camref.cam_state)
                    camref.queue_face.put([obj.face_id, obj.face_img, lp_text, lp_img])

                # draw result
                (x, y, w, h) = [int(v) for v in obj.faceBox]
                label = no_accent(obj.face_id)
                if label == 'unknown':
                    cv2.rectangle(frame, (x, y), ((x + w), (y + h)), (0, 0, 255), 2)
                else:
                    cv2.rectangle(frame, (x, y), ((x + w), (y + h)), (0, 255, 0), 2)
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(frame, (x, y - labelSize[1]), (x + labelSize[0], y + baseLine), (255, 255, 255), cv2.FILLED)
                cv2.putText(frame, label, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
        # add to html display

        draw = copy.copy(frame)
        if not camref.queue_frame.full():
            camref.queue_frame.put(draw)

        for i in range(len(objects) - 1, -1, -1):
            if (not objects[i].state):
                if len(objects[i].faceHist) > 0:
                    # search face
                    objects[i].updateTracker(None, None, None)
                else:
                    # delete object in list tracking
                    del(objects[i])

@csrf_exempt
def start_camera(request):
    if request.method != "POST":
        return HttpResponse('require "POST" method')
    logging.info('start start_camera()')

    cam_id = request.POST.get('cam_id')
    cam_url = request.POST.get('cam_url')
    if cam_url is None:
        cam_url = get_cam_url(cam_id)
        msg='get_cam_url: ' + cam_url
        logging.info(msg)
        if cam_url is None:
            return JsonResponse({'success':False, 'message':msg})

    if cam_id == 'cong-vao-1':
        cap.is_start_cam = True
        cap.region = (565, 60, 1290, 1010)
        cap.cam_state = "in"
        cap.newStrSource(cam_url)
        process_camera(cap, cap2, cam_id)
    elif cam_id == 'cong-ra-1':
        cap2.is_start_cam = True
        cap2.cam_state = "out"
        cap2.region = (770, 60, 1485, 1010)
        cap2.newStrSource(cam_url)
        process_camera(cap2, cap, cam_id)
    elif cam_id == 'cong-vao-2':
        cap3.is_start_cam = True
        cap3.cam_state = "in"
        cap3.region = (490, 60, 1448, 1010)
        cap3.newStrSource(cam_url)
        process_camera(cap3, cap4, cam_id)
    elif cam_id == 'cong-ra-2':
        cap4.is_start_cam = True
        cap4.cam_state = "out"
        cap4.region = (630, 60, 1455, 1010)
        cap4.newStrSource(cam_url)
        process_camera(cap4, cap3, cam_id)

    logging.info('end start_camera()')
    return HttpResponse('ok')

@csrf_exempt
def stop_camera(request):
    if request.method == "POST":
        cap.is_start_cam = False
        time.sleep(1)
    return HttpResponse('ok')


class CamerahrQueue():
    def __init__(self, *args):
        self.queue_face = Queue(maxsize=10)
        
    def get_faces(self):
        lface = []
        if not self.queue_face.empty():
            lface = list(self.queue_face.queue)
        if self.queue_face.full():
            self.queue_face.get()
        return lface


camhr = CamerahrQueue()
@csrf_exempt
def warningcamerahr(request):
    if request.method == "GET":
        try:
            channel_layer = get_channel_layer()
            print("2222222222222222222222")

            if camhr.queue_face.full():
                camhr.queue_face.get()
            camhr.queue_face.put(['1','2', '3', '4'])
            print("xxxx")
            async_to_sync(channel_layer.group_send)("room_camerahr",
                {
                    "type": "frame_hr_message",
                    'message': {'face_imgs': 1, 'face_infos': 2, 'lp_texts': 3, "lp_imgs": 4 },
                })
            print("enddddddddddddd")
            return JsonResponse({'success': True, 'msg': "canh bao thanh cong"})
        except:
            return JsonResponse({'success': False, 'msg': "canh bao that bai"})
    else:
        return JsonResponse({'success': False, 'msg': "method not support. Have suport POST"})
