# api_client.py
from __future__ import annotations

import os
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests


# -----------------------------
# Config
# -----------------------------
@dataclass
class ApiConfig:
    base_url: str
    token: str
    timeout_seconds: int = 20
    client_id: str = "kim-varmap-ui"


def load_api_config() -> Optional[ApiConfig]:
    """
    Read API connection details from environment variables.
    Works well for Streamlit Cloud secrets too.
    """
    base_url = os.getenv("KIM_API_BASE_URL", "").strip()
    token = os.getenv("KIM_API_TOKEN", "").strip()
    client_id = os.getenv("KIM_CLIENT_ID", "kim-varmap-ui").strip()

    if not base_url or not token:
        return None

    # normalize base_url (no trailing slash)
    base_url = base_url.rstrip("/")
    return ApiConfig(base_url=base_url, token=token, client_id=client_id)


# -----------------------------
# Low-level HTTP
# -----------------------------
class KimApiError(RuntimeError):
    pass


def _headers(cfg: ApiConfig) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {cfg.token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Client-Id": cfg.client_id,
    }


def _request_json(
    cfg: ApiConfig,
    method: str,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    url = f"{cfg.base_url}{path}"
    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=_headers(cfg),
            params=params,
            data=json.dumps(payload) if payload is not None else None,
            timeout=cfg.timeout_seconds,
        )
    except requests.RequestException as exc:
        raise KimApiError(f"API request failed: {exc}") from exc

    if response.status_code >= 400:
        # try to show useful message
        try:
            details = response.json()
        except Exception:
            details = response.text
        raise KimApiError(f"API error {response.status_code} on {method} {path}: {details}")

    # response might be empty (rare) — handle safely
    if not response.text.strip():
        return {}
    return response.json()


# -----------------------------
# Public functions (what Streamlit uses)
# -----------------------------
def api_is_configured() -> bool:
    return load_api_config() is not None


def healthcheck() -> Tuple[bool, str]:
    """
    If Jan exposes a real health endpoint, use it.
    If not, we treat "configured" as the first check.
    """
    cfg = load_api_config()
    if cfg is None:
        return False, "Missing KIM_API_BASE_URL or KIM_API_TOKEN"

    # Try a common health path. If Jan uses something else, we’ll adjust later.
    # If it fails, we still return a helpful message.
    try:
        _request_json(cfg, "GET", "/health")
        return True, "OK"
    except KimApiError as exc:
        return False, str(exc)


def pull_mappings(project_id: str) -> pd.DataFrame:
    """
    Pull current mappings for a project.
    Expects API to return either:
      - {"rows": [...]}  OR
      - [...] (list of rows)
    Each row should include: row_key + fields.
    """
    cfg = load_api_config()
    if cfg is None:
        raise KimApiError("API not configured (missing env vars).")

    data = _request_json(cfg, "GET", "/v1/mappings", params={"project_id": project_id})

    rows: List[Dict[str, Any]]
    if isinstance(data, dict) and "rows" in data:
        rows = data["rows"] or []
    elif isinstance(data, list):
        rows = data
    else:
        rows = []

    df = pd.DataFrame(rows)

    # Normalize to your app convention:
    # backend row_key -> app __row_key__
    if "row_key" in df.columns and "__row_key__" not in df.columns:
        df["__row_key__"] = df["row_key"]

    return df


def upsert_mappings(project_id: str, df_rows: pd.DataFrame, dry_run: bool = False) -> Dict[str, Any]:
    """
    Upsert rows to backend.
    We send rows as JSON dicts.
    """
    cfg = load_api_config()
    if cfg is None:
        raise KimApiError("API not configured (missing env vars).")

    rows = df_rows.to_dict(orient="records")

    payload = {
        "project_id": project_id,
        "client_id": cfg.client_id,
        "dry_run": dry_run,
        "rows": rows,
    }

    return _request_json(cfg, "POST", "/v1/mappings:upsert", payload=payload)


def delete_mappings(project_id: str, row_keys: List[str]) -> Dict[str, Any]:
    """
    Delete rows by row_key.
    """
    cfg = load_api_config()
    if cfg is None:
        raise KimApiError("API not configured (missing env vars).")

    payload = {
        "project_id": project_id,
        "client_id": cfg.client_id,
        "row_keys": row_keys,
    }

    return _request_json(cfg, "POST", "/v1/mappings:delete", payload=payload)
