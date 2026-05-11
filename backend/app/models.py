from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class Score(BaseModel):
    category: str
    score: int
    note: Optional[str] = None
    submitted_at: datetime
    submitted_by: str

class Candidate(BaseModel):
    id: int
    name: str
    email: str
    role_applied: str
    status: str
    skills: List[str]
    experience_years: int
    location: str
    scores: List[Score] = []
    ai_summary: Optional[str] = None
    created_at: datetime

# In-memory database
candidates_db = {}

# Sample data
_sample_candidates = [
    Candidate(
        id=1,
        name="John Smith",
        email="john@example.com",
        role_applied="Senior Software Engineer",
        status="review",
        skills=["Python", "FastAPI", "React", "PostgreSQL"],
        experience_years=5,
        location="New York, NY",
        scores=[
            Score(category="technical", score=4, note="Strong Python skills", 
                  submitted_at=datetime.now(), submitted_by="tech_lead"),
            Score(category="communication", score=5, note="Excellent communication",
                  submitted_at=datetime.now(), submitted_by="hr_manager")
        ],
        ai_summary="John is a highly skilled candidate with 5+ years of experience. His Python expertise is impressive, and he demonstrates strong system design abilities. Recommended for technical interview.",
        created_at=datetime.now()
    ),
    Candidate(
        id=2,
        name="Sarah Johnson",
        email="sarah@example.com",
        role_applied="Frontend Developer",
        status="pending",
        skills=["React", "TypeScript", "Tailwind", "Next.js"],
        experience_years=3,
        location="Austin, TX",
        scores=[],
        ai_summary=None,
        created_at=datetime.now()
    ),
    Candidate(
        id=3,
        name="Michael Chen",
        email="michael@example.com",
        role_applied="DevOps Engineer",
        status="review",
        skills=["AWS", "Kubernetes", "Terraform", "Docker"],
        experience_years=7,
        location="Seattle, WA",
        scores=[
            Score(category="technical", score=5, note="Extensive cloud experience",
                  submitted_at=datetime.now(), submitted_by="tech_lead")
        ],
        ai_summary="Michael brings 7 years of DevOps experience with strong AWS and Kubernetes expertise. His infrastructure-as-code approach is solid.",
        created_at=datetime.now()
    ),
    Candidate(
        id=4,
        name="Emily Rodriguez",
        email="emily@example.com",
        role_applied="Senior Software Engineer",
        status="approved",
        skills=["Python", "Django", "React", "MongoDB"],
        experience_years=6,
        location="San Francisco, CA",
        scores=[
            Score(category="technical", score=5, note="Excellent full-stack knowledge",
                  submitted_at=datetime.now(), submitted_by="tech_lead"),
            Score(category="communication", score=4, note="Good team player",
                  submitted_at=datetime.now(), submitted_by="hr_manager"),
            Score(category="problem_solving", score=5, note="Great analytical skills",
                  submitted_at=datetime.now(), submitted_by="tech_lead")
        ],
        ai_summary="Emily is an outstanding full-stack engineer with strong leadership potential. Her problem-solving abilities are exceptional. Highly recommended for senior position.",
        created_at=datetime.now()
    ),
    Candidate(
        id=5,
        name="David Kim",
        email="david@example.com",
        role_applied="Data Engineer",
        status="rejected",
        skills=["SQL", "Spark", "Airflow", "Python"],
        experience_years=2,
        location="Chicago, IL",
        scores=[
            Score(category="technical", score=2, note="Limited experience with big data tools",
                  submitted_at=datetime.now(), submitted_by="tech_lead")
        ],
        ai_summary="David shows potential but lacks depth in data engineering tools for senior role. Consider for junior position.",
        created_at=datetime.now()
    )
]

for candidate in _sample_candidates:
    candidates_db[candidate.id] = candidate