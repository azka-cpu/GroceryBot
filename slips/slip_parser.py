import os
import json
import base64
from datetime import datetime
from dotenv import load_dotenv
from db.database import get_session
from db.models import GrocerySlip, GroceryItem
load_dotenv()

def image_to_base64(image_path: str) -> tuple[str, str]:
    ext = image_path.lower().split(".")[-1]
    mime = {"jpg":"image/jpeg","jpeg":"image/jpeg",
            "png":"image/png","webp":"image/webp"}.get(ext,"image/jpeg")
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return b64, mime

def read_with_groq_vision(image_path: str) -> dict:
    from groq import Groq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env")

    client = Groq(api_key=api_key)
    b64, mime = image_to_base64(image_path)
    print(f"  Groq Vision reading slip...")

    response = client.chat.completions.create(
        model = "meta-llama/llama-4-scout-17b-16e-instruct",
        messages = [{
            "role" : "user",
            "content": [
                {
                    "type" : "image_url",
                    "image_url": {"url": f"data:{mime};base64,{b64}"}
                },
                {
                    "type": "text",
                    "text": """You are a grocery receipt reader.
Extract ALL items from this grocery slip image.
Return ONLY valid JSON, no markdown, no explanation:
{
  "store_name": "store name or Unknown",
  "date": "YYYY-MM-DD",
  "month": "YYYY-MM",
  "total_amount": 0.0,
  "items": [
    {
      "name": "Item Name",
      "quantity": 1.0,
      "unit": "kg or g or ltr or pcs",
      "unit_price": 0.0,
      "total_price": 0.0
    }
  ]
}
Rules:
- Item names in Title Case
- Skip tax/discount/change lines
- Use today's date if not visible
- Calculate unit_price = total_price / quantity if needed"""
                }
            ]
        }],
        max_tokens = 2000,
        temperature = 0,
    )
    raw = response.choices[0].message.content.strip()
    print("\n====== RAW ReSPONSE ======")
    print(raw)
    print("=========================\n")

    if "```" in raw:
        for part in raw.split("```"):
            if "{" in part:
                raw = part[4:] if part.startswith("json") else part
                break
    raw = raw.strip()

    data = json.loads(raw)
    try:
        data = json.loads(raw)
    except Exception as e:
        print("JSON ERROR:" , e)
        print("RAW JSON:")
        print(raw)
        raise
    print(f"  Found {len(data.get('items',[]))} items in {(lambda: __import__('time'))()} seconds")
    return data

def save_slip_to_db(data: dict, user_id: int = 1, image_path: str = "") -> str:
    session = get_session()
    try:
        existing = session.query(GrocerySlip).filter_by(
            user_id=user_id, month=data["month"]
        ).first()
        if existing:
            return f" {data['month']} already saved — skipped."

        slip = GrocerySlip(
            user_id = user_id,
            month = data["month"],
            store_name = data.get("store_name", "Unknown"),
            slip_date = data.get("date", ""),
            total_amount = float(data.get("total_amount", 0.0)),
            image_path = image_path,
        )
        total_calc = 0.0
        for it in data.get("items", []):
            item = GroceryItem(
                name = it.get("name", "Unknown"),
                quantity = float(it.get("quantity", 1.0)),
                unit = it.get("unit", "pcs"),
                unit_price = float(it.get("unit_price", 0.0)),
                total_price = float(it.get("total_price", 0.0)),
                slip = slip,
            )
            total_calc += item.total_price

        if slip.total_amount == 0.0:
            slip.total_amount = round(total_calc, 2)

        session.add(slip)
        session.commit()
        return (
            f" Saved [{data['month']}] | "
            f"{slip.store_name} | "
            f"{len(data['items'])} items | "
            f"Rs.{slip.total_amount}"
        )
    except Exception as e:
        session.rollback()
        return f" DB error: {e}"
    finally:
        session.close()

def process_slip_image(image_path: str, user_id: int = 1) -> str:
    """Full pipeline: image → Groq Vision → save to DB. Takes 2-5 seconds!"""
    print(f"\n  {os.path.basename(image_path)}")
    try:
        data = read_with_groq_vision(image_path)
        print(f"  Store : {data.get('store_name','?')}")
        print(f"  Month : {data.get('month','?')}")
        print(f"  Total : Rs.{data.get('total_amount',0)}")
        print(f"  Items : {len(data.get('items',[]))}")
        if not data.get("items"):
            return " No items found — make sure image is clear"
        return save_slip_to_db(data, user_id=user_id, image_path=image_path)
    except json.JSONDecodeError as e:
        return f" JSON parse error: {e}"
    except Exception as e:
        return f"Failed: {e}"

if __name__ == "__main__":
    import sys
    from db.database import init_db
    init_db()
    if len(sys.argv) > 1:
        print(process_slip_image(sys.argv[1]))
    else:
        print("Usage: python -m slips.slip_parser path/to/slip.jpg")