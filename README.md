# COSC-4368-SmartWatt
Team Members: Jose Conde, Clark Horak, Adam Nguyen, Ben Tuason

Our code was written in Google Colab.

How to run: 
Ensure you have a virtual Environment created on your system.
activate your Virtual Environment 


install these packages to run: Tensorflow, numpy, pandas, matplotlib, and meteostat

pip install Tensorflow
pip install numpy
pip install pandas
pip install matplotlib
pip install meteostat
pip install keras
pip install keras-models

Have a virtual environment set up to plot 

further questions please feel free to reach out to any collaborators.

Project Description

This project was completed in collaboration with a startup called SmartWatts, which provided us with two years of residential energy usage data — approximately 900,000 records collected at 15-minute intervals. Our task was to explore the dataset, generate insights, and propose ways to model and forecast energy consumption patterns.

We hypothesized that temperature would be a key driver of energy usage, especially during extreme heat in Texas, when cooling demand spikes. To test this, we integrated weather data from the Meteostat API, aligning historical temperature data with energy usage timestamps. Since the API only included data up to the current date, we needed to forecast both temperature and energy usage into the future.

The data was preprocessed by removing irrelevant features, handling missing values, and scaling to account for outliers. Each user’s energy profile was isolated to train models individually, with generalization tested across users. We found a strong correlation between temperature and energy use, validating our hypothesis.

For modeling, we trained and evaluated three deep learning architectures: Recurrent Neural Networks (RNNs), Long Short-Term Memory (LSTM), and Gated Recurrent Units (GRU). After comparing model performance, LSTM outperformed the others with a 97% accuracy rate. We validated this by holding out a full month of data and comparing forecasted values to actual readings, achieving approximately 95% match. Confidence intervals were used to assess the reliability of the forecasts.



# SmartWatts Pipeline

Personal ML data engineering project.  
Ingests historical 15-min interval smart meter data, builds a
bronze/silver/gold warehouse in BigQuery, trains four forecasting
models on Google Colab (free T4 GPU), generates daily forecasts,
and serves a gold layer to Power BI.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ONE-TIME SETUP (local)                  │
│                                                             │
│  CSV file                                                   │
│     │                                                       │
│     ▼                                                       │
│  gcs_upload.py ─────────────────────► GCS (raw zone)        │
│                                                             │
│  prefetch_weather.py ───────────────► GCS (weather parquet) │
│                                                             │
│  bq_schema.py ──────────────────────► BigQuery tables       │
│                                                             │
│  ingest.py ─────────────────────────► BigQuery bronze/silver│
│    reads CSV + weather from GCS                             │
│    resamples 15min → hourly                                 │
│    merges temperature                                       │
│                                                             │
│  smartwatts_retrain.ipynb ──────────► GCS model registry    │
│    open in Colab manually first time                        │
│    trains RNN / LSTM / GRU / Prophet                        │
│    saves models to GCS                                      │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  SCHEDULED (Cloud Run + Scheduler)          │
│                                                             │
│  Cloud Scheduler ──► Cloud Run Job                          │
│  (daily 02:00 UTC)   cloudrun_job.py                        │
│                        loads models from GCS                │
│                        generates 24hr forecasts             │
│                        writes → BigQuery silver/gold        │
│                                                             │
│  Weekly (manual)   open Colab, run retrain notebook         │
│                        retrains all 4 models on latest data │
│                        saves updated models → GCS           │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                     SERVING LAYER                           │
│                                                             │
│  BigQuery Gold Views                                        │
│  ├── vw_model_comparison        all 4 models side by side   │
│  ├── vw_best_forecast           Prophet point estimate + CI │
│  └── vw_historical_vs_forecast  full timeline per ESIID     │
│                   │                                         │
│                   ▼                                         │
│              Power BI Desktop                               │
│         (BigQuery native connector)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Warehouse Layers

```
Bronze  ── raw_meter_usage
           Exactly what came out of the CSV after hourly resample.
           Source of truth — never overwritten after initial load.

Silver  ── hourly_meter_usage
           Bronze + weather merged, nulls handled, validated.
           What the models train and predict on.

Gold    ── vw_model_comparison
           vw_best_forecast
           vw_historical_vs_forecast
           Aggregated, Power BI ready views.
           These are what you connect to in Power BI Desktop.
```

---

## File Overview

```
smartwatts_pipeline/
├── gcs_upload.py              Upload raw CSV to GCS (run once)
├── bq_schema.py               Create BigQuery dataset + tables (run once)
├── prefetch_weather.py        Pull Houston hourly weather → GCS (run once)
├── ingest.py                  Clean CSV + merge weather → BigQuery bronze/silver
├── forecast_pipeline.py       Predict: load models from GCS → write BQ silver/gold
├── cloudrun_job.py            Cloud Run entrypoint — wraps forecast_pipeline
├── Dockerfile                 Packages forecast_pipeline for Cloud Run
├── smartwatts_retrain.ipynb   Colab GPU notebook: retrain all 4 models → GCS
├── bq_gold_layer.sql          Gold layer view definitions for Power BI
├── requirements.txt           Python dependencies
└── README.md
```

