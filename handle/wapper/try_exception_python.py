from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Any, Dict

# Decorator to handle exceptions and raise HTTPException
def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"An error occurred: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
    return wrapper

# SQLAlchemy ORM model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

    @classmethod
    @handle_exceptions
    def create(cls, db: Session, **kwargs: Dict[str, Any]):
        user = cls(**kwargs)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @classmethod
    def get(cls, db: Session, user_id: int):
        return db.query(cls).filter(cls.id == user_id).first()

    def update(self, db: Session, **kwargs: Dict[str, Any]):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db: Session):
        db.delete(self)
        db.commit()
        return self

# Example usage
if __name__ == "__main__":
    # Example of CRUD operations
    with SessionLocal() as session:
        try:
            created_user = User.create(db=session, name="John Doe", email="john@example.com")
            print("Created user:", created_user.id, created_user.name, created_user.email)
        
            retrieved_user = User.get(db=session, user_id=created_user.id)
            print("Retrieved user by ID:", retrieved_user.id, retrieved_user.name, retrieved_user.email)
        
            updated_user = retrieved_user.update(db=session, name="Jane Doe", email="jane@example.com")
            print("Updated user:", updated_user.id, updated_user.name, updated_user.email)
        
            deleted_user = updated_user.delete(db=session)
            print("Deleted user:", deleted_user.id, deleted_user.name, deleted_user.email)
        except HTTPException as e:
            print(f"An HTTP error occurred: {e}")
# advance

# Decorator để bọc một phương thức với xử lý ngoại lệ
def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            # Gọi phương thức gốc với các đối số được truyền vào
            return func(*args, **kwargs)
        except Exception as e:
            print(f"An error occurred: {e}")
            # Xử lý ngoại lệ tại đây, ví dụ: raise e; hoặc return một giá trị mặc định
            raise e  # Ném lại ngoại lệ để xử lý bên ngoài
    return wrapper

# Hàm để bọc lại tất cả các phương thức của một lớp với decorator xử lý ngoại lệ
def wrap_class_with_exception_handler(Class):
    # Lặp qua tất cả các phương thức trong lớp
    for name, method in vars(Class).items():
        # Kiểm tra xem phần tử đó có phải là một phương thức không
        if callable(method):
            # Ghi đè phương thức bằng phiên bản mới đã được bọc
            setattr(Class, name, handle_exceptions(method))
    return Class

# Định nghĩa một lớp với các phương thức có thể sinh ra ngoại lệ
@wrap_class_with_exception_handler
class MyClass:
    def my_method1(self):
        raise ValueError("Error in my_method1!")

    def my_method2(self):
        raise TypeError("Error in my_method2!")

# Lớp con kế thừa từ MyClass
class MySubClass(MyClass):
    def my_method3(self):
        raise IndexError("Error in my_method3!")

# Sử dụng lớp con với các phương thức đã được bọc
my_sub_object = MySubClass()
try:
    my_sub_object.my_method1()
except Exception as e:
    print(f"Caught error in my_method1: {e}")

try:
    my_sub_object.my_method2()
except Exception as e:
    print(f"Caught error in my_method2: {e}")

try:
    my_sub_object.my_method3()
except Exception as e:
    print(f"Caught error in my_method3: {e}")
