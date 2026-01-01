import os
import httpx
from fastapi import HTTPException

LDA_BASE_URL = "https://lda.senate.gov/api/v1/filings/"

def require_api_key() -> str:
    api_key = os.getenv("LDA_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Missing LDA_API_KEY environment variable")
    return api_key

def lda_headers(api_key: str) -> dict:
    return {"Authorization": f"Token {api_key}"}

async def lda_ping() -> dict:
    api_key = require_api_key()

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            r = await client.get(
                LDA_BASE_URL,
                headers=lda_headers(api_key),
                params={"page_size": 1},
            )
            r.raise_for_status()
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Senate LDA API timed out")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

    data = r.json()
    results = data.get("results") or [{}]
    first = results[0] if results else {}
    return {
        "status": "ok",
        "count": data.get("count"),
        "next": data.get("next"),
        "sample_keys": list(first.keys()),
    }

async def lda_list_filings(page_size: int, extra_params: dict) -> list[dict]:
    api_key = require_api_key()

    params = {"page_size": page_size}
    params.update(extra_params)

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            r = await client.get(
                LDA_BASE_URL,
                headers=lda_headers(api_key),
                params=params,
            )
            r.raise_for_status()
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Senate LDA API timed out")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

    data = r.json()
    return data.get("results") or []
