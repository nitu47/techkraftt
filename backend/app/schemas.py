from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ScoreCreate(BaseModel):
    category: str
    score: int
    note: Optional[str] = None

class ScoreResponse(BaseModel):
    category: str
    score: int
    note: Optional[str]
    submitted_at: datetime
    submitted_by: str

class CandidateListResponse(BaseModel):
    id: int
    name: str
    role_applied: str
    status: str
    skills: List[str]
    experience_years: int
    location: str

class CandidateDetailResponse(BaseModel):
    id: int
    name: str
    email: str
    role_applied: str
    status: str
    skills: List[str]
    experience_years: int
    location: str
    scores: List[ScoreResponse]
    ai_summary: Optional[str]
    created_at: datetime

class AIMSummaryResponse(BaseModel):
    candidate_id: int
    summary: str