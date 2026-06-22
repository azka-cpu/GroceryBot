import os
from dotenv import load_dotenv
from slips.slip_parser import process_slip_image
load_dotenv()

SLIPS_FOLDER      = os.getenv("SLIPS_FOLDER", "./slips_folder")
SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".webp")

def process_all_slips(user_id: int = 1):
    """Process every image in slips_folder/."""
    if not os.path.exists(SLIPS_FOLDER):
        os.makedirs(SLIPS_FOLDER)
        print(f" Created: {SLIPS_FOLDER}")
        print("  Drop your slip photos there and run again.")
        return

    images = sorted([
        f for f in os.listdir(SLIPS_FOLDER)
        if f.lower().endswith(SUPPORTED_FORMATS)
    ])

    if not images:
        print(f" No images found in {SLIPS_FOLDER}")
        print("  Supported: .jpg .jpeg .png .webp")
        return

    print(f"\n{'═'*50}")
    print(f"   Found {len(images)} slip image(s)")
    print(f"{'═'*50}")

    results = []
    for i, img_name in enumerate(images, 1):
        print(f"\n[{i}/{len(images)}] {img_name}")
        full_path = os.path.join(SLIPS_FOLDER, img_name)
        result    = process_slip_image(full_path, user_id=user_id)
    print(f"\n{'═'*50}")
    print("   SUMMARY")
    print(f"{'═'*50}")
    success = 0
    for name, status in results:
        icon = "OK" if status.startswith("Saved") else "Fail"
        print(f"  {icon} {name:30s}")
        if status.startswith("Saved"):
            success += 1

    print(f"\n  Done: {success}/{len(images)} slips saved successfully")

if __name__ == "__main__":
    from db.database import init_db
    init_db()
    process_all_slips()