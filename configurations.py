from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://philjin97:october31%40@debate-cluster.5ww3q.mongodb.net/"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

db = client.room_allocation_db
collection_roomList = db["roomList"]
collection_schedule= db["schedule"]
collection_diary= db["diary"]

