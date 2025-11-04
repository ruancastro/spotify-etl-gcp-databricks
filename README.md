# 🎧 Spotify ETL Pipeline — Databricks + GCP

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Built with](https://img.shields.io/badge/Built%20with-Databricks%20%2B%20GCP-blue)
![Data Engineering](https://img.shields.io/badge/domain-Data%20Engineering-orange.svg)

---

## 📖 Overview
This project demonstrates a **complete ETL pipeline** using **Databricks** and **Google Cloud Platform (GCP)** to extract, transform, and load data from the **Spotify API** into a structured data lake architecture (Bronze → Silver → Gold).

It was built to showcase data engineering best practices, including orchestration, incremental updates, and schema evolution.

---

## ⚙️ Tech Stack
- **Databricks** – Orchestration and transformations
- **Apache Spark (PySpark)** – Data processing
- **Google Cloud Storage (GCS)** – Raw and curated data layers
- **BigQuery** – Analytics-ready data
- **Spotify API** – Data source
- **Cloud Run + Cloud Scheduler (GCP)** – Automated daily ingestion triggers

---

## 🧩 Architecture
```
                    +----------------------+
                    |   Cloud Scheduler     |
                    | (Daily trigger)       |
                    +----------+------------+
                               |
                               v
                    +----------------------+
                    |     Cloud Run         |
                    | (Runs ETL script)     |
                    +----------+------------+
                               |
                               v
                    +----------------------+
                    |   Spotify API         |
                    | (Data source)         |
                    +----------+------------+
                               |
                               v
                    +----------------------+
                    |  Google Cloud Storage |
                    | (Bronze Layer - Raw)  |
                    +----------+------------+
                               |
                               v
                    +----------------------+
                    |     Databricks        |
                    | (Silver/Gold Layers)  |
                    | Transformations + Job |
                    +----------+------------+
                               |
                               v
                    +----------------------+
                    |     BigQuery          |
                    | (Analytics / BI)      |
                    +----------------------+
```

---

## 🚀 Automation on GCP

The ingestion process runs automatically using **Cloud Scheduler** and **Cloud Run**:

1. **Cloud Scheduler** triggers a **HTTP request** daily.
2. The request hits a **Cloud Run** endpoint hosting a lightweight Python API.
3. This API executes the **Spotify ETL extraction**, writing new data to the **Bronze Layer** (GCS).
4. Once the raw data is updated, a **Databricks Job** is triggered for further transformation and loading into **Silver** and **Gold** tables.

This setup allows full automation with minimal cost (below R$5/month).

---

## 📊 Data Flow Summary
1. **Extract:** Spotify API → Cloud Run
2. **Load (Raw):** Cloud Run → GCS (Bronze)
3. **Transform:** Databricks → Silver/Gold layers
4. **Analyze:** BigQuery / Power BI

---

## 📜 License
This project is licensed under the [MIT License](LICENSE).
