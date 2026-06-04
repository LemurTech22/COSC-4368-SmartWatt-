# COSC-4368-SmartWatt
Team Members: Jose Conde, Clark Horak, Adam Nguyen, Ben Tuason

Our code was written in Google Colab.

How to run: 
You need a virtual environment of your choice, for this project i decieded to use UV. 
WHY? well it has a faster package resolution compared to the pip and runs more efficently. You'll notice the commands are similar but the only difference is the keyword `uv`.

Creating your Virtual Environment
You need: 
   cloned repo
   virtual environment of your choice like anaconda, uv, miniconda, etc.

**ensure you install virtual environment before proceeding. Ill provide commands for both uv and miniconda.**

1. Installation 
   
   Cd into the directory
   `cd COSC-4368-SMARTWATT-`
   
   create environment
   **Using Uv venv**
   `uv venv`
   `activate .venv/bin/activate`

   **miniconda**
   `conda create --name myenv` 
   `conda activate myenv`

2. Package Installation

   In the folder you'll see a requirements.txt to install all the necessary packages.

   **UV**
   `uv pip install -r requirements.txt`

   **miniconda**
   `pip install -r requirements.txt`


Project Description

This project was completed in collaboration with a startup called SmartWatts, which provided us with two years of residential energy usage data — approximately 900,000 records collected at 15-minute intervals. Our task was to explore the dataset, generate insights, and propose ways to model and forecast energy consumption patterns.

We hypothesized that temperature would be a key driver of energy usage, especially during extreme heat in Texas, when cooling demand spikes. To test this, we integrated weather data from the Meteostat API, aligning historical temperature data with energy usage timestamps. Since the API only included data up to the current date, we needed to forecast both temperature and energy usage into the future.

The data was preprocessed by removing irrelevant features, handling missing values, and scaling to account for outliers. Each user’s energy profile was isolated to train models individually, with generalization tested across users. We found a strong correlation between temperature and energy use, validating our hypothesis.

For modeling, we trained and evaluated three deep learning architectures: Recurrent Neural Networks (RNNs), Long Short-Term Memory (LSTM), and Gated Recurrent Units (GRU). After comparing model performance, LSTM outperformed the others with a 97% accuracy rate. We validated this by holding out a full month of data and comparing forecasted values to actual readings, achieving approximately 95% match. Confidence intervals were used to assess the reliability of the forecasts.


---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ONE-TIME SETUP (local)                  │
│                                                             │
│  CSV file, Weather API                                      │
│     │                                                       │
│     ▼                                                       │
│  gcs_upload.py ─────────────────────► GCS (raw zone)        │ │
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
├── gcs_upload.py              Upload raw CSV 
├── bq_schema.py               Create BigQuery dataset + tables (run once)
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
Step 1 — gcs_upload.py         Upload CSV & weather api into to GCS
Step 2 — bq_schema.py          Provision BigQuery tables
Step 3 — ingest.py --dry-run   Sanity check before writing
Step 4 — ingest.py             Load bronze/silver data to BQ
Step 5 — retrain.ipynb         Open in Colab, run manually to seed models in GCS
Step 6 — bq_gold_layer.sql     Run in BQ console to create gold views
Step 7 — cloudrun_job.py       Deploy to Cloud Run, set Cloud Scheduler trigger
Step 8 — Power BI              Connect Desktop to BQ gold views
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


================================================================================
  SMARTWATTS PIPELINE — PROJECT TODO
  Energy Usage Forecasting · GCP · Power BI
================================================================================

  Stack  : Python · GCS · BigQuery · Cloud Run · Cloud Scheduler · Colab T4
  Goal   : Forecast kWh usage to today (May 2026) from late 2024 data
  Status : In Development


================================================================================
  PHASE 1 — LOCAL ENVIRONMENT SETUP COMPLETE
  Get your machine ready before touching any GCP service
================================================================================

  [X] Install uv
        curl -LsSf https://astral.sh/uv/install.sh | sh

  [X] Install gcloud CLI
        https://cloud.google.com/sdk/docs/install

  [X] Install Docker Desktop
        https://docs.docker.com/get-docker

  [X] Install Power BI using web interface 
        https://powerbi.microsoft.com/desktop

  [X] Create virtual environment
        uv venv
        source .venv/bin/activate

  [X] Install dependencies
        uv pip install -r requirements.txt

  [X] Create .gitignore
        echo ".venv/" >> .gitignore
        echo "__pycache__/" >> .gitignore
        echo "*.pyc" >> .gitignore
        echo ".env" >> .gitignore

  [X] Create .env file for local secrets
        PROJECT=your-gcp-project-id
        BUCKET=smartwatts-data-lake
        DATASET=smartwatts

  [X] Verify Python imports work
        python -c "from google.cloud import bigquery; print('BQ ok')"
        python -c "from google.cloud import storage; print('GCS ok')"
        python -c "import tensorflow as tf; print(tf.__version__)"
        python -c "from prophet import Prophet; print('Prophet ok')"


