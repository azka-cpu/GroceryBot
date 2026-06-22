import hashlib
from datetime import datetime
from sqlalchemy.orm import Session
from db.models import User, GrocerySlip, GroceryItem, ChatHistory
from db.schemas import UserCreate, GrocerySlipCreate

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed

def create_user(session: Session, data: UserCreate) -> User | str:
    existing = session.query(User).filter_by(email=data.email).first()
    if existing:
        return f"Email {data.email} is already registered."

    user = User(
        name=data.name,
        email=data.email,
        phone=data.phone,
        password=hash_password(data.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def login_user(session: Session, email: str, password: str) -> User | str:
    user = session.query(User).filter_by(email=email).first()
    if not user:
        return "Email not found."
    if not verify_password(password, user.password):
        return "Wrong password."
    if not user.is_active:
        return "Account is deactivated."
    return user

def get_user_by_id(session: Session, user_id: int) -> User | None:
    return session.query(User).filter_by(id=user_id).first()

def get_user_by_email(session: Session, email: str) -> User | None:
    return session.query(User).filter_by(email=email).first()


def get_all_users(session: Session) -> list[User]:
    return session.query(User).filter_by(is_active=True).all()

def deactivate_user(session: Session, user_id: int) -> str:
    user = get_user_by_id(session, user_id)
    if not user:
        return "User not found."
    user.is_active = False
    session.commit()
    return f"User {user.email} deactivated."

def create_slip(session: Session, user_id: int, data: GrocerySlipCreate, image_path: str = "") -> GrocerySlip | str:
    existing = session.query(GrocerySlip).filter_by(user_id=user_id, month=data.month).first()
    if existing:
        return f"Slip for {data.month} already exists."

    slip = GrocerySlip(
        user_id=user_id,
        month=data.month,
        store_name=data.store_name,
        slip_date=data.slip_date,
        total_amount=data.total_amount,
        image_path=image_path,
    )

    running_total = 0.0
    for item_data in data.items:
        item = GroceryItem(
            name=item_data.name,
            quantity=item_data.quantity,
            unit=item_data.unit,
            unit_price=item_data.unit_price,
            total_price=item_data.total_price,
            category=item_data.category,
            brand=item_data.brand,
            slip=slip,
        )
        running_total += item.total_price

    if slip.total_amount == 0.0:
        slip.total_amount = round(running_total, 2)

    session.add(slip)
    session.commit()
    session.refresh(slip)
    return slip

def get_all_slips(session: Session, user_id: int) -> list[GrocerySlip]:
    return (
        session.query(GrocerySlip)
        .filter_by(user_id=user_id)
        .order_by(GrocerySlip.month)
        .all()
    )

def get_slip_by_month(session: Session, user_id: int, month: str) -> GrocerySlip | None:
    return session.query(GrocerySlip).filter_by(user_id=user_id, month=month).first()

def get_slip_summary(session: Session, user_id: int) -> list[dict]:
    slips = get_all_slips(session, user_id)
    return [
        {
            "month": s.month,
            "store": s.store_name,
            "total": s.total_amount,
            "item_count": len(s.items),
            "date": s.slip_date,
        }
        for s in slips
    ]

def delete_slip(session: Session, user_id: int, month: str) -> str:
    slip = get_slip_by_month(session, user_id, month)
    if not slip:
        return f"No slip found for {month}."
    session.delete(slip)
    session.commit()
    return f"Slip for {month} deleted."

def verify_slip(session: Session, user_id: int, month: str) -> str:
    slip = get_slip_by_month(session, user_id, month)
    if not slip:
        return f"No slip found for {month}."
    slip.is_verified = True
    session.commit()
    return f"Slip for {month} marked as verified."

def get_item_history(session: Session, user_id: int, item_name: str) -> list[dict]:
    items = (
        session.query(GroceryItem)
        .join(GrocerySlip)
        .filter(
            GrocerySlip.user_id == user_id,
            GroceryItem.name.ilike(f"%{item_name}%")
        )
        .order_by(GrocerySlip.month)
        .all()
    )
    return [
        {
            "month": item.slip.month,
            "store": item.slip.store_name,
            "name": item.name,
            "quantity": item.quantity,
            "unit": item.unit,
            "unit_price": item.unit_price,
            "total_price": item.total_price,
        }
        for item in items
    ]

def get_most_expensive_items(session: Session, user_id: int, limit: int = 5) -> list[dict]:
    items = (
        session.query(GroceryItem)
        .join(GrocerySlip)
        .filter(GrocerySlip.user_id == user_id)
        .order_by(GroceryItem.total_price.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "name": i.name,
            "month": i.slip.month,
            "total_price": i.total_price,
            "unit_price": i.unit_price,
            "unit": i.unit,
        }
        for i in items
    ]

def get_monthly_totals(session: Session, user_id: int) -> list[dict]:
    slips = get_all_slips(session, user_id)
    return [
        {"month": s.month, "total": s.total_amount}
        for s in slips
    ]

def compare_two_months(session: Session, user_id: int, month1: str, month2: str) -> dict:
    slip1 = get_slip_by_month(session, user_id, month1)
    slip2 = get_slip_by_month(session, user_id, month2)

    if not slip1:
        return {"error": f"No slip found for {month1}"}
    if not slip2:
        return {"error": f"No slip found for {month2}"}

    items1 = {i.name.lower(): i for i in slip1.items}
    items2 = {i.name.lower(): i for i in slip2.items}
    all_names = sorted(set(items1.keys()) | set(items2.keys()))

    item_comparison = []
    for name in all_names:
        p1 = items1[name].unit_price if name in items1 else None
        p2 = items2[name].unit_price if name in items2 else None
        change = round(p2 - p1, 2) if (p1 and p2) else None
        pct = round((p2 - p1) / p1 * 100, 1) if (p1 and p2 and p1 > 0) else None

        if change and change > 0:
            status = "increased"
        elif change and change < 0:
            status = "decreased"
        elif p1 is None:
            status = "new item"
        elif p2 is None:
            status = "removed"
        else:
            status = "same"

        item_comparison.append({
            "name": name.title(),
            "month1_price": p1,
            "month2_price": p2,
            "change": change,
            "pct_change": pct,
            "status": status,
        })

    total_change = round(slip2.total_amount - slip1.total_amount, 2)
    total_pct = round(total_change / slip1.total_amount * 100, 1) if slip1.total_amount else 0

    return {
        "month1": month1,
        "month2": month2,
        "total1": slip1.total_amount,
        "total2": slip2.total_amount,
        "total_change": total_change,
        "total_pct_change": total_pct,
        "item_comparison": item_comparison,
    }

def save_message(session: Session, user_id: int, thread_id: str, role: str, content: str):
    msg = ChatHistory(
        user_id=user_id,
        thread_id=thread_id,
        role=role,
        content=content,
    )
    session.add(msg)
    session.commit()

def get_chat_history(session: Session, user_id: int, thread_id: str) -> list[dict]:
    messages = (
        session.query(ChatHistory)
        .filter_by(user_id=user_id, thread_id=thread_id)
        .order_by(ChatHistory.created_at)
        .all()
    )
    return [
        {"role": m.role, "content": m.content, "created_at": m.created_at}
        for m in messages
    ]
