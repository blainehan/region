import os, re, httpx
from fastapi import FastAPI, HTTPException, Query

PUBLICDATA_KEY = os.getenv("PUBLICDATA_KEY", "")
MOIS_BASE = "http://apis.data.go.kr/1741000/StanReginCd"
MOIS_PATH = "getStanReginCdList"

app = FastAPI(title="RegionCd Lookup", version="1.0.0")

def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

@app.get("/region_cd")
async def region_cd(
    text: str = Query(..., description="법정동 입력 (예: 읍내리, 서초구 양재동)"),
    type: str = Query("json", description="MOIS 응답 포맷: json | xml (default=json)"),
):
    if not PUBLICDATA_KEY:
        raise HTTPException(status_code=500, detail="PUBLICDATA_KEY not set")

    params = {
        "ServiceKey": PUBLICDATA_KEY,
        "type": type,
        "flag": "Y",
        "pageNo": "1",
        "numOfRows": "5",
        "locatadd_nm": _normalize_text(text),
    }
    url = f"{MOIS_BASE}/{MOIS_PATH}"

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url, params=params)
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail=f"MOIS API error {r.status_code}")
        data = r.json() if type == "json" else None  # XML은 단순화

    try:
        rows = data["StanReginCd"]["row"]
        if isinstance(rows, dict):
            return {"region_cd": rows["region_cd"]}
        elif isinstance(rows, list) and rows:
            return {"region_cd": rows[0]["region_cd"]}
    except Exception:
        pass

    return {"region_cd": None}
