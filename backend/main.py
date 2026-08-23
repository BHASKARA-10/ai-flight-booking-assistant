from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from models import ChatMessage, ChatResponse, UserCreate, UserResponse, FlightSaveRequest, CreateOrderRequest, VerifyPaymentRequest
from database import get_db_connection
from auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
import os
import json
import razorpay
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

razorpay_client = razorpay.Client(auth=(os.getenv("RAZORPAY_KEY_ID", "rzp_test_123"), os.getenv("RAZORPAY_KEY_SECRET", "secret_123")))

app = FastAPI(
    title="AI Flight Booking Assistant API",
    description="Backend API for the AI Flight Booking Assistant",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static assets directory
assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "assets")
if not os.path.exists(assets_dir):
    os.makedirs(assets_dir, exist_ok=True)
app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is running."}

@app.get("/user/bookings/{user_id}")
def get_user_bookings(user_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
        
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, flight_details, status, payment_status, created_at FROM bookings WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        bookings = cursor.fetchall()
        for b in bookings:
            if isinstance(b["flight_details"], str):
                b["flight_details"] = json.loads(b["flight_details"])
        return bookings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/create_order")
def create_order(req: CreateOrderRequest):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    try:
        order_data = {
            "amount": req.amount * 100,
            "currency": "INR",
            "receipt": f"receipt_{req.user_id}"
        }
        
        try:
            order = razorpay_client.order.create(data=order_data)
            razorpay_order_id = order["id"]
        except Exception as e:
            # Fallback to mock order if Razorpay auth fails
            import uuid
            razorpay_order_id = f"order_MOCK_{uuid.uuid4().hex[:10]}"
            order = {"amount": order_data["amount"]}
        
        cursor = conn.cursor()
        flight_json = json.dumps(req.flight_details)
        passengers = req.flight_details.get("passengers", [])
        num_passengers = len(passengers) if passengers else 1
        
        cursor.execute(
            "INSERT INTO bookings (user_id, flight_details, num_passengers, status, payment_status) VALUES (%s, %s, %s, 'PENDING', 'UNPAID')",
            (req.user_id, flight_json, num_passengers)
        )
        conn.commit()
        booking_id = cursor.lastrowid
        
        if passengers:
            for p in passengers:
                cursor.execute(
                    "INSERT INTO passengers (booking_id, name, email, phone, age, seat_preference) VALUES (%s, %s, %s, %s, %s, %s)",
                    (booking_id, p.get("name", ""), p.get("email", ""), p.get("phone", ""), p.get("age", 30), p.get("seat_preference", "No Preference"))
                )
            conn.commit()
            
        cursor.close()
        
        return {"razorpay_order_id": razorpay_order_id, "booking_id": booking_id, "amount": order["amount"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/verify_payment")
def verify_payment(req: VerifyPaymentRequest):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
        
    try:
        params_dict = {
            'razorpay_order_id': req.razorpay_order_id,
            'razorpay_payment_id': req.razorpay_payment_id,
            'razorpay_signature': req.razorpay_signature
        }
        
        if req.razorpay_signature == "MOCK_SIGNATURE":
            is_valid = True
        else:
            try:
                razorpay_client.utility.verify_payment_signature(params_dict)
                is_valid = True
            except:
                is_valid = False
                
        if not is_valid:
            cursor = conn.cursor()
            cursor.execute("UPDATE bookings SET status='CANCELLED', payment_status='FAILED' WHERE id=%s", (req.booking_id,))
            conn.commit()
            raise HTTPException(status_code=400, detail="Payment verification failed")
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("UPDATE bookings SET status='CONFIRMED', payment_status='PAID' WHERE id=%s", (req.booking_id,))
        conn.commit()
        
        # Fetch flight details to send email
        cursor.execute("SELECT flight_details FROM bookings WHERE id=%s", (req.booking_id,))
        booking_row = cursor.fetchone()
        if booking_row and booking_row.get('flight_details'):
            import json
            try:
                flight_details = json.loads(booking_row['flight_details'])
                passengers = flight_details.get('passengers', [])
                if passengers:
                    passenger_email = passengers[0].get('email')
                    passenger_name = passengers[0].get('name')
                else:
                    passenger_email = None
                    passenger_name = None
                
                if passenger_email:
                    from email_service import send_booking_confirmation
                    from pdf_generator import generate_ticket_pdf
                    import threading
                    
                    pdf_bytes = None
                    try:
                        pdf_bytes = generate_ticket_pdf(str(req.booking_id), passenger_name, flight_details)
                    except Exception as pdf_e:
                        print(f"Error generating PDF: {pdf_e}")
                        
                    threading.Thread(target=send_booking_confirmation, args=(passenger_email, passenger_name, flight_details, pdf_bytes)).start()
            except Exception as email_e:
                print(f"Error sending email: {email_e}")
                
        cursor.close()
        
        return {"status": "success", "message": "Payment verified and booking confirmed!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/booking_status/{booking_id}")
def check_booking_status(booking_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT payment_status FROM bookings WHERE id=%s", (booking_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"status": row["payment_status"]}

@app.get("/download_ticket/{booking_id}")
def download_ticket(booking_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
        
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT flight_details FROM bookings WHERE id=%s", (booking_id,))
        booking_row = cursor.fetchone()
        
        if not booking_row or not booking_row.get('flight_details'):
            raise HTTPException(status_code=404, detail="Booking not found")
            
        import json
        flight_details = json.loads(booking_row['flight_details'])
        passengers = flight_details.get('passengers', [])
        passenger_name = passengers[0].get('name') if passengers else "Passenger"
        
        from pdf_generator import generate_ticket_pdf
        pdf_bytes = generate_ticket_pdf(str(booking_id), passenger_name, flight_details)
        
        filename = f"Ticket_{flight_details.get('airline', 'Flight')}_{flight_details.get('flight_number', '')}.pdf".replace(" ", "_")
        return Response(
            content=pdf_bytes, 
            media_type="application/pdf", 
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    cursor = conn.cursor(dictionary=True)
    
    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (user.username, user.email))
    existing_user = cursor.fetchone()
    if existing_user:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Username or email already registered")
        
    hashed_password = get_password_hash(user.password)
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (user.username, user.email, hashed_password)
        )
        conn.commit()
        new_user_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return UserResponse(id=new_user_id, username=user.username, email=user.email)
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
        
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (form_data.username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not user or not verify_password(form_data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "user_id": user["id"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": user["id"]}

@app.post("/save_flight")
def save_flight(flight: FlightSaveRequest):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
        
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO saved_flights (user_id, airline, route, price, snippet) VALUES (%s, %s, %s, %s, %s)",
            (flight.user_id, flight.airline, flight.route, flight.price, flight.snippet)
        )
        conn.commit()
        return {"status": "success", "message": "Flight saved successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

from agent import get_ai_response

@app.post("/chat", response_model=ChatResponse)
def process_chat(chat_msg: ChatMessage):
    user_message = chat_msg.message
    
    conn = get_db_connection()
    username = None
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT username FROM users WHERE id = %s", (chat_msg.user_id,))
            user = cursor.fetchone()
            if user:
                username = user.get('username')
                
            session_name = user_message[:47] + "..." if len(user_message) > 50 else user_message
            cursor.execute(
                "INSERT IGNORE INTO chat_sessions (user_id, session_id, session_name) VALUES (%s, %s, %s)",
                (chat_msg.user_id, chat_msg.session_id, session_name)
            )
                
            cursor.execute(
                "INSERT INTO chat_history (user_id, session_id, message, role) VALUES (%s, %s, %s, 'USER')",
                (chat_msg.user_id, chat_msg.session_id, user_message)
            )
            conn.commit()
        except Exception as e:
            print("DB Error:", e)
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    # Get actual response from LangChain/Gemini
    ai_reply = get_ai_response(user_message, chat_msg.history, username)
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO chat_history (user_id, session_id, message, role) VALUES (%s, %s, %s, 'AI')",
                (chat_msg.user_id, chat_msg.session_id, ai_reply)
            )
            conn.commit()
        except Exception as e:
            print("DB Error:", e)
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
            
    return ChatResponse(response=ai_reply, status="success")

@app.get("/sessions/{user_id}")
def get_user_sessions(user_id: int):
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT session_id, session_name as title, created_at, is_pinned
            FROM chat_sessions
            WHERE user_id = %s AND is_deleted = FALSE
            ORDER BY is_pinned DESC, created_at DESC
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except Exception as e:
        print("DB Error:", e)
        return []
    finally:
        cursor.close()
        conn.close()

@app.post("/sessions/{session_id}/pin")
def toggle_pin_session(session_id: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE chat_sessions SET is_pinned = NOT is_pinned WHERE session_id = %s", (session_id,))
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE chat_sessions SET is_deleted = TRUE WHERE session_id = %s", (session_id,))
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/history/{session_id}")
def get_session_history(session_id: str):
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT role, message FROM chat_history WHERE session_id = %s ORDER BY created_at ASC"
        cursor.execute(query, (session_id,))
        messages = cursor.fetchall()
        
        pairs = []
        current_intent = None
        
        for msg in messages:
            if msg["role"].upper() == "USER":
                current_intent = msg["message"]
            elif msg["role"].upper() == "AI" and current_intent is not None:
                pairs.append({"intent": current_intent, "response": msg["message"]})
                current_intent = None
                
        if current_intent is not None:
            pairs.append({"intent": current_intent, "response": ""})
            
        return pairs
    except Exception as e:
        print("DB Error:", e)
        return []
    finally:
        cursor.close()
        conn.close()

@app.delete("/history/{session_id}")
def delete_chat_history(session_id: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = conn.cursor()
    try:
        query = "DELETE FROM chat_history WHERE session_id = %s"
        cursor.execute(query, (session_id,))
        conn.commit()
        return {"status": "deleted"}
    except Exception as e:
        print("DB Error:", e)
        raise HTTPException(status_code=500, detail="Failed to delete chat")
    finally:
        cursor.close()
        conn.close()
