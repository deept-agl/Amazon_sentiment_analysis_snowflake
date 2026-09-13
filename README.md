# Amazon Review Sentiment Analysis on Snowflake

Build an end-to-end Amazon Review Sentiment Analysis solution in Snowflake using Marketplace data, Cortex AI `AI_SENTIMENT`, SQL analytics, and Streamlit.

## Project Goal

Customer reviews contain valuable product feedback, but manually reading thousands of reviews is slow and inconsistent.

This project shows how to:

**Marketplace Data → Sample Reviews → AI_SENTIMENT → Analytics Views → Streamlit Dashboard**

The goal is to convert unstructured customer feedback into structured sentiment insights that can be explored at product and aspect level.

---

## Project Flow

```text
Amazon Marketplace Data
        ↓
Review Sample
        ↓
Snowflake Cortex AI
        ↓
AI_SENTIMENT
        ↓
Analysis Tables
        ↓
SQL Views
        ↓
Streamlit Dashboard
```

---

## What This Project Covers

- Read product and review data from Snowflake Marketplace
- Create a cost-controlled review sample
- Run overall sentiment analysis using `AI_SENTIMENT`
- Perform aspect-level sentiment analysis
- Compare star ratings with written sentiment
- Identify negative reviews that may need attention
- Create analytics views for reporting
- Build an interactive Streamlit dashboard

---

## Repository Structure

```text
Amazon_sentiment_analysis_snowflake/
│
├── Review_analysis_app/
│   │
│   ├── .streamlit/
│   │   ├── .folder
│   │   └── config.toml
│   │
│   ├── .folder
│   ├── pyproject.toml
│   ├── snowflake.yml
│   └── streamlit_app.py
│
├── docs/
│   ├── .folder
│   └── project_image.png
│
├── sql/
│   ├── .folder
│   ├── 01_account_setup.sql
│   ├── 02_inspect_marketplace_data.sql
│   ├── 03_create_review_sample.sql
│   ├── 04_test_sentiment.sql
│   ├── 05_create_analysis_table.sql
│   ├── 06_create_processing_procedure.sql
│   ├── 07_run_analysis.sql
│   └── 08_create_views.sql
│
├── README.md
└── cleanup.sql
```

---

## Run the Project

### 1. Account Setup

Run:

```text
sql/01_account_setup.sql
```

Creates the required Snowflake objects and environment.

### 2. Inspect Marketplace Data

Run:

```text
sql/02_inspect_marketplace_data.sql
```

Review the available product and customer review data.

### 3. Create Review Sample

Run:

```text
sql/03_create_review_sample.sql
```

Creates a manageable review sample for sentiment processing.

### 4. Test Cortex AI Sentiment

Run:

```text
sql/04_test_sentiment.sql
```

Validates `AI_SENTIMENT` on sample review text.

### 5. Create Analysis Table

Run:

```text
sql/05_create_analysis_table.sql
```

Creates the structured table used to store sentiment results.

### 6. Create Processing Procedure

Run:

```text
sql/06_create_processing_procedure.sql
```

Creates the procedure used to process review sentiment.

### 7. Run Sentiment Analysis

Run:

```text
sql/07_run_analysis.sql
```

Executes the sentiment pipeline.

### 8. Create Analytics Views

Run:

```text
sql/08_create_views.sql
```

Creates views used by the Streamlit dashboard.

### 9. Run Streamlit App

The Streamlit application is available under:

```text
Review_analysis_app/
```

Main file:

```text
Review_analysis_app/streamlit_app.py
```

---

## Key Insights

The project helps answer questions such as:

- Which products have the most negative reviews?
- Which product aspects are driving negative sentiment?
- Do star ratings match the written review sentiment?
- Which reviews should be prioritized for investigation?
- What are the overall sentiment trends across products?

---

## Tech Stack

- Snowflake
- Snowflake Marketplace
- Snowflake Cortex AI
- `AI_SENTIMENT`
- SQL
- Stored Procedures
- Streamlit

---

## Cleanup

To remove the project objects, run:

```text
cleanup.sql
```

---

## Key Takeaway

This project demonstrates how Snowflake Cortex AI can turn large volumes of unstructured review text into structured, queryable sentiment insights.

Instead of manually reading reviews:

```text
Reviews → AI Sentiment → Structured Insights → Dashboard
```

---

## Connect

YouTube: https://youtube.com/@DeeptiBuilds  
LinkedIn: https://linkedin.com/in/deeptiagrawal29  
GitHub: https://github.com/deept-agl  
Medium: https://medium.com/@deepti.agl2912
