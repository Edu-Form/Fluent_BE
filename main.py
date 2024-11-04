from fastapi import FastAPI, APIRouter, HTTPException, Query
from configurations import collection_roomList, collection_schedule
from database.schemas import room_list, schedule_list
from database.models import RoomList, Schedule

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
router = APIRouter()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from this origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Helper function to convert ObjectId fields to strings
def serialize_document(document):
    document["_id"] = str(document["_id"])
    return document

# Register New Room into Rooms List. 
# Use this later to get the parameters for rooms 
@router.post("/room_list/")
async def create_room(new_room: RoomList):
    try:
        resp = collection_roomList.insert_one(dict(new_room))
        return {"status_code":200, "id":str(resp.inserted_id), "room_name": new_room.room_name}

    except Exception as e:
        return HTTPException(status_code=500, detail=f"Some error occured {e}")

# Get all rooms on the list
# After using .find(), need to convert to a list for JSON serializable format.
# When you use list(data), the MongoDB cursor (data from collection_roomList.find()) is converted into a list directly, which seems convenient. 
# However, MongoDB documents contain fields like _id, which are ObjectId types, and these are not JSON serializable by default. 
# FastAPI's JSONResponse expects all data to be in JSON serializable format, so without converting ObjectId fields, FastAPI raises an error when it tries to serialize the response.
@router.get("/room_list/")
async def get_all_rooms():
    data = collection_roomList.find()
    rooms = [serialize_document(room) for room in data]
    return rooms


# Create new schedule 
@router.post("/schedules/")
async def create_schedule(new_schedule: Schedule):
    try:
        resp = collection_schedule.insert_one(dict(new_schedule))
        return {"status_code":200, "id":str(resp.inserted_id)}

    except Exception as e:
        return HTTPException(status_code=500, detail=f"Some error occured {e}")
    
# Get all schedules
# Need to sort by room, time in asc order (low to high). 
@router.get("/schedules/")
async def get_schedules():
    filtered_schedules = collection_schedule.find().sort([("room_name", 1), ("time", 1)])
    schedules = [serialize_document(schedule) for schedule in filtered_schedules]
    return schedules


# Get schedules for a specific date
# Need to sort by room, time in asc order (low to high). 
@router.get("/schedules/date/{param}/")
async def get_schedules(param: str):
    filtered_schedules = collection_schedule.find({"date": param}).sort([("room_name", 1), ("time", 1)])
    schedules = [serialize_document(schedule) for schedule in filtered_schedules]
    return schedules

@router.get("/schedules/teacher/{param}/")
async def get_schedules(param: str):
    filtered_schedules = collection_schedule.find({"teacher_name": param}).sort([("room_name", 1), ("time", 1)])
    schedules = [serialize_document(schedule) for schedule in filtered_schedules]
    return schedules

@router.get("/schedules/student/{param}/")
async def get_schedules(param: str):
    filtered_schedules = collection_schedule.find({"student_name": param}).sort([("room_name", 1), ("time", 1)])
    schedules = [serialize_document(schedule) for schedule in filtered_schedules]
    return schedules

# Get schedules to search for available rooms. 
# Get date, time inputs and filter all schedules for that time. 
# Get the list of all room names and if there is a room registered during that time, remove it from the list. 
# Return the list of rooms without any schedule. 
@router.get("/schedules/search_rooms/{date}/{time}/")
async def get_schedules(date: str, time: int):
    filtered_schedules = collection_schedule.find({"date": date, "time": time})

    # Get all room names
    all_room_names = []
    all_rooms = collection_roomList.find()
    for room in all_rooms:
        all_room_names.append(room["room_name"])
    print(all_room_names)

    # Cross out rooms that are unavailable 
    available_room_names = all_room_names 
    print(filtered_schedules)
    for schedule in filtered_schedules:
        print(schedule)
        available_room_names.remove(schedule["room_name"])
    
    # Return room_names in a list. ex) ["206", "2-2"]
    return available_room_names

# Get one day schedule for one teacher
@router.get("/schedules/oneday_oneteacher/{date}/{teacher}/")
async def get_schedules(date: str, teacher: str):
    filtered_schedules = collection_schedule.find({"date": date, "teacher_name": teacher}).sort([("time", 1)])

    parsedSchedule = []
    for schedule in filtered_schedules:
        parsedSchedule.append({"room_name":f'{schedule["room_name"]}', "student_name": f'{schedule["student_name"]}',"time":f'{schedule["time"]}',"time_range": f'{int(schedule["time"]) - 12}pm ~ {int(schedule["time"]) - 11}pm'})

    return parsedSchedule









app.include_router(router)