---

## Setup Order (run once)

```
Step 1 — gcs_upload.py         Upload CSV to GCS
Step 2 — bq_schema.py          Provision BigQuery tables
Step 3 — prefetch_weather.py   Pull Houston weather → GCS
Step 4 — ingest.py --dry-run   Sanity check before writing
Step 5 — ingest.py             Load bronze/silver data to BQ
Step 6 — retrain.ipynb         Open in Colab, run manually to seed models in GCS
Step 7 — bq_gold_layer.sql     Run in BQ console to create gold views
Step 8 — cloudrun_job.py       Deploy to Cloud Run, set Cloud Scheduler trigger
Step 9 — Power BI              Connect Desktop to BQ gold views
```

---

## How Scheduling Works

**Daily forecast — Cloud Run + Cloud Scheduler**
Cloud Scheduler pings the Cloud Run job at 02:00 UTC every day.
The container loads saved models from GCS, generates 24 hours of
forecasts per ESIID, and writes them to BigQuery. No GPU needed.
Cost: Cloud Run free tier covers this easily. Cloud Scheduler ~$0.10/month.

**Weekly retrain — manual Colab**
Open `smartwatts_retrain.ipynb` in Colab, connect to a T4 GPU runtime,
and run all cells. The notebook pulls the latest data from BigQuery
(historical + accumulated forecasts), retrains all 4 models, and saves
updated weights to GCS. Takes ~30–60 minutes on a free T4.
Next daily Cloud Run job automatically picks up the new models.

---

## Tech Stack

| Layer         | Technology          | Cost         | Why                                      |
|---------------|---------------------|--------------|------------------------------------------|
| Storage       | Google Cloud Storage| Free (5GB)   | Stores CSV, weather, models, notebook    |
| Warehouse     | BigQuery            | Free tier    | 10GB storage + 1TB queries/month free    |
| Training      | Google Colab        | Free         | T4 GPU, run manually weekly              |
| Scheduling    | Cloud Scheduler     | ~$0.10/month | Triggers daily Cloud Run job             |
| Compute       | Cloud Run           | Free tier    | Runs forecast container daily            |
| Visualization | Power BI Desktop    | Free         | Connects natively to BigQuery            |
| Orchestration | None                | $0           | Too small for Composer ($300/month)      |

---

## Models

| Model   | Type           | Input → Output    | Notes                                    |
|---------|----------------|-------------------|------------------------------------------|
| RNN     | Deep learning  | 24hrs → 24hrs     | Baseline, fast                           |
| LSTM    | Deep learning  | 24hrs → 24hrs     | Better long-range dependencies           |
| GRU     | Deep learning  | 24hrs → 24hrs     | Faster than LSTM, similar accuracy       |
| Prophet | Additive model | full history      | Uses temperature as external regressor   |

All deep learning models: MinMax scaled, Adam/SGD optimizer, 10 epochs, batch size 64.

---

## GCS Bucket Layout

```
gs://YOUR_BUCKET/
├── raw/smartwatts/              Raw CSV (never modified)
├── weather/
│   └── houston_hourly.parquet   Prefetched Meteostat data
├── models/
│   └── {esiid}/{model}/
│       ├── model.keras          RNN / LSTM / GRU weights
│       ├── model.pkl            Prophet model
│       ├── scaler.pkl           MinMaxScaler
│       └── metadata.json        trained_at, MAE, RMSE, MAPE
└── notebook_outputs/            Executed Colab notebooks per run
```

---

## BigQuery Dataset Layout

```
smartwatts/
├── raw_meter_usage              Bronze — hourly kWh per ESIID
├── hourly_meter_usage           Silver — cleaned + weather merged
├── forecasted_meter_usage       Silver — model predictions + CI
├── model_run_log                Silver — metrics per training run
├── vw_model_comparison          Gold  — all 4 models side by side
├── vw_best_forecast             Gold  — Prophet forecast + CI
└── vw_historical_vs_forecast    Gold  — full timeline per ESIID
```

---

## Power BI Setup

```
1. Open Power BI Desktop
2. Get Data → Google BigQuery
3. Sign in with your Google account
4. Select dataset: smartwatts
5. Load these views:
   - vw_historical_vs_forecast   (main timeline chart)
   - vw_model_comparison         (model performance comparison)
   - vw_best_forecast            (forecast with confidence bands)
6. Set scheduled refresh in Power BI Service if publishing
```

---
