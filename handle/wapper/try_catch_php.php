<?php

// Decorator function to handle exceptions and return appropriate response
function handle_exceptions($method) {
    return function() use ($method) {
        try {
            return call_user_func_array($method, func_get_args());
        } catch (Exception $e) {
            // Log the error
            error_log("An error occurred: " . $e->getMessage());
            // Return appropriate response
            http_response_code(500);
            echo json_encode(array("error" => "Internal Server Error"));
            exit();
        }
    };
}

// Class definition
class User {
    private $id;
    private $name;
    private $email;

    // Constructor
    public function __construct($id, $name, $email) {
        $this->id = $id;
        $this->name = $name;
        $this->email = $email;
    }

    // Static method to create a new user
    public static function create($id, $name, $email) {
        $user = new User($id, $name, $email);
        // Perform database operations to create user
        // For example:
        // $user->saveToDatabase();
        return $user;
    }

    // Method to retrieve a user by ID
    public static function get($id) {
        // Perform database operations to retrieve user
        // For example:
        // return User::find($id);
    }

    // Method to update user details
    public function update($name, $email) {
        // Update user details
        $this->name = $name;
        $this->email = $email;
        // Perform database operations to update user
        // For example:
        // $this->saveToDatabase();
        return $this;
    }

    // Method to delete user
    public function delete() {
        // Perform database operations to delete user
        // For example:
        // $this->deleteFromDatabase();
        return $this;
    }
}

// Example usage
try {
    // Wrap the create method with the handle_exceptions decorator
    $create = handle_exceptions('User::create');
    $created_user = $create(1, "John Doe", "john@example.com");
    echo "Created user: " . $created_user->id . ", " . $created_user->name . ", " . $created_user->email;
} catch (Exception $e) {
    echo "An error occurred: " . $e->getMessage();
}
?>


<?php
// Định nghĩa một hàm
function add($a, $b) {
    return $a + $b;
}

// Mảng chứa các tham số cần truyền vào hàm add
$parameters = array(2, 3);

// Gọi hàm add với các tham số từ mảng $parameters
$result = call_user_func_array("add", $parameters);

// In kết quả
echo "Result: " . $result; // Kết quả sẽ là 5
?>


// advance

// Lớp cha với xử lý ngoại lệ
class ParentClass {
    // Phương thức chung xử lý ngoại lệ
    protected function handleException(callable $callback, $args) {
        try {
            // Gọi phương thức được chỉ định
            return call_user_func_array($callback, $args);
        } catch (Exception $e) {
            // Xử lý ngoại lệ
            echo "An error occurred: " . $e->getMessage() . "\n";
            throw $e; // Ném lại ngoại lệ để xử lý ở nơi khác nếu cần
        }
    }
    
    // Ghi đè tất cả các phương thức của lớp cha để bọc chúng trong xử lý ngoại lệ
    public function __call($name, $args) {
        if (method_exists($this, $name)) {
            return $this->handleException([$this, $name], $args);
        } else {
            throw new Exception("Method $name not found.");
        }
    }
}

// Lớp con kế thừa từ lớp cha và có các phương thức bình thường
class ChildClass extends ParentClass {
    public function method1() {
        // Một phương thức có thể sinh ra ngoại lệ
        throw new Exception("Error in method1");
    }

    public function method2() {
        // Một phương thức khác
        return "Result from method2";
    }
}

// Sử dụng lớp con với các phương thức đã được bọc trong xử lý ngoại lệ
$child = new ChildClass();
try {
    echo $child->method1() . "\n";
} catch (Exception $e) {
    echo "Caught error: " . $e->getMessage() . "\n";
}

echo $child->method2() . "\n";

