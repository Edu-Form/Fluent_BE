from pydantic import BaseModel 

class RoomList(BaseModel):
    room_name: str 
    description: str

class Schedule(BaseModel):
    room_name: str 
    date: str
    time: int
    duration: int
    teacher_name: str 
    student_name: str 
