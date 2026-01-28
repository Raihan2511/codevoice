import asyncio
from django.core.management.base import BaseCommand
from django.conf import settings
from livekit import api
from apps.simulation.bot import run_ai_bot



class Command(BaseCommand):
    help = "Starts the CodeVoice AI (LiveKit)"

    def handle(self, *args, **options):
        ROOM_NAME = "interview-room-1"
        BOT_ID = "ai-interviewer"

        token = api.AccessToken(
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET,
        ).with_identity(BOT_ID) \
         .with_name("AI Interviewer") \
         .with_grants(api.VideoGrants(
            room_join=True,
            room=ROOM_NAME,
         )).to_jwt()

        self.stdout.write(self.style.SUCCESS("🚀 LiveKit AI starting"))

        asyncio.run(
            run_ai_bot(
                settings.LIVEKIT_API_URL,
                token,
                ROOM_NAME,
            )
        )
