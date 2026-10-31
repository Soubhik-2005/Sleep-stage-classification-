# SleepAI – Sleep Stage Classification

End-to-end system: **EDF recording → 30 s epochs → 1D CNN → Wake/N1/N2/N3/REM → hypnogram dashboard.**

```
ml/        data loading, preprocessing, CNN, training, evaluation, inference
backend/   FastAPI (upload, background analysis, results, signal slices, history) + MongoDB/JSON store
frontend/  React + Vite + Tailwind + Recharts dashboard
scripts/   smoke tests and demo-file generator
```

## 1. Setup
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
```

## 2. Train on real data (Sleep-EDF)
```bash
python -m ml.src.train --download 10 --epochs 30     # downloads 10 subjects via MNE (~1 GB), trains, evaluates
# or, if you already downloaded PSG/Hypnogram files into dataset/raw/:
python -m ml.src.train --data-dir dataset/raw
```
Output: `ml/saved_models/sleep_stage_model.keras`, `preprocessing_config.json` (normalization stats, channels,
filter, class map, test metrics). Split is **by subject** (70/15/15); normalization uses training data only;
class-weighting is applied for the rare N1 class. More subjects (`--download 40` or more) → better results.

> The repo ships a model trained on **synthetic** signals so the app runs immediately. Its predictions are meaningless
> (the UI shows a warning). Overwrite it by running the command above.

## 3. Run the app
```bash
uvicorn backend.app.main:app --reload --port 8000     # terminal 1  (from project root)
cd frontend && npm run dev                            # terminal 2  -> http://localhost:5173
```
Try it without real data: `python -m scripts.make_demo_edf` then upload `sample_data/demo_night.edf`.

Optional MongoDB: `docker compose up -d && export MONGO_URI=mongodb://localhost:27017` (otherwise JSON files in `backend/data/db`).

## API
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | status, DB type, model availability |
| POST | `/api/upload` | upload EDF (validated: extension, header, size) |
| POST | `/api/analyze/{id}` | start background analysis (poll results for progress) |
| GET | `/api/results/{id}` | status + stages, probabilities, sleep statistics |
| GET | `/api/recordings/{id}/signal?epoch=N` | preprocessed waveform for epoch N |
| GET | `/api/history` | all recordings with summaries |
| DELETE | `/api/recordings/{id}` | delete recording + results |

## Tests
```bash
python -m scripts.smoke_ml     # MNE loader round-trip
python -m scripts.smoke_api    # upload → analyze → results → delete (needs a model)
```

## Limitations
Educational/research system. Not clinically validated; not a substitute for expert polysomnography scoring.
Input EDFs must contain `EEG Fpz-Cz`, `EEG Pz-Oz`, `EOG horizontal`. No user authentication yet — add it before any multi-user or
production deployment, and protect/retain uploaded physiological data appropriately.
