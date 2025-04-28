import streamlit as st
import random
import time
import pandas as pd
from datetime import datetime, timedelta

# --- Helper Functions ---
def generate_random_datetime(start_date, end_date):
    """Generate a random datetime between start and end dates."""
    time_between_dates = end_date - start_date
    days_between = time_between_dates.days
    random_number_of_days = random.randrange(days_between)
    random_date = start_date + timedelta(days=random_number_of_days)
    random_time = datetime.min.time().replace(
        hour=random.randint(0, 23), 
        minute=random.randint(0, 59), 
        second=random.randint(0, 59)
    )
    return datetime.combine(random_date, random_time).strftime("%Y-%m-%d %H:%M:%S")

# --- Mock Data Generation ---
def generate_mock_data():
    """Generate comprehensive mock data for the telecom application."""
    customer_id = f"VZ{random.randint(100000, 999999)}"
    customer_name = f"{random.choice(['Alice', 'Bob', 'Charlie', 'David', 'Emma'])} {random.choice(['J.', 'M.', 'S.'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'])}"
    
    # Order Statuses
    order_statuses = [
        "Pending Verification", "Processing", "Shipped", 
        "Out for Delivery", "Delivered", "Installation Scheduled", 
        "Completed", "Cancelled"
    ]
    
    # Case Data
    interaction_cases = [
        {"case_id": f"IC-{random.randint(10000, 99999)}", 
         "date": generate_random_datetime(datetime.now() - timedelta(days=30), datetime.now()),
         "subject": "Network Connectivity Issue", 
         "status": "Open", 
         "priority": "High"},
        {"case_id": f"IC-{random.randint(10000, 99999)}", 
         "date": generate_random_datetime(datetime.now() - timedelta(days=30), datetime.now()),
         "subject": "Billing Inquiry - Monthly Statement", 
         "status": "Open", 
         "priority": "Medium"},
        {"case_id": f"IC-{random.randint(10000, 99999)}", 
         "date": generate_random_datetime(datetime.now() - timedelta(days=30), datetime.now()),
         "subject": "Device Replacement Request", 
         "status": "Open", 
         "priority": "High"},
        {"case_id": f"IC-{random.randint(10000, 99999)}", 
         "date": generate_random_datetime(datetime.now() - timedelta(days=30), datetime.now()),
         "subject": "Account Verification", 
         "status": "Open", 
         "priority": "Low"},
        {"case_id": f"IC-{random.randint(10000, 99999)}", 
         "date": generate_random_datetime(datetime.now() - timedelta(days=30), datetime.now()),
         "subject": "Service Upgrade Information", 
         "status": "Closed", 
         "priority": "Medium"}
    ]
    
    follow_up_cases = [
        {"case_id": f"FC-{random.randint(10000, 99999)}", 
         "date": generate_random_datetime(datetime.now() - timedelta(days=30), datetime.now()),
         "subject": "Double Billing Issue", 
         "status": "Open", 
         "priority": "High"},
        {"case_id": f"FC-{random.randint(10000, 99999)}", 
         "date": generate_random_datetime(datetime.now() - timedelta(days=30), datetime.now()),
         "subject": "Signal Dropout Investigation", 
         "status": "In Progress", 
         "priority": "Medium"},
        {"case_id": f"FC-{random.randint(10000, 99999)}", 
         "date": generate_random_datetime(datetime.now() - timedelta(days=30), datetime.now()),
         "subject": "Contract Renewal Follow-up", 
         "status": "Pending Customer", 
         "priority": "Low"}
    ]
    
    # Tracking Details
    mock_tracking_details = {
        "Pending Verification": [
            "Order submitted. Awaiting verification of details.",
            f"Tracking Number: PV{random.randint(10000, 99999)}"
        ],
        "Processing": [
            "Order being processed at our fulfillment center.",
            f"Expected Processing Time: {random.randint(1, 5)} business days"
        ],
        "Shipped": [
            f"Shipment dispatched via {random.choice(['Speedy Logistics', 'Quick Deliver', 'Fast Track'])}",
            f"Tracking ID: SL{random.randint(10000, 99999)}",
            f"Estimated Delivery: {(datetime.now() + timedelta(days=random.randint(2, 7))):%Y-%m-%d}"
        ]
    }
    
    # Knowledge Base Articles
    kb_articles = [
        {"kb_id": "KB-8374", "title": "Resolving Network Connectivity Issues", "category": "Technical Support"},
        {"kb_id": "KB-6291", "title": "Understanding Your Monthly Bill", "category": "Billing"},
        {"kb_id": "KB-9452", "title": "Device Replacement Process", "category": "Customer Service"},
        {"kb_id": "KB-5017", "title": "Service Upgrade Options", "category": "Sales"},
        {"kb_id": "KB-7725", "title": "Troubleshooting Signal Problems", "category": "Technical Support"}
    ]
    
    # Past Support Cases
    past_cases = [
        {"case_id": "CSR-7392", "description": "Customer reported intermittent service interruptions", "resolution": "Router reset and diagnostics performed remotely", "status": "Resolved"},
        {"case_id": "CSR-6104", "title": "Billing adjustment request", "resolution": "Credit applied for service outage period", "status": "Resolved"},
        {"case_id": "CSR-8271", "title": "Device not connecting to network", "resolution": "SIM card replaced", "status": "Resolved"},
        {"case_id": "CSR-5549", "title": "Service upgrade inquiry", "resolution": "Customer upgraded to premium plan", "status": "Resolved"}
    ]
    
    # Troubleshooting Steps
    mock_troubleshooting_steps = {
        "No Internet": [
            "1. Check Modem & Router: Ensure both devices are powered ON",
            "2. Verify Cable Connections: Check all network cables",
            "3. Restart Network Devices: Power cycle modem and router",
            "4. Check Service Status: Verify no known outages"
        ],
        "Slow Connection": [
            "1. Run Speed Test: Measure current internet speed",
            "2. Check Device Interference: Minimize nearby electronic interference",
            "3. Update Router Firmware: Ensure latest software is installed",
            "4. Contact Support for Advanced Diagnostics"
        ],
        "Signal Drop": [
        "1. Check Antenna Connections: Ensure all cables are securely connected",
        "2. Verify Signal Strength: Use device's signal status page",
        "3. Reboot Equipment: Power cycle modem and router",
        "4. Check for Obstructions: Remove any physical barriers near equipment"
        ]
    }
    
    # Appointments
    mock_appointments = [
        {
            "appt_id": f"APT{random.randint(1000, 9999)}",
            "date": (datetime.now() + timedelta(days=random.randint(1, 10))).strftime("%Y-%m-%d"),
            "time": f"{random.randint(9, 17):02d}:00 - {random.randint(9, 17)+2:02d}:00",
            "type": random.choice(["Installation", "Repair", "Consultation"]),
            "status": random.choice(["Scheduled", "Pending Confirmation"]),
            "technician": f"{random.choice(['John', 'Jane', 'Mike', 'Sarah'])} {random.choice(['Doe', 'Smith', 'Johnson'])}"
        } for _ in range(3)
    ]
    
    # Store Locations
    store_locations = [
        {"id": "ST001", "name": "Downtown VZ Store", "address": "123 Main St, Anytown", "distance": "2.3 miles"},
        {"id": "ST002", "name": "Westfield Mall VZ Store", "address": "456 Shopping Way, Anytown", "distance": "4.1 miles"},
        {"id": "ST003", "name": "Eastside VZ Store", "address": "789 East Blvd, Anytown", "distance": "5.8 miles"},
        {"id": "ST004", "name": "Northpoint VZ Store", "address": "101 North Ave, Anytown", "distance": "7.2 miles"}
    ]
    
    # Equipment Compatibility
    mock_equipment_compatibility = {
        "Fiber Home Basic": ["FH-M2000 (Modem)", "WRT-300 (Router)"],
        "High-Speed Internet & TV Bundle": ["GH-X5000 (Modem/Router Combo)", "STB-HD-01 (HD Set-Top Box)"],
        "Premium Mobile & Broadband": [
            "Nokia G400 5G (Device)", 
            "FH-M2500 (Modem)", 
            "Linksys AX1800 (Router)"
        ]
    }
    
    # Recent Activity
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    mock_recent_activity = [
        {
            "timestamp": generate_random_datetime(start_date, end_date),
            "type": random.choice(["Call", "SMS", "Data Usage", "Payment", "Website Visit"]),
            "details": random.choice([
                "Customer inquired about data usage",
                "Reminder for upcoming bill payment",
                "Used 15 GB of 50 GB data allowance",
                "Payment received",
                "Viewed upgrade options"
            ])
        } for _ in range(5)
    ]
    
    # Bill Overview
    mock_bill_overview = {
        "Account Number": f"ACCT{random.randint(100000, 999999)}",
        "Billing Period": f"{(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')} - {datetime.now().strftime('%Y-%m-%d')}",
        "Current Balance": f"${random.randint(500, 2000)}.00",
        "Due Date": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
        "Last Payment": f"${random.randint(1000, 5000)}.00 on {(datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')}",
        "Service Charges": {
            "Internet (50 Mbps)": f"${random.randint(300, 600)}.00",
            "Voice (Unlimited Local)": f"${random.randint(100, 300)}.00"
        },
        "Usage This Month": {
            "Internet (50 Mbps)": f"${random.randint(300, 600)}.00",
            "Voice (Unlimited Local)": f"${random.randint(100, 300)}.00"
        },
        "Pending Charges": "$0.00"
    }
    
    # Promotions
    mock_promotions = [
        {
            "promo_code": f"PROMO{random.randint(100, 999)}",
            "name": random.choice([
                "Free Fiber Upgrade", 
                "20% Off Internet Bundle", 
                "Unlimited Mobile Data"
            ]),
            "details": random.choice([
                "Upgrade to our super-fast fiber plan",
                "Bundle internet and get massive discounts",
                "Enjoy unlimited data for the next 3 months"
            ])
        } for _ in range(3)
    ]
    
    # Customer Details
    customer_details = {
        "personal_info": {
            "name": customer_name,
            "email": f"{customer_name.split()[0].lower()}@example.com",
            "phone": f"(555) {random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "address": f"{random.randint(100, 999)} {random.choice(['Maple', 'Oak', 'Pine', 'Cedar'])} {random.choice(['St', 'Ave', 'Blvd', 'Rd'])}, {random.choice(['Springfield', 'Riverdale', 'Oakwood', 'Maplewood'])}, {random.choice(['CA', 'NY', 'TX', 'FL'])} {random.randint(10000, 99999)}"
        },
        "account_info": {
            "account_number": f"ACCT{random.randint(100000, 999999)}",
            "customer_id": customer_id,
            "customer_since": (datetime.now() - timedelta(days=random.randint(100, 1000))).strftime('%B %d, %Y'),
            "loyalty_tier": random.choice(["Silver", "Gold", "Platinum", "Diamond"]),
            "credit_score": f"{random.randint(650, 850)} (Excellent)",
            "auto_pay": random.choice(["Enabled", "Disabled"]),
            "paperless_billing": random.choice(["Enabled", "Disabled"])
        },
        "service_info": {
            "plan": random.choice(["Premium Mobile & Broadband", "High-Speed Internet & TV Bundle", "Fiber Home Basic"]),
            "status": "Active",
            "products": [
                {"type": "Internet", "details": "Fiber 1 Gbps", "monthly_fee": f"${random.randint(800, 1200)}.00"},
                {"type": "Mobile", "details": "Unlimited Plan (2 lines)", "monthly_fee": f"${random.randint(800, 1200)}.00"},
                {"type": "TV", "details": "Premium Entertainment Package", "monthly_fee": f"${random.randint(800, 1200)}.00"}
            ],
            "equipment": [
                {"type": "Modem", "model": random.choice(["VZ-FiberX Pro", "Nokia G400 5G", "GH-X5000", "FH-M2500"]), "status": "Active"},
                {"type": "Router", "model": random.choice(["VZ-WiFi 6E", "Linksys AX1800", "WRT-300", "TP-Link Archer AX73"]), "status": "Active"},
                {"type": "Set-Top Box", "model": random.choice(["VZ-Stream Ultra", "STB-HD-01", "Amazon Fire TV Cube", "Roku Ultra"]), "status": "Active"}
            ]
        },
        "support_history": {
            "total_cases": random.randint(3, 10),
            "open_cases": random.randint(0, 2),
            "last_interaction": (datetime.now() - timedelta(days=random.randint(5, 30))).strftime('%B %d, %Y'),
            "preferred_contact": random.choice(["Email", "Phone", "SMS", "In-app"])
        }
    }
    
    return {
        "customer_id": customer_id,
        "customer_name": customer_name,
        "customer_details": customer_details,
        "order_statuses": order_statuses,
        "interaction_cases": interaction_cases,
        "follow_up_cases": follow_up_cases,
        "tracking_details": mock_tracking_details,
        "troubleshooting_steps": mock_troubleshooting_steps,
        "appointments": mock_appointments,
        "equipment_compatibility": mock_equipment_compatibility,
        "recent_activity": mock_recent_activity,
        "bill_overview": mock_bill_overview,
        "promotions": mock_promotions,
        "kb_articles": kb_articles,
        "past_cases": past_cases,
        "store_locations": store_locations
    }

