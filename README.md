# CodeVoice: AI-Powered Technical Interview Simulator

**CodeVoice** is a scalable, real-time AI platform designed to conduct automated technical interviews. It acts as an interactive "Interviewer Bot" that can listen to candidates, evaluate their responses using LLMs, and provide real-time feedback.

The system is built on a **Service-Oriented Architecture** using **Django** for the control plane and **Pipecat** for the real-time AI pipeline.

---

## 🏗 System Architecture

The application is composed of three main layers:

### 1. The Control Plane (Django Monolith)
*   **Role**: Manages users, interview sessions, data persistence, and business logic.
*   **Core Components**:
    *   **REST API**: Built with `djangorestframework` (Foundations laid in `apps.users`, `apps.interviews`).
    *   **Database**: PostgreSQL (via Docker) stores Users, Questions, and Interview history.
    *   **Task Queue**: Redis + Celery (configured in `settings.py`) for handling long-running tasks like audio processing or report generation.

### 2. The AI Pipeline (Pipecat & LiveKit)
*   **Role**: Handles the real-time audio/video streaming and "thinking" process.
*   **Location**: `src/apps/simulation/bot.py`.
*   **Flow**:
    1.  **Transport**: **LiveKit** handles the WebRTC room connection (Audio I/O).
    2.  **STT (Ears)**: **Deepgram** transcribes user speech to text in real-time.
    3.  **LLM (Brain)**: **OpenAI / Krutrim** (GPT-OSS-120b) receives the transcript + context and generates a response.
    4.  **TTS (Mouth)**: **Deepgram** converts the LLM's text response back to high-quality audio (`aura-helios-en` voice).

### 3. The Real-Time Gateway (ASGI & WebSockets)
*   **Role**: Connects the user's browser to the backend.
*   **Technology**: **Daphne** (ASGI Server) sits in front of Django to handle WebSocket connections alongside standard HTTP requests.

---

## 📂 Codebase Deep Dive

### 1. Simulation App (`src/apps/simulation/`)
 This is the heart of the AI functionality.
*   **`bot.py`**: Contains the `run_ai_bot` function.
    *   **Pipeline Assembly**: connects `DeepgramSTTService` -> `OpenAILLMService` -> `DeepgramTTSService`.
    *   **Event Handling**: Listens for `on_first_participant_joined` to trigger the "System Online" greeting.
    *   **Logic**: It uses `pipecat.pipeline.task.PipelineTask` to run the conversation loop asynchronously.

### 2. Interviews App (`src/apps/interviews/`)
Manages the structure of an interview.
*   **`models.py`**:
    *   **`Question`**: Stores the question bank, currently supporting difficulty levels (EASY, MEDIUM, HARD) and "expected key points" for grading.
    *   **`InterviewSession`**: A state machine tracking a user's specific attempt (Started -> Completed/Failed). Tracks total score.
    *   **`InterviewTurn`**: Granular tracking of every exchange. Stores the `ai_message`, `user_transcript`, and even the `audio_file` for audit trails. Includes an AI-generated `score` (0-10) per answer.

### 3. Users App (`src/apps/users/`)
Custom authentication logic.
*   **`models.py`**: Implements a custom `User` model inheriting from `AbstractUser`.
    *   **Security Feature**: Uses **UUIDs** instead of sequential integers for primary keys to prevent ID enumeration attacks.

### 4. Configuration (`src/config/`)
*   **`settings.py`**:
    *   **Environment Variables**: Heavily uses `django-environ` to read secrets (API Keys, DB URLs) from `.env`.
    *   **Apps**: Registers `daphne` (top priority) and custom apps (`users`, `interviews`, `simulation`).
    *   **CORS**: Configured to allow frontend connections (currently open to all for dev).
*   **`asgi.py`**: The entry point for the Async server. (Note: WebSocket routing is currently a placeholder awaiting implementation).

---

## 🚀 Setup & Installation

### Prerequisites
*   **Docker Desktop** (for Redis & Postgres)
*   **Python 3.10+**
*   **LiveKit Server** (Managed or Local)
*   **API Keys**: Deepgram, OpenAI/Krutrim.

### Step 1: Services (Docker)
Start the backing services (Database & Broker):
```bash
docker-compose up -d
```
*   Verifies that `codevoice_db` (Postgres) and `codevoice_redis` are running.

### Step 2: Environment
Create a `.env` file in the project root:
```ini
DEBUG=on
DATABASE_URL=postgres://user:password@localhost:5432/codevoice
REDIS_URL=redis://localhost:6379/0
DEEPGRAM_API_KEY=your_key
KRUTRIM_API_KEY=your_key
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```
*Note: This installs heavy dependencies like `pipecat-ai`, `livekit`, `torch` (via silero implied dependency), and `django`.*

### Step 4: Database Setup
Apply the migrations to create the tables tailored to our apps:
```bash
python src/manage.py migrate
```

### Step 5: Run the Server
Use the Django command which wraps Daphne:
```bash
python src/manage.py runserver
```

---

## 🔮 Roadmap / Pending Implementation

While the infrastructure is solid, these connections need to be finalized:

1.  **Orchestrator**: Connecting the `run_ai_bot` function (in `simulation`) to a Celery task or an API endpoint so a frontend can "start" an interview.
2.  **WebSocket Routing**: Updates to `src/config/asgi.py` to route WebSocket traffic to a consumer that manages the LiveKit token generation.
3.  **Frontend**: A simple UI to login, view the dashboard, and join the LiveKit room.

---

**Tech Stack**: Python, Django 5, PostgreSQL, Redis, Celery, LiveKit, Pipecat AI, LangChain, Deepgram.
