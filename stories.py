from typing import List, Literal
from langchain_core.pydantic_v1 import BaseModel, Field

class Line(BaseModel):
    character: str = Field(description="The character speaking the line, or the word 'Narrator' if the narrator is speaking")
    gender: Literal['m', 'f']
    line: str = Field(description="The line of the story")

class Story(BaseModel):
    foreign_language: List[Line] = Field(description="The lines of the story")
    english: List[Line] = Field(description="The English translation of the lines of the story")


class TimedLine(Line):
    start_sec: float = 0.0
    end_sec: float = 0.0

class TimedStory(Story):
    foreign_language: List[TimedLine]
    english: List[TimedLine]

class DailyStory(BaseModel):
    story: TimedStory = Field(description="The story for the day")
    abstract: str = Field(description="The abstract of the story")
    date: str = Field(description="The date of the story")
    theme: str = Field(description="The theme of the story")
    topic: str = Field(description="The topic of the story")