# --- UI Styling Function ---
def apply_custom_styling():
    st.markdown("""
    <style>
    /* Overall App Styling */
    .stApp {
        background-color: #f4f6f9;
        font-family: 'Inter', sans-serif;
    }
    
    /* Widget Card Styling */
    .widget-card {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 20px;
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    .widget-card:hover {
        transform: scale(1.02);
    }
    
    /* Widget Header Styling */
    .widget-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        border-bottom: 2px solid #f0f2f5;
        padding-bottom: 10px;
    }
    .widget-header h3 {
        margin: 0;
        margin-left: 10px;
        color: #2c3e50;
    }
    
    /* Button Styling */
    .stButton > button {
        background-color: #3498db;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 15px;
        transition: background-color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #2980b9;
    }
    
    /* Expander Styling */
    .stExpander {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Enhanced Agent Dashboard Styling */
    .agent-profile {
        background-color: #2c3e50;
        color: white;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .agent-profile h2 {
        margin: 0;
        color: white;
        font-size: 1.5em;
    }
    .agent-profile p {
        margin: 5px 0;
        opacity: 0.8;
    }
    
    /* Navigation Styling */
    .stRadio > div {
        background-color: #ecf0f1;
        border-radius: 12px;
        padding: 10px;
    }
    .stRadio > div > label {
        background-color: white;
        border-radius: 8px;
        padding: 8px 12px;
        margin: 5px 0;
        transition: all 0.3s ease;
    }
    .stRadio > div > label:hover {
        background-color: #3498db;
        color: white;
    }
    
    /* Agent Performance Badge */
    .performance-badge {
        background-color: #27ae60;
        color: white;
        border-radius: 20px;
        padding: 5px 10px;
        font-size: 0.8em;
        display: inline-block;
        margin-top: 10px;
    }
    
    /* Table Styling */
    .styled-table {
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 0.9em;
        font-family: sans-serif;
        min-width: 400px;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
        border-radius: 8px;
        overflow: hidden;
    }
    .styled-table thead tr {
        background-color: #009879;
        color: #ffffff;
        text-align: left;
    }
    .styled-table th,
    .styled-table td {
        padding: 12px 15px;
    }
    .styled-table tbody tr {
        border-bottom: 1px solid #dddddd;
    }
    .styled-table tbody tr:nth-of-type(even) {
        background-color: #f3f3f3;
    }
    .styled-table tbody tr:last-of-type {
        border-bottom: 2px solid #009879;
    }
    
    /* KB Article Link Styling */
    .kb-link {
        color: #3498db;
        text-decoration: none;
        font-weight: bold;
        transition: color 0.3s;
    }
    .kb-link:hover {
        color: #2980b9;
        text-decoration: underline;
    }
    
    /* Case Link Styling */
    .case-link {
        background-color: #f0f7fc;
        border: 1px solid #d1e6f8;
        border-radius: 4px;
        padding: 4px 8px;
        margin: 2px 0;
        display: inline-block;
        font-size: 0.9em;
        color: #3498db;
        transition: all 0.3s;
    }
    .case-link:hover {
        background-color: #d1e6f8;
    }
    
    /* AI Assistant Styling */
    .ai-assistant-panel {
        background-color: #f8f9fa;
        border-left: 4px solid #3498db;
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 0 8px 8px 0;
    }
    .ai-assistant-panel h4 {
        color: #2c3e50;
        margin-top: 0;
    }
    .ai-step {
        margin-bottom: 10px;
        padding-left: 20px;
        position: relative;
    }
    .ai-step:before {
        content: "→";
        position: absolute;
        left: 0;
        color: #3498db;
    }
    </style>
    """, unsafe_allow_html=True)

