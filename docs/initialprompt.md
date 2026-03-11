# GitHub Plan for “Expose Corruption with Machine Speed” System

## Executive Summary

I propose a GitHub‑driven roadmap to build our corruption‑exposure platform. We will set up a well‑structured repo with clear modules for data ingestion, processing, ML, UI and reporting. Our team roles (data engineers, ML engineers, frontend/backend developers, legal experts) and tech stack (Python, JavaScript, Airflow, Docker, etc.) are defined. We outline step‑by‑step tasks, milestones, and GitHub practices (branch strategy, actions, PR templates) to ensure code quality and compliance (CI/CD, testing, security). We leverage GitHub Copilot to speed development: for each task we include example prompts and code snippets (e.g. “*Write a Python Scrapy spider to download eTender JSON*”). We emphasise South African context: using official data sources (eTender portal【46†L39-L42】, Municipal Finance Data【48†L249-L251】, gov’t gazettes), observing POPIA/privacy and legal hooks (whistleblower, defamation), and hosting in SA cloud regions. We also compare three scales (Pilot, Regional, National) in a table. The plan includes templates for README, CONTRIBUTING, issues/PRs, tests, architecture diagram (Mermaid), data schema, verification checklist, and social media posts. The output is a comprehensive, developer‑oriented blueprint, ready for Copilot‑assisted coding.

## Repository Structure and Modules

We will organise the code in a mono-repo (or clear workspace) with folders for each component:

- `README.md`: Overview, installation, quickstart.
- `docs/`: Detailed documentation and architecture diagrams (in Markdown).
- `data/`: Schema definitions, example datasets (small).
- `src/`: Core code, subdivided into modules:
  - `src/ingest/`: Data ingestion scripts (eTender API, municipal APIs, Gazette scrapers).
  - `src/etl/`: ETL and normalization pipelines (Python scripts or Airflow DAGs).
  - `src/ocr/`: OCR utilities (Tesseract wrappers for scanned PDFs).
  - `src/ml/`: Machine-learning models (anomaly detection, entity resolution).
  - `src/ui/`: Web UI code (e.g. React/Flask for verification and dashboard).
  - `src/evidence/`: Evidence packaging and redaction tools.
  - `src/social/`: Social media post template generators.
- `config/`: Configuration files (API keys, endpoint URLs – encrypted or via GitHub Secrets).
- `.github/`: GitHub setup:
  - `workflows/`: CI/CD YAML files (GitHub Actions).
  - `ISSUE_TEMPLATE/`: Issue and PR templates (Bug, Feature, etc.).
  - `PULL_REQUEST_TEMPLATE.md`: PR template.
  - `CONTRIBUTING.md`: Contribution guide.
- `tests/`: Unit and integration tests, organized by module.
- `Dockerfile` and `docker-compose.yml`: Container definitions for services (database, web).
- `requirements.txt` / `package.json`: Dependencies.

Each module will have its own subdirectory with code, docs, and tests. For example, `src/ingest/etenders.py` and `src/ingest/municipal.py`. We’ll use Git submodules or monorepo with subfolders – likely a single repo with clear folders is simpler.

### Modules and Responsibilities

- **Data Ingestion (`src/ingest/`)**: Scrapy spiders or Python scripts to pull JSON/CSV from eTender【46†L39-L42】【50†L36-L44】, municipal finance APIs【48†L249-L251】, and download Government Gazettes (using e.g. `requests` or `Selenium`).  
- **ETL/Normalization (`src/etl/`)**: Code to parse raw downloads, apply OCR (Tesseract) on PDFs, clean and store data. We may use Apache Airflow to schedule ETL jobs.  
- **ML Models (`src/ml/`)**: Implement anomaly detection (Isolation Forest, clustering), entity resolution (fuzzy matching), network analysis (NetworkX/Neo4j). These produce a list of flagged cases.  
- **UI & Verification (`src/ui/`)**: A web app for analysts to review flagged cases. Could be Flask/React. Allows confirming anomalies, adding notes.  
- **Evidence Packaging (`src/evidence/`)**: Tools to compile documents (contracts, invoices), redact personal data (POPIA-safe), and generate export bundles for press.  
- **Social Toolkit (`src/social/`)**: Scripts to auto-generate social posts or visualisations from analysis results (e.g. markdown templates, image generation).

At the root we include configuration (e.g. `config/default.json` listing data source endpoints) and infrastructure code (Docker). All code is open-source.

## Roles and Required Skills

Our project team will include:

- **Lead Developer/Architect:** Oversees repo design, branching strategy, CI/CD. Skills: GitHub, Docker, cloud deployment (AWS/Azure), security.
- **Data Engineers (2):** Build data pipelines, ETL, scrapers. Skills: Python, Airflow, SQL, APIs, OCR (Tesseract/PDFBox). Familiar with eTender and municipal data formats.
- **Machine Learning Engineers (2):** Develop anomaly and entity-resolution models. Skills: Python, scikit-learn/TensorFlow, graph libraries (NetworkX, Neo4j), NLP. Data analysis, feature engineering.
- **Backend Developers (1):** Implement data storage and APIs. Skills: Node.js or Python (Flask/Django), PostgreSQL or MongoDB, REST design.
- **Frontend Developer (1):** Build verification UI and dashboard. Skills: React or Vue.js, D3.js for charts.
- **UX/Design (1):** (Optional) Design data dashboard and social visuals.
- **DevOps Engineer (1):** Set up CI/CD, testing pipeline, cloud infrastructure. Skills: GitHub Actions, Docker, Kubernetes, security practices.
- **Legal/Data Compliance Officer (1):** Ensures POPIA, chain-of-custody, and legal review processes. Skills: Knowledge of SA privacy laws, whistleblower protections【50†L29-L33】【46†L149-L153】.
- **Product Manager/Analyst (1):** Writes documentation, coordinates milestones, communicates with journalists. Familiar with corruption context.

All developers should be proficient with Git/GitHub workflow, code reviews, and writing tests. We expect many to use GitHub Copilot; familiarity with prompt engineering is a plus.

## Implementation Roadmap and Milestones

We break down the project into phases, each with milestones and issue templates:

1. **Repo Scaffold (Weeks 1–2):** 
   - *Tasks:* Initialize repository; create `README.md`, `LICENSE` (e.g. MIT), basic folder structure.  
   - *Milestones:* Repo publicly live; basic CI test passing.  
   - *Copilot Prompt Example:* “*Generate a README.md template with sections: Installation, Usage, Contributing.*”  
   - *Issue Template:* *“As a new developer, set up initial repo and CI”*.

