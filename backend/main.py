# main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional
from database import (
    init_database, get_candidates, get_candidate_by_id, 
    add_score, generate_ai_summary, get_total_candidates_count,
    CandidateListResponse, CandidateDetailResponse, ScoreCreate, 
    AIMSummaryResponse
)

# Define lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    print("🚀 Starting up...")
    init_database()
    print("✅ Database initialized and ready!")
    yield
    # Shutdown: Clean up if needed
    print("👋 Shutting down...")
    # Add any cleanup code here if needed

# Create FastAPI app with lifespan
app = FastAPI(
    title="Candidate Review API", 
    version="1.0.0",
    lifespan=lifespan  # Use lifespan instead of on_event
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ API Endpoints ============

@app.get("/")
async def root():
    return {
        "message": "Candidate Review API is running with SQLite",
        "total_candidates": get_total_candidates_count(),
        "database": "SQLite"
    }

@app.get("/candidates", response_model=List[CandidateListResponse])
async def list_candidates(
    status: Optional[str] = Query(None, description="Filter by status"),
    role_applied: Optional[str] = Query(None, description="Filter by role"),
    skill: Optional[str] = Query(None, description="Filter by skill"),
    keyword: Optional[str] = Query(None, description="Search by name, email, or role"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get list of candidates with filters and pagination"""
    candidates = get_candidates(status, role_applied, skill, keyword, limit, offset)
    
    return [
        CandidateListResponse(
            id=c.id,
            name=c.name,
            role_applied=c.role_applied,
            status=c.status,
            skills=c.skills,
            experience_years=c.experience_years,
            location=c.location
        )
        for c in candidates
    ]

@app.get("/candidates/{candidate_id}", response_model=CandidateDetailResponse)
async def get_candidate(candidate_id: int):
    """Get detailed information about a specific candidate"""
    candidate = get_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return CandidateDetailResponse(
        id=candidate.id,
        name=candidate.name,
        email=candidate.email,
        role_applied=candidate.role_applied,
        status=candidate.status,
        skills=candidate.skills,
        experience_years=candidate.experience_years,
        location=candidate.location,
        scores=[s.dict() for s in candidate.scores],
        ai_summary=candidate.ai_summary,
        created_at=candidate.created_at
    )

@app.post("/candidates/{candidate_id}/scores")
async def submit_score(candidate_id: int, score_data: ScoreCreate):
    """Submit a score for a candidate"""
    if score_data.score < 1 or score_data.score > 5:
        raise HTTPException(status_code=400, detail="Score must be between 1 and 5")
    
    candidate = add_score(candidate_id, score_data.category, score_data.score, score_data.note)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return {
        "message": "Score submitted successfully",
        "candidate_id": candidate_id,
        "category": score_data.category,
        "score": score_data.score
    }

@app.post("/candidates/{candidate_id}/generate-summary", response_model=AIMSummaryResponse)
async def generate_summary_endpoint(candidate_id: int):
    """Generate AI summary for a candidate"""
    candidate = get_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Generate summary
    summary = generate_ai_summary(candidate_id)
    
    return {
        "candidate_id": candidate_id,
        "summary": summary or "Summary generation failed"
    }

@app.get("/candidates/{candidate_id}/summary")
async def get_summary(candidate_id: int):
    """Get the AI summary for a candidate"""
    candidate = get_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return {
        "candidate_id": candidate_id,
        "summary": candidate.ai_summary or "No summary available yet"
    }

if __name__ == "__main__":
    import uvicorn
    # Run without 'reload' parameter to avoid the warning, or use import string
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)