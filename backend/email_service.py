import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

def send_booking_confirmation(passenger_email: str, passenger_name: str, flight_details: dict, pdf_bytes: bytes = None):
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not smtp_email or not smtp_password or smtp_email == "YOUR_GMAIL_ADDRESS_HERE":
        print("SMTP Credentials not set. Skipping email send.")
        return False
        
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "✈️ Your Flight Booking is Confirmed!"
        msg["From"] = f"AI Flight Assistant <{smtp_email}>"
        msg["To"] = passenger_email
        
        airline = flight_details.get("airline", "Unknown Airline")
        flight_number = flight_details.get("flight_number", "")
        route = flight_details.get("route", "")
        date = flight_details.get("date", "")
        price = flight_details.get("price", "")
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px;">
                <div style="max-width: 600px; margin: auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                    <div style="background-color: #00C9FF; padding: 20px; text-align: center; color: white;">
                        <h1 style="margin: 0;">Booking Confirmed! 🎉</h1>
                    </div>
                    <div style="padding: 30px;">
                        <p style="font-size: 16px; color: #333;">Dear <strong>{passenger_name}</strong>,</p>
                        <p style="font-size: 16px; color: #555;">Your payment was successful and your ticket has been issued.</p>
                        
                        <div style="background-color: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #00C9FF;">
                            <h3 style="margin-top: 0; color: #333;">Flight Details</h3>
                            <p style="margin: 5px 0;"><strong>Route:</strong> {route}</p>
                            <p style="margin: 5px 0;"><strong>Date:</strong> {date}</p>
                            <p style="margin: 5px 0;"><strong>Flight:</strong> {airline} {flight_number}</p>
                            <p style="margin: 5px 0;"><strong>Total Paid:</strong> {price}</p>
                        </div>
                        
                        <p style="font-size: 14px; color: #777;">Thank you for booking with AI Flight Assistant! We wish you a wonderful journey.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        part = MIMEText(html_content, "html", "utf-8")
        msg.attach(part)
        
        if pdf_bytes:
            pdf_attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
            filename = f"Ticket_{flight_details.get('airline', 'Flight')}_{flight_details.get('flight_number', '')}.pdf".replace(" ", "_")
            pdf_attachment.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(pdf_attachment)
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(smtp_email, smtp_password.replace(" ", ""))
        server.sendmail(smtp_email, passenger_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
