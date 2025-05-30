from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from main import scrape_page, analyze_with_gemini, revise_article_with_gemini

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    url: str

class ReviseRequest(BaseModel):
    content: str
    suggestions: str

@app.post("/analyze")
def analyze_doc(request: AnalyzeRequest):
    url = request.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    try:
        content = scrape_page(url)
        analysis = analyze_with_gemini(content, url)
        return {content, analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/revise")
def revise_doc(request: ReviseRequest):
    try:
        revised_article = revise_article_with_gemini(request.content, request.suggestions)
        return {"revised": revised_article}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
