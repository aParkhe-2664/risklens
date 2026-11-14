# RiskLens: AI-Based Portfolio Risk Analysis (Indian markets)

- `docs/index.html`: frontend (hosted on GitHub Pages). Set `const API=''` near the top to your backend URL.
- `backend/`: FastAPI + yfinance API.

## Run the backend locally
    cd backend
    python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    uvicorn main:app --reload        # http://127.0.0.1:8000/api/health

Then set `const API='http://127.0.0.1:8000'` in `docs/index.html` and open it in a browser.

## Deploy
Frontend: GitHub repo -> Settings -> Pages -> branch `main`, folder `/docs`.
Backend (Render): root dir `backend`, build `pip install -r requirements.txt`,
start `uvicorn main:app --host 0.0.0.0 --port $PORT`, env `ALLOWED_ORIGINS=https://<you>.github.io`.

Academic project; historical data only, not financial advice.