2. **Data Ingestion (Weeks 3–6):** 
   - *Tasks:* Implement scripts to fetch data:
     - eTender JSON (via API or bulk download)【46†L75-L83】. 
     - Municipal JSON API (apply for API key from https://municipaldata.treasury.gov.za)【48†L259-L263】.
     - Government Gazette PDFs (download from https://www.gpwonline.co.za).  
     - Scrapers for NGO/corruption watch sites if needed.  
   - *Milestones:* Automated pipeline fetching raw data daily/weekly. Successful fetch from at least two sources.  
   - *Copilot Snippet Example:* Python `requests` to eTender API, or Scrapy spider.  
   - *Issue Template:* “Fetch data from eTender: [endpoint], validate JSON schema.”

3. **ETL and OCR Pipelines (Weeks 5–10, overlapping):**
   - *Tasks:* 
     - Develop ETL scripts to parse raw feeds, map to unified schema.  
     - Integrate OCR for scanned docs (Tesseract or AWS Textract).  
     - Normalize fields (dates, currency, org names).  
     - Load cleaned data into a database (e.g. PostgreSQL) or data lake (AWS S3).  
     - Create Airflow DAGs or scheduled tasks, with logging/provenance.  
   - *Milestones:* Data pipeline ingesting data, running without errors. Stored data ready for analysis.  
   - *Copilot Prompt Example:* “*Write a Python function that reads a PDF from URL and extracts text using Tesseract.*”  
   - *Issue Template:* “ETL: normalize [field] and insert into database; write unit tests for date parsing.”

4. **Feature Engineering (Weeks 7–12):**
   - *Tasks:* Design features for ML:
     - Price deviations (contract value vs estimated).  
     - Bid counts, time between advert and award.  
     - Supplier history (previous wins, blacklists).  
   - *Milestones:* Feature tables created; code (e.g. in `src/ml/features.py`) computing these from the DB.  
   - *Copilot Snippet Example:* Pandas code to calculate Z-score of `contract_value`.  
   - *Issue:* “Create feature: supplier win count in last year.”

5. **ML Model Development (Weeks 9–14):**
   - *Tasks:* 
     - Implement anomaly detection (Isolation Forest, clustering).  
     - Implement entity resolution (fuzzy matching on company names, addresses).  
     - Develop network analysis (build graph of buyers-suppliers).  
     - Validate on known irregular cases (if available).  
   - *Milestones:* Models that output risk scores for contracts and potential collusion clusters. Performance metrics documented.  
   - *Copilot Prompt:* “*Use scikit-learn IsolationForest on a DataFrame to flag outliers.*”  
   - *Issue:* “Train anomaly detection model; evaluate precision on held-out data.”

6. **Verification UI and Evidence Tools (Weeks 12–18):**
   - *Tasks:* 
     - Build a web interface where analysts can log in and review flagged cases (show details, attach documents, mark as confirmed).  
     - Implement evidence packaging: export PDF bundles, redaction (e.g. Python script using PyMuPDF to redact PII).  
   - *Milestones:* Interactive UI prototype, ability to accept/reject flagged cases. Evidence package generation working.  
   - *Copilot Prompt:* “*Generate a Flask route that serves contract details in HTML template.*”  
   - *Issue:* “UI: create review page showing contract record and documents.”

7. **Social Media Template Scripts (Weeks 14–18):**
   - *Tasks:* Create code to format flagged findings into social posts (text templates, charts). Possibly use a templating engine (Jinja2) for tweets or images (Matplotlib).  
   - *Milestones:* Sample outputs of tweet threads or infographic images from real data.  
   - *Issue:* “Generate an infographic (bar chart) from contract expenditure data.”

8. **Testing, CI/CD, Security (Weeks 15–20):**
   - *Tasks:* Write unit tests (`pytest` for Python, `Jest` for JS). Set up GitHub Actions to run tests, lint (flake8, ESLint) on PRs. Containerise components for consistent environments. Implement secret management (GitHub Secrets for API keys).  
   - *Milestones:* All tests passing on merge to `main`. Automatic builds and deployments on push (see sample workflows below).  
   - *Issue:* “Add GitHub Actions workflow for Python lint and pytest on pull requests.”

9. **Deployment and Documentation (Weeks 18–24):**
   - *Tasks:* Deploy the application stack to cloud (e.g. AWS ECS or Azure App Service in South Africa). Write thorough docs (architecture, API usage). Finalize `CONTRIBUTING.md` and license.  
   - *Milestones:* System live, team onboarded. Full documentation complete.  
   - *Issue:* “Deploy UI and backend services to AWS; ensure compliance with SA region.”

Each milestone will have associated issues. We will use GitHub Projects or Milestones to track progress. Milestone deadlines can be adjusted for each scale (see table below).

## Example Copilot Prompts and Code Snippets

We will leverage GitHub Copilot for boilerplate and complex logic. Example prompts and snippets:

- **eTender Scraper:**  
  *Copilot Prompt:* “*Write a Python function to fetch tender JSON from South Africa’s eTender API and save to a file.*”  
  ```python
  import requests, json
  def fetch_etender_data(page=1):
      url = f"https://ocds-api.etenders.gov.za/api/1.0/releases?page={page}"
      resp = requests.get(url)
      data = resp.json()
      with open(f"data/etenders_page_{page}.json", "w") as f:
          json.dump(data, f)
      return len(data['releases'])
  ```
- **CSV Ingestion (Pandas):**  
  *Prompt:* “*Load the municipal budget CSV into a Pandas DataFrame and clean column names.*”  
  ```python
  import pandas as pd
  df = pd.read_csv('data/municipal_budget.csv')
  df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
  df['amount'] = df['amount'].replace('[\$,]', '', regex=True).astype(float)
  ```
- **OCR PDF (Tesseract):**  
  *Prompt:* “*Use pytesseract to extract text from a downloaded contract PDF.*”  
  ```python
  from pdf2image import convert_from_path
  import pytesseract
  pages = convert_from_path('docs/contract.pdf', dpi=200)
  text = ""
  for page in pages:
      text += pytesseract.image_to_string(page, lang='eng')
  ```
- **Anomaly Model (IsolationForest):**  
  *Prompt:* “*Given a DataFrame `df` with a numeric column 'contract_value', train an IsolationForest to find outliers.*”  
  ```python
  from sklearn.ensemble import IsolationForest
  model = IsolationForest(contamination=0.01)
  model.fit(df[['contract_value']])
  df['outlier'] = model.predict(df[['contract_value']])
  flagged = df[df['outlier'] == -1]
  ```
- **Entity Resolution (Fuzzy):**  
  *Prompt:* “*Use thefuzz library to match similar supplier names.*”  
  ```python
  from thefuzz import process
  choices = ['Supplier A (Pty) Ltd', 'Supplier B Ltd', 'ABC Co.']
  matches = process.extract("AB.C Co", choices, limit=2)
  ```
- **Graph Construction (NetworkX):**  
  *Prompt:* “*Build a NetworkX graph where nodes are companies and edges represent shared ownership or joint bids.*”  
  ```python
  import networkx as nx
  G = nx.Graph()
  for bidder, partner in bid_partners:
      G.add_edge(bidder, partner)
  clusters = list(nx.community.greedy_modularity_communities(G))
  ```
- **Frontend Route (Flask):**  
  *Prompt:* “*Create a Flask route `/case/<id>` that retrieves case data from DB and renders `case.html` template.*”  
  ```python
  from flask import Flask, render_template
  app = Flask(__name__)
  @app.route('/case/<int:id>')
  def view_case(id):
      case = db.session.query(Case).get(id)
      return render_template('case.html', case=case)
  ```
- **Unit Test (pytest):**  
  *Prompt:* “*Write a pytest for the price z‑score calculation function.*”  
  ```python
  def test_price_zscore():
      df = pd.DataFrame({'price': [100, 150, 200, 1000]})
      df = compute_zscore(df, 'price')
      assert df['zscore'].iloc[-1] > 3
  ```
These examples illustrate how Copilot can jumpstart development. Each prompt is stored as a comment or issue for reproducibility.

## Tech Stack, CI/CD, Testing and Deployment

We choose mature open-source tools and SA‑region cloud options:

- **Languages:** Python 3.10+ for data/ML; JavaScript/TypeScript for frontend (React) and Node.js backends.  
- **Data & ML Libraries:** Pandas, NumPy; Scikit‑Learn or LightGBM; PyTorch/TensorFlow if needed; NetworkX or Neo4j for graphs; spaCy or Hugging Face for any NLP. Tesseract OCR (or AWS Textract) for document parsing.  
- **Databases:** PostgreSQL for structured data; ElasticSearch for text search; Neo4j or JanusGraph for relationships. All can run in Docker containers.  
- **Infrastructure/Cloud:** AWS (Cape Town region, `af-south-1`) or Azure (South Africa North) for deployment; Docker/EKS or Azure App Service for hosting. Use managed RDS for Postgres.  
- **CI/CD:** GitHub Actions for continuous integration. We’ll set up workflows (see sample below) to run linting (flake8, ESLint), unit tests, Docker build on each PR and `main` merge. On `main` merge, automatically deploy to a staging/production environment.  
- **Testing:** Unit tests (pytest, Jest), integration tests (end-to-end with Selenium or Cypress for UI). Aim for >80% coverage.  
- **Security:** Implement pre‑commit checks to scan for secrets. Use HTTPS for APIs and SSH for repo access. Follow OWASP best practices: sanitize inputs in UI, use parameterized queries. Store sensitive credentials (API keys, DB passwords) in GitHub Secrets or AWS Secret Manager.  
- **DevOps:** Dockerize each service. Use `docker-compose` locally. Kubernetes (EKS) can orchestrate services in production. Use Terraform or CloudFormation for infrastructure-as-code (optional).  
- **Monitoring:** Include basic logging. Later, add Prometheus/Grafana for pipeline health. 

**Sample GitHub Actions Workflow (Python):**  
```yaml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env: POSTGRES_USER: testuser
        ...
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v3
        with: python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Lint with flake8
        run: flake8 src tests
      - name: Run tests
        run: pytest --maxfail=1 --disable-warnings -q
```
This ensures every commit is tested and linted.

## Data Governance, POPIA and Legal Review

We must handle data ethically and legally:

- **POPIA Compliance:** As the eTender documentation states, all personal bidder data is removed【46†L149-L153】. We must treat any personal information with care. In practice, we avoid storing names/IDs of individuals; focus on company data only. Any scraped data containing PII must be redacted or hashed immediately. We’ll implement redaction filters in `src/evidence/` (e.g. regex to blank out ID numbers). Importantly, POPIA has a journalistic exemption【26†L186-L194】 for public interest, but we will document our use and stick to open data as much as possible.  

- **Protected Disclosures:** Our submission tool can include anonymity options. We will encourage whistleblowers to use secure channels. All leaked documents fed into the repo must be tagged with chain-of-custody metadata (collector, date). For example, a hashed filename or PDF stamp. This preserves evidentiary integrity.

- **Defamation Mitigation:** Every reported case in our output will be tagged “**Suspected Irregularity** – under investigation.” We will require at least two independent data points before publishing. The legal team will review all major releases. Contributors must answer a checklist before merging any code that generates public reports.

- **Audit Trail:** The code itself will enforce logging of data transformations. For example, every time a record is flagged, we log the source file and algorithm version. This ensures reproducibility. For data governance, we maintain a data provenance log (possibly using a tool like [2] or built-in audit tables).

- **Data Retention:** We’ll follow POPIA’s principle of minimal retention. Non-essential raw data (like intermediate CSVs) will be archived/purged after processing. Sensitive test data will be anonymized.

By embedding these practices into the code and docs (e.g. a `DATA_PRIVACY.md` file), we meet SA legal requirements.

## GitHub Workflow: Branch Strategy, CI and Contributor Guidelines

We adopt a **Gitflow-like strategy**: `main` (protected) for releases, `develop` for integration, and feature branches (`feature/*`) for new tasks. Each pull request (PR) targets `develop` and must pass the CI pipeline. After testing, `develop` is merged into `main` for deployment.

- **Branching:**   
  - `main` — always deployable; only updated via merge from `develop`.  
  - `develop` — latest stable code; merged PRs from feature branches.  
  - `feature/xxx` — created from `develop` for each issue/feature.  
  - `hotfix/xxx` — urgent fixes branched from `main` when needed.  

- **Code Reviews:** Each PR must have ≥1 approving review (preferably 2). Reviews should check: adherence to coding style, passing tests, documentation updates. A `CODE_REVIEW.md` checklist will be in the repo, e.g. “Did you write/update tests? Did you document new configs?”.

- **Issue Templates:** We create `.github/ISSUE_TEMPLATE/bug_report.md` and `feature_request.md`:
  ```markdown
  **Bug Report**

  **Description:** [Clear description of the bug]
  **Steps to Reproduce:** [Step-by-step]
  **Expected Behavior:** [What should happen]
  **Actual Behavior:** [What happens]
  ```

- **PR Template:** In `.github/PULL_REQUEST_TEMPLATE.md`:
  ```markdown
  ## Description
  [Brief description of changes]

  ## Type of change
  - [ ] Bug fix
  - [ ] New feature
  - [ ] Documentation
  - [ ] Refactor

  ## How to test
  [Steps to test this PR]

  ## Checklist
  - [ ] My code follows the style guidelines
  - [ ] I added tests covering my changes
  - [ ] I updated the README/CHANGELOG if needed
  ```

- **CONTRIBUTING.md:** Outlines branch strategy, coding conventions (e.g. PEP 8, commit message format), licensing, and how to run tests locally. It also describes how to use Copilot responsibly and encouraging meaningful prompts.

- **Security Checks:** Add a GitHub Action to scan for secrets (e.g. `truffleHog`) and known vulnerabilities (`CodeQL`).

## Pilot/Regional/National Scale Comparison

| **Aspect**         | **Pilot (1 City)**                  | **Regional (Multi-city/Prov)**           | **National**                 |
|--------------------|-------------------------------------|-----------------------------------------|------------------------------|
| **Duration**       | ~3–4 months                         | ~9–12 months                            | ~18–24 months               |
| **Staff (≈)**      | 4 developers, 1 data scientist, 1 PM | 8 developers/analysts, 2 ML/data, 1 PM   | 15+ cross-functional (devs, data, devops, QA, PM, legal) |
| **Deliverables**   | - Basic repo scaffold<br>- Data fetchers for one metro<br>- Simple ETL pipeline<br>- One ML model<br>- Prototype dashboard | - Extended data pipelines (multiple sources)<br>- Multiple ML models<br>- Data warehouse<br>- User login & review UI<br>- Automated packaging/redaction | - Full platform with CI/CD<br>- Scalable infrastructure<br>- Comprehensive ML suite<br>- National reporting pipeline<br>- SLA and monitoring |
| **Timeline (approx)**| 3-4 months                        | 9-12 months                              | 18-24 months                 |
| **Role Focus**     | Full-stack devs (ingest+UI), basic ML | Specialised data/ML teams, devops        | Large teams with ops/security/legal oversight |
| **Output Quality** | Proof-of-concept with limited data  | Robust tool for province-level oversight | Enterprise-grade system covering entire country |
| **Cost (ZAR)**     | TBD (<R0.5M)                        | TBD (≈R2–5M)                             | TBD (>R10M)                  |

This table guides planning at each scale. For example, a pilot might analyse one city’s eTender and one budget dataset and produce a report, while the national project ingests all provinces and integrates with national Treasury.

## Sample Templates and Schemas

- **Architecture Diagram (Mermaid):** Below is a simplified system flow:
  ```mermaid
  flowchart TB
      A[GitHub Repo] --> B[Data Ingestion Module]
      B --> C[Data Lake / DB]
      C --> D[ETL Processing]
      D --> E[ML Models]
      E --> F[Flagged Cases DB]
      F --> G[Verification UI]
      G --> H[Evidence Packaging & Reports]
      F --> I[Social Media Generator]
      subgraph CI/CD
        A --> J[GitHub Actions]
        J --> B
        J --> E
        J --> G
      end
  ```
  This shows how components connect and where CI/CD fits.

- **Data Schema (contracts table example):**

  | Column         | Type       | Description                          |
  | -------------- | ---------- | ------------------------------------ |
  | `tender_id`    | STRING     | Unique ID of the tender              |
  | `buyer_org`    | STRING     | Procuring entity name                |
  | `supplier`     | STRING     | Winning bidder name                  |
  | `award_date`   | DATE       | Contract award date                  |
  | `value`        | FLOAT      | Awarded amount (ZAR)                 |
  | `currency`     | STRING     | Currency code (“ZAR”)                |
  | `description`  | TEXT       | Description of goods/services        |
  | `flag_score`   | FLOAT      | Anomaly score from ML model          |
  | `flag_reasons` | JSON       | Red-flag attributes (e.g. “high_price”) |
  | `source_url`   | STRING     | Source link or document path         |

  This schema guides ETL. We version it in `data/schema/contracts.json`.

- **Verification Checklist:** (for UI workflow)
  - ✔️ Confirm data match official source (Tender Bulletin or eTender record)【46†L39-L42】.  
  - ✔️ Check supplier registration (CIPC) and blacklist status【50†L29-L33】.  
  - ✔️ Verify numbers (quantities, prices) align with budgets or market standards.  
  - ✔️ Corroborate with at least one news report or audit finding.  
  - ✔️ Log chain-of-custody (source of document, who accessed it).  
  - ✔️ If publishing, review with legal and anonymise any unnecessary PII.

- **Social Post Templates:**  
  *Example Tweet:* “🚨 *ALERT:* Our analysis finds [Company X] won a R10m school contract with no competition (only bidder). The price is 5× higher than last year’s tenders for similar work. Documents: [link] #SAcorruption”  
  *Facebook/Instagram:* A short text with infographic: “*Visual: Bar chart of price vs. average.* Huge overspend uncovered in Limpopo school project. We compiled official docs showing the expense – see bio for details!”  

- **GitHub Issue Template (bug_report.md):**  
  ```markdown
  **Title:** [Concise bug summary]
  **Description:** Steps to reproduce the issue. What did you expect vs what happened?
  **Environment:** (OS, Python version, etc.)
  **Logs/Error:** Attach any error messages or logs.
  ```

- **GitHub PR Template (PULL_REQUEST_TEMPLATE.md):**  
  ```markdown
  ## Summary
  Briefly describe changes and link relevant issue.
  ## Type of change
  - [ ] Bug fix
  - [ ] New feature
  - [ ] Documentation
  ## How to test
  Steps to run tests or verify functionality.
  ## Checklist
  - [ ] Code builds and tests pass
  - [ ] Changelog updated (if applicable)
  - [ ] Documentation updated
  - [ ] CI checks completed
  ```

- **README.md Outline:** Key sections:
  ```
  # Expose Corruption System
  ## Project Overview
  ## Installation
  - Prerequisites (Python, Node, etc.)
  - Setup (pip install, npm install)
  ## Usage
  - How to run data pipeline
  - How to launch UI
  ## Contributing
  - See CONTRIBUTING.md
  ## License
  ```
- **CONTRIBUTING.md:** Should explain our branching, coding style, how to run tests, commit message format (e.g. Conventional Commits).

- **Unit/Integration Test Cases (example):**  
  - *Test ETL:* Given a small example tender JSON, ETL should correctly parse and insert one row in DB.  
  - *Test Anomaly:* On synthetic data with one outlier, the model should flag that row.  
  - *Test UI Route:* A test client fetching `/case/<id>` should return status 200 and expected fields.

## References

We will build on official SA data and guidelines. Priority sources include the National Treasury eTender portal【46†L39-L42】【50†L29-L33】, Municipal Finance API【48†L249-L251】【48†L259-L263】, and legal provisions (POPIA, Protected Disclosures)【46†L149-L153】【26†L186-L194】. All code will cite these sources in documentation and ensure compliance with South African laws.

