# filepath: /Users/paedarrader/DormView-CompletelyMerged/staging-main/external/management/commands/run_roomgpt.py
import subprocess
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Run the RoomGPT Next.js server'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting RoomGPT server...")
        subprocess.Popen(["npm", "run", "dev"], cwd="roomgpt")