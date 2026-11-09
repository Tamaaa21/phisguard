# Setup

## Prasyarat
- Python 3.11+
- Git
- (Opsional) Docker, Node.js bila memakai frontend React

## Langkah
```bash
git clone <url-repo> phishguard
cd phishguard
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Perintah utama (target, dibuat bertahap di milestone)
```bash
python -m src.training.prepare_data      # M02: siapkan dataset
python -m src.training.train             # M04-M05: latih & simpan model
uvicorn src.api.main:app --reload        # M06: jalankan API di localhost:8000
pytest                                   # M09: jalankan tes
```

## requirements.txt awal
```
fastapi
uvicorn[standard]
scikit-learn
xgboost
pandas
numpy
tldextract
joblib
pydantic
pytest
httpx
```

## Variabel lingkungan
| Nama | Fungsi | Default |
|---|---|---|
| `MODEL_PATH` | Lokasi artefak model | `models/latest.joblib` |
| `RATE_LIMIT_PER_MIN` | Batas permintaan per IP | `30` |
| `MAX_URL_LENGTH` | Panjang URL maksimum | `2048` |
