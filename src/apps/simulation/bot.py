import os
import sys
import aiohttp
from django.conf import settings
from loguru import logger

# --- PIPECAT IMPORTS ---
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask

# 1. FRAMES (Updated to fix the Warning)
from pipecat.frames.frames import LLMMessagesUpdateFrame

# 2. TRANSPORT
from pipecat.transports.livekit.transport import LiveKitTransport, LiveKitParams

# 3. SERVICES
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.deepgram.tts import DeepgramTTSService
from pipecat.services.openai.llm import OpenAILLMService

async def run_ai_bot(room_url: str, token: str, room_name: str):
    logger.info(f"🤖 AI connecting to room: {room_name} at {room_url}")

    async with aiohttp.ClientSession() as session:
        
        # --- A. CONFIGURE SERVICES ---
        llm = OpenAILLMService(
            api_key=settings.KRUTRIM_API_KEY, 
            base_url="https://cloud.olakrutrim.com/v1",
            model="gpt-oss-120b",
        )

        stt = DeepgramSTTService(api_key=settings.DEEPGRAM_API_KEY)
        tts = DeepgramTTSService(api_key=settings.DEEPGRAM_API_KEY, voice="aura-helios-en")

        # --- B. CONFIGURE TRANSPORT ---
        transport = LiveKitTransport(
            url=room_url,
            token=token,
            room_name=room_name,
            params=LiveKitParams(audio_in_enabled=True, audio_out_enabled=True),
        )

        # --- C. BUILD PIPELINE ---
        pipeline = Pipeline([
            transport.input(),   # Listen
            stt,                 # Transcribe
            llm,                 # Think
            tts,                 # Speak
            transport.output(),  # Play Audio
        ])

        task = PipelineTask(pipeline)

        # --- D. EVENT HANDLERS ---
        @transport.event_handler("on_first_participant_joined")
        async def on_first_participant_joined(transport, participant):
            logger.success(f"User joined: {participant}")
            
            # THE FIX: Use LLMMessagesUpdateFrame with run_llm=True
            # This forces the AI to process this message immediately.
            await task.queue_frames([
                LLMMessagesUpdateFrame(
                    messages=[{
                        "role": "user", 
                        "content": "Hello! I am ready for the interview. Please introduce yourself briefly."
                    }],
                    run_llm=True  # <--- This triggers the "Generating chat" action
                )
            ])

        runner = PipelineRunner()
        await runner.run(task)