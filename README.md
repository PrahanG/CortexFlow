# CortexFlow - Autonomous Enterprise Document Governance & Triage

CortexFlow is a premium, multi-agent AI document governance, triage, and RAG search platform. It parses unstructured enterprise documents, runs privacy audits, performs NLP enrichment, and drafts routing actions through a LangGraph agentic swarm.

Built using a decoupled modern stack:
* **Frontend**: Angular 18 (Standalone architecture) with a space-tech glassmorphism dashboard and custom SVG visualizations.
* **Backend**: Python FastAPI service with SQLAlchemy (asynchronous engine) and WebSockets.
* **Swarm Orchestration**: LangGraph StateGraph (Agentic Workflow).
* **Storage & Retrieval**: MySQL (structured telemetry/metadata) and ChromaDB (vector indexing & grounded semantic search).
* **AI Models**: Google Gemini `gemini-2.5-flash` for agent reasoning & RAG; `gemini-embedding-2-preview` for native multi-modal vector embeddings.

---

## 🏗️ Architecture Design

The following diagram illustrates the end-to-end data ingestion, vector indexing, multi-agent swarm execution, and real-time dashboard notification pipelines:

```mermaid
flowchart TD
    subgraph Client [Frontend Interface]
        Dashboard[Angular Dashboard]
        WS[WebSocket Client]
        Chat[Sliding RAG Chatbot]
    end

    subgraph Ingestion [Ingestion Pipeline]
        Upload[FastAPI Ingestion Endpoint]
        Parser[Layout-Aware PDF Block Parser]
        Embeddings[Gemini Embeddings Service]
    end

    subgraph DB [Storage Layers]
        Chroma[(ChromaDB Vector Store)]
        MySQL[(Aiven MySQL Database)]
    end

    subgraph Swarm [LangGraph Agent Swarm]
        Triage[Agent A: Triage & Classify]
        Compliance[Agent B: Privacy Guardian]
        Enrichment[NLP Enrichment Node]
        Router[Agent C: Action Router]
    end

    %% Flow Steps
    Dashboard -->|1. Ingest File| Upload
    Upload -->|2. Extract Blocks| Parser
    Parser -->|3. Generate Vectors| Embeddings
    Embeddings -->|4. Index Passage Chunks| Chroma

    Upload -->|5. Trigger Swarm| Triage
    Triage -->|Extract Metadata & Type| Compliance
    Compliance -->|Audit PII & Risk Level| Enrichment
    Enrichment -->|Sentiment, Readability, NER| Router
    Router -->|Recommend Action & Draft Template| MySQL

    %% Real-time Updates
    Swarm -->|6. Stream Node Logs via WS| WS
    WS -->|7. Update UI Timeline| Dashboard
    MySQL -->|8. Fetch Metadata & Audits| Dashboard
    Chat -->|9. Grounded RAG Query| Chroma
```

---

## 🚀 Key Features

1. **Layout-Aware PDF Block Parsing**: Parses documents using PyMuPDF and orders them by coordinate-sorted visual reading sequence (avoiding split paragraphs or broken RAG chunks).
2. **Multi-Agent Swarm Workflow**:
   * **Agent A (Triage)**: Classifies documents (Invoices, Contracts, HR Policies) and extracts key metadata properties.
   * **Agent B (Privacy Guardian)**: Audits files for sensitive PII (Social Security Numbers, Credit Cards, Emails) and assigns risk ratings (Low, Medium, High).
   * **Enrichment Node**: Analyzes text sentiment tone, extracts named entities (NER tags), and computes Flesch readability indices.
   * **Agent C (Action Router)**: Recommends governance actions and drafts communication templates.
3. **Grounded RAG Chatbot**: A sliding chatbot overlay that queries indexed document passages and returns grounded answers with clickable source citations.
4. **Interactive SVG Visualizations**: Native dashboard metrics featuring an SVG donut chart with hover legend segments and animated compliance risk progress bars.
5. **EIM Ingestion Simulator (Export)**: Packs the original file, a structured `governance_report.json` metadata report, and the routed email draft into a downloadable ZIP archive.

---

## 🛠️ Local Installation & Setup

### Prerequisites
* Docker & Docker Compose
* Python 3.11+
* Node.js v20+

### Step 1: Start MySQL and ChromaDB Services
Run Docker Compose in the project root to spin up databases:
```bash
docker-compose up -d
```

### Step 2: Configure and Run the Backend
1. Navigate to the `backend/` directory.
2. Create a `.env` file:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   DATABASE_URL=mysql+aiomysql://docuswarm_user:docuswarm_password@127.0.0.1:3306/docuswarm_db
   CHROMA_HOST=127.0.0.1
   CHROMA_PORT=8000
   ```
3. Initialize the virtual environment and install requirements:
   ```bash
   python -m venv env
   env\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```
4. Run the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --port 8080 --host 127.0.0.1
   ```

### Step 3: Configure and Run the Frontend
1. Navigate to the `frontend/` directory.
2. Install Node packages:
   ```bash
   npm install
   ```
3. Start the Angular development server:
   ```bash
   npm start
   ```
4. Open `http://localhost:4200` in your web browser.

---

## ☁️ Cloud Deployment Configuration

CortexFlow is fully pre-configured for cloud-native deployment:

### 1. Database & Vector DB Setup
* **MySQL Database**: Host on **Aiven MySQL** (GCP `us-central1` recommended). Copy the Service URI and update the connection protocol to `mysql+aiomysql://`.
* **Vector Database**: Create a collection on **TryChroma / Chroma Cloud** (AWS `us-east-1` recommended). Save your API Key, Tenant ID, and Database Name.

### 2. Backend Deployment (Google Cloud Run)
* Build the container using Google Cloud Build and deploy the service:
  ```bash
  gcloud builds submit --tag gcr.io/<your-gcp-project-id>/cortexflow-backend backend/
  gcloud run deploy cortexflow-backend --image gcr.io/<your-gcp-project-id>/cortexflow-backend --platform managed --region us-central1 --allow-unauthenticated
  ```
* Set the following Environment Variables in the Cloud Run configuration panel:
  * `DATABASE_URL`: `mysql+aiomysql://avnadmin:password@yourhost.aivencloud.com:port/defaultdb?ssl-mode=REQUIRED`
  * `GEMINI_API_KEY`: `<your-gemini-api-key>`
  * `CHROMA_API_KEY`: `<your-trychroma-api-key>`
  * `CHROMA_TENANT`: `<your-trychroma-tenant-id>`
  * `CHROMA_DATABASE`: `<your-trychroma-database-name>`
  * `WS_URL`: `wss://<your-cloud-run-domain>/api/v1/documents`

### 3. Frontend Deployment (Vercel)
1. Replace the placeholder URL in `frontend/vercel.json` with your actual Google Cloud Run service URL.
2. Link your GitHub repository to Vercel and import the `frontend/` folder.
3. Vercel will automatically compile the Angular standalone project and serve it.
