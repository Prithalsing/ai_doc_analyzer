# 🔍 MoEngage Doc Analyzer

This project provides an AI-powered tool that analyzes and revises MoEngage documentation using LangChain. Two versions are available: a backend-only version with full LangChain integration, and a simplified fullstack version for demonstration.

---

## 🚀 Setup Instructions

### ✅ Backend-Only (With Full LangChain Integration)

This version uses LangChain to analyze, summarize, and revise documentation intelligently.

```bash
cd backend
python main.py
```

**Requirements**:
- Python 3.9+
- Install dependencies using `pip install -r requirements.txt`
- An OpenAI API key (set as an environment variable: `OPENAI_API_KEY=your_key_here`)

---

### 🌐 Fullstack Version (Simplified Backend)

This version runs a minimal FastAPI backend with a frontend UI.

#### 1. Start the backend
```bash
cd src/app/backend
python api.py
```

#### 2. Start the frontend
```bash
npm install
npm run dev
```

**Note**: This backend does **not** include LangChain functionality. For full features, use the `backend_just` version.

---

## 🧠 Assumptions

- MoEngage documentation is consistent in format and content structure.
- Users want a tool that can not only summarize but also improve documentation quality using language models.
- The backend and frontend are run separately; no Docker or orchestration is assumed.
- Output revisions are saved/displayed for user inspection but not automatically published.

---

## 🎨 Design Choices & Approach

- **LangChain** was used to build modular, flexible language workflows (Agents, Tools).
- **FastAPI** powers the API for both backend setups due to its speed and easy async support.
- **Frontend (if used)** is built with a simple React/Next.js stack to demonstrate interactivity.
- The LangChain-based backend parses and critiques input text with a multi-step agent, following style and clarity guidelines inspired by industry documentation standards.
- A basic file loader or web scraper parses input documentation, which is then processed in stages (summarization, critique, revision).

---

## 🛠 Challenges & Future Work

### Challenges Faced
- Integrating LangChain Agents required extensive prompt tuning to ensure useful revisions.
- Ensuring consistent formatting in output was difficult without custom templates.
- The simplified backend used in the fullstack version had to forego LangChain to keep response times low and integration simple.

### Future Improvements
- Add better frontend UX for viewing side-by-side original vs. revised outputs.
- Integrate MoEngage API (if available) to fetch docs automatically.
- Include version control and change tracking on revised documents.

---


### OUTPUT CAN BE SEEN WITH SEPARATE FILE NAME AS OUTPUT IN REPO
