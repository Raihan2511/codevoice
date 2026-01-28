# src\apps\simulation\bot.py
import os
from loguru import logger

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.frames.frames import TextFrame, LLMMessagesFrame
from pipecat.transports.livekit.transport import LiveKitTransport, LiveKitParams

from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.deepgram.tts import DeepgramTTSService
from pipecat.services.openai.llm import OpenAILLMService

from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)

from pipecat.turns.user_turn_strategies import UserTurnStrategies
from pipecat.turns.user_stop.turn_analyzer_user_turn_stop_strategy import (
    TurnAnalyzerUserTurnStopStrategy,
)
from pipecat.audio.turn.smart_turn.local_smart_turn_v3 import (
    LocalSmartTurnAnalyzerV3,
)


async def run_ai_bot(room_url: str, token: str, room_name: str):
    """Main entry point for the AI interviewer bot"""
    logger.info(f"🤖 AI connecting to room: {room_name}")

    # -------- SERVICES --------
    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY")
    )

    tts = DeepgramTTSService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        voice="aura-helios-en",
    )

    llm = OpenAILLMService(
        api_key=os.getenv("KRUTRIM_API_KEY"),
        base_url="https://cloud.olakrutrim.com/v1",
        model="gpt-oss-120b",
    )

    # -------- TRANSPORT --------
    transport = LiveKitTransport(
        url=room_url,
        token=token,
        room_name=room_name,
        params=LiveKitParams(
            audio_in_enabled=True,
            audio_out_enabled=True
        ),
    )

    # -------- CONTEXT --------
    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI technical interviewer. "
                "Ask one clear interview question at a time. "
                "Wait for the user to finish speaking before responding. "
                "Provide constructive feedback on their answers."
            )
        }
    ]
    
    context = LLMContext(messages)

    user_aggr, assistant_aggr = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(
            user_turn_strategies=UserTurnStrategies(
                stop=[
                    TurnAnalyzerUserTurnStopStrategy(
                        turn_analyzer=LocalSmartTurnAnalyzerV3()
                    )
                ]
            )
        ),
    )

    # -------- PIPELINE --------
    pipeline = Pipeline([
        transport.input(),
        stt,
        user_aggr,
        llm,
        tts,
        transport.output(),
        assistant_aggr,
    ])

    task = PipelineTask(pipeline)

    # -------- EVENT HANDLERS --------
    @transport.event_handler("on_first_participant_joined")
    async def on_first_participant_joined(transport, participant):
        logger.success(f"👤 User joined: {participant}")
        # Greet the user and start the interview
        messages.append({
            "role": "system",
            "content": "Greet the candidate and ask the first technical interview question."
        })
        await task.queue_frames([LLMMessagesFrame(messages)])

    @transport.event_handler("on_participant_left")
    async def on_participant_left(transport, participant, reason):
        logger.warning(f"👤 User left: {participant}")
        await task.cancel()

    # -------- RUN --------
    runner = PipelineRunner()
    await runner.run(task)
