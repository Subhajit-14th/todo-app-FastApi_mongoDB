from fastapi import FastAPI
from config.database import get_database, get_authentication, get_collection
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# Define lifespan event handler to manage resources
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Perform actions at app startup
    db, collection_name = get_collection("todoDB", "todo_collection")  # Check MongoDB connection
    if db is None or collection_name is None:
        raise Exception("Failed to connect to MongoDB during startup.")
    
    db, authentication_collection = get_collection("todoDB", "authentication")
    if db is None or authentication_collection is None:
        raise Exception("Failed to connect to MongoDB during startup.")
    
    # Pass control to the application
    yield

    # Perform cleanup actions at shutdown (if needed)
    print("App is shutting down.")

# Initialize the FastAPI app with lifespan context
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers.routers import router

# Include your router
app.include_router(router)
