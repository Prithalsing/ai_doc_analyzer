
## 🔄 Project Execution Instructions

### ✅ Backend-Only (With Full LangChain Integration)
To run only the backend with full LangChain-based analysis and revision functionality:

```bash
cd backend_just
python main.py
```

### 🌐 Fullstack Version (Simplified Backend)

If you'd like to run the fullstack version of the app:

1. **Start the FastAPI backend:**
```bash
cd src/app/backend
python api.py
```

2. **Start the frontend:**
```bash
npm run dev
```

> ⚠️ **Note:** The backend used with the frontend is a simplified version **without LangChain integration**.  
For the complete backend functionality, please refer to the `backend_just` folder.