# --- AI Query Processing ---
def process_ai_query(query, mock_data):
    """
    Process customer service queries using enhanced AI logic
    
    Args:
        query (str): User's query
        mock_data (dict): Mock customer data
    
    Returns:
        dict: AI generated response with structure for professional display
    """
    # Normalize query
    query = query.lower()
    
    # Mimic AI processing steps
    steps = [
        "Analyzing query intent and context...",
        "Accessing knowledge base and customer history...",
        "Retrieving relevant cases and information...",
        "Formulating personalized response..."
    ]
    
    # Find relevant KB articles
    relevant_kb_articles = []
    if "upgrade" in query or "service" in query:
        relevant_kb_articles.append({"id": "KB-5017", "title": "Service Upgrade Options"})
    if "bill" in query or "payment" in query:
        relevant_kb_articles.append({"id": "KB-6291", "title": "Understanding Your Monthly Bill"})
    if "troubleshoot" in query or "issue" in query or "problem" in query:
        relevant_kb_articles.append({"id": "KB-8374", "title": "Resolving Network Connectivity Issues"})
        relevant_kb_articles.append({"id": "KB-7725", "title": "Troubleshooting Signal Problems"})
    if "device" in query or "equipment" in query:
        relevant_kb_articles.append({"id": "KB-9452", "title": "Device Replacement Process"})
    
    # Find similar past cases
    similar_cases = []
    if "connectivity" in query or "internet" in query or "signal" in query:
        similar_cases.append({"id": "CSR-7392", "title": "Intermittent service interruptions"})
    if "bill" in query or "payment" in query:
        similar_cases.append({"id": "CSR-6104", "title": "Billing adjustment request"})
    if "device" in query or "equipment" in query:
        similar_cases.append({"id": "CSR-8271", "title": "Device not connecting to network"})
    if "upgrade" in query:
        similar_cases.append({"id": "CSR-5549", "title": "Service upgrade inquiry"})
    
    # Generate response based on query type
    if "upgrade" in query:
        summary = f"""
        <strong>Customer is inquiring about service upgrade options.</strong>
        <ul>
            <li>Current Plan: {mock_data['customer_details']['service_info']['plan']}</li>
            <li>Eligibility: Yes (account in good standing)</li>
            <li>Recommended: Premium Mobile & Broadband</li>
            <li>Promotional Offers: 3 months discounted rate available</li>
        </ul>
        <p>Consider highlighting fiber speed benefits and entertainment package add-ons based on customer's usage patterns.</p>
        """
    elif "bill" in query:
        summary = f"""
        <strong>Customer has a billing inquiry.</strong>
        <ul>
            <li>Current Balance: {mock_data['bill_overview']['Current Balance']}</li>
            <li>Billing Period: {mock_data['bill_overview']['Billing Period']}</li>
            <li>Due Date: {mock_data['bill_overview']['Due Date']}</li>
            <li>Payment Method: {mock_data['customer_details']['account_info']['auto_pay']}</li>
        </ul>
        <p>Remind customer of paperless billing discount and autopay options if not already enrolled.</p>
        """
    elif "troubleshoot" in query or "issue" in query or "problem" in query:
        issue_type = "No Internet" if "internet" in query else "Slow Connection"
        summary = f"""
        <strong>Customer experiencing technical difficulties: {issue_type}</strong>
        <ul>
            <li>Equipment: {mock_data['customer_details']['service_info']['equipment'][0]['model']} (Modem)</li>
            <li>Last Connection: Today at {datetime.now().strftime('%H:%M')}</li>
            <li>Connection Status: Unstable</li>
            <li>Recent Outages: None reported in customer's area</li>
        </ul>
        <p>Recommend troubleshooting steps and offer remote diagnostics if basic steps don't resolve issue.</p>
        """
    else:
        summary = f"""
        <strong>General inquiry detected.</strong>
        <ul>
            <li>Customer Profile: {mock_data['customer_details']['account_info']['loyalty_tier']} tier</li>
            <li>Account Status: Active, good standing</li>
            <li>Recent Activity: {mock_data['recent_activity'][0]['type']} on {datetime.now().strftime('%Y-%m-%d')}</li>
        </ul>
        <p>Please request more specific information from customer to better assist with their needs.</p>
        """
    
    # Build comprehensive response
    response = {
        "processing_steps": steps,
        "kb_articles": relevant_kb_articles,
        "similar_cases": similar_cases,
        "response_summary": summary,
        "followup_question": "Is there anything specific about this matter that you'd like me to address further?"
    }
    
    return response

