from pydantic import BaseModel

class HerbQuery(BaseModel):
    code: str
    question: str

class HerbAnswer(BaseModel):
    answer: str
    source: str | None = None  
    source_title: str | None = None