================================================================================
  PHASE 2 — GCP PROJECT SETUP
  One-time cloud infrastructure provisioning
================================================================================

  [X] Create a GCP project at console.cloud.google.com
      named: SmartWatts-Project

  [X] Enable billing (required even for free tier)

  [ ] Enable required APIs
        gcloud services enable bigquery.googleapis.com
        gcloud services enable storage.googleapis.com
        gcloud services enable run.googleapis.com
        gcloud services enable cloudscheduler.googleapis.com
        gcloud services enable cloudbuild.googleapis.com

  [X] Authenticate gcloud CLI
        gcloud auth login
        gcloud auth application-default login
        gcloud config set project YOUR_PROJECT

  [ ] Create a service account for pipeline scripts ?
        gcloud iam service-accounts create smartwatts-pipeline \
          --display-name "SmartWatts Pipeline"

  [ ] Grant service account permissions?
        roles/bigquery.dataEditor
        roles/bigquery.jobUser
        roles/storage.objectAdmin
        roles/run.invoker

  [ ] Download service account key?
        gcloud iam service-accounts keys create key.json \
          --iam-account smartwatts-pipeline@YOUR_PROJECT.iam.gserviceaccount.com

  [ ] Set credentials env var?
        export GOOGLE_APPLICATION_CREDENTIALS=path/to/key.json

  [X] Create GCS bucket
        gcloud storage buckets create gs://smartwatts-data-lake \
          --location=us-central1


  [X] Verify bucket accessible
        gsutil ls gs://smartwatts-data-lake


