"""FastAPI Application for PhishGuard inference service."""

from __future__ import annotations

from contextlib import asynccontextmanager
import json
import logging
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api.rate_limiter import limiter
from src.api.schemas import CheckRequest, CheckResponse, ModelInfoResponse
from src.features.reasons import generate_reasons
from src.model.predictor import PhishGuardModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Global model and metadata state
_MODEL_PREDICTOR: PhishGuardModel | None = None
_MODEL_METADATA: dict | None = None

MAX_URL_LENGTH = 2048
ALLOWED_SCHEMES = {"http", "https"}


def load_model_and_metadata() -> None:
    """Ensure model and metadata are loaded into memory."""
    global _MODEL_PREDICTOR, _MODEL_METADATA
    if _MODEL_PREDICTOR is not None:
        return

    model_path = Path("models/latest.joblib")
    if not model_path.exists():
        model_path = Path("models/best_model.joblib")

    if model_path.exists():
        try:
            _MODEL_PREDICTOR = PhishGuardModel(model_path)
            logger.info("Model %s loaded successfully.", _MODEL_PREDICTOR.model_name)
        except Exception as exc:
            logger.error("Failed to load model artifact: %s", exc)
            _MODEL_PREDICTOR = None

    metadata_path = Path("models/metadata.json")
    if metadata_path.exists():
        with open(metadata_path, encoding="utf-8") as f:
            _MODEL_METADATA = json.load(f)
    else:
        _MODEL_METADATA = {}


# Eager load on module import so TestClient works without explicit lifespan context
load_model_and_metadata()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for ASGI servers."""
    load_model_and_metadata()
    yield
    logger.info("Shutting down PhishGuard API service.")


app = FastAPI(
    title="PhishGuard API",
    description="Detektor Link Phishing berbasis Machine Learning pada Fitur Lexical & Host URL.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return clean 422 JSON response."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()[0]["msg"] if exc.errors() else "Validation error"},
    )


@app.get("/api/health")
def health_check() -> dict[str, Any]:
    """Health check endpoint confirming API status and model readiness."""
    is_ready = _MODEL_PREDICTOR is not None and _MODEL_PREDICTOR.model is not None
    version = _MODEL_METADATA.get("version", "1.0.0") if _MODEL_METADATA else "1.0.0"
    return {
        "status": "ok",
        "model_loaded": is_ready,
        "version": version,
    }


@app.get("/api/model-info", response_model=ModelInfoResponse)
def get_model_info():
    """Return detailed metadata, hyperparameters, and test metrics of active model."""
    if not _MODEL_METADATA:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Informasi model belum tersedia.",
        )

    return ModelInfoResponse(
        model_name=_MODEL_METADATA.get("model_name", "LightGBM"),
        model_version=_MODEL_METADATA.get("version", "1.0.0"),
        trained_at=_MODEL_METADATA.get("trained_at", ""),
        feature_count=_MODEL_METADATA.get("feature_count", 49),
        train_samples=_MODEL_METADATA.get("train_samples", 7550),
        test_samples=_MODEL_METADATA.get("test_samples", 1690),
        metrics_test=_MODEL_METADATA.get("metrics_test", {}),
        metrics_validation=_MODEL_METADATA.get("metrics_validation", {}),
        threshold_config=_MODEL_METADATA.get("threshold_config", {}),
        top_features=_MODEL_METADATA.get("top_features", []),
    )


def sanitize_url_for_logging(url_str: str) -> str:
    """Mask sensitive query parameters and auth info before logging."""
    try:
        parsed = urlparse(url_str)
        safe_netloc = parsed.netloc.split("@")[-1] if "@" in parsed.netloc else parsed.netloc
        return f"{parsed.scheme}://{safe_netloc}{parsed.path}"
    except Exception:
        return "[redacted_url]"


@app.post("/api/check", response_model=CheckResponse)
def check_url(payload: CheckRequest, request: Request):
    """
    Check if a given URL is phishing or legitimate based on lexical & host features.
    Does NOT open or download the target page (safe from SSRF).
    """
    limiter.check(request)

    global _MODEL_PREDICTOR
    if _MODEL_PREDICTOR is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model belum siap dimuat.",
        )

    raw_url = payload.url

    # 1. Check length (413 if too long)
    if len(raw_url) > MAX_URL_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"URL terlalu panjang ({len(raw_url)} karakter). Maksimum {MAX_URL_LENGTH} karakter.",
        )

    # 2. Check empty or whitespace
    clean_url = raw_url.strip()
    if not clean_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL tidak boleh kosong.",
        )

    # 3. Parse and validate scheme
    if ":" in clean_url:
        scheme_candidate = clean_url.split(":", 1)[0].lower()
        if (
            scheme_candidate
            and scheme_candidate[0].isalpha()
            and all(c.isalnum() or c in "+-." for c in scheme_candidate)
            and "/" not in scheme_candidate
            and "." not in scheme_candidate
        ):
            if scheme_candidate not in ALLOWED_SCHEMES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Skema URL '{scheme_candidate}' tidak didukung. Gunakan HTTP atau HTTPS.",
                )

    check_url_str = clean_url
    if "://" not in check_url_str:
        if check_url_str.startswith("//"):
            check_url_str = "http:" + check_url_str
        else:
            check_url_str = "http://" + check_url_str

    try:
        parsed = urlparse(check_url_str)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format URL tidak valid.",
        )

    scheme = parsed.scheme.lower()
    if scheme not in ALLOWED_SCHEMES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Skema URL '{scheme}' tidak didukung. Gunakan HTTP atau HTTPS.",
        )

    netloc = parsed.netloc.strip()
    if not netloc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL tidak memiliki nama domain/host yang valid.",
        )

    # Check for non-printable control characters
    if any(ord(c) < 32 for c in clean_url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL mengandung karakter kontrol ilegal.",
        )

    # 4. Predict using inference model
    try:
        prediction = _MODEL_PREDICTOR.predict_url(clean_url)
    except Exception as exc:
        logger.error("Inference error on URL '%s': %s", sanitize_url_for_logging(clean_url), exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan internal saat memeriksa URL.",
        )

    score = float(prediction["phishing_probability"])
    risk_level = str(prediction["risk_level"]).lower()
    is_phishing = bool(prediction["is_phishing"])
    label = "phishing" if is_phishing else "legitimate"
    features = prediction["features"]
    contributions = prediction.get("contributions", {})

    # 5. Generate human-readable reasons in Indonesian
    reasons = generate_reasons(clean_url, features, score, risk_level, contributions=contributions)

    model_version = _MODEL_METADATA.get("version", "1.0.0") if _MODEL_METADATA else "1.0.0"
    disclaimer = (
        "Hasil ini merupakan perkiraan berbasis model machine learning pada struktur URL, "
        "bukan jaminan mutlak. Jangan memasukkan data rahasia atau kredensial pada situs yang mencurigakan."
    )

    return CheckResponse(
        url=clean_url,
        label=label,
        score=score,
        risk_level=risk_level,
        reasons=reasons,
        model_version=model_version,
        disclaimer=disclaimer,
    )


# Serve frontend static assets and UI
WEB_DIR = Path("web")
if WEB_DIR.exists() and (WEB_DIR / "index.html").exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend_index():
        """Serve the single page frontend application."""
        return FileResponse(WEB_DIR / "index.html")
