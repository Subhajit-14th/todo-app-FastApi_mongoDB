from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from typing import Optional, Any
import bcrypt
import os
from dotenv import load_dotenv
import jwt
import datetime
from fastapi import Depends, HTTPException, Header


load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRATION_DELTA = datetime.timedelta(hours=1)


# Custom ObjectId type for Pydantic v2
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field=None):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError(f"Invalid ObjectId: {v}")

    @classmethod
    def __get_pydantic_json_schema__(cls, *args):
        return {"type": "string", "format": "objectId"}

# Todo model with id (mapped to MongoDB _id)
class Todo(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")  # Maps MongoDB _id
    name: str
    description: str
    complete: bool = Field(default=False)

    def get_token(self, x_token: str = Header(...)):
        if not x_token:
            raise HTTPException(status_code=403, detail="Token is missing")
        return x_token

    class Config:
        populate_by_name = True  # Use this in place of allow_population_by_field_name
        arbitrary_types_allowed = True  # Allow ObjectId
        json_encoders = {ObjectId: str}  # Convert ObjectId to string when serializing

class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")  # Maps MongoDB _id
    name: Optional[str]
    email: EmailStr
    password: str
    profile_picture: Optional[str] = ''

    # Method to hash the password
    def hash_password(self):
        self.password = bcrypt.hashpw(self.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Method to verify a password against the hashed password
    def verify_password(self, plain_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), self.password.encode('utf-8'))
    
    def create_jwt_token(self, email: str, user_id: str) -> str:
        payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.datetime.utcnow() + JWT_EXPIRATION_DELTA
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token


    class Config:
        populate_by_name = True  # Allow using both field name and alias
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}  # For JSON serialization if needed


# For accepting login email and password in raw body
class LoginRequest(BaseModel):
    email: EmailStr
    password: str