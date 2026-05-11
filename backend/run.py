# run.py
import uvicorn

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Starting Candidate Review API with SQLite")
    print("=" * 50)
    print("📊 API Documentation: http://127.0.0.1:8000/docs")
    print("💾 Database: candidates.db (SQLite)")
    print("=" * 50)
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )