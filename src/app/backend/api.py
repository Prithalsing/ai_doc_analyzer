from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Literal

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

class CategoryData(BaseModel):
    score: Literal["Excellent", "Good", "Fair", "Poor"]
    issues: List[str]
    suggestions: List[str]

class Analysis(BaseModel):
    readability: CategoryData
    structure: CategoryData
    completeness: CategoryData
    style_guidelines: CategoryData

class AnalysisResponse(BaseModel):
    content: str
    analysis: Analysis

class ReviseRequest(BaseModel):
    content: str
    suggestions: Dict[str, CategoryData]  # Change Analysis to Dict[str, CategoryData]

class ReviseResponse(BaseModel):
    revised: str

@app.post("/analyze", response_model=AnalysisResponse)
def analyze_doc(request: AnalyzeRequest):
    url = request.url.strip()   
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    try:
        content = scrape_page(url)
        analysis = analyze_with_gemini(content, url)
        
        # Validate analysis structure
        if not all(key in analysis for key in ["readability", "structure", "completeness", "style_guidelines"]):
            raise ValueError("Invalid analysis structure")
            
        return {
            "content": content,
            "analysis": analysis
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/revise", response_model=ReviseResponse)
def revise_doc(request: ReviseRequest):
    if not request.content or not request.suggestions:
        raise HTTPException(status_code=400, detail="Content and suggestions are required")
    try:
        # Convert suggestions to dict format that revise_article_with_gemini expects
        suggestions_dict = {
            k: {
                'score': v.score,
                'issues': v.issues,
                'suggestions': v.suggestions
            } for k, v in request.suggestions.items()
        }
        revised = revise_article_with_gemini(request.content, suggestions_dict)
        return {"revised": revised}
    except Exception as e:
        print(f"Error in revision: {str(e)}")  # Add debugging
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
