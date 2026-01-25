from django.core.management.base import BaseCommand
from django.conf import settings
from livekit import api

class Command(BaseCommand):
    help = 'Generates a token for a HUMAN user to join the interview room.'

    def handle(self, *args, **options):
        # 1. Config
        ROOM_NAME = "interview-room-1"  # Must match the Bot's room
        USER_IDENTITY = "human-candidate"
        
        # 2. Create Token
        token = api.AccessToken(
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET
        ).with_identity(USER_IDENTITY) \
         .with_name("Human Candidate") \
         .with_grants(api.VideoGrants(
             room_join=True,
             room=ROOM_NAME,
         )).to_jwt()

        self.stdout.write(self.style.SUCCESS("\n✅ HERE IS YOUR TOKEN (Copy the long string below):\n"))
        self.stdout.write(token)
        self.stdout.write(self.style.SUCCESS("\n---------------------------------------------------\n"))