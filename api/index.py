import os, re, httpx, xml.etree.ElementTree as ET
from fastapi import FastAPI, HTTPException, Query

PUBLICDATA_KEY = os.getenv("PUBLICDATA_KEY", "")
MOIS_BASE = "http://apis.data.go.kr/1741000/StanReginCd"
MOIS_PATH = "getStanReginCdList"

app = FastAPI(title="RegionCd Lookup", version="1.1.0")

def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()

async def _fetch_from_mois(locatadd_nm: str, resp_type: str) -> tuple[list[dict], int|None]:
    params = {
        "ServiceKey": PUBLICDATA_KEY,
        "type": resp_type,
        "flag": "Y",
        "pageNo": "1",
        "numOfRows": "5",
        "locatadd_nm": locatadd_nm,
    }
    url = f"{MOIS_BASE}/{MOIS_PATH}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url, params=params)
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"MOIS API error {r.status_code}")
    if resp_type == "json":
        data = r.json()
        root = data.get("StanReginCd", {})
        rows = root.get("row", [])
        if isinstance(rows, dict):
            rows = [rows]
        # normalize string values
        rows = [{k: ("" if v is None else str(v)) for k, v in row.items()} for row in rows]
        return rows, None
    # xml
    text = r.text
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return [], None
    rows = []
    for row in root.findall("row"):
        item = {child.tag: (child.text or "").strip() for child in row}
        rows.append(item)
    return rows, None

@app.get("/healthz")
def healthz():
    return {"ok": True, "version": app.version}

@app.get("/region_cd")
async def region_cd(
    text: str = Query(..., description="법정동 입력 (예: 읍내리, 서초구 양재동)"),
    type: str = Query("json", description="MOIS 응답 포맷: json | xml (default=json)"),
):
    if not PUBLICDATA_KEY:
        raise HTTPException(status_code=500, detail="PUBLICDATA_KEY not set")
    t = type.lower().strip()
    if t not in ("json", "xml"):
        t = "json"
    q = _normalize_text(text)
    if not q:
        return {"region_cd": None}

    rows, _ = await _fetch_from_mois(q, t)
    if not rows:
        return {"region_cd": None}
    # 첫 번째 결과만 반환
    rc = rows[0].get("region_cd")
    return {"region_cd": rc if rc else None}
