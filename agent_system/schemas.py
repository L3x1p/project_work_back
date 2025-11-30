from pydantic import BaseModel
from typing import Optional


class InitStoryRequest(BaseModel):
    parent_result_id: Optional[int] = None


class SubmitAnswerRequest(BaseModel):
    story_id: int
    answer_text: str


class GetStoryRequest(BaseModel):
    story_id: int
