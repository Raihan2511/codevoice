# src\apps\simulation\run_ai_bot.py
from livekit import rtc
from apps.simulation.bot import build_pipecat_task
from apps.simulation.livekit_adapter import LiveKitAudioAdapter


async def run_ai_bot(ws_url: str, token: str, room_name: str):
    room = rtc.Room()

    await room.connect(ws_url, token)

    adapter = LiveKitAudioAdapter(room)
    await adapter.start()

    task = build_pipecat_task(
        adapter.audio_input,
        adapter.audio_output,
    )

    await task.run()
