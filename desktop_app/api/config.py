import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ApiConfig:
    base_url: str
    timeout_seconds: float
    health_path: str


def load_api_config() -> ApiConfig:
    base_url = os.getenv("HR_API_BASE_URL", "http://localhost:3000/api").rstrip("/")
    timeout_raw = os.getenv("HR_API_TIMEOUT_SEC", "8")
    try:
        timeout = max(1.0, float(timeout_raw))
    except ValueError:
        timeout = 8.0

    health_path = os.getenv("HR_API_HEALTH_PATH", "/health")
    if not health_path.startswith("/"):
        health_path = f"/{health_path}"

    return ApiConfig(base_url=base_url, timeout_seconds=timeout, health_path=health_path)
