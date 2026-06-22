from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

class UserCreate(BaseModel):
    """Validate new user data before saving."""
    name     : str
    email    : EmailStr         
    phone    : Optional[str] = None
    password : str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters")
        return v

    @field_validator("password")
    @classmethod
    def password_strong(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

    @field_validator("phone")
    @classmethod
    def phone_format(cls, v):
        if v is None:
            return v
        
        v = v.replace(" ", "").replace("-", "")
        if not v.isdigit():
            raise ValueError("Phone must contain only numbers")
        if len(v) < 10:
            raise ValueError("Phone must be at least 10 digits")
        return v
class UserLogin(BaseModel):
    """Validate login credentials."""
    email    : EmailStr
    password : str

class UserResponse(BaseModel):
    """What we send back to user — never send password!"""
    id       : int
    name     : str
    email    : str
    phone    : Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class GroceryItemCreate(BaseModel):
    """Validate one grocery item."""
    name        : str
    quantity    : float = 1.0
    unit        : str   = "pcs"
    unit_price  : float = 0.0
    total_price : float = 0.0
    category    : str   = "General"
    brand       : str   = ""

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Item name cannot be empty")
        return v.title()

    @field_validator("quantity")
    @classmethod
    def qty_positive(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v

    @field_validator("unit_price", "total_price")
    @classmethod
    def price_not_negative(cls, v):
        if v < 0:
            raise ValueError("Price cannot be negative")
        return round(v, 2)

    @field_validator("unit")
    @classmethod
    def valid_unit(cls, v):
        allowed = ["kg", "g", "ltr", "ml", "pcs", "pack",
                   "dz", "dozen", "box", "bag"]
        v = v.lower().strip()
        if v not in allowed:
            return "pcs"   
        return v
class GroceryItemResponse(BaseModel):
    """Item data returned to user."""
    id          : int
    name        : str
    quantity    : float
    unit        : str
    unit_price  : float
    total_price : float
    category    : str
    brand       : str

    class Config:
        from_attributes = True

class GrocerySlipCreate(BaseModel):
    """Validate a full grocery slip before saving."""
    month        : str
    store_name   : str                         = "Unknown"
    slip_date    : str                         = ""
    total_amount : float                       = 0.0
    items        : list[GroceryItemCreate]     = []

    @field_validator("month")
    @classmethod
    def valid_month(cls, v):
        import re
        v = v.strip()
        if not re.match(r"^\d{4}-\d{2}$", v):
            raise ValueError(
                "Month must be YYYY-MM format e.g. 2025-01"
            )
        return v

    @field_validator("total_amount")
    @classmethod
    def total_not_negative(cls, v):
        if v < 0:
            raise ValueError("Total amount cannot be negative")
        return round(v, 2)

    @field_validator("store_name")
    @classmethod
    def clean_store_name(cls, v):
        return v.strip().title() if v.strip() else "Unknown"

class GrocerySlipResponse(BaseModel):
    """Slip data returned to user."""
    id           : int
    month        : str
    store_name   : str
    slip_date    : str
    total_amount : float
    is_verified  : bool
    items        : list[GroceryItemResponse] = []

    class Config:
        from_attributes = True