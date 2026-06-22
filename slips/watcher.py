import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
from slips.slip_parser import process_slip_image

load_dotenv()

SLIPS_FOLDER      = os.getenv("SLIPS_FOLDER", "./slips_folder")
SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".webp")

class SlipHandler(FileSystemEventHandler):
    """Handles new file events in slips_folder/."""

    def __init__(self, user_id: int = 1):
        self.user_id = user_id

    def on_created(self, event):
        if event.is_directory:
            return

        path = event.src_path
        if not path.lower().endswith(SUPPORTED_FORMATS):
            return

        print(f"\n{'─'*50}")
        print(f"   New slip detected!")
        print(f"  File: {os.path.basename(path)}")
        print(f"{'─'*50}")

        time.sleep(1)
        result = process_slip_image(path, user_id=self.user_id)
        print(f"  Result: {result}")
        print(f"\n Watching for new slips... (Ctrl+C to stop)")

def start_watcher(user_id: int = 1):
    """Start watching slips_folder/."""
    if not os.path.exists(SLIPS_FOLDER):
        os.makedirs(SLIPS_FOLDER)

    handler  = SlipHandler(user_id=user_id)
    observer = Observer()
    observer.schedule(handler, SLIPS_FOLDER, recursive=False)
    observer.start()

    print(f"\n{'═'*50}")
    print(f"   Watching: {SLIPS_FOLDER}")
    print(f"  Drop .jpg/.png slip photos to auto-process")
    print(f"  Press Ctrl+C to stop")
    print(f"{'═'*50}\n")

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n   Watcher stopped.")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    from db.database import init_db
    init_db()
    start_watcher()