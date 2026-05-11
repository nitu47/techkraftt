from fastapi import APIRouter, HTTPException, BackgroundTasks
from ..database import add_score, generate_ai_summary, get_candidate_by_id
from ..schemas import ScoreCreate, AIMSummaryResponse

router = APIRouter(prefix="/candidates", tags=["scores"])

@router.post("/{candidate_id}/scores")
async def submit_score(candidate_id: int, score_data: ScoreCreate):
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

@router.post("/{candidate_id}/generate-summary", response_model=AIMSummaryResponse)
async def generate_summary(candidate_id: int, background_tasks: BackgroundTasks):
    candidate = get_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Simulate async processing
    background_tasks.add_task(generate_ai_summary, candidate_id)
    
    return {
        "candidate_id": candidate_id,
        "summary": "AI summary generation started. Please refresh to view."
    }

@router.get("/{candidate_id}/summary")
async def get_summary(candidate_id: int):
    candidate = get_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return {
        "candidate_id": candidate_id,
        "summary": candidate.ai_summary or "No summary available yet"
    }