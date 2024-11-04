
def room_list(RoomList):
    return {
        "room_name": RoomList["room_name"],
        "description": RoomList["description"]
    }

def schedule_list(Schedule):
    return {
        "room_name": Schedule["room_name"],
        "date": Schedule["date"],
        "time": Schedule["time"],
        "duration": Schedule["duration"],
        "teacher_name": Schedule["teacher_name"],
        "student_name": Schedule["student_name"],
    }