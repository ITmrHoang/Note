# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import cv2
import base64
from .views import *

PREFERED_FPS=60
FRAME_DELAY=1/PREFERED_FPS
global NCLIENTS, broadcast_task
NCLIENTS=0

global NCLIENTSHR, broadcast_taskhr
NCLIENTSHR=0

async def broadcast(channel_layer, room_group_name):
    print('*********Start broadcasting..')
    nSize = -1
    while True:
        await asyncio.sleep(FRAME_DELAY)
        status, frame=cap.display()
        if not status or frame is None:
            pass
        else:
            retval, buf = cv2.imencode('.jpg', frame)
            img = base64.b64encode(buf)
            img = 'data:image/jpeg;base64,' + str(img, 'utf-8')
            await channel_layer.group_send(
                room_group_name,
                {
                    'type': 'frame_message',
                    'message': img,
                    'cam_idx' : '1',
                }
            )

            lface = cap.get_faces()
            length = len(lface)
            if length > 0 and nSize != length:
                nSize = length
                face_infos = []
                face_imgs = []
                lp_texts = []
                lp_imgs = []
                for face_id, face_img, lp_text, lp_img in lface:
                    retval, buf = cv2.imencode('.jpg', face_img)
                    img = base64.b64encode(buf)
                    img = 'data:image/jpeg;base64,' + str(img, 'utf-8')
                    face_infos.append(face_id)
                    face_imgs.append(img)

                    lp_texts.append(lp_text)

                    retvallp, buflp = cv2.imencode('.jpg', lp_img)
                    imglp = base64.b64encode(buflp)
                    imglp = 'data:image/jpeg;base64,' + str(imglp, 'utf-8')
                    lp_imgs.append(imglp)


                await channel_layer.group_send(
                    room_group_name,
                    {
                        'type': 'crop_message',
                        'message': {'face_imgs': face_imgs, 'face_infos': face_infos, 'lp_texts': lp_texts, "lp_imgs": lp_imgs },
                        'cam_idx' : '1',
                    }
                )

        # camera2
        status2, frame2=cap2.display()
        if not status2 or frame2 is None:
            pass
        else:
            retval, buf = cv2.imencode('.jpg', frame2)
            img = base64.b64encode(buf)
            img = 'data:image/jpeg;base64,' + str(img, 'utf-8')
            await channel_layer.group_send(
                room_group_name,
                {
                    'type': 'frame_message',
                    'message': img,
                    'cam_idx' : '2',
                }
            )

            lface = cap2.get_faces()
            length = len(lface)
            if length > 0 and nSize != length:
                nSize = length
                face_infos = []
                face_imgs = []
                lp_texts = []
                lp_imgs = []
                for face_id, face_img, lp_text, lp_img in lface:
                    retval, buf = cv2.imencode('.jpg', face_img)
                    img = base64.b64encode(buf)
                    img = 'data:image/jpeg;base64,' + str(img, 'utf-8')
                    face_infos.append(face_id)
                    face_imgs.append(img)

                    lp_texts.append(lp_text)

                    retvallp, buflp = cv2.imencode('.jpg', lp_img)
                    imglp = base64.b64encode(buflp)
                    imglp = 'data:image/jpeg;base64,' + str(imglp, 'utf-8')
                    lp_imgs.append(imglp)

                await channel_layer.group_send(
                    room_group_name,
                    {
                        'type': 'crop_message',
                        'message': {'face_imgs': face_imgs, 'face_infos': face_infos, 'lp_texts': lp_texts, "lp_imgs": lp_imgs },
                        'cam_idx' : '2',
                    }
                )

        # camera3 vao 2
        status3, frame3=cap3.display()
        if not status3 or frame3 is None:
            pass
        else:
            retval, buf = cv2.imencode('.jpg', frame3)
            img = base64.b64encode(buf)
            img = 'data:image/jpeg;base64,' + str(img, 'utf-8')
            await channel_layer.group_send(
                room_group_name,
                {
                    'type': 'frame_message',
                    'message': img,
                    'cam_idx' : '3',
                }
            )

            lface = cap3.get_faces()
            length = len(lface)
            if length > 0 and nSize != length:
                nSize = length
                face_infos = []
                face_imgs = []
                lp_texts = []
                lp_imgs = []
                for face_id, face_img, lp_text, lp_img in lface:
                    retval, buf = cv2.imencode('.jpg', face_img)
                    img = base64.b64encode(buf)
                    img = 'data:image/jpeg;base64,' + str(img, 'utf-8')
                    face_infos.append(face_id)
                    face_imgs.append(img)

                    lp_texts.append(lp_text)

                    retvallp, buflp = cv2.imencode('.jpg', lp_img)
                    imglp = base64.b64encode(buflp)
                    imglp = 'data:image/jpeg;base64,' + str(imglp, 'utf-8')
                    lp_imgs.append(imglp)

                await channel_layer.group_send(
                    room_group_name,
                    {
                        'type': 'crop_message',
                        'message': {'face_imgs': face_imgs, 'face_infos': face_infos, 'lp_texts': lp_texts, "lp_imgs": lp_imgs },
                        'cam_idx' : '3',
                    }
                )

        # camera4 ra2
        status4, frame4=cap4.display()
        if not status4 or frame4 is None:
            pass
        else:
            retval, buf = cv2.imencode('.jpg', frame4)
            img = base64.b64encode(buf)
            img = 'data:image/jpeg;base64,' + str(img, 'utf-8')
            await channel_layer.group_send(
                room_group_name,
                {
                    'type': 'frame_message',
                    'message': img,
                    'cam_idx' : '4',
                }
            )

            lface = cap4.get_faces()
            length = len(lface)
            if length > 0 and nSize != length:
                nSize = length
                face_infos = []
                face_imgs = []
                lp_texts = []
                lp_imgs = []
                for face_id, face_img, lp_text, lp_img in lface:
                    retval, buf = cv2.imencode('.jpg', face_img)
                    img = base64.b64encode(buf)
                    img = 'data:image/jpeg;base64,' + str(img, 'utf-8')
                    face_infos.append(face_id)
                    face_imgs.append(img)

                    lp_texts.append(lp_text)

                    retvallp, buflp = cv2.imencode('.jpg', lp_img)
                    imglp = base64.b64encode(buflp)
                    imglp = 'data:image/jpeg;base64,' + str(imglp, 'utf-8')
                    lp_imgs.append(imglp)

                await channel_layer.group_send(
                    room_group_name,
                    {
                        'type': 'crop_message',
                        'message': {'face_imgs': face_imgs, 'face_infos': face_infos, 'lp_texts': lp_texts, "lp_imgs": lp_imgs },
                        'cam_idx' : '4',
                    }
                )


class VideoStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        global NCLIENTS, broadcast_task
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'room_%s' % self.room_name
        NCLIENTS+=1

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        # if no client connected yet, start broadcast task
        if NCLIENTS==1:
            loop = asyncio.get_event_loop()
            broadcast_task=loop.create_task(broadcast(self.channel_layer, self.room_group_name))

    async def disconnect(self, close_code):
        global NCLIENTS, broadcast_task
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        NCLIENTS-=1
        if NCLIENTS==0:
            print('*********Stop broadcasting..')
            broadcast_task.cancel()
        
    # Receive message from WebSocket
    async def receive(self, text_data):
        pass

    # Receive message from room group
    async def frame_message(self, event):
        # Send message to WebSocket
        msg=event['message']
        camp = event['cam_idx']
        await self.send(text_data=json.dumps({
            'type': 'frame',
            'data': msg,
            "cam_idx": camp
        }))

    # Receive message from room group
    async def crop_message(self, event):
        # Send message to WebSocket
        msg=event['message']
        camp = event['cam_idx']
        await self.send(text_data=json.dumps({
            'type': 'crop',
            'data': msg,
            "cam_idx": camp
        }))


async def broadcasthr(channel_layer, room_group_name):
    print('*********Start broadcasting HR..')
    nSize = -1
    while True:
        await asyncio.sleep(FRAME_DELAY)
        status, frame=cap.display()
        if not status or frame is None:
            pass
        else:
            retval, buf = cv2.imencode('.jpg', frame)
            img = base64.b64encode(buf)
            img = 'data:image/jpeg;base64,' + str(img, 'utf-8')
            await channel_layer.group_send(
                room_group_name,
                {
                    'type': 'frame_message',
                    'message': img,
                    'cam_idx' : '1',
                }
            )

            lface = cap.get_faces()
            length = len(lface)
            if length > 0 and nSize != length:
                nSize = length
                face_infos = []
                face_imgs = []
                lp_texts = []
                lp_imgs = []
                for face_id, face_img, lp_text, lp_img in lface:
                    retval, buf = cv2.imencode('.jpg', face_img)
                    img = base64.b64encode(buf)
                    img = 'data:image/jpeg;base64,' + str(img, 'utf-8')
                    face_infos.append(face_id)
                    face_imgs.append(img)

                    lp_texts.append(lp_text)

                    retvallp, buflp = cv2.imencode('.jpg', lp_img)
                    imglp = base64.b64encode(buflp)
                    imglp = 'data:image/jpeg;base64,' + str(imglp, 'utf-8')
                    lp_imgs.append(imglp)


                await channel_layer.group_send(
                    room_group_name,
                    {
                        'type': 'crop_message',
                        'message': {'face_imgs': face_imgs, 'face_infos': face_infos, 'lp_texts': lp_texts, "lp_imgs": lp_imgs },
                        'cam_idx' : '1',
                    }
                )



class CameraHRStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        global NCLIENTSHR, broadcast_taskhr
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'room_%s' % self.room_name
        NCLIENTSHR+=1
        print(self.room_name, self.room_group_name)
        # Join room group room_camerahr
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # data_first = camhr.get_faces()
        # await self.group_send(
        #         self.room_group_name,
        #         {
        #             'type': 'first_connect',
        #             'message': data_first ,
        #             'cam_idx' : '1',
        #         }
        #     )
        # if no client connected yet, start broadcast task
        # if NCLIENTSHR==1:
        #     loop = asyncio.get_event_loop()
        #     broadcast_taskhr=loop.create_task(broadcasthr(self.channel_layer, self.room_group_name))

    async def disconnect(self, close_code):
        global NCLIENTSHR, broadcast_taskhr
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        NCLIENTSHR-=1
        # if NCLIENTSHR==0:
        #     print('*********Stop  HR..')
            # broadcast_taskhr.cancel()
        
    # Receive message from WebSocket
    async def receive(self, text_data):
        if (text_data == 'connect'):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'get_first_data',
                }
            )
    async def sound_message(self, event):
        # Send message to WebSocket
        msg=event['message']
        await self.send(text_data=json.dumps({
            'type': 'sound',
            'data': msg,
        }))
    # Receive message from room group
    async def frame_hr_message(self, event):
        msg=event['message']
        print('frame_hr_message',msg)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'frame',
            'data': msg,
        }))

    async def get_first_data(self,event):
        data_first = camhr.get_faces()
        await self.send(text_data=json.dumps(
                {
                    'type': 'data_first',
                    'data': data_first ,
                })
            )
    async def first_connect(self, event):
        # Send message to WebSocket
        msg=event['message']
        print('first_connect',msg)
        await self.send(text_data=json.dumps({
            'type': 'first',
            'data': msg,
        }))
