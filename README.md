# CodeVoice - AI-Powered Voice Application

## 1. Project Overview & Deep Analysis

**CodeVoice** is architected as a high-performance, real-time AI application foundation. It is designed to handle voice data, manage asynchronous tasks, and integrate with modern AI pipelines, though currently, it primarily provides the **infrastructure layer**.

### Core Architecture
The system follows a **Event-Driven, Service-Oriented Architecture** (monolithic repo, but modular services):

1.  **Django (The Brain)**:
    *   Serves as the control plane for Users, Data, and Business Logic.
    *   Configured to use **Daphne** (ASGI) instead of WSGI, enabling **WebSockets** and **Async** capabilities crucial for real-time voice streaming.
2.  **Backing Services (The Muscle)**:
    *   **PostgreSQL**: Relational data storage (Users, Metadata).
    *   **Redis**: High-speed message broker for:
        *   **Celery**: Background task processing (e.g., "Process this recording", "Summarize interview").
        *   **Channel Layers**: Handling WebSocket message distribution for real-time chat/voice state.
3.  **AI Integration (The Intelligence - Planning Phase)**:
    *   Dependencies are present for **LangChain** (LLM Orchestration) and **Pipecat** (Real-time multimodal agents), but the specific implementation logic (Agents, Pipelines) is yet to be added to the source code.

---

## 2. Detailed Folder Structure

Here is exactly what exists in your project and what each file/folder does:

```text
codevoice/
├── .env                    # [Generated] Environment variables (Database URLs, API Keys).
├── .env.example            # Template for your .env file.
├── docker-compose.yml      # Orchestration instructions to spin up Postgres & Redis.
├── requirements.txt        # List of all Python libraries needed.
├── docker/                 # Helper scripts for Docker/Development.
│   └── local/
│       └── django/
│           ├── start.sh    # Script to boot the Django server (currently empty/placeholder).
│           └── celery...   # (Future) Scripts to start background workers.
│
├── src/                    # THE SOURCE CODE ROOT
│   ├── manage.py           # Django's command-line utility (runserver, migrate, etc.).
│   │
│   ├── apps/               # Business Logic Modules
│   │   ├── users/          # [ACTIVE] User Management App.
│   │   │   ├── models.py   # Defines the Custom 'User' database table.
│   │   │   └── ...         # Standard Django app files.
│   │   ├── interviews/     # [EMPTY] Placeholder for Interview logic (recordings, sessions).
│   │   └── simulation/     # [EMPTY] Placeholder for AI Simulation logic.
│   │
│   └── config/             # Project Configuration (The "Core")
│       ├── settings.py     # Global settings (Apps, DB connection, Middleware).
│       ├── urls.py         # URL Routing (currently only has /admin).
│       ├── asgi.py         # Entry point for Async Server (WebSockets).
│       └── wsgi.py         # Entry point for traditional HTTP Server.
```

---

## 3. Current Capabilities vs. Road Map

| Feature Area | Current Status | Description |
| :--- | :--- | :--- |
| **Infrastructure** | ✅ **Ready** | Dockerized Postgres & Redis are working. Env vars are set up. |
| **User System** | ✅ **Ready** | Custom User model is active and migrated to DB. |
| **Authentication** | ⚠️ **Partial** | Backend support exists (Django Auth), but no API endpoints (Login/Signup) are defined in `urls.py`. |
| **Real-Time Voice** | ❌ **Pending** | `interviews` app is empty. `asgi.py` is default (no WebSocket routing). LiveKit/Pipecat logic is missing. |
| **AI Processing** | ❌ **Pending** | `simulation` app is empty. LangChain/OpenAI dependencies are installed but not used yet. |

---

## 4. Quick Start Guide

### Prerequisites
*   Docker Desktop (Running)
*   Python 3.10+
*   Git

### How to Run (The "Happy Path")

1.  **Start Database & Redis**
    ```bash
    docker-compose up -d
    ```

2.  **Install Application**
    ```bash
    # Install dependencies
    pip install -r requirements.txt
    
    # Run Database Migrations
    python src/manage.py migrate
    ```

3.  **Run Server**
    ```bash
    python src/manage.py runserver
    ```
    *   Server runs at: `http://127.0.0.1:8000/`
    *   Admin Panel: `http://127.0.0.1:8000/admin` (You'll need to create a superuser with `python src/manage.py createsuperuser` to log in).

### Troubleshooting
*   **Database connection failed?** Ensure Docker container `codevoice_db` is running (`docker ps`).
*   **Import Errors?** If you see errors about `pipecat-ai`, likely the "extras" failed to install. We fixed this by installing the base package.

---

## 5. Next Development Steps (Developer Guide)
To advance this project from "Skeleton" to "Application", you should:

1.  **Define API Endpoints**: Add `djangorestframework` views to `src/apps/users/` for Login/Register.
2.  **Build the Interview App**: Create models in `src/apps/interviews/models.py` to store "Sessions" and "Recordings".
3.  **Wire up WebSockets**: Modify `src/config/asgi.py` to route WebSocket connections to a Consumer (which will handle real-time voice data).