================================================================================
  PHASE 3 — ONE-TIME DATA PIPELINE
  Load historical data into BigQuery (start HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
================================================================================

  [X] Upload raw CSV to GCS
        python gcs_upload.py \
          --bucket smartwatts-data-lake \
          --source SmartWatts_Interval_Meter_Usage.csv

  [X] Verify CSV landed in GCS
        gsutil ls gs://smartwatts-data-lake/raw/smartwatts/

  [X] Provision BigQuery tables
        python bq_schema.py \
          --project YOUR_PROJECT \
          --dataset smartwatts

  [X] Verify tables created in BQ console
        smartwatts.raw_meter_usage
        smartwatts.forecasted_meter_usage
        smartwatts.model_run_log

  [X] Prefetch Houston weather data to GCS (one-time)
        python extractor.py \
          --bucket smartwatts-data-lake \
          --start 2022-10-01 \
          --end 2024-11-30

  [X] Verify weather parquet saved
        gsutil ls gs://smartwatts-data-lake/weather/

  [X] Dry run ingest to sanity check data
        python ingest.py \
          --bucket smartwatts-data-lake \
          --project YOUR_PROJECT \
          --dry-run

  [X] Review dry run output
        Check shape, ESIID list, sample rows look correct
        Check temp_fahrenheit column has values (not all NULL)

  [X] Run real ingest — loads data into BigQuery
        python ingest.py \
          --bucket smartwatts-data-lake \
          --project YOUR_PROJECT

  [X] Verify data in BigQuery
        Run in BQ console:
        SELECT esiid, COUNT(*) as rows, MIN(usage_start), MAX(usage_start)
        FROM smartwatts.raw_meter_usage
        GROUP BY esiid
        ORDER BY esiid


================================================================================
  PHASE 4 — ML TRAINING (COLAB)
  Train all 4 models on GPU and save to GCS
================================================================================

  [ ] Upload retrain notebook to GCS
        gsutil cp smartwatts_retrain.ipynb \
          gs://smartwatts-data-lake/notebooks/

  [ ] Open smartwatts_retrain.ipynb in Google Colab
        Go to colab.research.google.com
        File → Open notebook → Google Drive or upload directly

  [ ] Connect to T4 GPU runtime
        Runtime → Change runtime type → T4 GPU

  [ ] Update parameters cell in notebook
        PROJECT  = 'your-gcp-project-id'
        BUCKET   = 'smartwatts-data-lake'
        ESIIDS   = 'all'
        DRY_RUN  = False

  [ ] Run all cells — training takes ~30-60 mins on T4

  [ ] Watch for any ESIID failures in output
        Models save per ESIID so partial failures don't break everything

  [ ] Verify models saved to GCS after training
        gsutil ls gs://smartwatts-data-lake/models/
        gsutil ls gs://smartwatts-data-lake/models/Alfa/prophet/

  [ ] Check metadata.json for at least one model
        gsutil cat gs://smartwatts-data-lake/models/Alfa/prophet/metadata.json
        Should show trained_at, MAE, RMSE, MAPE values


================================================================================
  PHASE 5 — DAILY FORECAST (LOCAL TEST)
  Test predict mode locally before deploying to Cloud Run
================================================================================

  [ ] Run unit tests first
        python test_cloudrun_job.py
        All tests should pass before touching GCP

  [ ] Run forecast pipeline in dry-run mode
        python forecast_pipeline.py \
          --project YOUR_PROJECT \
          --dataset smartwatts \
          --bucket smartwatts-data-lake \
          --esiids Alfa \
          --horizon-days 1 \
          --mode predict \
          --dry-run

  [ ] Check output — should print 24 forecast rows for Alfa

  [ ] Run real predict for one ESIID
        python forecast_pipeline.py \
          --project YOUR_PROJECT \
          --dataset smartwatts \
          --bucket smartwatts-data-lake \
          --esiids Alfa \
          --horizon-days 1 \
          --mode predict

  [ ] Verify forecast rows landed in BigQuery
        SELECT * FROM smartwatts.forecasted_meter_usage
        WHERE esiid = 'Alfa'
        ORDER BY forecast_start DESC
        LIMIT 24

  [ ] Run full predict for all ESIIDs
        python forecast_pipeline.py \
          --project YOUR_PROJECT \
          --dataset smartwatts \
          --bucket smartwatts-data-lake \
          --horizon-days 1 \
          --mode predict

  [ ] Verify all 12 ESIIDs have forecast rows in BQ


================================================================================
  PHASE 6 — CLOUD RUN DEPLOYMENT
  Containerize and deploy forecast job
================================================================================

  [ ] Write Dockerfile
        Packages forecast_pipeline.py + cloudrun_job.py
        Base image: python:3.11-slim
        COPY requirements.txt + all pipeline scripts
        RUN uv pip install -r requirements.txt
        CMD ["python", "cloudrun_job.py"]

  [ ] Build Docker image locally and test
        docker build -t smartwatts-forecast .
        docker run \
          -e PROJECT=YOUR_PROJECT \
          -e BUCKET=smartwatts-data-lake \
          -e DRY_RUN=true \
          -e ESIIDS=Alfa \
          smartwatts-forecast

  [ ] Push image to Google Container Registry
        gcloud builds submit --tag gcr.io/YOUR_PROJECT/smartwatts-forecast

  [ ] Create Cloud Run Job
        gcloud run jobs create smartwatts-daily-forecast \
          --image gcr.io/YOUR_PROJECT/smartwatts-forecast \
          --region us-central1 \
          --set-env-vars PROJECT=YOUR_PROJECT,BUCKET=smartwatts-data-lake \
          --memory 2Gi \
          --timeout 3600

  [ ] Test Cloud Run Job manually
        gcloud run jobs execute smartwatts-daily-forecast \
          --region us-central1

  [ ] Watch logs to confirm job succeeded
        gcloud run jobs executions list \
          --job smartwatts-daily-forecast \
          --region us-central1

  [ ] Run integration test against real Cloud Run job
        PROJECT=YOUR_PROJECT BUCKET=smartwatts-data-lake \
        python test_cloudrun_job.py --integration

  [ ] Create Cloud Scheduler trigger (daily 02:00 UTC)
        gcloud scheduler jobs create http smartwatts-forecast-trigger \
          --location us-central1 \
          --schedule "0 2 * * *" \
          --uri "https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/YOUR_PROJECT/jobs/smartwatts-daily-forecast:run" \
          --oauth-service-account-email smartwatts-pipeline@YOUR_PROJECT.iam.gserviceaccount.com \
          --message-body "{}"

  [ ] Manually trigger scheduler to verify end-to-end
        gcloud scheduler jobs run smartwatts-forecast-trigger \
          --location us-central1


================================================================================
  PHASE 7 — GOLD LAYER + POWER BI
  Build serving views and connect dashboard
================================================================================

  [ ] Write bq_gold_layer.sql with three views
        vw_model_comparison        all 4 models side by side per ESIID per hour
        vw_best_forecast           Prophet only, point estimate + CI bands
        vw_historical_vs_forecast  bronze + gold unified timeline per ESIID

  [ ] Run SQL in BigQuery console to create views

  [ ] Verify views return data
        SELECT * FROM smartwatts.vw_historical_vs_forecast
        WHERE esiid = 'Alfa'
        LIMIT 100

  [ ] Open Power BI Desktop
        Get Data → Google BigQuery
        Sign in with Google account
        Select project → smartwatts dataset

  [ ] Load gold views into Power BI
        vw_historical_vs_forecast   (main timeline chart)
        vw_model_comparison         (model performance comparison)
        vw_best_forecast            (forecast with confidence bands)

  [ ] Build main timeline chart
        X axis  : usage_start / forecast_start
        Y axis  : usage_kwh / forecasted_kwh
        Legend  : data_source (historical vs forecasted)
        Filter  : ESIID slicer

  [ ] Build model comparison chart
        X axis  : forecast_start
        Y axis  : forecasted_kwh
        Legend  : model_name (rnn, lstm, gru, prophet)

  [ ] Build confidence band chart
        Line    : forecasted_kwh (Prophet)
        Bands   : lower_bound_95 + upper_bound_95
        Filter  : ESIID slicer

  [ ] Add ESIID slicer to all pages for filtering


================================================================================
  PHASE 8 — BACKFILL TO TODAY
  Fill the ~18 month gap from late 2024 to May 2026
================================================================================

  [ ] Check last forecast date in BQ
        SELECT MAX(forecast_start) FROM smartwatts.forecasted_meter_usage

  [ ] Calculate how many days to backfill
        From last forecast date to today (May 2026)
        Roughly 550 days

  [ ] Run backfill using longer horizon
        python forecast_pipeline.py \
          --project YOUR_PROJECT \
          --dataset smartwatts \
          --bucket smartwatts-data-lake \
          --horizon-days 550 \
          --mode predict

  [ ] NOTE: this is a long run — do it in chunks if needed
        --horizon-days 90 (run 6 times to cover 18 months)

  [ ] Retrain Colab notebook on backfill data once complete
        Open smartwatts_retrain.ipynb
        Run all cells — models will improve with more data

  [ ] Verify full timeline in Power BI
        Should see continuous data from Oct 2022 → May 2026


================================================================================
  PHASE 9 — WEEKLY RETRAIN SCHEDULE
  Set up recurring model retraining in Colab
================================================================================

  [ ] Add scheduled retrain reminder (manual for now)
        Every Sunday — open Colab and run smartwatts_retrain.ipynb
        This retrains on historical + accumulated forecasts

  [ ] Save retrain output notebook to GCS each run
        Colab: File → Save a copy in Drive or download + upload to GCS
        gs://smartwatts-data-lake/notebook_outputs/

  [ ] Check model_run_log in BQ after each retrain
        SELECT model_name, esiid, mae, rmse, mape, trained_at
        FROM smartwatts.model_run_log
        ORDER BY trained_at DESC
        LIMIT 50

  [ ] Monitor MAE / RMSE trend over time
        If metrics get worse → check for data quality issues
        If metrics improve → model is learning from accumulated forecasts


================================================================================
  PHASE 10 — CLEANUP + DOCUMENTATION
  Tidy up before calling it done
================================================================================

  [ ] Delete files no longer needed. Update files here


  [ ] Push final code to GitHub

  [ ] Confirm .env and key.json are NOT in the repo
        git status — should not see these files

  [ ] Update README.md with your actual project + bucket names

  [ ] Screenshot Power BI dashboard for portfolio

  [ ] Update resume with completed project details
        Add final metrics: MAE, RMSE per model
        Add record count: 900K+ historical + forecasted rows
        Add tech stack header with full stack


================================================================================
  QUICK REFERENCE — RUN ORDER FOR FRESH SETUP
================================================================================

  1.  uv venv && source .venv/bin/activate
  2.  uv pip install -r requirements.txt
  3.  gcloud auth application-default login
  4.  python gcs_upload.py --bucket BUCKET --source CSV
  5.  python bq_schema.py --project PROJECT --dataset smartwatts
  6.  python prefetch_weather.py --bucket BUCKET
  7.  python ingest.py --bucket BUCKET --project PROJECT --dry-run
  8.  python ingest.py --bucket BUCKET --project PROJECT
  9.  Open Colab → run smartwatts_retrain.ipynb (GPU)
  10. python forecast_pipeline.py ... --mode predict --dry-run
  11. python forecast_pipeline.py ... --mode predict
  12. docker build → gcloud builds submit → gcloud run jobs create
  13. gcloud scheduler jobs create ...
  14. Run bq_gold_layer.sql in BQ console
  15. Connect Power BI Desktop to BigQuery gold views
