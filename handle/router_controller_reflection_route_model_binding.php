<?php

class UserController
{
    public function getUserById(int $id)
    {
        return "Get user by ID: $id";
    }

    public function getUserByName(string $name)
    {
        return "Get user by name: $name";
    }
}

function analyzeControllerMethod($controllerClassName, $methodName)
{
    $reflectionClass = new ReflectionClass($controllerClassName);
    $reflectionMethod = $reflectionClass->getMethod($methodName);

    $parameters = $reflectionMethod->getParameters();
    $parameterTypes = [];

    foreach ($parameters as $parameter) {
        $parameterName = $parameter->getName();
        $parameterType = $parameter->getType();

        if ($parameterType) {
            $parameterTypes[$parameterName] = $parameterType->getName();
        } else {
            $parameterTypes[$parameterName] = 'mixed'; // Nếu không có kiểu dữ liệu được định nghĩa, mặc định là 'mixed'
        }
    }

    return $parameterTypes;
}

// Phân tích phương thức getUserById trong UserController
$userControllerParams = analyzeControllerMethod('UserController', 'getUserById');
echo "getUserById parameter types: \n";
print_r($userControllerParams);

// Phân tích phương thức getUserByName trong UserController
$userControllerParams = analyzeControllerMethod('UserController', 'getUserByName');
echo "\ngetUserByName parameter types: \n";
print_r($userControllerParams);


//call fuction via name , and name agrument prams
function greet($message, $name) {
    echo "Hello $name, $message!";
}

$args = [
    'name' => 'John',
    'message' => 'how are you?'
];

call_user_func_array('greet', $args);
//c2

<?php
function makeyogurt($container: int)
{
    return  $container
}
function makeyogurt($container: str)
{
    return  $container
}

echo makeyogurt(style: "natural");
?>
