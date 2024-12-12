from fastapi import FastAPI, APIRouter, HTTPException, Query
from configurations import collection_roomList, collection_schedule, collection_diary, collection_user, collection_quizlet
from database.schemas import room_list, schedule_list
from database.models import RoomList, Schedule, MultipleSchedules, RawDiary, User, RawQuizlet
from ai import ai_diary_correction, ai_diary_expressions, ai_diary_summary, generate_inline_comparison_html, parse_quizlet, translate_quizlet
from bson import ObjectId

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


# Return all users. 
@router.get("/user/")
async def get_all_users():
    data = collection_user.find()
    users = [serialize_document(user) for user in data]
    return users

# Check if user exists. 
@router.get("/user/{user_number}")
async def get_all_users(user_number: str):
    data = collection_user.find({"user_number":user_number})
    users = [serialize_document(user) for user in data]
    if len(users) == 1:
        return users
    else:
        # Return a response indicating the user doesn't exist
        return {"message":"no user"}

# Register user. 
@router.post("/user/")
async def create_user(new_user: User):
    try:
        resp = collection_user.insert_one(dict(new_user))
        return {"status_code":200, "id":str(resp.inserted_id), "user_name": new_user.user_name, "user_number": new_user.user_number, "user_number": new_user.type}

    except Exception as e:
        return HTTPException(status_code=500, detail=f"Some error occured {e}")


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

# Delete schedule
@router.delete("/schedules/{schedule_id}")
async def delete_schedule(schedule_id: str):
    try: 
        configured_item_id = ObjectId(schedule_id)
    except: 
        return {"message": f"Schedule with ID {schedule_id} is not a valid ID"}
    result = collection_schedule.delete_one({"_id": configured_item_id})
    if result.deleted_count == 0:
        return {"message": f"Schedule with ID {schedule_id} doesn't exist"}
    
    return {"message": f"Schedule with ID {schedule_id} deleted successfully"}

# Get schedules for a specific date
# Need to sort by room, time in asc order (low to high). 
@router.get("/schedules/date/{param}/")
async def get_schedules(param: str):
    filtered_schedules = collection_schedule.find({"date": param}).sort([("room_name", 1), ("time", 1)])
    schedules = [serialize_document(schedule) for schedule in filtered_schedules]
    return schedules

@router.get("/schedules/teacher/{param}/")
async def get_schedules(param: str):
    filtered_schedules = collection_schedule.find({"teacher_name": param}).sort([("date", 1), ("time", 1), ("room_name", 1)])
    schedules = [serialize_document(schedule) for schedule in filtered_schedules]
    return schedules

@router.get("/schedules/student/{param}/")
async def get_schedules(param: str):
    filtered_schedules = collection_schedule.find({"student_name": param}).sort([("date", 1), ("time", 1), ("room_name", 1)])
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

# Register schedule for multiple days during the same time. 
@router.post("/schedules/auto/")
async def create_multiple_schedules(schedules: MultipleSchedules):
    all_dates = schedules.dates
    time = schedules.time
    duration = schedules.duration
    teacher_name = schedules.teacher_name
    student_name = schedules.student_name
    room_name = ""
    all_saved_rooms = []


    # For each date 
    for date in all_dates:

        # Find an empty room and return. 
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
        
        # Check if there is atleast one available room. 
        if len(available_room_names) != 0:
            # Save the first room in room_name. 
            room_name = available_room_names[0]
        else:
            return 


        # Add new schedule with the room_name to the database.
        each_schedule = {"room_name": room_name, "date": date, "time": time, "duration": duration, "teacher_name": teacher_name, "student_name": student_name}
        resp = collection_schedule.insert_one(dict(each_schedule))
        all_saved_rooms.append(room_name)
    
    
    return {"status_code":200, "all_dates": all_dates, "all_rooms": all_saved_rooms, "time": time}


# Get all diary. 
@router.get("/diary/")
async def get_diaries():
    filtered_diaries = collection_diary.find().sort([("date", 1)])
    filtered_diaries = [serialize_document(diary) for diary in filtered_diaries]
    return filtered_diaries


