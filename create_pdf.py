from fpdf import FPDF
import os

pdf = FPDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)

# Title
pdf.set_font("helvetica", "B", 20)
pdf.cell(0, 15, "AI Flight Assistant - Master Knowledge Base V2", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.ln(5)

sections = {
    "1. Comprehensive Baggage Policies": [
        "Economy Class: 1 personal item (laptop bag/purse), 1 carry-on (up to 7kg), 1 checked bag (up to 15kg).",
        "Premium Economy: 1 personal item, 1 carry-on (up to 10kg), 2 checked bags (up to 20kg each).",
        "Business/First Class: 1 personal item, 2 carry-on bags (up to 15kg total), 2 checked bags (up to 32kg each).",
        "Excess Baggage Fees: INR 2000 per extra 5kg block purchased online. INR 3000 if purchased at the airport counter.",
        "Infant Baggage: Infants traveling on lap are allowed 1 diaper bag (up to 5kg) and 1 fully collapsible stroller.",
        "Sporting Equipment: Golf clubs, surfboards, bicycles, and ski equipment are charged a flat handling fee of INR 3500 per flight.",
        "Musical Instruments: Small instruments (violins/guitars) can be carried in the cabin. Cellos require purchasing an extra seat."
    ],
    "2. Prohibited & Restricted Items (Security)": [
        "Liquids Rule: All liquids in carry-on bags must be in containers of 100ml or less, placed in a single, transparent, resealable plastic bag.",
        "Power Banks & Lithium Batteries: STRICTLY PROHIBITED in checked luggage. Must be carried in cabin baggage only. Maximum capacity allowed is 160Wh.",
        "Hoverboards & E-Scooters: Completely banned on all flights due to fire risks.",
        "Duty-Free Alcohol: Maximum of 5 liters per passenger in retail packaging, containing between 24% and 70% alcohol by volume."
    ],
    "3. Cancellation, Modifications, & Refunds": [
        "24-Hour Grace Period: Full 100% refund to the original payment method if canceled within 24 hours of booking.",
        "Standard Cancellation (More than 7 days prior): INR 1500 cancellation fee per passenger. Remaining balance refunded in 5-7 business days.",
        "Late Cancellation (Less than 7 days prior): Non-refundable. Passenger receives a travel-credit voucher for 50% of the base fare, valid for 6 months.",
        "No-Show Policy: Failure to board without prior cancellation results in 100% ticket forfeiture. No refunds or credits.",
        "Flight Modifications: Date or route changes allowed up to 48 hours before departure. Modification fee is INR 1000 plus any fare difference."
    ],
    "4. Traveling with Pets": [
        "In-Cabin Pets: Only small dogs, cats, and household birds (under 8kg total with carrier) are allowed in the cabin. Fee: INR 2500 per segment.",
        "Cargo Pets: Larger pets must travel in the climate-controlled cargo hold. Fee: INR 5000. Temperature restrictions apply during summer.",
        "Brachycephalic (Snub-nosed) Breeds: Pugs, Bulldogs, Boxers, and Persian cats are STRICTLY PROHIBITED in the cargo hold due to severe respiratory risks at high altitudes.",
        "Service Animals: Certified guide dogs and emotional support animals travel free of charge in the cabin, provided proper documentation is submitted 48 hours in advance."
    ],
    "5. Special Assistance & Medical Policies": [
        "Wheelchair Assistance: Provided completely free of charge. Must be requested at least 48 hours prior to departure.",
        "Pregnancy Policy: Expectant mothers can fly safely up to 28 weeks without documentation. Between 28-36 weeks, a certified medical clearance certificate from a doctor is mandatory. Flying after 36 weeks is strictly prohibited.",
        "Unaccompanied Minors (UMNR): Mandatory for children aged 5-11 traveling alone. Fee is INR 3000 per flight. Airline staff will escort the child from check-in to the receiving guardian.",
        "Dietary Meals: Vegan, Vegetarian, Gluten-Free, Halal, and Kosher meals are available on flights exceeding 3 hours. Must be requested 24 hours prior to departure."
    ],
    "6. Travel Documentation & Visas": [
        "Domestic Travel: Valid government-issued photo ID (Aadhaar, PAN, Driving License, or Voter ID) is mandatory.",
        "International Travel: Passport must be valid for a minimum of 6 months beyond the date of the return flight.",
        "Schengen Visas: For travel to Europe, travelers must obtain the visa from the country where they will spend the majority of their time.",
        "Transit Visas: Passengers flying through the United States or Canada require a transit visa even if they do not leave the airport."
    ],
    "7. Corporate Travel & Reimbursement Policy (Company Specific)": [
        "Mandatory Booking Channel: All corporate travel MUST be booked exclusively through the AI Flight Assistant portal.",
        "Domestic Ticket Caps: Maximum allowed spend for domestic flights is INR 15,000.",
        "International Ticket Caps: Maximum allowed spend for international flights is INR 80,000.",
        "Class Approvals: All flights under 6 hours must be Economy Class. Business Class is strictly limited to flights exceeding 6 hours AND requires direct VP (Vice President) written approval.",
        "Executive Overrides: C-Level Executives (CEO, CFO, CTO) are exempt from price caps and class restrictions.",
        "Per Diem Rates: Employees receive a daily allowance of INR 2500 for domestic travel and USD $100 for international travel to cover meals and incidentals.",
        "Non-Reimbursable Expenses: In-flight Wi-Fi, alcohol, excess baggage for personal items, and cancellation fees due to personal reasons will NOT be reimbursed."
    ],
    "8. Loyalty Program (SkyRewards)": [
        "Silver Tier: Achieved at 25,000 miles. Benefits: 10% bonus miles, priority boarding, and 5kg extra baggage.",
        "Gold Tier: Achieved at 50,000 miles. Benefits: 25% bonus miles, free lounge access for member, and 10kg extra baggage.",
        "Platinum Tier: Achieved at 100,000 miles. Benefits: 50% bonus miles, free lounge access for member + 1 guest, two free upgrades per year, and 20kg extra baggage."
    ],
    "9. Flight Delays & Overbooking Compensation": [
        "Delays 2-4 Hours: Passengers receive free meal vouchers at the airport.",
        "Delays Over 4 Hours: Passengers are entitled to a full refund or rebooking on the next available flight, plus hotel accommodation if overnight.",
        "Involuntary Denied Boarding (Overbooking): If bumped from a flight, passengers receive a direct cash compensation of INR 10,000 plus a confirmed seat on the next flight."
    ]
}

for title, bullet_points in sections.items():
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(51, 51, 51)
    for point in bullet_points:
        pdf.multi_cell(190, 7, txt=f"- {point}")
    pdf.ln(6)

data_dir = os.path.join(os.path.dirname(__file__), "backend", "data")
os.makedirs(data_dir, exist_ok=True)

pdf_path = os.path.join(data_dir, "Company_Travel_Policy.pdf")
pdf.output(pdf_path)
print(f"Massive V2 PDF successfully generated at: {pdf_path}")
