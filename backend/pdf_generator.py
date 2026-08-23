import os
import qrcode
from fpdf import FPDF
from io import BytesIO
import tempfile

def generate_ticket_pdf(booking_id: str, passenger_name: str, flight_details: dict) -> bytes:
    """
    Generates a stylized PDF boarding pass and returns it as bytes.
    """
    # Create QR Code
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr_data = f"Booking ID: {booking_id}\nName: {passenger_name}\nFlight: {flight_details.get('airline')} {flight_details.get('flight_number')}\nRoute: {flight_details.get('route')}\nDate: {flight_details.get('date')}"
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code to a temp file because fpdf requires a path or a file-like object sometimes,
    # but fpdf2 allows images from file path.
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_qr:
        img.save(tmp_qr.name)
        qr_path = tmp_qr.name

    # Create PDF
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    
    # Title
    pdf.set_font("helvetica", "B", 24)
    pdf.set_text_color(0, 201, 255) # #00C9FF cyan
    pdf.cell(0, 20, "AI Flight Assistant - Boarding Pass", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    # Border Box
    pdf.set_draw_color(200, 200, 200)
    pdf.set_fill_color(249, 249, 249)
    pdf.rect(10, 40, 190, 120, style="DF")
    
    pdf.set_y(45)
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 10, "Passenger Details", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 12)
    pdf.cell(50, 8, "Name:")
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, passenger_name, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 12)
    pdf.cell(50, 8, "Booking ID:")
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, str(booking_id), new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(5)
    
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "Flight Information", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 12)
    pdf.cell(50, 8, "Airline:")
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, flight_details.get("airline", "N/A"), new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 12)
    pdf.cell(50, 8, "Flight Number:")
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, flight_details.get("flight_number", "N/A"), new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 12)
    pdf.cell(50, 8, "Route:")
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, flight_details.get("route", "N/A"), new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 12)
    pdf.cell(50, 8, "Date:")
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, flight_details.get("date", "N/A"), new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 12)
    pdf.cell(50, 8, "Price Paid:")
    pdf.set_font("helvetica", "B", 12)
    
    # FPDF with helvetica doesn't support the ₹ symbol, replace it with Rs.
    price_text = str(flight_details.get("price", "N/A")).replace("₹", "Rs. ")
    pdf.cell(0, 8, price_text, new_x="LMARGIN", new_y="NEXT")
    
    # Add QR code image
    pdf.image(qr_path, x=140, y=70, w=50)
    
    pdf.set_y(170)
    pdf.set_font("helvetica", "I", 10)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, "Please present this digital boarding pass at the gate. Have a safe flight!", align="C")

    # Get PDF as bytes
    pdf_bytes = bytes(pdf.output())
    
    # Cleanup temp qr
    try:
        os.remove(qr_path)
    except:
        pass
        
    return pdf_bytes
