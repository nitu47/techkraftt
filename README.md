# TechKraft Candidate Review Dashboard

A full-stack candidate scoring and review dashboard for TechKraft's recruitment workflow.

## Setup & Run Instructions

### Backend
```bash
cd C:\techkraft\backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
Frontend (New Terminal)
bash
cd C:\techkraft\frontend
python -m http.server 3000 --bind 127.0.0.1
Open browser: http://127.0.0.1:3000

API Endpoints
Method	Endpoint	Description
GET	/candidates	List all candidates
GET	/candidates/{id}	Get candidate details
POST	/candidates/{id}/scores	Submit score (1-5)
POST	/candidates/{id}/generate-summary	Generate AI summary
Example API Calls
bash
# Get all candidates
curl http://127.0.0.1:8000/candidates

# Submit a score
curl -X POST http://127.0.0.1:8000/candidates/1/scores \
  -H "Content-Type: application/json" \
  -d '{"category":"technical","score":5,"note":"Great skills"}'

# Generate AI summary
curl -X POST http://127.0.0.1:8000/candidates/1/generate-summary
Architecture Decisions (ADR)
1. FastAPI over Flask
Why: Automatic API docs, async support, built-in validation

Trade-off: Smaller ecosystem but faster development

2. SQLite with SQLAlchemy
Why: Zero-config, file-based database, easy to backup

Trade-off: Not for high concurrency, perfect for internal tools

3. Modular Router Structure
Why: Clean code organization, easy to add features

Trade-off: More files but better maintainability

Debugging & Common Issues
Issue	Solution
ModuleNotFoundError: No module named 'app'	Run from backend folder: cd C:\techkraft\backend
Port 8000 already in use	Kill process or use different port: --port 8001
CORS errors	Ensure CORS middleware has allow_origins=["*"]
Database not created	Check write permissions in backend folder
Learning Reflection
Challenges Faced
Import issues - Resolved by proper Python package structure with __init__.py

CORS configuration - Learned about same-origin policy and proper middleware setup

SQLAlchemy JSON fields - Used Column(JSON) for storing skills array

Key Takeaways
FastAPI's automatic validation saves development time

SQLite is perfect for internal tools (no separate database server)

Modular architecture makes debugging easier

Background tasks work well for AI summary generation

Requirements
Create backend/requirements.txt:

txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-multipart==0.0.6
Quick Start with Sample Data
The database auto-creates with 3 sample candidates:

John Smith (Senior Software Engineer)

Sarah Johnson (Frontend Developer)

Michael Chen (DevOps Engineer)

Testing the API
Open Swagger documentation: http://127.0.0.1:8000/docs

Or test with Python:

python
import requests

# Get all candidates
response = requests.get('http://127.0.0.1:8000/candidates')
print(response.json())

# Submit score
response = requests.post('http://127.0.0.1:8000/candidates/1/scores', 
    json={'category': 'technical', 'score': 5})
print(response.json())
Troubleshooting
Backend not starting?

bash
# Check if uvicorn is installed
pip list | findstr uvicorn

# Reinstall if needed
pip install --force-reinstall uvicorn fastapi
Frontend can't connect?

Verify backend is running on port 8000

Check CORS settings in main.py

Use 127.0.0.1 not localhost

Database errors?

Delete techkraft.db and restart server to recreate

Check write permissions in backend folder

License
Internal use for TechKraft recruitment process.

text

This shorter version includes all the required sections:
- Setup and run instructions
- ADR section (3 decisions)
- Debugging bug identification
- Learning reflection
- Example API calls (curl commands)


 PS C:\techkraft\backend> python main.py
 PS C:\techkraft\frontend> python -m http.server 3000 --bind 127.0.0.1
