from pydantic import BaseModel 
from typing import List

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

class MultipleSchedules(BaseModel):
    dates: List[str]
    time: int
    duration: int
    teacher_name: str
    student_name: str
