"""RiskLens API: serves date-aligned Indian-market prices from yfinance."""
import os, time
import numpy as np, pandas as pd, yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sklearn.ensemble import IsolationForest

app = FastAPI(title="RiskLens API")
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")   # set to your GitHub Pages URL in production
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET"])

N = 253            # 1 year of NSE trading days (the frontend expects exactly this)
TTL = 15 * 60      # cache for 15 minutes to respect Yahoo rate limits
_cache = {}

def _download(symbols):
    key = ",".join(sorted(symbols))
    hit = _cache.get(key)
    if hit and time.time() - hit[0] < TTL:
        return hit[1]
    data = yf.download(list(dict.fromkeys(symbols + ["^NSEI"])), period="2y", auto_adjust=True,
                       progress=False, group_by="column")["Close"]
    nse_days = data["^NSEI"].dropna().index[-N:]          # align everything to NSE trading days
    data = data.reindex(nse_days).ffill()                  # crypto/forex values carried onto NSE days
    out = {
        "dates": [d.strftime("%d %b %y") for d in nse_days],
        "series": {c: [round(float(v), 4) for v in data[c]]
                   for c in data.columns if c != "^NSEI" or "^NSEI" in symbols
                   if not data[c].isna().any()},           # drop symbols with gaps; frontend falls back to simulated
    }
    _cache[key] = (time.time(), out)
    return out

@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/prices")
def prices(symbols: str):
    syms = [s.strip() for s in symbols.split(",") if s.strip()][:60]
    if not syms:
        raise HTTPException(400, "No symbols")
    return _download(syms)

@app.get("/api/anomalies/{symbol}")
def anomalies(symbol: str):
    """Real IsolationForest drop detection (not yet wired into the frontend)."""
    close = yf.download(symbol, period="1y", auto_adjust=True, progress=False)["Close"].squeeze().dropna()
    r = np.log(close / close.shift(1)).dropna()
    X = pd.DataFrame({"r": r, "vol": r.rolling(20).std()}).dropna()
    flag = IsolationForest(contamination=0.03, random_state=0).fit_predict(X)
    hits = X.index[(flag == -1) & (X["r"] < 0)]
    return {"symbol": symbol, "dates": [d.strftime("%d %b %y") for d in hits]}