# --- Enhanced Functions ---
def render_agent_dashboard(mock_data):
    """Enhanced agent dashboard with comprehensive customer details."""
    # Agent Profile Section
    st.markdown("""
    <div class="agent-profile">
        <h2>🕴️ Agent Profile</h2>
        <p><strong>Name:</strong> Sarah Thompson</p>
        <p><strong>Department:</strong> Customer Support</p>
        <p><strong>Shift:</strong> Morning (8:00 AM - 4:00 PM)</p>
        <div class="performance-badge">
            🏆 Performance: Excellent
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Customer Details Section with expanded information
    customer_details = mock_data['customer_details']
    
    st.markdown(f"""
    <div class="widget-card">
        <div class="widget-header">
            <h3>👤 Customer Details</h3>
        </div>
        <p><strong>Name:</strong> {customer_details['personal_info']['name']}</p>
        <p><strong>Email:</strong> {customer_details['personal_info']['email']}</p>
        <p><strong>Phone:</strong> {customer_details['personal_info']['phone']}</p>
        <p><strong>Address:</strong> {customer_details['personal_info']['address']}</p>
        <hr>
        <p><strong>Account #:</strong> {customer_details['account_info']['account_number']}</p>
        <p><strong>Customer ID:</strong> {customer_details['account_info']['customer_id']}</p>
        <p><strong>Customer Since:</strong> {customer_details['account_info']['customer_since']}</p>
        <p><strong>Loyalty Tier:</strong> {customer_details['account_info']['loyalty_tier']}</p>
        <p><strong>Credit Score:</strong> {customer_details['account_info']['credit_score']}</p>
        <hr>
        <p><strong>Current Plan:</strong> {customer_details['service_info']['plan']}</p>
        <p><strong>Status:</strong> {customer_details['service_info']['status']}</p>
        <p><strong>Auto-Pay:</strong> {customer_details['account_info']['auto_pay']}</p>
        <p><strong>Paperless Billing:</strong> {customer_details['account_info']['paperless_billing']}</p>
    </div>
    """, unsafe_allow_html=True)

def render_dashboard(mock_data):
    """Render the dashboard with key metrics and case management."""
    st.header("🏠 Customer Support Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="widget-card">
            <div class="widget-header">
                <h3>📦 Active Orders</h3>
            </div>
            <p>Total Active: <strong>{len(mock_data['appointments'])}</strong></p>
            <p>Processing: <strong>{random.randint(1, len(mock_data['appointments']))}</strong></p>
            <p>Scheduled: <strong>{random.randint(1, len(mock_data['appointments']))}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="widget-card">
            <div class="widget-header">
                <h3>🛠️ Support Tickets</h3>
            </div>
            <p>Open Tickets: <strong>{random.randint(10, 50)}</strong></p>
            <p>Resolved Today: <strong>{random.randint(5, 30)}</strong></p>
            <p>Average Resolution Time: <strong>{random.randint(1, 4)} hrs</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="widget-card">
            <div class="widget-header">
                <h3>📋 Case Management</h3>
            </div>
            <p>Interaction Cases: <strong>{len(mock_data['interaction_cases'])}</strong></p>
            <p>Follow-up Cases: <strong>{len(mock_data['follow_up_cases'])}</strong></p>
            <p>Priority Cases: <strong>{random.randint(1, 3)}</strong></p>
        </div>
        """, unsafe_allow_html=True)

    
    # Case Management Details (expanded when clicked)
    if st.checkbox("View Case Management Details"):
        st.subheader("Case Management Overview")
        
        # Tabs for different case types
        tab1, tab2 = st.tabs(["Interaction Cases", "Follow-up Cases"])
        
        with tab1:
            st.markdown("<h4>Active Interaction Cases</h4>", unsafe_allow_html=True)
            interaction_df = pd.DataFrame(mock_data['interaction_cases'])
            st.dataframe(interaction_df, use_container_width=True)
            
            if st.button("Process Selected Interaction Case"):
                st.success("Case assigned for processing!")
        
        with tab2:
            st.markdown("<h4>Customer Follow-up Cases</h4>", unsafe_allow_html=True)
            
            # Display follow-up cases with more details
            for case in mock_data['follow_up_cases']:
                with st.expander(f"{case['case_id']}: {case['subject']} - {case['status']}"):
                    st.markdown(f"""
                    <div style="padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
                        <p><strong>Case ID:</strong> {case['case_id']}</p>
                        <p><strong>Created:</strong> {case['date']}</p>
                        <p><strong>Subject:</strong> {case['subject']}</p>
                        <p><strong>Status:</strong> {case['status']}</p>
                        <p><strong>Priority:</strong> {case['priority']}</p>
                        <p><strong>Description:</strong> Customer reported {case['subject'].lower()} and requested follow-up.</p>
                        <p><strong>Scheduled Follow-up:</strong> {(datetime.now() + timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%d")}</p>
                        <p><strong>Assigned Agent:</strong> {random.choice(['Sarah Thompson', 'Michael Lee', 'Jessica Rodriguez', 'David Kim'])}</p>
                        <p><strong>Notes:</strong> {random.choice([
                            "Customer prefers to be contacted in the afternoon.",
                            "Customer requested email notification prior to call.",
                            "Customer indicated billing questions need clarification.",
                            "Technical issue may require escalation to tier 2 support."
                        ])}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    action_col1, action_col2 = st.columns(2)
                    with action_col1:
                        st.button(f"Mark Resolved - {case['case_id']}", key=f"resolved_{case['case_id']}")
                    with action_col2:
                        st.button(f"Escalate - {case['case_id']}", key=f"escalate_{case['case_id']}")

import streamlit as st
import random
import time
from datetime import datetime, timedelta

def render_customer_tools(mock_data):
    """Enhanced customer tools with interactive elements and realistic tracking."""
    st.header("🛠️ Customer Service Tools")

    # Initialize session states
    if 'diagnostics_run' not in st.session_state:
        st.session_state.diagnostics_run = False
    if 'current_device' not in st.session_state:
        st.session_state.current_device = ""
    if 'available_slots' not in st.session_state:
        st.session_state.available_slots = []
    if 'appointment_confirmed' not in st.session_state:
        st.session_state.appointment_confirmed = False
    if 'selected_appointment' not in st.session_state:
        st.session_state.selected_appointment = None
    if 'show_initial_diag' not in st.session_state:
        st.session_state.show_initial_diag = False
    if 'show_guide' not in st.session_state:
        st.session_state.show_guide = False
    if 'show_slots' not in st.session_state:
        st.session_state.show_slots = False

    # Predefined Input Scenarios
    tool_scenarios = {
        "Order Tracking": {
            "inputs": [
                {"label": "Order Number", "type": "text", "default": f"ORD-{random.randint(10000, 99999)}"},
                {"label": "Customer Phone", "type": "text", "default": mock_data['customer_details']['personal_info']['phone']}
            ],
            "action": "Track Order"
        },
        "Troubleshooting": {
            "inputs": [
                {"label": "Issue Type", "type": "selectbox", "options": ["No Internet", "Slow Connection", "Signal Drop"]},
                {"label": "Device Model", "type": "text", "default": random.choice([eq["model"] for eq in mock_data['customer_details']['service_info']['equipment']])}
            ],
            "action": "Diagnose Issue"
        },
        "Appointments": {
            "inputs": [
                {"label": "Service Type", "type": "selectbox", "options": ["Installation", "Repair", "Consultation"]},
                {"label": "Preferred Date", "type": "date", "default": datetime.now() + timedelta(days=3)}
            ],
            "action": "Schedule Appointment"
        }
    }

    # Tool Selection
    selected_tool = st.radio("Select Service Tool", list(tool_scenarios.keys()))
    st.subheader(f"{selected_tool} Tool")

    # Dynamic Input Generation
    with st.form(key=f'{selected_tool}_form'):
        inputs = {}
        for input_field in tool_scenarios[selected_tool]['inputs']:
            if input_field['type'] == 'text':
                inputs[input_field['label']] = st.text_input(
                    input_field['label'], value=input_field.get('default', '')
                )
            elif input_field['type'] == 'selectbox':
                inputs[input_field['label']] = st.selectbox(
                    input_field['label'], input_field['options']
                )
            elif input_field['type'] == 'date':
                inputs[input_field['label']] = st.date_input(
                    input_field['label'], value=input_field.get('default', datetime.now())
                )
        submit_button = st.form_submit_button(label=tool_scenarios[selected_tool]['action'])

    # Handle form submission per tool
    if submit_button:
        st.success(f"Processing {selected_tool}...")
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)

        if selected_tool == "Order Tracking":
            # Order Tracking Results
            st.markdown("### 📦 Order Tracking Results")
            st.markdown(f"""
            <div class="widget-card">
                <div class="widget-header"><h3>Order Information</h3></div>
                <p><strong>Order Number:</strong> {inputs['Order Number']}</p>
                <p><strong>Customer:</strong> {mock_data['customer_name']}</p>
                <p><strong>Order Date:</strong> {(datetime.now() - timedelta(days=random.randint(3, 10))).strftime("%Y-%m-%d")}</p>
                <p><strong>Current Status:</strong> <span style="color: #e67e22; font-weight: bold;">In Transit</span></p>
            </div>

            <div class="widget-card">
                <div class="widget-header"><h3>Tracking Timeline</h3></div>
                <table class="styled-table" style="width:100%">
                    <thead><tr><th>Date</th><th>Status</th><th>Location</th><th>Details</th></tr></thead>
                    <tbody>
                        <tr><td>{(datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M")}</td><td>Order Placed</td><td>Online</td><td>Order successfully submitted</td></tr>
                        <tr><td>{(datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d %H:%M")}</td><td>Payment Verified</td><td>Billing Department</td><td>Payment processed successfully</td></tr>
                        <tr><td>{(datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M")}</td><td>Processing</td><td>Fulfillment Center</td><td>Items being prepared for shipment</td></tr>
                        <tr><td>{(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")}</td><td>Shipped</td><td>Logistics Partner</td><td>Package handed to delivery partner</td></tr>
                        <tr><td>{datetime.now().strftime("%Y-%m-%d %H:%M")}</td><td>In Transit</td><td>Regional Hub</td><td>Package en route to delivery address</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="widget-card">
                <div class="widget-header"><h3>Delivery Information</h3></div>
                <p><strong>Estimated Delivery:</strong> {(datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")}</p>
                <p><strong>Delivery Address:</strong> {mock_data['customer_details']['personal_info']['address']}</p>
                <p><strong>Delivery Method:</strong> Standard Shipping</p>
                <p><strong>Tracking Number:</strong> {random.choice(["UPS","FedEx","USPS"])}-{random.randint(10000000,99999999)}</p>
            </div>
            """, unsafe_allow_html=True)

        elif selected_tool == "Troubleshooting":
            # Prepare initial diagnostics state
            st.session_state.troubleshooting_device = inputs.get('Device Model', random.choice([eq["model"] for eq in mock_data['customer_details']['service_info']['equipment']]))
            st.session_state.troubleshooting_issue = inputs.get('Issue Type', 'No Internet')
            st.session_state.show_initial_diag = True
            st.session_state.diagnostics_run = False

        elif selected_tool == "Appointments":
            # Generate appointment slots
            st.session_state.appointment_service_type = inputs.get('Service Type', 'Installation')
            st.session_state.appointment_preferred_date = inputs.get('Preferred Date', datetime.now() + timedelta(days=3))
            base_dt = datetime.combine(st.session_state.appointment_preferred_date, datetime.min.time())
            slots = []
            for d in range(3):
                day = base_dt + timedelta(days=d)
                for h in [9, 12, 15]:
                    slots.append({
                        "date": day,
                        "time": f"{h:02d}:00 - {h+3:02d}:00",
                        "technician": f"{random.choice(['John','Sarah','Mike','Lisa'])} {random.choice(['Doe','Smith','Johnson','Garcia'])}",
                        "available": True
                    })
            st.session_state.available_slots = slots
            st.session_state.show_slots = True

    # INITIAL DIAGNOSTICS
    if selected_tool == "Troubleshooting" and st.session_state.show_initial_diag:
        st.markdown("### 🔍 Initial Diagnostics Results")
        st.markdown(f"""
        <div class="widget-card" style="margin-bottom:20px;">
            <div class="widget-header"><h3>Issue Analysis: {st.session_state.troubleshooting_issue}</h3></div>
            <p><strong>Device:</strong> {st.session_state.troubleshooting_device}</p>
            <p><strong>Connection Status:</strong> <span style="color: {'red' if st.session_state.troubleshooting_issue == 'No Internet' else 'orange'};">{'Offline' if st.session_state.troubleshooting_issue == 'No Internet' else 'Unstable'}</span></p>
            <p><strong>Last Connected:</strong> {(datetime.now() - timedelta(hours=random.randint(1,5))).strftime("%Y-%m-%d %H:%M")}</p>
            <p><strong>Signal Quality:</strong> {random.choice(['Poor','Fair','Good'])}</p>
            <p><strong>Recommended Action:</strong> {random.choice(['Restart equipment','Check cable connections','Verify account status'])}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔍 Run Advanced Diagnostics", key="run_advanced_diag"):
            st.session_state.diagnostics_run = True
            st.session_state.diag_results = {
                "signal_strength": random.randint(10,99),
                "packet_loss": f"{random.uniform(0.1,15.0):.1f}%",
                "latency": f"{random.randint(15,450)}ms",
                "dns_status": random.choice(["Operational","Partial Outage","Resolving Issues"]),
                "interference": random.choice(["Low","Medium","High"]),
                "router_status": random.choice(["Online","Connection Issues","Firmware Outdated"])
            }

    # ADVANCED DIAGNOSTICS RESULTS
    if selected_tool == "Troubleshooting" and st.session_state.diagnostics_run:
        st.markdown("### 📊 Advanced Diagnostics Results")
        st.markdown(f"""
        <div class="widget-card">
            <div class="widget-header"><h3>Technical Report</h3></div>
            <div style="padding:15px;">
                <p>📶 <strong>Signal Strength:</strong> <span style="color: {'red' if st.session_state.diag_results['signal_strength'] < 40 else 'orange' if st.session_state.diag_results['signal_strength'] < 60 else 'green'}">{st.session_state.diag_results['signal_strength']}%</span></p>
                <p>📦 <strong>Packet Loss:</strong> <span style="color: {'red' if float(st.session_state.diag_results['packet_loss'].strip('%'))>8 else 'orange' if float(st.session_state.diag_results['packet_loss'].strip('%'))>3 else 'green'}">{st.session_state.diag_results['packet_loss']}</span></p>
                <p>⏱️ <strong>Latency:</strong> <span style="color: {'red' if int(st.session_state.diag_results['latency'][:-2])>200 else 'orange' if int(st.session_state.diag_results['latency'][:-2])>80 else 'green'}">{st.session_state.diag_results['latency']}</span></p>
                <p>🔗 <strong>DNS Status:</strong> {st.session_state.diag_results['dns_status']}</p>
                <p>📡 <strong>Interference Level:</strong> {st.session_state.diag_results['interference']}</p>
                <p>🖥️ <strong>Router Status:</strong> {st.session_state.diag_results['router_status']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("### 🔧 Recommended Actions")
        if st.session_state.diag_results['router_status'] == "Firmware Outdated":
            rec = "Update router firmware to latest version"
        elif float(st.session_state.diag_results['packet_loss'].strip('%'))>5:
            rec = "Schedule line quality inspection"
        else:
            rec = "Perform equipment reset and monitor connection"
        st.markdown(f"""
        <div class="widget-card" style="background-color:#e3f2fd;">
            <p>🚨 <strong>Priority:</strong> {random.choice(['High','Medium'])}</p>
            <p>📝 <strong>Action Required:</strong> {rec}</p>
            <p>⏳ <strong>Estimated Resolution Time:</strong> {random.randint(1,24)} hours</p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Generate Trouble Ticket", key="gen_ticket"):
                t_id = f"TT-{random.randint(1000,9999)}"
                st.success(f"Ticket {t_id} created! Assigned to technical team.")
        with col2:
            if st.button("📞 Schedule Callback", key="schedule_callback"):
                st.info("Callback scheduled for next available agent")

    # TROUBLESHOOTING GUIDE
    if selected_tool == "Troubleshooting" and st.session_state.show_guide:
        st.markdown("""
        <div class="widget-card" style="margin-top:20px;">
            <div class="widget-header"><h3>📑 Troubleshooting Steps</h3></div>
            <ol>
                <li><strong>Power cycle your equipment:</strong><ul><li>Turn off your router and modem</li><li>Wait 30 seconds</li><li>Turn on your modem and wait for it to connect</li><li>Turn on your router and wait 2 minutes</li></ul></li>
                <li><strong>Check all physical connections:</strong><ul><li>Ensure all cables are securely connected</li><li>Check for damaged cables and replace if necessary</li></ul></li>
                <li><strong>Check for service outages:</strong><ul><li>Visit our service status page</li><li>Check for announced maintenance in your area</li></ul></li>
                <li><strong>Try connecting with a different device</strong> to determine if the issue is device-specific</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        if st.button("← Back to Diagnostics", key="back_to_diag"):
            st.session_state.show_guide = False

    # APPOINTMENT SLOTS DISPLAY
    if selected_tool == "Appointments" and st.session_state.show_slots and st.session_state.available_slots:
        st.markdown("### 📅 Available Appointment Slots")
        st.markdown(f"Service type: **{st.session_state.appointment_service_type}**")
        slot_opts = [f"{slot['date'].strftime('%a, %b %d')} | {slot['time']} | {slot['technician']}" for slot in st.session_state.available_slots]
        idx = st.radio("Choose a time slot:", options=range(len(slot_opts)), format_func=lambda i: slot_opts[i], key="slot_radio")
        st.session_state.selected_slot_index = idx
        if st.button("✅ Confirm This Appointment", key="confirm_button"):
            st.session_state.selected_appointment = st.session_state.available_slots[idx]
            st.session_state.appointment_confirmed = True

    # APPOINTMENT CONFIRMATION
    if selected_tool == "Appointments" and st.session_state.appointment_confirmed and st.session_state.selected_appointment:
        details = st.session_state.selected_appointment
        confirmation_code = f"VZ-{random.randint(100000,999999)}"
        st.success("Appointment confirmed successfully!")
        st.markdown("### 🎉 Appointment Confirmation")
        st.markdown(f"**Service Type:** {st.session_state.appointment_service_type}")
        st.markdown(f"**Date:** {details['date'].strftime('%B %d, %Y')}")
        st.markdown(f"**Time:** {details['time']}")
        st.markdown(f"**Technician:** {details['technician']}")
        st.markdown("#### 📨 Notifications Sent")
        st.markdown(f"✓ SMS confirmation sent to: {mock_data['customer_details']['personal_info']['phone']}")
        st.markdown(f"✓ Email confirmation sent to: {mock_data['customer_details']['personal_info']['email']}")
        st.markdown("✓ Calendar invite created")
        st.markdown(f"**Confirmation Code:** {confirmation_code}")
        if st.button("Schedule Another Appointment", key="schedule_another"):
            st.session_state.appointment_confirmed = False
            st.session_state.selected_appointment = None
            
def render_ai_assistance(mock_data):
    """Enhanced AI assistance with realistic knowledge retrieval and case references."""
    st.header("🤖 AI-Powered Assistance")
    
    # Predefined Query Categories
    query_categories = [
        "Activation Issue",
        "Billing Inquiry",
        "Technical Support",
        "Service Upgrade",
        "Contract Details"
    ]
    
    # Query Selection
    selected_category = st.selectbox("Select Query Category", query_categories)
    
    # Custom Query Input
    query = st.text_area("Refine Your Query", 
        value=f"I'm experiencing an {selected_category.lower()}..."
    )
    
    if st.button("Process AI Query"):
        with st.spinner("AI analyzing query..."):
            # Simulate processing steps with visual feedback
            progress_steps = ["Analyzing query intent...", "Searching knowledge base...", "Retrieving past cases...", "Generating response..."]
            progress_bar = st.progress(0)
            progress_text = st.empty()
            
            for i, step in enumerate(progress_steps):
                progress_text.text(step)
                progress_bar.progress((i + 1) * 25)
                time.sleep(0.5)
            
            response = process_ai_query(query, mock_data)
            st.success("AI Response Generated")
            
            # Display processing steps
            st.markdown("<div class='ai-assistant-panel'>", unsafe_allow_html=True)
            st.markdown("<h4>🔍 Processing</h4>", unsafe_allow_html=True)
            for step in response['processing_steps']:
                st.markdown(f"<div class='ai-step'>{step}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Display relevant KB articles
            if response['kb_articles']:
                st.markdown("<div class='ai-assistant-panel'>", unsafe_allow_html=True)
                st.markdown("<h4>📚 Knowledge Base Articles</h4>", unsafe_allow_html=True)
                for article in response['kb_articles']:
                    st.markdown(f"<a href='#' class='kb-link'>{article['id']}: {article['title']}</a>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Display similar cases
            if response['similar_cases']:
                st.markdown("<div class='ai-assistant-panel'>", unsafe_allow_html=True)
                st.markdown("<h4>📎 Similar Cases</h4>", unsafe_allow_html=True)
                for case in response['similar_cases']:
                    st.markdown(f"<span class='case-link'>{case['id']}: {case['title']}</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Display AI response summary
            st.markdown("<div class='ai-assistant-panel'>", unsafe_allow_html=True)
            st.markdown("<h4>💡 Agent Guidance</h4>", unsafe_allow_html=True)
            st.markdown(response['response_summary'], unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Followup question
            st.markdown("<div class='ai-assistant-panel'>", unsafe_allow_html=True)
            st.markdown(f"<h4>❓ Next Steps</h4><p>{response['followup_question']}</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Optional: Confidence Score
            confidence = random.uniform(0.8, 0.98)
            st.metric("AI Confidence", f"{confidence:.2%}")

def render_automated_actions(mock_data):
    """Render enhanced automated service actions with uniform layout."""
    st.header("⚙️ Automated Service Actions")

    # Custom styling for cards
    st.markdown("""
    <style>
        .action-card {
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
            background: white;
            transition: all 0.3s ease;
        }
        .action-card:hover {
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .action-header {
            font-size: 1.2em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }
        .action-header span {
            margin-right: 8px;
        }
        .form-row {
            display: flex;
            flex-direction: column;
            margin-bottom: 15px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    actions = [
        {
            "name": "Activate Service",
            "icon": "🔥",
            "description": "Initiate new service activation",
            "fields": [
                {"name": "service_plan", "label": "Service Plan", "type": "selectbox",
                 "options": ["Fiber Home Basic", "High-Speed Internet & TV Bundle", "Premium Mobile & Broadband"]},
                {"name": "activation_date", "label": "Activation Date", "type": "date"},
                {"name": "special_instructions", "label": "Special Instructions", "type": "text_area"}
            ],
            "mock_response": lambda inputs: f"""
            <div style="padding:15px; background-color:#f8f9fa; border-radius:8px;">
                <h4>📡 Service Activation Summary</h4>
                <table style="width:100%">
                    <tr><td><strong>Customer:</strong></td><td>{mock_data['customer_name']}</td></tr>
                    <tr><td><strong>Plan:</strong></td><td>{inputs['service_plan']}</td></tr>
                    <tr><td><strong>Activation Date:</strong></td><td>{inputs['activation_date']}</td></tr>
                    <tr><td><strong>Monthly Fee:</strong></td><td>${random.randint(50,200)}.00</td></tr>
                </table>
                <div style="margin-top:15px; padding:10px; background-color:#e3f2fd; border-radius:6px;">
                    <p>📨 Notifications Sent:</p>
                    <ul>
                        <li>Email to {mock_data['customer_details']['personal_info']['email']}</li>
                        <li>SMS to {mock_data['customer_details']['personal_info']['phone']}</li>
                    </ul>
                </div>
            </div>
            """
        },
        {
            "name": "Cancel Service",
            "icon": "🚫",
            "description": "Process service termination",
            "fields": [
                {"name": "cancellation_reason", "label": "Reason", "type": "selectbox",
                 "options": ["Moving", "Switching Provider", "Financial", "Service Issues"]},
                {"name": "end_date", "label": "End Date", "type": "date"},
                {"name": "return_equipment", "label": "Equipment Return", "type": "checkbox"}
            ],
            "mock_response": lambda inputs: f"""
            <div style="padding:15px; background-color:#f8f9fa; border-radius:8px;">
                <h4>⛔ Service Cancellation</h4>
                <table style="width:100%">
                    <tr><td><strong>Effective Date:</strong></td><td>{inputs['end_date']}</td></tr>
                    <tr><td><strong>Reason:</strong></td><td>{inputs['cancellation_reason']}</td></tr>
                    <tr><td><strong>Final Credit:</strong></td><td>${random.randint(0,150)}.00</td></tr>
                </table>
                <div style="margin-top:15px; padding:10px; background-color:#ffebee; border-radius:6px;">
                    <p>📦 Return Kit: {'Shipped' if inputs['return_equipment'] else 'Not Required'}</p>
                </div>
            </div>
            """
        },
        {
            "name": "Send Reminder",
            "icon": "📧",
            "description": "Dispatch customer reminder",
            "fields": [
                {"name": "reminder_type", "label": "Type", "type": "selectbox",
                 "options": ["Payment", "Appointment", "Renewal"]},
                {"name": "channels", "label": "Channels", "type": "multiselect",
                 "options": ["Email", "SMS", "Push"]},
                {"name": "priority", "label": "Priority", "type": "radio",
                 "options": ["High", "Medium", "Low"]}
            ],
            "mock_response": lambda inputs: f"""
            <div style="padding:15px; background-color:#f8f9fa; border-radius:8px;">
                <h4>✉️ Reminder Dispatched</h4>
                <table style="width:100%">
                    <tr><td><strong>Type:</strong></td><td>{inputs['reminder_type']}</td></tr>
                    <tr><td><strong>Channels:</strong></td><td>{', '.join(inputs['channels'])}</td></tr>
                    <tr><td><strong>Tracking ID:</strong></td><td>MSG-{random.randint(100000,999999)}</td></tr>
                </table>
                <div style="margin-top:15px; padding:10px; background-color:#e8f5e9; border-radius:6px;">
                    <p>✅ Confirmation Received:</p>
                    <ul>
                        <li>{datetime.now().strftime('%Y-%m-%d %H:%M')}</li>
                        <li>Status: Queued for delivery</li>
                    </ul>
                </div>
            </div>
            """
        },
        {
            "name": "Bill Copy",
            "icon": "📄",
            "description": "Send duplicate bill",
            "fields": [
                {"name": "bill_month", "label": "Month", "type": "selectbox",
                 "options": [(datetime.now() - timedelta(days=30*i)).strftime("%B %Y") for i in range(6)]},
                {"name": "method", "label": "Method", "type": "selectbox",
                 "options": ["Email", "Mail", "Both"]},
                {"name": "consent", "label": "Consent", "type": "checkbox"}
            ],
            "mock_response": lambda inputs: f"""
            <div style="padding:15px; background-color:#f8f9fa; border-radius:8px;">
                <h4>🧾 Duplicate Bill Generated</h4>
                <table style="width:100%">
                    <tr><td><strong>Period:</strong></td><td>{inputs['bill_month']}</td></tr>
                    <tr><td><strong>Amount:</strong></td><td>${random.randint(50,500)}.00</td></tr>
                    <tr><td><strong>Delivery:</strong></td><td>{inputs['method']}</td></tr>
                </table>
            </div>
            """
        },
        {
            "name": "Store Appointment",
            "icon": "🏬",
            "description": "Book store visit",
            "fields": [
                {"name": "service_type", "label": "Service", "type": "selectbox",
                 "options": ["Installation","Repair","Consultation"]},
                {"name": "store", "label": "Store", "type": "selectbox",
                 "options": [loc["name"] for loc in mock_data["store_locations"]]},
                {"name": "appt_date", "label": "Date", "type": "date"}
            ],
            "mock_response": lambda inputs: f"""
            <div style="padding:15px; background-color:#f8f9fa; border-radius:8px;">
                <h4>📆 Store Appointment</h4>
                <table style="width:100%">
                    <tr><td><strong>Location:</strong></td><td>{inputs['store']}</td></tr>
                    <tr><td><strong>Service:</strong></td><td>{inputs['service_type']}</td></tr>
                    <tr><td><strong>Confirmation:</strong></td><td>ST-{random.randint(10000,99999)}</td></tr>
                </table>
            </div>
            """
        },
        {
            "name": "Update Contact",
            "icon": "✏️",
            "description": "Change customer info",
            "fields": [
                {"name": "new_email", "label": "Email", "type": "text",
                 "default": mock_data["customer_details"]["personal_info"]["email"]},
                {"name": "new_phone", "label": "Phone", "type": "text",
                 "default": mock_data["customer_details"]["personal_info"]["phone"]},
                {"name": "verify", "label": "Verification", "type": "checkbox"}
            ],
            "mock_response": lambda inputs: f"""
            <div style="padding:15px; background-color:#f8f9fa; border-radius:8px;">
                <h4>📇 Contact Updated</h4>
                <table style="width:100%">
                    <tr><td><strong>New Email:</strong></td><td>{inputs['new_email']}</td></tr>
                    <tr><td><strong>New Phone:</strong></td><td>{inputs['new_phone']}</td></tr>
                    <tr><td><strong>Verified:</strong></td><td>{'✅' if inputs['verify'] else '❌'}</td></tr>
                </table>
            </div>
            """
        }
    ]

    # Create 3 columns for uniform layout
    cols = st.columns(3)

    for idx, action in enumerate(actions):
        with cols[idx % 3]:
            with st.expander(f"{action['icon']}  {action['name']}", expanded=True):
                st.markdown('<div class="action-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="action-header"><span>{action["icon"]}</span>{action["name"]}</div>', unsafe_allow_html=True)

                with st.form(key=f"form_{action['name']}"):
                    inputs = {}
                    for field in action["fields"]:
                        st.markdown('<div class="form-row">', unsafe_allow_html=True)

                        if field["type"] == "selectbox":
                            inputs[field["name"]] = st.selectbox(
                                field["label"], field["options"],
                                key=f"{action['name']}_{field['name']}"
                            )
                        elif field["type"] == "date":
                            inputs[field["name"]] = st.date_input(
                                field["label"], value=field.get("default", datetime.now()),
                                key=f"{action['name']}_{field['name']}"
                            )
                        elif field["type"] == "checkbox":
                            inputs[field["name"]] = st.checkbox(
                                field["label"],
                                key=f"{action['name']}_{field['name']}"
                            )
                        elif field["type"] == "text":
                            inputs[field["name"]] = st.text_input(
                                field["label"], value=field.get("default", ""),
                                key=f"{action['name']}_{field['name']}"
                            )
                        elif field["type"] == "multiselect":
                            inputs[field["name"]] = st.multiselect(
                                field["label"], field["options"],
                                key=f"{action['name']}_{field['name']}"
                            )
                        elif field["type"] == "radio":
                            inputs[field["name"]] = st.radio(
                                field["label"], field["options"],
                                key=f"{action['name']}_{field['name']}"
                            )
                        elif field["type"] == "text_area":
                            inputs[field["name"]] = st.text_area(
                                field["label"], value=field.get("default", ""),
                                key=f"{action['name']}_{field['name']}"
                            )

                        st.markdown('</div>', unsafe_allow_html=True)

                    if st.form_submit_button("🚀 Execute"):
                        st.markdown(action["mock_response"](inputs), unsafe_allow_html=True)
                        st.success("Action completed successfully!")
                        st.toast("Transaction logged in system", icon="📝")

                st.markdown('</div>', unsafe_allow_html=True)

# --- Main Application Launcher ---
def main():
    st.set_page_config(
        page_title="VZ Project Nebula",
        page_icon="🌐",
        layout="wide"
    )
    apply_custom_styling()
    mock_data = generate_mock_data()
    st.title("🌐 VZ Project Nebula")

    with st.sidebar:
        render_agent_dashboard(mock_data)
        nav = st.radio("Navigate", ["Dashboard", "Customer Tools", "AI Assistance", "Automated Actions"])

    if nav == "Dashboard":
        render_dashboard(mock_data)
    elif nav == "Customer Tools":
        render_customer_tools(mock_data)
    elif nav == "AI Assistance":
        render_ai_assistance(mock_data)
    elif nav == "Automated Actions":
        render_automated_actions(mock_data)

if __name__ == "__main__":
    main()
