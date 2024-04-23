import inspect

class UserController:
    def get_user_by_id(self, id: int):
        return f"Get user by ID: {id}"

    def get_user_by_name(self, name: str):
        return f"Get user by name: {name}"

def analyze_controller_method(controller_class, method_name):
    try:
        method = getattr(controller_class(), method_name)
        parameters = inspect.signature(method).parameters
        parameter_types = {name: param.annotation for name, param in parameters.items() if param.annotation != inspect.Parameter.empty}
        return parameter_types
    except AttributeError:
        return None

# Phân tích phương thức get_user_by_id trong UserController
user_controller_params = analyze_controller_method(UserController, 'get_user_by_id')
if user_controller_params is not None:
    print("get_user_by_id parameter types:")
    print(user_controller_params)
else:
    print("Method get_user_by_id not found in UserController")

# Phân tích phương thức get_user_by_name trong UserController
user_controller_params = analyze_controller_method(UserController, 'get_user_by_name')
if user_controller_params is not None:
    print("\nget_user_by_name parameter types:")
    print(user_controller_params)
else:
    print("Method get_user_by_name not found in UserController")

# Phân tích phương thức không tồn tại trong UserController
non_existent_method_params = analyze_controller_method(UserController, 'non_existent_method')
if non_existent_method_params is not None:
    print("\nnon_existent_method parameter types:")
    print(non_existent_method_params)
else:
    print("Method non_existent_method not found in UserController")
