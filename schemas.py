"""
Database Schemas for Teeth Whitening Store

Each Pydantic model below maps to a MongoDB collection. The collection name is the
lowercased class name (e.g., Order -> "order").
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

class Whiteningproduct(BaseModel):
    """
    Collection: "whiteningproduct"
    Represents a teeth whitening product (e.g., strips, kits).
    """
    title: str = Field(..., description="Product title")
    subtitle: Optional[str] = Field(None, description="Short tagline or subheading")
    description: Optional[str] = Field(None, description="Full product description")
    price: float = Field(..., ge=0, description="Price in your store currency")
    compare_at_price: Optional[float] = Field(None, ge=0, description="Strikethrough price for discount display")
    image: Optional[str] = Field(None, description="Primary image URL")
    gallery: Optional[List[str]] = Field(default_factory=list, description="Additional image URLs")
    badges: Optional[List[str]] = Field(default_factory=list, description="Small selling point badges")
    in_stock: bool = Field(True, description="Whether product is available")

class OrderItem(BaseModel):
    product_id: str = Field(..., description="ID of the product document")
    title: str
    unit_price: float = Field(..., ge=0)
    quantity: int = Field(1, ge=1)

class Order(BaseModel):
    """
    Collection: "order"
    Stores a placed order from checkout.
    """
    email: EmailStr
    full_name: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    region: Optional[str] = None
    postal_code: str
    country: str
    items: List[OrderItem]
    subtotal: float = Field(..., ge=0)
    shipping: float = Field(0, ge=0)
    total: float = Field(..., ge=0)
    marketing_opt_in: bool = False

class Subscriber(BaseModel):
    """
    Collection: "subscriber"
    For email capture (newsletter/discounts).
    """
    email: EmailStr
    source: Optional[str] = Field(None, description="Where the signup happened (e.g. hero, footer)")
