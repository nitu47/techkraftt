# database.py
import sqlite3
import json
from datetime import datetime
from typing import List, Optional
from contextlib import contextmanager
from pydantic import BaseModel

DATABASE_PATH = "candidates.db"

# ============ Pydantic Models ============
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

# ============ Database Functions ============
@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_database():
    """Initialize database tables with sample data"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create candidates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role_applied TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                skills TEXT NOT NULL,
                experience_years INTEGER,
                location TEXT,
                ai_summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create scores table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                score INTEGER NOT NULL,
                note TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                submitted_by TEXT DEFAULT 'reviewer',
                FOREIGN KEY (candidate_id) REFERENCES candidates (id) ON DELETE CASCADE
            )
        """)
        
        # Check if we need to insert sample data
        cursor.execute("SELECT COUNT(*) as count FROM candidates")
        result = cursor.fetchone()
        
        if result['count'] == 0:
            print("📝 Inserting sample data...")
            
            # Insert sample candidates
            sample_candidates = [
                (1, "John Smith", "john@example.com", "Senior Software Engineer", "review", 
                 json.dumps(["Python", "FastAPI", "React", "PostgreSQL"]), 5, "New York, NY", 
                 "John is a highly skilled candidate with 5+ years of experience. His Python expertise is impressive."),
                (2, "Sarah Johnson", "sarah@example.com", "Frontend Developer", "pending",
                 json.dumps(["React", "TypeScript", "Tailwind", "Next.js"]), 3, "Austin, TX", None),
                (3, "Michael Chen", "michael@example.com", "DevOps Engineer", "review",
                 json.dumps(["AWS", "Kubernetes", "Terraform", "Docker"]), 7, "Seattle, WA",
                 "Michael brings 7 years of DevOps experience with strong AWS and Kubernetes expertise."),
                (4, "Emily Rodriguez", "emily@example.com", "Senior Software Engineer", "approved",
                 json.dumps(["Python", "Django", "React", "MongoDB"]), 6, "San Francisco, CA",
                 "Emily is an outstanding full-stack engineer with strong leadership potential."),
                (5, "David Kim", "david@example.com", "Data Engineer", "rejected",
                 json.dumps(["SQL", "Spark", "Airflow", "Python"]), 2, "Chicago, IL",
                 "David shows potential but lacks depth in data engineering tools for senior role."),
            ]
            
            cursor.executemany("""
                INSERT INTO candidates (id, name, email, role_applied, status, skills, experience_years, location, ai_summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_candidates)
            
            # Insert sample scores
            sample_scores = [
                (1, "technical", 4, "Strong Python skills", "tech_lead"),
                (1, "communication", 5, "Excellent communication", "hr_manager"),
                (3, "technical", 5, "Extensive cloud experience", "tech_lead"),
                (4, "technical", 5, "Excellent full-stack knowledge", "tech_lead"),
                (4, "communication", 4, "Good team player", "hr_manager"),
                (4, "problem_solving", 5, "Great analytical skills", "tech_lead"),
                (5, "technical", 2, "Limited experience with big data tools", "tech_lead"),
            ]
            
            cursor.executemany("""
                INSERT INTO scores (candidate_id, category, score, note, submitted_by)
                VALUES (?, ?, ?, ?, ?)
            """, sample_scores)
            
            # Reset sequence
            cursor.execute("UPDATE sqlite_sequence SET seq = 5 WHERE name = 'candidates'")
            print("✅ Sample data inserted successfully!")
        
        print("✅ Database initialized successfully!")

def get_candidates(
    status: Optional[str] = None,
    role_applied: Optional[str] = None,
    skill: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Candidate]:
    """Get candidates with filters"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM candidates WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if role_applied:
            query += " AND role_applied LIKE ?"
            params.append(f"%{role_applied}%")
        
        if keyword:
            query += " AND (name LIKE ? OR email LIKE ? OR role_applied LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
        
        query += " ORDER BY id LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        candidates = []
        for row in rows:
            # Get scores for this candidate
            cursor.execute("SELECT * FROM scores WHERE candidate_id = ? ORDER BY submitted_at DESC", (row['id'],))
            score_rows = cursor.fetchall()
            
            scores = [
                Score(
                    category=s['category'],
                    score=s['score'],
                    note=s['note'],
                    submitted_at=datetime.fromisoformat(s['submitted_at']) if isinstance(s['submitted_at'], str) else s['submitted_at'],
                    submitted_by=s['submitted_by']
                )
                for s in score_rows
            ]
            
            # Apply skill filter (needs to be done after fetching)
            if skill:
                candidate_skills = json.loads(row['skills'])
                if not any(skill.lower() in s.lower() for s in candidate_skills):
                    continue
            
            candidate = Candidate(
                id=row['id'],
                name=row['name'],
                email=row['email'],
                role_applied=row['role_applied'],
                status=row['status'],
                skills=json.loads(row['skills']),
                experience_years=row['experience_years'],
                location=row['location'],
                scores=scores,
                ai_summary=row['ai_summary'],
                created_at=datetime.fromisoformat(row['created_at']) if isinstance(row['created_at'], str) else row['created_at']
            )
            candidates.append(candidate)
        
        return candidates

def get_candidate_by_id(candidate_id: int) -> Optional[Candidate]:
    """Get a single candidate by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Get scores
        cursor.execute("SELECT * FROM scores WHERE candidate_id = ? ORDER BY submitted_at DESC", (candidate_id,))
        score_rows = cursor.fetchall()
        
        scores = [
            Score(
                category=s['category'],
                score=s['score'],
                note=s['note'],
                submitted_at=datetime.fromisoformat(s['submitted_at']) if isinstance(s['submitted_at'], str) else s['submitted_at'],
                submitted_by=s['submitted_by']
            )
            for s in score_rows
        ]
        
        return Candidate(
            id=row['id'],
            name=row['name'],
            email=row['email'],
            role_applied=row['role_applied'],
            status=row['status'],
            skills=json.loads(row['skills']),
            experience_years=row['experience_years'],
            location=row['location'],
            scores=scores,
            ai_summary=row['ai_summary'],
            created_at=datetime.fromisoformat(row['created_at']) if isinstance(row['created_at'], str) else row['created_at']
        )

def add_score(candidate_id: int, category: str, score: int, note: Optional[str], submitted_by: str = "reviewer") -> Optional[Candidate]:
    """Add a score to a candidate"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if candidate exists
        cursor.execute("SELECT id FROM candidates WHERE id = ?", (candidate_id,))
        if not cursor.fetchone():
            return None
        
        # Insert score
        cursor.execute("""
            INSERT INTO scores (candidate_id, category, score, note, submitted_by)
            VALUES (?, ?, ?, ?, ?)
        """, (candidate_id, category, score, note, submitted_by))
        
        return get_candidate_by_id(candidate_id)

def generate_ai_summary(candidate_id: int) -> Optional[str]:
    """Generate AI summary for a candidate"""
    candidate = get_candidate_by_id(candidate_id)
    if not candidate:
        return None
    
    # Calculate average score
    avg_score = sum(s.score for s in candidate.scores) / len(candidate.scores) if candidate.scores else 0
    
    # Generate summary based on data
    if avg_score >= 4.5:
        strength = "exceptional candidate with outstanding qualifications"
    elif avg_score >= 3.5:
        strength = "strong candidate with good potential"
    elif avg_score >= 2.5:
        strength = "decent candidate with some areas for improvement"
    else:
        strength = "candidate who may need more experience"
    
    summary = f"{candidate.name} is a {strength}. "
    summary += f"With {candidate.experience_years} years of experience in {', '.join(candidate.skills[:3])}, "
    summary += f"they have applied for {candidate.role_applied}. "
    
    if candidate.scores:
        summary += f"Current average score: {avg_score:.1f}/5. "
    
    if avg_score >= 4:
        summary += "Highly recommended for next interview stage."
    elif avg_score >= 3:
        summary += "Recommended for further consideration."
    else:
        summary += "May require additional technical assessment."
    
    # Update database
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE candidates SET ai_summary = ? WHERE id = ?", (summary, candidate_id))
    
    return summary

def get_total_candidates_count() -> int:
    """Get total number of candidates"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM candidates")
        return cursor.fetchone()['count']