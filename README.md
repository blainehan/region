# RegionCd Lookup

간단한 FastAPI 서버로, 행안부 법정동코드 API를 호출하여 입력한 법정동의 `region_cd`를 반환합니다.

## 설치

```bash
pip install -r requirements.txt
uvicorn api.index:app --reload --port 8000
```

## 사용법

로컬 실행 후 예시:

```bash
curl "http://127.0.0.1:8000/region_cd?text=읍내리"
# {"region_cd": "2871040022"}
```

## 배포

- GitHub 업로드 후 Vercel에서 새 프로젝트로 Import
- Environment Variables:
  - `PUBLICDATA_KEY`: 공공데이터포털 Decoding 서비스키