# Get diaries for student name. 
@router.get("/diary/student/{student_name}")
async def get_student_diaries(student_name: str):
    filtered_diaries = collection_diary.find({"student_name": student_name}).sort([("date", 1)])
    filtered_diaries = [serialize_document(diary) for diary in filtered_diaries]
    return filtered_diaries


# Get Diary URLs for students taught by the teacher. 
@router.get("/diary/teacher/{teacher_name}")
async def get_teacher_diaries(teacher_name: str):
    students_list = []
    diary_url_list = []
    filtered_schedules = collection_schedule.find({"teacher_name": teacher_name}).sort([("date", -1), ("time", -1), ("room_name", 1)])
    for schedule in filtered_schedules:
        if schedule["student_name"] not in students_list:
            students_list.append(schedule["student_name"])
    for student in students_list:
        diary_url_list.append(f"diary?user={student}&type=student")
    return diary_url_list

# Create new diary, modify, and save AI corrected diary. 
@router.post("/diary/")
async def create_diary(raw_diary: RawDiary):
    student_name = raw_diary.student_name
    class_date = raw_diary.class_date
    date = raw_diary.date
    original_text = raw_diary.original_text
    diary_correction = ai_diary_correction(original_text)
    modified_diary_correction = generate_inline_comparison_html(original_text, diary_correction)
    diary_expressions = ai_diary_expressions(original_text)
    diary_summary = ai_diary_summary(original_text)

    modified_diary = {
        "student_name": student_name,
        "class_date": class_date,
        "date": date,
        "original_text": original_text,
        "diary_correction": diary_correction, 
        "modified_diary_correction": modified_diary_correction,
        "diary_expressions": diary_expressions, 
        "diary_summary": diary_summary
    }

    try:
        resp = collection_diary.insert_one(dict(modified_diary))
        return {"status_code":200, "id":str(resp.inserted_id), "student_name": student_name, "date": date, "message": modified_diary}

    except Exception as e:
        return {"status_code":500, "detail":f"Some error occured {e}"}
    


# Get all quizlets. 
@router.get("/quizlet/")
async def get_quizlets():
    filtered_quizlets = collection_quizlet.find().sort([("date", -1)])
    filtered_quizlets = [serialize_document(quizlet) for quizlet in filtered_quizlets]
    return filtered_quizlets


# Get quizlets for student name. 
@router.get("/quizlet/student/{student_name}")
async def get_student_quizlets(student_name: str):
    filtered_quizlets = collection_quizlet.find({"student_name": student_name}).sort([("date", -1)])
    filtered_quizlets = [serialize_document(quizlet) for quizlet in filtered_quizlets]
    return filtered_quizlets



# Create new quizlet. Return list of words with translation. 
@router.post("/quizlet/")
async def create_quizlet(raw_quizlet: RawQuizlet):
    student_name = raw_quizlet.student_name
    class_date = raw_quizlet.class_date
    date = raw_quizlet.date
    original_text = raw_quizlet.original_text
    eng_quizlet = parse_quizlet(original_text)
    kor_quizlet = translate_quizlet(eng_quizlet)

    modified_quizlet = {
        "student_name": student_name,
        "class_date": class_date,
        "date": date,
        "original_text": original_text,
        "eng_quizlet": eng_quizlet,
        "kor_quizlet": kor_quizlet
    }

    try:
        resp = collection_quizlet.insert_one(dict(modified_quizlet))
        return {"status_code":200, "id":str(resp.inserted_id), "student_name": student_name, "date": date, "eng_quizlet": eng_quizlet, "kor_quizlet": kor_quizlet}

    except Exception as e:
        return {"status_code":500, "detail":f"Some error occured {e}"}

# Delete all schedules. Use in case of Emergency. 
# @router.get("/delete/")
# async def delete_all_schedules():
#     result = collection_schedule.delete_many({})
#     return {"message": "done"}

app.include_router(router, prefix="/api")