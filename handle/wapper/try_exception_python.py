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
