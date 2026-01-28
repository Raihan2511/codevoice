# src\apps\simulation\livekit_adapter.py
import asyncio
import numpy as np

from livekit import rtc
from pipecat.processors.audio.audio_input import AudioInput
from pipecat.processors.audio.audio_output import AudioOutput


class LiveKitAudioAdapter:
    def __init__(self, room: rtc.Room):
        self.room = room

        self.audio_input = AudioInput(
            sample_rate=16000,
            channels=1,
        )

        self.audio_output = AudioOutput(
            callback=self._send_audio_to_livekit,
            sample_rate=16000,
            channels=1,
        )

        self._audio_source = rtc.AudioSource(
            sample_rate=16000,
            channels=1,
        )

        self._local_track = rtc.LocalAudioTrack.create_audio_track(
            "ai-voice",
            self._audio_source,
        )

    async def start(self):
        await self.room.local_participant.publish_track(
            self._local_track
        )

        @self.room.on("track_subscribed")
        async def on_track(track, publication, participant):
            if track.kind != rtc.TrackKind.KIND_AUDIO:
                return

            async for frame in track:
                pcm = np.frombuffer(frame.data, dtype=np.int16)
                self.audio_input.push(pcm)

    def _send_audio_to_livekit(self, pcm: np.ndarray):
        frame = rtc.AudioFrame(
            data=pcm.tobytes(),
            sample_rate=16000,
            channels=1,
            samples_per_channel=len(pcm),
        )
        self._audio_source.capture_frame(frame)
