from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import Collection
from pymongo.database import Database
from typing import Tuple, Optional


# Function to get a specific collection in the database
def get_collection(db_name: str, collection_name: str) -> Tuple[Optional[Database], Optional[Collection]]:
    """
    Connect to MongoDB, check if the specified collection exists, and create it if not.
    
    Parameters:
        db_name (str): Name of the database to connect to.
        collection_name (str): Name of the collection to access or create.
    
    Returns:
        Tuple[Optional[object], Optional[Collection]]: The database and collection objects.
    """
    try:
        # Initialize MongoDB client
        client = MongoClient("mongodb+srv://subhajitdtt700:Nw1IBOQxXKPiiuwK@startone.or1v9.mongodb.net/?retryWrites=true&w=majority&appName=startOne", server_api=ServerApi('1'))

        # Access the database
        db = client[db_name]

        # Check if collection exists
        existing_collections = db.list_collection_names()
        if collection_name in existing_collections:
            print(f"Collection '{collection_name}' already exists.")
        else:
            print(f"Collection '{collection_name}' does not exist. Creating new collection.")
            db.create_collection(collection_name)
            print(f"Collection '{collection_name}' created successfully.")

        # Access the collection
        collection = db[collection_name]

        # Ensure that db and collection_name are valid
        if db is None or collection is None:
            print("Database or Collection is None!")
            # return None, None
        
        # Attempt to retrieve one document to confirm the connection
        document = collection.find_one()
        
        # Check if a document was found or if the collection is empty
        if document is not None:
            print("MongoDB connection established successfully! Found a document.")
        else:
            print("MongoDB connection established successfully! No documents found in the collection.")

        return db, collection

    except Exception as e:
        print("Error connecting to MongoDB:", e)
        return None, None



def get_database() -> Tuple[Optional[object], Optional[Collection]]:
    """
    Connect to the MongoDB database and return the database and collection.
    
    Returns:
        A tuple containing the database and the collection.
    """
    try:
        # Initialize MongoDB client
        client = MongoClient("mongodb+srv://subhajitdtt700:Nw1IBOQxXKPiiuwK@startone.or1v9.mongodb.net/?retryWrites=true&w=majority&appName=startOne", server_api=ServerApi('1'))

        # Access the database
        db = client.todoDB
        
        # Access the collection
        collection_name = db['todo_collection']

        # Ensure that db and collection_name are valid
        if db is None or collection_name is None:
            print("Database or Collection is None!")
            return None, None
        
        # Attempt to retrieve one document to confirm the connection
        document = collection_name.find_one()
        
        # Check if a document was found or if the collection is empty
        if document is not None:
            print("MongoDB connection established successfully! Found a document.")
        else:
            print("MongoDB connection established successfully! No documents found in the collection.")
        
        return db, collection_name

    except Exception as e:
        print("Error connecting to MongoDB:", e)
        return None, None

    
# for authentication collection name
def get_authentication() -> Tuple[Optional[object], Optional[Collection]]:
    try:
        # Initialize MongoDB client.
        client = MongoClient("mongodb+srv://subhajitdtt700:Nw1IBOQxXKPiiuwK@startone.or1v9.mongodb.net/?retryWrites=true&w=majority&appName=startOne", server_api=ServerApi('1'))

        # Access the database
        db = client.todoDB
        
        # Access the collection
        collection_name = db['authentication']

         # Ensure that db and collection_name are valid
        if db is None or collection_name is None:
            print("Database or Collection is None!")
            return None, None
        
        # Attempt to retrieve one document to confirm the connection
        document = collection_name.find_one()
        
        # Check if a document was found or if the collection is empty
        if document is not None:
            print("MongoDB connection established successfully! Found a document.")
        else:
            print("MongoDB connection established successfully! No documents found in the collection.")

        return db, collection_name
    except Exception as e:
        print("Error connecting to MongoDB:", e)
        return None, None