"""
서버 실행 진입점
실행: python run.py
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    print(f"\n{'='*50}")
    print(f"  Venture - IT 공모전 서버 시작")
    print(f"  http://localhost:{port}")
    print(f"  API 문서: http://localhost:{port}/docs")
    print(f"{'='*50}\n")
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )
