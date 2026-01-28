# CodeVoice: AI-Powered Technical Interview Simulator

**CodeVoice** is a real-time, voice-to-voice AI platform designed to conduct automated technical interviews. It acts as an interactive "Interviewer Bot" that listens to candidates, evaluates their responses using LLMs, and provides real-time feedback through natural conversation.

---

## 🏗️ System Architecture

CodeVoice is built on a **Service-Oriented Architecture** with three main layers working together:

```
┌─────────────────────────────────────────────────────────────┐
│                    USER (Browser)                           │
│              test_room.html + LiveKit Client                │
│                  (WebRTC Audio Stream)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓ Real-time Audio
┌─────────────────────────────────────────────────────────────┐
│              LiveKit Server (Docker Container)              │
│           Real-time Audio/Video Router (Port 7880)          │
│              Routes audio between Bot & User                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│         AI Bot (Pipecat Pipeline - src/apps/simulation)     │
│  ┌──────────┐  ┌──────┐  ┌─────┐  ┌──────┐  ┌──────────┐  │
│  │ Audio In │→ │ STT  │→ │ LLM │→ │ TTS  │→ │ Audio Out│  │
│  └──────────┘  └──────┘  └─────┘  └──────┘  └──────────┘  │
│   LiveKit     Deepgram  Krutrim  Deepgram    LiveKit       │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              Django Control Plane (Backend)                 │
│    User Management, Sessions, Database (PostgreSQL)         │
│         Task Queue (Celery + Redis)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Interaction Flow

### **Phase 1: Bot Initialization**

When you run `python src/manage.py run_bot`:

1. **Management Command** (`run_bot.py`):
   - Generates a **Bot Token** using LiveKit API keys
   - Bot identity: `ai-interviewer`
   - Room name: `interview-room-1`
   - Calls `run_ai_bot(ws_url, token, room_name)`

2. **Bot Startup** (`bot.py` - `run_ai_bot()` function):
   
   **Services Initialization:**
   - **STT (Speech-to-Text)**: Deepgram
     - Converts audio → text in real-time
     - Model: Default streaming model
   
   - **LLM (Brain)**: Krutrim AI (OpenAI-compatible)
     - Model: `gpt-oss-120b`
     - Endpoint: `https://cloud.olakrutrim.com/v1`
     - Generates intelligent responses
   
   - **TTS (Text-to-Speech)**: Deepgram
     - Voice: `aura-helios-en`
     - Converts text → natural-sounding audio
   
   **Transport Setup:**
   - Creates `LiveKitTransport` connection
   - Connects to LiveKit server as a participant
   - Enables audio input and output channels
   
   **Pipeline Construction:**
   ```python
   Pipeline([
       transport.input(),     # Receive audio from LiveKit
       stt,                   # Audio → Text
       user_aggr,             # Wait for complete user turn
       llm,                   # Generate AI response
       tts,                   # Text → Audio
       transport.output(),    # Send audio to LiveKit
       assistant_aggr,        # Save response to context
   ])
   ```

3. **Bot Status**: Connected to room, waiting for participants

---

### **Phase 2: User Joins the Interview**

When you open `test_room.html` and click "Connect":

1. **Browser Actions**:
   - Requests microphone permission
   - Connects to LiveKit using **User Token**
   - Publishes local audio track (your microphone)

2. **LiveKit Routing**:
   - Notifies bot: "New participant joined!"
   - Establishes bidirectional audio stream

3. **Bot Event Handler Triggers**:
   ```python
   @transport.event_handler("on_first_participant_joined")
   async def on_first_participant_joined(transport, participant):
       logger.success(f"👤 User joined: {participant}")
       messages.append({
           "role": "system",
           "content": "Greet the candidate and ask the first technical interview question."
       })
       await task.queue_frames([LLMMessagesFrame(messages)])
   ```

4. **What Happens**:
   - Bot adds system instruction to context
   - Sends to **LLM** (Krutrim)
   - LLM generates greeting + first question
   - Example: *"Hello! I'm your AI interviewer. Let's begin. Can you explain the difference between a process and a thread?"*
   - Text → **TTS** → Audio
   - Audio streams to your browser
   - **You hear the AI speaking!**

---

### **Phase 3: The Conversation Loop**

This is the core of the interview experience:

#### **When You Speak:**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Your Voice (Microphone)                                  │
│    "A process has its own memory space, while threads..."   │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Browser → LiveKit Server                                 │
│    Audio packets streamed in real-time                      │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. LiveKit → Bot Pipeline (transport.input())               │
│    Raw audio frames received                                │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. STT Service (Deepgram)                                   │
│    Audio → "A process has its own memory space..."          │
│    Real-time transcription                                  │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. User Aggregator (Turn Detection)                         │
│    - Uses LocalSmartTurnAnalyzerV3 AI model                 │
│    - Analyzes: silence, speech patterns, natural pauses     │
│    - Waits for you to finish speaking                       │
│    - Detects: "User stopped talking" ✓                      │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. LLM Service (Krutrim AI)                                 │
│    Input:                                                    │
│    - System prompt (interviewer instructions)               │
│    - Conversation history                                   │
│    - Your latest transcript                                 │
│                                                              │
│    Output:                                                   │
│    "That's correct! Processes are isolated. Can you         │
│     explain why thread synchronization is important?"       │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. TTS Service (Deepgram)                                   │
│    Text → Audio (Natural voice: aura-helios-en)             │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 8. Bot → LiveKit → Your Browser                             │
│    You hear the AI's response!                              │
└─────────────────────────────────────────────────────────────┘
```

**This loop repeats for the entire interview!**

---

## 🧠 Key Technical Components

### **1. Turn Detection System**

**Why it matters**: Prevents the bot from interrupting you mid-sentence.

```python
user_params=LLMUserAggregatorParams(
    user_turn_strategies=UserTurnStrategies(
        stop=[
            TurnAnalyzerUserTurnStopStrategy(
                turn_analyzer=LocalSmartTurnAnalyzerV3()
            )
        ]
    )
)
```

**How it works**:
- **LocalSmartTurnAnalyzerV3** is a specialized AI model (ONNX format)
- Analyzes audio patterns in real-time
- Detects:
  - Natural pauses vs. thinking pauses
  - End-of-sentence markers
  - Silence duration
- Only triggers LLM when confident you're done speaking
- Prevents awkward interruptions

---

### **2. Context Management (Conversation Memory)**

```python
messages = [
    {
        "role": "system",
        "content": "You are an AI technical interviewer..."
    }
]

context = LLMContext(messages)
```

**How it works**:
- Maintains full conversation history
- Each interaction adds to the context:
  - Your speech → "user" message
  - AI response → "assistant" message
- LLM sees the **entire conversation** each time
- Enables follow-up questions and contextual responses

**Example Context Flow**:
```json
[
  {"role": "system", "content": "You are an AI interviewer..."},
  {"role": "assistant", "content": "Hello! What is a process?"},
  {"role": "user", "content": "A process is an instance of a program..."},
  {"role": "assistant", "content": "Correct! Now explain threads..."}
]
```

---

### **3. The Pipecat Pipeline (Data Flow)**

Think of it as a **factory assembly line** for audio/text processing:

```python
Pipeline([
    transport.input(),     # 1. Receive audio from LiveKit
    stt,                   # 2. Convert audio → text
    user_aggr,             # 3. Wait for complete turn
    llm,                   # 4. Generate intelligent response
    tts,                   # 5. Convert text → audio
    transport.output(),    # 6. Send audio to LiveKit
    assistant_aggr,        # 7. Save to conversation history
])
```

**Frame Types** flowing through the pipeline:
- **AudioRawFrame**: Raw audio data
- **TranscriptionFrame**: Text from STT
- **TextFrame**: LLM-generated text
- **LLMMessagesFrame**: Context updates
- **TTSAudioRawFrame**: Synthesized speech

Each processor:
- Receives frames from the previous stage
- Processes them
- Outputs new frames to the next stage

---

## 🔑 Token System Explained

### **Why Two Tokens?**

1. **Bot Token** (Generated by `run_bot.py`):
   - Identity: `ai-interviewer`
   - Permissions: Join room, publish/subscribe audio
   - Generated automatically when bot starts

2. **User Token** (Generated by `get_user_token.py`):
   - Identity: `human-candidate`
   - Permissions: Join room, publish/subscribe audio
   - You need this to connect from the browser

### **Important Discovery: Browser Connection Persistence**

> **Key Insight**: If your browser tab (`test_room.html`) remains open, it maintains the LiveKit connection even with an old token. This is why the bot was responding before you updated the token - the browser was still connected from a previous session!

**Solution**: Always refresh the browser page after:
- Restarting the bot
- Generating a new token
- Changing room configuration

---

## 📂 Codebase Deep Dive

### **1. Simulation App** (`src/apps/simulation/`)

The heart of the AI functionality.

#### **`bot.py`**
Main AI pipeline implementation.

**Key Function**: `run_ai_bot(room_url, token, room_name)`

**Responsibilities**:
- Initialize AI services (STT, LLM, TTS)
- Create LiveKit transport
- Build Pipecat pipeline
- Set up event handlers
- Manage conversation context

**Event Handlers**:
- `on_first_participant_joined`: Greet user, start interview
- `on_participant_left`: Clean up when user disconnects

**Pipeline Flow**:
```
Audio In → STT → User Aggregator → LLM → TTS → Audio Out
         ↓                                        ↓
    Transcription                           Synthesized Speech
```

---

#### **`management/commands/run_bot.py`**
Django management command to start the bot.

**What it does**:
1. Loads LiveKit credentials from Django settings
2. Generates bot token
3. Launches `run_ai_bot()` with asyncio

**Usage**:
```bash
python src/manage.py run_bot
```

---

#### **`management/commands/get_user_token.py`**
Generates tokens for users to join the interview.

**What it does**:
1. Creates a LiveKit access token
2. Sets user identity and permissions
3. Prints token to console

**Usage**:
```bash
python src/manage.py get_user_token
```

**Output**:
```
✅ HERE IS YOUR TOKEN (Copy the long string below):
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### **2. Interviews App** (`src/apps/interviews/`)

Manages interview structure and data persistence.

#### **`models.py`**

**`Question` Model**:
- Stores interview questions
- Fields: `text`, `difficulty` (EASY/MEDIUM/HARD), `expected_key_points`
- Used for grading and evaluation

**`InterviewSession` Model**:
- Tracks a user's interview attempt
- State machine: `Started` → `Completed`/`Failed`
- Fields: `user`, `status`, `total_score`, `started_at`, `completed_at`

**`InterviewTurn` Model**:
- Granular tracking of each Q&A exchange
- Fields:
  - `session`: Foreign key to InterviewSession
  - `question`: Foreign key to Question
  - `ai_message`: What the bot asked
  - `user_transcript`: What you said
  - `audio_file`: Recording for audit trails
  - `score`: AI-generated score (0-10)

---

### **3. Users App** (`src/apps/users/`)

Custom authentication system.

#### **`models.py`**

**Custom `User` Model**:
- Inherits from `AbstractUser`
- **Security Feature**: Uses UUIDs instead of sequential integers for primary keys
- Prevents ID enumeration attacks

---

### **4. Configuration** (`src/config/`)

#### **`settings.py`**
Django settings with environment variable management.

**Key Configurations**:
- **Environment Variables**: Uses `django-environ` to read from `.env`
- **Apps**: Registers `daphne`, `users`, `interviews`, `simulation`
- **CORS**: Configured for frontend connections
- **Database**: PostgreSQL via Docker
- **Cache/Queue**: Redis for Celery tasks

**Required Environment Variables**:
```ini
DEBUG=on
DATABASE_URL=postgres://user:password@localhost:5432/codevoice
REDIS_URL=redis://localhost:6379/0
DEEPGRAM_API_KEY=your_deepgram_key
KRUTRIM_API_KEY=your_krutrim_key
LIVEKIT_API_URL=ws://localhost:7880
LIVEKIT_API_KEY=your_livekit_key
LIVEKIT_API_SECRET=your_livekit_secret
```

---

#### **`asgi.py`**
ASGI entry point for async server.

**Purpose**:
- Enables WebSocket support (for future features)
- Currently uses Daphne as ASGI server

---

## 🚀 Setup & Installation

### **Prerequisites**
- **Docker Desktop** (for Redis, Postgres, LiveKit)
- **Python 3.10+**
- **API Keys**: Deepgram, Krutrim

---

### **Step 1: Start Services**

```bash
docker-compose up -d
```

**Verifies**:
- `codevoice_db` (PostgreSQL)
- `codevoice_redis` (Redis)
- `codevoice_livekit` (LiveKit Server)

---

### **Step 2: Environment Configuration**

Create `.env` file in project root:

```ini
DEBUG=on
DATABASE_URL=postgres://user:password@localhost:5432/codevoice
REDIS_URL=redis://localhost:6379/0
DEEPGRAM_API_KEY=your_deepgram_key
KRUTRIM_API_KEY=your_krutrim_key
LIVEKIT_API_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```

---

