import base64
from bson import ObjectId
from pydantic import EmailStr
from config.database import get_database, get_collection
from models.models import Todo, UserModel
from typing import Tuple, Optional
from gridfs import GridFS
from fastapi.responses import StreamingResponse

# get all the todos data
def get_all_todos(user_id: str) -> list:
    try:
        db, collection_name = get_collection("todoDB", "todo_collection")

        if collection_name is None:
            raise Exception("Collection not found!")

        data = collection_name.find({"user_id": user_id})
        todos = []
        
        for doc in data:
            doc['id'] = str(doc['_id'])  # Convert ObjectId to string
            todos.append(Todo(**doc))  # Create a Todo instance

        return todos
    except Exception as e:
        raise Exception(f"Error fetching todos: {e}")

# to get a perticuler todo item
from bson import ObjectId

# # get perticular todos
# def get_particular_todo(todo_id: str, user_id: str) -> Todo:
#     try:
#         db, collection_name = get_collection("todoDB", "todo_collection")

#         if collection_name is None:
#             raise Exception("Collection not found!")
        
#         # Convert todo_id to ObjectId
#         object_id = ObjectId(todo_id)

#         # Fetch data from MongoDB
#         data = collection_name.find_one({"_id": object_id, "user_id": user_id})
        
#         if not data:
#             raise Exception(f"Todo with id {todo_id} not found")
        
#         # Convert MongoDB document to Todo model
#         todo = Todo(**data)

#         return todo
#     except Exception as e:
#         raise Exception(f"Error fetching particular todo: {e}")


# to create a new todo
def create_new_todo(new_task: Todo, user_id: str) -> str:
    try:
        db, collection_name = get_collection("todoDB", "todo_collection")
        if collection_name is None:
            raise Exception("Collection not found!")
        
        print(user_id)

        # Exclude the `id` field when creating the task
        task_data = new_task.dict(exclude={"id"})  # Exclude id when creating
        task_data['user_id'] = user_id


        result = collection_name.insert_one(task_data)
        print(result)
        
        return str(result.inserted_id)  # Return the ID of the inserted task
    except Exception as e:
        raise Exception(f"Error creating new todo: {e}")

# to update particular todo
def update_particular_todo(todo_id: str, updated_task: dict) -> str:
    try:
        db, collection_name = get_collection("todoDB", "todo_collection")
        if collection_name is None:
            raise Exception("Collection not found!")
        
        object_id = ObjectId(todo_id)
        
        # Convert the updated_task to a dictionary, excluding the 'id' field
        # Fetch existing todo
        existing_todo = collection_name.find_one({"_id": object_id})

        if not existing_todo:
            raise Exception(f"Todo with id {todo_id} not found")

        # Update the todo document in MongoDB
        result = collection_name.find_one_and_update(
            {"_id": object_id},  # Query to match the todo with this _id
            {"$set": updated_task},
            return_document=True
        )

        # Check if the update was successful
        if result is None:
            raise Exception(f"Todo with id {todo_id} was not updated")
        
        return f"Todo with id {todo_id} updated successfully"
    except Exception as e:
        raise Exception(f"Error updating particular todo: {e}")

# to delete a particuler todo
def delete_particuler_todo(todo_id: str) -> str:
    try:
        db, collection_name = get_collection("todoDB", "todo_collection")
        if collection_name is None:
            raise Exception("Collection not found!")
        
        # Convert string ID to ObjectId
        object_id = ObjectId(todo_id)

        # Delete the document
        result = collection_name.delete_one({"_id": object_id})

        # Check if the deletion was successful
        if result.deleted_count == 0:
            raise Exception(f"Todo with id {todo_id} not found")

        return f"Item deleted successfully with id {todo_id}"
    except Exception as e:
        raise Exception(f"Error deleting particular todo: {e}")

# to create a new user   
def user_registration(userDetails: UserModel) -> str:
    try:
        db, collection_name = get_collection("todoDB", "authentication")
        if collection_name is None:
            raise Exception("Collection not found!")
        
        # Check if the email already exists
        existing_user = collection_name.find_one({"email": userDetails.email})
        if existing_user:
            return 'User email is already exists'
        
        userDetails.hash_password()
        
        # Exclude the `id` field when creating the task
        user_registration_data = userDetails.dict(exclude={"id"})  # Exclude id when creating
        result = collection_name.insert_one(user_registration_data)

        return str('Registration is Succuessfully')
    except Exception as e:
        raise Exception(f"Error registering user: {e}")

# to login that user
def user_login(email: EmailStr, password: str) ->  Tuple[str, Optional[UserModel], str]:
    try:
        db, collection_name = get_collection("todoDB", "authentication")
        if collection_name is None:
            raise Exception("Collection not found!")
        
        existing_user = collection_name.find_one({"email": email})
        if not existing_user:
            return str("Incorrect email or password"), None, str('')
        
        # Create a UserModel instance from the database record
        user = UserModel(**existing_user)

        # Verify the password
        if not user.verify_password(password):
            return str("Incorrect email or password"), None, str('')
        
        # Generate JWT token
        token = user.create_jwt_token(email, str(user.id))

        print(token)

        return str('User login successfully'), user, token
    except Exception as e:
        raise Exception(f"Error logging in user: {e}")

# to update profile
def update_user_profile(user_id: str, profile_image: dict) -> Optional[bool]:
    try:
        db, collection_name = get_collection("todoDB", "authentication")

        # Ensure the collection and database are not None
        if db is None or collection_name is None:
            raise Exception("Database or collection not found!")
        
        if not ObjectId.is_valid(user_id):
            raise Exception("Invalid user ID format")

        object_id = ObjectId(user_id)

        # Initialize GridFS with the database
        fs = GridFS(db)

        # Check if user already has a profile picture in GridFS
        existing_user = collection_name.find_one({"_id": object_id})
        print('My file id is', existing_user)

        if existing_user and "profile_picture" in existing_user:
            # If a profile picture already exists, delete the old file from GridFS
            old_file_id_str = existing_user["profile_picture"]
            if old_file_id_str and ObjectId.is_valid(old_file_id_str):
                old_file_id = ObjectId(old_file_id_str)
                print('Deleting old file id:', old_file_id)
                fs.delete(old_file_id)
            else:
                print("Existing profile_picture is not a valid ObjectId")

         
        # Read and store the new profile picture in GridFS
        content = profile_image['profile_picture']
        content_bytes = base64.b64decode(content)
        print('My image data is:', content_bytes)
        file_id = fs.put(content_bytes, filename=f"{user_id}_profile_photo.png")
        print('My file id is', file_id) # Retrieve the file from GridFS using the file ID
        file_data = fs.get(file_id)
        print('My file data is', StreamingResponse(file_data, media_type="image/png"))

        
        # # Update the todo document in MongoDB
        # result = collection_name.find_one_and_update(
        #     {"_id": object_id},  # Query to match the todo with this _id
        #     {"$set": {"profile_picture": str(file_data)}},
        #     return_document=True
        # )

        # return result is not None
    except Exception as e:
        raise Exception(f"Error updating user profile: {e}")