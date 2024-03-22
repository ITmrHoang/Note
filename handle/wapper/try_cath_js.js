// Hàm để bọc một hàm trong một hàm mới xử lý ngoại lệ
function handleExceptions(func) {
    return function(...args) {
        try {
            // Gọi hàm gốc với các đối số được truyền vào
            return func.apply(this, args);
        } catch (error) {
            console.error("An error occurred:", error);
            // Xử lý ngoại lệ tại đây, ví dụ: throw error; hoặc return một giá trị mặc định
            throw error; // Ném lại ngoại lệ để xử lý bên ngoài
        }
    };
}

// Định nghĩa một lớp với phương thức có thể sinh ra ngoại lệ
class MyClass {
    // Phương thức có thể sinh ra ngoại lệ
    myMethod() {
        // Giả sử có một lỗi xảy ra ở đây
        throw new Error("Something went wrong!");
    }
}

// Bọc phương thức myMethod bằng hàm handleExceptions
MyClass.prototype.myMethod = handleExceptions(MyClass.prototype.myMethod);

// Sử dụng lớp với phương thức đã được bọc
const myObject = new MyClass();
try {
    myObject.myMethod();
} catch (error) {
    console.error("Caught error outside:", error);
}

// avancde

// Hàm để bọc một phương thức trong một lớp với hàm xử lý ngoại lệ
function wrapMethodWithExceptionHandler(Class) {
    // Duyệt qua tất cả các thuộc tính của lớp
    for (let propertyName of Object.getOwnPropertyNames(Class.prototype)) {
        // Lấy giá trị của thuộc tính
        let propertyValue = Class.prototype[propertyName];
        // Kiểm tra xem nó có phải là một phương thức không
        if (typeof propertyValue === 'function') {
            // Bọc phương thức trong hàm xử lý ngoại lệ
            Class.prototype[propertyName] = function(...args) {
                try {
                    // Gọi phương thức gốc với các đối số được truyền vào
                    return propertyValue.apply(this, args);
                } catch (error) {
                    console.error("An error occurred:", error);
                    // Xử lý ngoại lệ tại đây, ví dụ: throw error; hoặc return một giá trị mặc định
                    throw error; // Ném lại ngoại lệ để xử lý bên ngoài
                }
            };
        }
    }
}

// Định nghĩa một lớp với các phương thức có thể sinh ra ngoại lệ
class MyClass {
    myMethod1() {
        throw new Error("Error in myMethod1!");
    }

    myMethod2() {
        throw new Error("Error in myMethod2!");
    }
}

// Bọc tất cả các phương thức trong lớp MyClass với hàm xử lý ngoại lệ
wrapMethodWithExceptionHandler(MyClass);

// Sử dụng lớp với các phương thức đã được bọc
const myObject = new MyClass();
try {
    myObject.myMethod1();
} catch (error) {
    console.error("Caught error in myMethod1:", error);
}

try {
    myObject.myMethod2();
} catch (error) {
    console.error("Caught error in myMethod2:", error);
}
