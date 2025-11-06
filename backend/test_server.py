"""
Minimal test server to verify uvicorn works
"""
from fastapi import FastAPI

app = FastAPI(title="Water API")

@app.get("/")
def root():
    return {"message": "Server is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
