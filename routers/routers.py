from fastapi import APIRouter, HTTPException
from config.database import get_database
from controller import todo_controllers
from fastapi import Response, Depends, HTTPException, Header, File, UploadFile
from models import models
import jwt
import os
from dotenv import load_dotenv
import base64

router = APIRouter()

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

# Dependency to get the token from the headers
def get_token(authorization: str = Header(...)):
    if not authorization:
        raise HTTPException(status_code=403, detail="Authorization header is missing")
    
    # Check for 'Bearer <token>' format
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Invalid authorization token format")
    
    # Extract the token by slicing off the 'Bearer ' part
    token = authorization.split(" ")[1]
    return token

# Decode the token
def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[str(JWT_ALGORITHM)])
        print(f"Decoded payload: {payload}")  # Log the decoded payload
        return payload['user_id']  # Ensure this key exists in the payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid token")

# for get all the todo data
@router.get("/getAllTodos")
async def get_all_todos(token: str = Depends(get_token)):
    try:
        user_id = decode_token(token)  # Function to decode the token and extract user_id
        print(user_id)
        todos = todo_controllers.get_all_todos(user_id)
        return {
            "status": 200,
            "message": "success",
            "data": todos,
        }
    except Exception as e:
        print(f"Error occurred while fetching todos: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# for get only one perticular todo
@router.get("/getSingleTodo/{todoId}")
async def getPerticularTodo(todoId: str, token: str = Depends(get_token)):
    try:
        user_id = decode_token(token)  # Function to decode the token and extract user_id
        print(user_id)
        todo = todo_controllers.get_particular_todo(todoId, user_id)
        return {
            "status": 200,
            "message": "success",
            "data": todo
        }
    except Exception as e:
        print(f"Error occurred while fetching perticular todo: {e}")

# for create new todo
@router.post("/createTodo")
async def create_task(new_task: models.Todo, token: str = Depends(get_token)):
    try:
        user_id = decode_token(token)  # Function to decode the token and extract user_id
        print(user_id)
        task_id = todo_controllers.create_new_todo(new_task, user_id)
        return {
            "status": 200,
            "message": "todo task created successfully",
        }
    except Exception as e:
        print(f"Error occurred while creating a task: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# for update perticular todo
@router.put("/updateTodo/{todoId}")
async def update_todo(todoId: str, updated_task: models.Todo):
    try:
        todo = todo_controllers.update_particular_todo(todoId, updated_task)
        return {
            "status": 200,
            "message": todo
            }
    except Exception as e:
        print(f"Error occurred while updating a task: {e}")

# for delete a particuler
@router.delete("/deletePerticulerTodo/{todoId}")
async def delete_todo(todoId: str):
    try:
        todo = todo_controllers.delete_particuler_todo(todoId)
        return {
            "status": 200,
            "message": todo
        }
    except Exception as e:
        print(f"Error occurred while deleting a task: {e}")

# for create a new user
@router.post("/createUser")
async def createUser(create_user: models.UserModel):
    try:
        user_id = todo_controllers.user_registration(create_user)
        return {
            "status": 200,
            "message": user_id,
        }
    except Exception as e:
        print(f"Error occurred while creating a user: {e}")

# for login that user
@router.post("/loginuser")
async def loginUser(login_data: models.LoginRequest,  response: Response):
    try:
        message, user_details, token = todo_controllers.user_login(login_data.email, login_data.password)

        if user_details is None:
            return {
                "status": 401,
                "message": message
            }
        
        response.set_cookie(
            key="jwt_token",
            value=token,
            httponly=True,   # Makes the cookie inaccessible to JavaScript
            # samesite=Literal['lax'],  # Protects against CSRF
            max_age=3600,    # Cookie expiration time (in seconds)
            secure=True      # Ensure this is True in production for HTTPS
        )

        return{
            "status": 200,
            "message": message,
            "token": token,
            "user_details": {
                "name": user_details.name,
                "email": user_details.email,
                "profile_picture": user_details.profile_picture
            }
        }
    except Exception as e:
        print(f"Error occurred while login a user: {e}")

# for uploading photo
@router.post("/updateProfilePhoto")
async def updateUser(file: UploadFile = File(...), token: str = Depends(get_token)):
    try:
        # get the token from the cookie
        try:
            user_id = decode_token(token)  # Function to decode the token and extract user_id
            print(user_id)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.PyJWTError:
            raise HTTPException(status_code=403, detail="Invalid token")
        

        # Read the file content
        content = await file.read()

        # Convert to base64
        content_base64 = base64.b64encode(content).decode("utf-8")

        print("My file is", content_base64)
        
        # Create a document to insert
        file_data = content_base64

        # Define the file path and name
        file_name = f"{user_id}_profile_photo.png"  # Adjust the extension as needed
        file_path = f"./uploads/{file_name}"

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Decode the base64 content and write to file
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(content_base64))

        print(f"File saved as: {file_path}")

        # Update MongoDB with the base64 image data
        update_status = todo_controllers.update_user_profile(user_id, {"profile_picture": content_base64})
        
        if update_status:
            return {"status": "success", "message": "Profile photo updated successfully"}
        else:
            return {"status": "failed", "message": "Failed to update profile photo in database"}
    except Exception as e:
        error_message = str(e)

        # Check if the error message contains "Token has expired"
        if "Token has expired" in error_message:
            return {"status": "failed", "message": "Token has expired"}
        else:
            return {"status": "failed", "message": error_message}