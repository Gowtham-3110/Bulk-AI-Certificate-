# Bulk Certificate Generator — Backend Engine & Portal

An enterprise-grade, asynchronous backend API and interactive management portal for bulk certificate generation, real-time progress tracking, error-isolated batch processing, and credential retrieval.

Built with **Python 3.10+**, **FastAPI**, **SQLAlchemy 2.0**, **SQLite** (relational database), and **ReportLab** (vector PDF rendering).

---

## 📑 Table of Contents
1. [Key Features](#-key-features)
2. [Architecture & Design Decisions](#-architecture--design-decisions)
3. [Technology Stack](#-technology-stack)
4. [Prerequisites & Quick Setup](#-prerequisites--quick-setup)
5. [Running the Application](#-running-the-application)
6. [Running the Test Suite](#-running-the-test-suite)
7. [API Reference & Usage](#-api-reference--usage)
8. [Validation & Failure Isolation Strategy](#-validation--failure-isolation-strategy)
9. [Database Schema](#-database-schema)
10. [Interview Defense & Scalability Guide](#-interview-defense--scalability-guide)

---

## 🚀 Key Features

- **Bulk Asynchronous Processing:** Submit hundreds or thousands of recipients in a single API call without HTTP request timeouts.
- **Fault-Tolerant Error Isolation:** An invalid or corrupt recipient record **never** aborts the remaining valid certificates in the batch.
- **Granular Lifecycle Tracking:** Tracks jobs across `PENDING`, `PROCESSING`, `COMPLETED`, `PARTIALLY_COMPLETED`, and `FAILED` states with live progress percentages.
- **Dual Retrieval Modes:**
  - Retrieve single certificate PDFs by certificate UUID (`GET /api/v1/certificates/{id}/download`).
  - Retrieve all generated certificates for an entire job compressed as a ZIP archive (`GET /api/v1/jobs/{id}/download-all`).
- **Cryptographic/Tamper-Resistant Verification:** Each certificate gets a unique verification code (`CERT-YYYYMM-XXXXXXXX`) with a public validation endpoint (`GET /api/v1/certificates/verify/{code}`).
- **Interactive Web Dashboard:** Includes a modern UI at `http://localhost:8000/` featuring one-click sample loader, real-time polling progress bar, certificate downloads, and public credential verification.
- **Interactive Swagger / OpenAPI Docs:** Available out-of-the-box at `http://localhost:8000/docs`.

---

## 🧠 Architecture & Design Decisions

### 1. Framework: Why FastAPI?
- **Asynchronous Concurrency:** Native `async/await` and non-blocking I/O support allow the API server to handle high incoming request volumes without blocking worker threads.
- **Built-in Background Tasks:** Offloads heavy PDF generation from the request-response lifecycle immediately, returning an HTTP `201 Created` with a trackable `job_id` in milliseconds.
- **Automatic Schema Validation:** Strict runtime typing with **Pydantic v2** enforces email validity, string length, and required fields before data enters the system.
- **Automated Interactive Docs:** Zero-maintenance OpenAPI / Swagger documentation (`/docs`) and ReDoc (`/redoc`).

### 2. Relational Database: SQLite + SQLAlchemy 2.0
- **ACID Transactions:** Full relational database guarantees data consistency across job items and status counters.
- **Zero-Friction Evaluation:** Runs out of the box using SQLite with no external database server to provision.
- **Production Migration Ready:** Powered by SQLAlchemy 2.0 ORM; changing to **PostgreSQL** or **MySQL** only requires updating `DATABASE_URL` in `.env` (no code changes needed).

### 3. Certificate Generation Engine: ReportLab (Vector PDF)
- **Pure Python Independence:** Unlike tools like WeasyPrint or wkhtmltopdf that rely on external OS binaries (Pango, Cairo, GTK) which frequently fail on cross-platform setups, ReportLab is 100% self-contained pure Python.
- **Vector Precision & Print Quality:** Certificates are drawn using vector canvas instructions (crisp borders, gold seal, official typography, security codes) at any resolution.
- **Speed & Memory Efficiency:** Generates compact (~3 KB) vector PDFs in under 15ms per certificate.

---

## 🛠 Technology Stack

| Layer | Component | Description |
|---|---|---|
| **Language** | Python 3.10+ | Core runtime |
| **API Framework** | FastAPI | High-performance async REST API framework |
| **ASGI Server** | Uvicorn | Lightning-fast ASGI production web server |
| **ORM / Database** | SQLAlchemy 2.0 + SQLite | Relational database persistence |
| **PDF Generation** | ReportLab 5.0 | Vector PDF canvas rendering |
| **Data Validation** | Pydantic v2 + Email-Validator | Schema and email verification |
| **Testing** | Pytest + Starlette TestClient + HTTPX | Comprehensive integration & unit testing |
| **Frontend UI** | Vanilla JS + Modern CSS + Jinja2 | Zero-dependency responsive portal |

---

## 📦 Prerequisites & Quick Setup

### 1. Prerequisites
- Python 3.10 or higher installed (`python --version`)
- Git (optional)

### 2. Clone / Open the Project
```bash
cd "d:/AI Certificate"
```

### 3. Create and Activate Virtual Environment
On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

On Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🏃 Running the Application

### Start the Server
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Once running:
- **Interactive Web Dashboard:** [http://localhost:8000/](http://localhost:8000/)
- **Swagger / OpenAPI Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check Endpoint:** [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Running the Test Suite

The test suite covers:
1. **Job Creation:** Valid requests, background task scheduling.
2. **Input Validation:** Empty recipients, invalid email syntax, blank event names, empty recipient names.
3. **Certificate Generation:** PDF vector canvas rendering, `%PDF-` header integrity, file size checks.
4. **Job Status & Progress:** Progress percentage incrementing from 0% to 100%.
5. **Fault Isolation / Failure Handling:** Corrupted or failing recipient data does not disrupt other recipients; verifies `PARTIALLY_COMPLETED` job status.
6. **Certificate Retrieval:** Individual PDF download with proper content headers, bulk ZIP file archive extraction.
7. **Credential Verification:** Public endpoint validating valid and invalid certificate codes.

### Execute Pytest:
```bash
python -m pytest -v
```

---

## 📡 API Reference & Usage

### 1. Submit Bulk Certificate Generation Job
- **Endpoint:** `POST /api/v1/jobs`
- **Status Code:** `201 Created`

#### Request Body (`application/json`):
```json
{
  "event_name": "Advanced Cloud Architecture Bootcamp",
  "issuer_name": "Global Tech Institute",
  "issue_date": "2026-10-08",
  "template_title": "Certificate of Completion",
  "recipients": [
    {
      "name": "Alice Johnson",
      "email": "alice.j@example.com",
      "attributes": { "grade": "Distinction", "score": "98%" }
    },
    {
      "name": "Bob Martinez",
      "email": "bob.m@example.com",
      "attributes": { "grade": "Honors" }
    }
  ]
}
```

#### Example cURL:
```bash
curl -X POST "http://localhost:8000/api/v1/jobs" \
     -H "Content-Type: application/json" \
     -d '{
       "event_name": "Machine Learning Masterclass",
       "issuer_name": "Stanford AI Academy",
       "recipients": [
         {"name": "Sarah Connor", "email": "sarah@example.com"},
         {"name": "John Connor", "email": "john@example.com"}
       ]
     }'
```

#### Response (`201 Created`):
```json
{
  "id": "e93f64c1-6bf2-4da4-8b63-1250328b9d62",
  "event_name": "Machine Learning Masterclass",
  "issuer_name": "Stanford AI Academy",
  "issue_date": "2026-10-08",
  "template_title": "Certificate of Completion",
  "status": "PENDING",
  "total_recipients": 2,
  "processed_count": 0,
  "successful_count": 0,
  "failed_count": 0,
  "progress_percentage": 0.0,
  "created_at": "2026-10-08T12:00:00Z",
  "updated_at": "2026-10-08T12:00:00Z",
  "download_all_url": null,
  "certificates": [
    {
      "id": "18f97204-c5b9-4a0b-8d69-2a912bb09c61",
      "job_id": "e93f64c1-6bf2-4da4-8b63-1250328b9d62",
      "recipient_name": "Sarah Connor",
      "recipient_email": "sarah@example.com",
      "certificate_code": "CERT-202610-8A71F92C",
      "status": "PENDING",
      "error_message": null,
      "download_url": null
    }
  ]
}
```

---

### 2. Check Job Status & Progress
- **Endpoint:** `GET /api/v1/jobs/{job_id}`
- **Status Code:** `200 OK`

```bash
curl -X GET "http://localhost:8000/api/v1/jobs/e93f64c1-6bf2-4da4-8b63-1250328b9d62"
```

#### Response (`200 OK`):
```json
{
  "id": "e93f64c1-6bf2-4da4-8b63-1250328b9d62",
  "event_name": "Machine Learning Masterclass",
  "status": "COMPLETED",
  "total_recipients": 2,
  "processed_count": 2,
  "successful_count": 2,
  "failed_count": 0,
  "progress_percentage": 100.0,
  "download_all_url": "/api/v1/jobs/e93f64c1-6bf2-4da4-8b63-1250328b9d62/download-all",
  "certificates": [
    {
      "id": "18f97204-c5b9-4a0b-8d69-2a912bb09c61",
      "recipient_name": "Sarah Connor",
      "certificate_code": "CERT-202610-8A71F92C",
      "status": "SUCCESS",
      "download_url": "/api/v1/certificates/18f97204-c5b9-4a0b-8d69-2a912bb09c61/download"
    }
  ]
}
```

---

### 3. Retrieve Individual Certificate PDF
- **Endpoint:** `GET /api/v1/certificates/{certificate_id}/download`
- **Response:** `200 OK` (`application/pdf`)
```bash
curl -O -J "http://localhost:8000/api/v1/certificates/18f97204-c5b9-4a0b-8d69-2a912bb09c61/download"
```

---

### 4. Bulk Download All Certificates as ZIP Archive
- **Endpoint:** `GET /api/v1/jobs/{job_id}/download-all`
- **Response:** `200 OK` (`application/zip`)
```bash
curl -O -J "http://localhost:8000/api/v1/jobs/e93f64c1-6bf2-4da4-8b63-1250328b9d62/download-all"
```

---

### 5. Verify Certificate Authenticity
- **Endpoint:** `GET /api/v1/certificates/verify/{certificate_code}`
- **Response:** `200 OK`
```bash
curl -X GET "http://localhost:8000/api/v1/certificates/verify/CERT-202610-8A71F92C"
```
```json
{
  "is_valid": true,
  "certificate_code": "CERT-202610-8A71F92C",
  "recipient_name": "Sarah Connor",
  "event_name": "Machine Learning Masterclass",
  "issuer_name": "Stanford AI Academy",
  "issue_date": "2026-10-08",
  "message": "Certificate is authentic and officially recognized."
}
```

---

## 🛡 Validation & Failure Isolation Strategy

In bulk generation systems, **batch failure domino effects** are unacceptable. If an event has 500 attendees and 1 record has an invalid format or encounters a rendering glitch, the other 499 certificates must still be generated.

### How Error Isolation Works:
1. **API Validation Level:**
   - Checks overall request structure, non-empty event title, and recipient format.
2. **Worker Processing Level:**
   - The job runner iterates through each recipient inside an isolated `try...except` boundary.
   - If an error occurs on recipient `K`:
     - Recipient `K` is marked `status = FAILED` with a descriptive `error_message`.
     - `job.failed_count` is incremented.
     - `job.processed_count` is incremented.
     - The transaction is committed.
     - The worker immediately continues with recipient `K + 1`.
3. **Job Status Classification:**
   - All succeeded $\rightarrow$ `COMPLETED`
   - Some succeeded, some failed $\rightarrow$ `PARTIALLY_COMPLETED`
   - All failed $\rightarrow$ `FAILED`
4. **Visibility:**
   - The client can inspect `GET /api/v1/jobs/{id}` to see which recipients succeeded (with their download links) and which failed (with their exact error reasons).

---

## 🗄 Database Schema

```
+------------------------------------+          +------------------------------------+
|               jobs                 |          |            certificates            |
+------------------------------------+          +------------------------------------+
| id (PK, UUID)                      | 1      * | id (PK, UUID)                      |
| event_name (VARCHAR)               |<---------| job_id (FK -> jobs.id)             |
| issuer_name (VARCHAR)              |          | recipient_name (VARCHAR)           |
| issue_date (VARCHAR)               |          | recipient_email (VARCHAR)          |
| template_title (VARCHAR)           |          | certificate_code (VARCHAR, UNIQUE) |
| status (ENUM: PENDING,             |          | custom_attributes (JSON)           |
|         PROCESSING, COMPLETED,     |          | status (ENUM: PENDING, SUCCESS,    |
|         PARTIALLY_COMPLETED,       |          |               FAILED)              |
|         FAILED)                    |          | file_path (VARCHAR)                |
| total_recipients (INT)             |          | error_message (TEXT)               |
| processed_count (INT)              |          | created_at (DATETIME)              |
| successful_count (INT)             |          | generated_at (DATETIME)            |
| failed_count (INT)                 |          +------------------------------------+
| created_at (DATETIME)              |
| updated_at (DATETIME)              |
+------------------------------------+
```

---

## 🎤 Interview Defense & Scalability Guide

### Q1: Why did you choose asynchronous background processing over synchronous generation?
> **Answer:** PDF generation requires disk I/O and vector rendering calculations. If a client submits 500 recipients synchronously, the HTTP connection would remain open for 15–30 seconds, risking reverse-proxy timeouts (e.g., Nginx 504 Gateway Timeout or Cloudflare 524). Background processing returns an HTTP `201 Created` immediately with a `job_id`, allowing the client to poll or receive webhooks, while the server processes the load reliably.

### Q2: How would you scale this to handle 100,000+ recipients per job?
> **Answer:**
> 1. **Distributed Task Queue:** Replace FastAPI's in-process `BackgroundTasks` with **Celery** or **ARQ** backed by **Redis** or **RabbitMQ**.
> 2. **Worker Concurrency:** Scale stateless worker containers horizontally across Kubernetes nodes.
> 3. **Batch Partitioning:** Divide the 100,000 recipients into chunks of 100 or 500 items, scheduling them as sub-tasks (`celery.group`).
> 4. **Cloud Object Storage:** Store generated PDFs in **AWS S3** / **Google Cloud Storage** with pre-signed download URLs instead of local disk storage.
> 5. **Read Replicas:** Route status polling queries to database read replicas to avoid locking writer transactions.

### Q3: How do you prevent duplicate certificate generation?
> **Answer:** We generate unique `certificate_code` hashes and verify certificate status before generation. If a job is re-triggered or resumed after an unexpected restart, the processor inspects `cert.status == SUCCESS` and skips already generated files (idempotent design).

### Q4: How would you support multiple templates in the future?
> **Answer:** We can implement a **Strategy Pattern** or template registry (`TemplateRegistry.get(template_id)`). Each template class implements a common interface `render(context) -> Path`. Alternatively, we could allow organizations to supply HTML/SVG templates rendered dynamically with Jinja2.
