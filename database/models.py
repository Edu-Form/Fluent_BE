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

class RawDiary(BaseModel):
    student_name: str
    class_date: str
    date: str
    original_text: str 

class User(BaseModel):
    user_name: str 
    user_number: str
    type: str 

class RawQuizlet(BaseModel):
    student_name: str 
    class_date: str
    date: str 
    original_text: str 
