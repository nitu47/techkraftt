from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from ..database import get_candidates, get_candidate_by_id
from ..schemas import CandidateListResponse, CandidateDetailResponse

router = APIRouter(prefix="/candidates", tags=["candidates"])

@router.get("/", response_model=List[CandidateListResponse])
async def list_candidates(
    status: Optional[str] = Query(None, description="Filter by status"),
    role_applied: Optional[str] = Query(None, description="Filter by role"),
    skill: Optional[str] = Query(None, description="Filter by skill"),
    keyword: Optional[str] = Query(None, description="Search by name, email, or role"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
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

@router.get("/{candidate_id}", response_model=CandidateDetailResponse)
async def get_candidate(candidate_id: int):
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