### **Step 3: Install Dependencies**

```bash
pip install -r requirements.txt
```

**Key Dependencies**:
- `pipecat-ai`: AI pipeline framework
- `livekit`: Real-time communication
- `django`: Web framework
- `deepgram-sdk`: STT/TTS services
- `openai`: LLM client (for Krutrim)

---

### **Step 4: Database Setup**

```bash
python src/manage.py migrate
```

Creates tables for:
- Users
- Questions
- Interview Sessions
- Interview Turns

---

### **Step 5: Run the Bot**

```bash
python src/manage.py run_bot
```

**Expected Output**:
```
🚀 LiveKit AI starting
🤖 AI connecting to room: interview-room-1
✅ Connected to interview-room-1
🎧 Deepgram STT initialized
🎙️ Deepgram TTS initialized
⏳ Waiting for participants...
```

---

### **Step 6: Get User Token**

In a new terminal:

```bash
python src/manage.py get_user_token
```

**Copy the token** from the output.

---

### **Step 7: Connect from Browser**

1. Open `src/templates/test_room.html`
2. Paste your token in the input field
3. Click "Connect"
4. Allow microphone access
5. **Start talking!**

---

## 🎯 Usage Workflow

### **Complete Interview Flow**

1. **Start Services**: `docker-compose up -d`
2. **Start Bot**: `python src/manage.py run_bot`
3. **Generate Token**: `python src/manage.py get_user_token`
4. **Open Browser**: Navigate to `test_room.html`
5. **Paste Token**: Enter the generated token
6. **Connect**: Click "Connect" button
7. **Interview Begins**: Bot greets you and asks first question
8. **Conversation**: Answer naturally, bot responds with feedback
9. **End Interview**: Close browser or click disconnect

---

## 🔧 Troubleshooting

### **Bot Not Responding**

**Check**:
1. Bot is running: `python src/manage.py run_bot`
2. LiveKit container is up: `docker ps | grep livekit`
3. Browser has microphone permission
4. **Refresh browser page** (important for token updates!)

---

### **Connection Failed**

**Verify**:
1. LiveKit URL matches in `.env` and `test_room.html`
2. Token is not expired (tokens expire after ~6 hours)
3. Generate fresh token: `python src/manage.py get_user_token`

---

### **No Audio Heard**

**Debug**:
1. Check browser console for errors
2. Ensure audio element is created (inspect DOM)
3. Try manually clicking play on audio element
4. Verify Deepgram API key is valid

---

### **Bot Interrupting Too Early**

**Adjust**:
- The `LocalSmartTurnAnalyzerV3` model controls turn detection
- Currently uses default sensitivity
- Can be tuned in `bot.py` if needed

---

## 🔮 Roadmap / Future Enhancements

### **Planned Features**

1. **Orchestrator API**:
   - REST endpoint to start/stop interviews
   - Programmatic control from frontend

2. **WebSocket Integration**:
   - Real-time status updates
   - Live transcription display
   - Score visualization

3. **Frontend Dashboard**:
   - User login/registration
   - Interview history
   - Performance analytics
   - Question bank management

4. **Advanced Evaluation**:
   - Automatic scoring based on key points
   - Code execution for programming questions
   - Multi-turn follow-up questions

5. **Recording & Playback**:
   - Save interview recordings
   - Review sessions
   - Export transcripts

---

## 📊 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Django 5 | Control plane, API, data persistence |
| **Database** | PostgreSQL | User data, questions, sessions |
| **Cache/Queue** | Redis + Celery | Task queue, caching |
| **Real-time** | LiveKit | WebRTC audio routing |
| **AI Pipeline** | Pipecat | Stream processing framework |
| **STT** | Deepgram | Speech-to-text |
| **LLM** | Krutrim (GPT-OSS-120b) | Conversational AI |
| **TTS** | Deepgram | Text-to-speech |
| **ASGI Server** | Daphne | Async/WebSocket support |

---

## 🎓 Learning Resources

### **Understanding the Stack**

- **Pipecat Documentation**: https://docs.pipecat.ai
- **LiveKit Docs**: https://docs.livekit.io
- **Deepgram API**: https://developers.deepgram.com
- **Django Async**: https://docs.djangoproject.com/en/5.0/topics/async/

---

## 📝 License

[Your License Here]

---

## 🤝 Contributing

[Your Contributing Guidelines Here]

---

**Built with ❤️ using Pipecat, LiveKit, and Django**
