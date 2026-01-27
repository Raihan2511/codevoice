import asyncio
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from livekit import api
from apps.simulation.bot import run_ai_bot

class Command(BaseCommand):
    help = 'Starts the CodeVoice AI Worker.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Initializing CodeVoice AI...'))

        # 1. CONFIG
        ROOM_NAME = "interview-room-1"
        BOT_IDENTITY = "ai-interviewer"

        # 2. GENERATE TOKEN
        token = api.AccessToken(
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET
        ).with_identity(BOT_IDENTITY) \
         .with_name("Interviewer Bot") \
         .with_grants(api.VideoGrants(
             room_join=True,
             room=ROOM_NAME,
         )).to_jwt()

        # 3. CONNECT
        ws_url = settings.LIVEKIT_API_URL
        
        # --- NEW: GENERATE USER TOKEN FOR THE BROWSER ---
        user_token = api.AccessToken(
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET
        ).with_identity("user-listener") \
         .with_name("Human User") \
         .with_grants(api.VideoGrants(
             room_join=True,
             room=ROOM_NAME,
         )).to_jwt()

        # Write token to a file for easier retrieval
        with open("token.txt", "w") as f:
            f.write(user_token)

        self.stdout.write(self.style.WARNING(f"\n📢 COPY THIS TOKEN FOR test_room.html:\n{user_token}\n"))

        self.stdout.write(f"🔹 Connecting Bot to: {ROOM_NAME}")
        
        try:
            # UPDATE: We now pass ROOM_NAME as the 3rd argument
            asyncio.run(run_ai_bot(ws_url, token, ROOM_NAME))
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\n🛑 Stopping AI Worker...'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))