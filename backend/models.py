from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

class ChatMessage(BaseModel):
    user_id: int
    session_id: str
    message: str
    history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    response: str
    status: str

class BookingCreate(BaseModel):
    user_id: int
    flight_details: Dict[str, Any]

class FlightSaveRequest(BaseModel):
    user_id: int
    airline: str
    route: str
    price: str
    snippet: str

class CreateOrderRequest(BaseModel):
    user_id: int
    amount: int
    flight_details: Dict[str, Any]

class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    booking_id: int
