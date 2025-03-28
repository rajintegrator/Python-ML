import streamlit as st
import random
import time
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
    customer_id = f"TEL{random.randint(100000, 999999)}"
    customer_name = f"{random.choice(['Alice', 'Bob', 'Charlie', 'David', 'Emma'])} {random.choice(['J.', 'M.', 'S.'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'])}"
    
    # Order Statuses
    order_statuses = [
        "Pending Verification", "Processing", "Shipped", 
        "Out for Delivery", "Delivered", "Installation Scheduled", 
        "Completed", "Cancelled"
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
        "Current Balance": f"₹{random.randint(500, 2000)}.00",
        "Due Date": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
        "Last Payment": f"₹{random.randint(1000, 5000)}.00 on {(datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')}",
        "Service Charges": {
            "Internet (50 Mbps)": f"₹{random.randint(300, 600)}.00",
            "Voice (Unlimited Local)": f"₹{random.randint(100, 300)}.00"
        },
        "Usage This Month": {
            "Internet": f"{random.randint(10, 50)} GB / 100 GB",
            "Calls": f"{random.randint(100, 500)} minutes"
        },
        "Pending Charges": "₹0.00"
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
    
    return {
        "customer_id": customer_id,
        "customer_name": customer_name,
        "order_statuses": order_statuses,
        "tracking_details": mock_tracking_details,
        "troubleshooting_steps": mock_troubleshooting_steps,
        "appointments": mock_appointments,
        "equipment_compatibility": mock_equipment_compatibility,
        "recent_activity": mock_recent_activity,
        "bill_overview": mock_bill_overview,
        "promotions": mock_promotions
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
    </style>
    """, unsafe_allow_html=True)

# --- AI Query Processing ---
def process_ai_query(query, mock_data):
    """
    Process customer service queries using mock AI logic
    
    Args:
        query (str): User's query
        mock_data (dict): Mock customer data
    
    Returns:
        str: AI generated response
    """
    # Normalize query
    query = query.lower()
    
    # Query type detection and response generation
    if "upgrade" in query:
        return f"""
        AI Analysis:
        - Device Upgrade Request Detected
        - Customer: {mock_data['customer_name']} (ID: {mock_data['customer_id']})
        - Current Status: Pending Order Review
        - Recommendation: Verify existing service plans and device compatibility
        """
    
    elif "bill" in query:
        return f"""
        Bill Inquiry Response:
        - Current Balance: {mock_data['bill_overview']['Current Balance']}
        - Billing Period: {mock_data['bill_overview']['Billing Period']}
        - Usage: {mock_data['bill_overview']['Usage This Month']['Internet']}
        """
    
    elif "troubleshoot" in query:
        issue_type = random.choice(list(mock_data['troubleshooting_steps'].keys()))
        return f"""
        Troubleshooting Guidance for {issue_type}:
        {chr(10).join(mock_data['troubleshooting_steps'][issue_type])}
        """
    
    else:
        return "I'm an AI assistant. Could you please rephrase or be more specific about your query?"

# --- Enhanced Functions ---
def render_agent_dashboard(mock_data):
    """Enhanced agent dashboard with more details."""
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

    # Customer Details Section
    st.markdown(f"""
    <div class="widget-card">
        <div class="widget-header">
            <h3>👤 Customer Details</h3>
        </div>
        <p><strong>Name:</strong> {mock_data['customer_name']}</p>
        <p><strong>Customer ID:</strong> {mock_data['customer_id']}</p>
        <p><strong>Membership:</strong> Premium Tier</p>
        <p><strong>Customer Since:</strong> {(datetime.now() - timedelta(days=random.randint(100, 1000))).strftime('%B %Y')}</p>
    </div>
    """, unsafe_allow_html=True)

def render_dashboard(mock_data):
    """Render the dashboard with key metrics."""
    st.header("🏠 Customer Service Dashboard")
    
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
                <h3>💰 Billing Overview</h3>
            </div>
            <p>Current Balance: <strong>{mock_data['bill_overview']['Current Balance']}</strong></p>
            <p>Due Date: <strong>{mock_data['bill_overview']['Due Date']}</strong></p>
            <p>Last Payment: <strong>{mock_data['bill_overview']['Last Payment'].split(' on ')[0]}</strong></p>
        </div>
        """, unsafe_allow_html=True)

def render_customer_tools(mock_data):
    """Enhanced customer tools with interactive elements."""
    st.header("🛠️ Customer Service Tools")
    
    # Predefined Input Scenarios
    tool_scenarios = {
        "Order Tracking": {
            "inputs": [
                {"label": "Order Number", "type": "text"},
                {"label": "Customer Phone", "type": "text"}
            ],
            "action": "Track Order"
        },
        "Troubleshooting": {
            "inputs": [
                {"label": "Issue Type", "type": "selectbox", "options": ["No Internet", "Slow Connection", "Signal Drop"]},
                {"label": "Device Model", "type": "text"}
            ],
            "action": "Diagnose Issue"
        },
        "Appointments": {
            "inputs": [
                {"label": "Service Type", "type": "selectbox", "options": ["Installation", "Repair", "Consultation"]},
                {"label": "Preferred Date", "type": "date"}
            ],
            "action": "Schedule Appointment"
        }
    }
    
    # Tool Selection
    selected_tool = st.radio("Select Service Tool", list(tool_scenarios.keys()))
    
    # Dynamic Input Generation
    st.subheader(f"{selected_tool} Tool")
    
    # Create input fields based on selected tool
    with st.form(key=f'{selected_tool}_form'):
        for input_field in tool_scenarios[selected_tool]['inputs']:
            if input_field['type'] == 'text':
                st.text_input(input_field['label'])
            elif input_field['type'] == 'selectbox':
                st.selectbox(input_field['label'], input_field['options'])
            elif input_field['type'] == 'date':
                st.date_input(input_field['label'])
        
        submit_button = st.form_submit_button(label=tool_scenarios[selected_tool]['action'])
        
        if submit_button:
            # Mocked Result Display
            st.success(f"Processing {selected_tool}...")
            time.sleep(1)
            
            if selected_tool == "Order Tracking":
                st.dataframe(mock_data['tracking_details'])
            elif selected_tool == "Troubleshooting":
                st.json(mock_data['troubleshooting_steps'])
            elif selected_tool == "Appointments":
                st.table(mock_data['appointments'])

def render_ai_assistance(mock_data):
    """Enhanced AI assistance with predefined queries."""
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
            time.sleep(1)
            response = process_ai_query(query, mock_data)
            st.success("AI Response Generated")
            st.info(response)
            
            # Optional: Confidence Score
            confidence = random.uniform(0.7, 1.0)
            st.metric("AI Confidence", f"{confidence:.2%}")

def render_automated_actions(mock_data):
    """Render automated service action triggers with interactive mock responses."""
    st.header("⚙️ Automated Service Actions")
    
    actions = [
        {
            "name": "Activate Service", 
            "icon": "🔥", 
            "description": "Initiate new service activation",
            "mock_response": f"""
            ✅ Service Activation Successful
            - Customer: {mock_data['customer_name']}
            - Service Plan: High-Speed Internet & TV Bundle
            - Activation Date: {datetime.now().strftime('%Y-%m-%d')}
            - Estimated Setup Time: 24-48 hours
            """
        },
        {
            "name": "Cancel Service", 
            "icon": "🚫", 
            "description": "Process service termination",
            "mock_response": f"""
            🔴 Service Cancellation Processed
            - Customer ID: {mock_data['customer_id']}
            - Cancellation Reason: Customer Request
            - Final Bill Calculation: Pending
            - Service End Date: {(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')}
            """
        },
        {
            "name": "Send Reminder", 
            "icon": "📧", 
            "description": "Dispatch automated customer reminder",
            "mock_response": f"""
            📨 Reminder Dispatched
            - Recipient: {mock_data['customer_name']}
            - Message Type: Bill Payment Reminder
            - Due Date: {mock_data['bill_overview']['Due Date']}
            - Amount Due: {mock_data['bill_overview']['Current Balance']}
            - Channels: SMS, Email
            """
        },
        {
            "name": "Update Details", 
            "icon": "🔄", 
            "description": "Sync customer information",
            "mock_response": f"""
            🔍 Customer Details Updated
            - Name: {mock_data['customer_name']}
            - Contact Method: Verified
            - Address: Sync Completed
            - Preferred Communication: Updated
            """
        },
        {
            "name": "Run Diagnostics", 
            "icon": "🔍", 
            "description": "Perform network health check",
            "mock_response": f"""
            🖥️ Network Diagnostics Report
            - Connection Type: Fiber
            - Current Speed: {random.randint(50, 100)} Mbps
            - Packet Loss: {random.uniform(0.1, 1.5):.2f}%
            - Latency: {random.randint(10, 50)} ms
            - Status: {random.choice(['Optimal', 'Good', 'Needs Attention'])}
            """
        },
        {
            "name": "Billing Adjustment", 
            "icon": "💸", 
            "description": "Process billing modifications",
            "mock_response": f"""
            💰 Billing Adjustment Processed
            - Current Balance: {mock_data['bill_overview']['Current Balance']}
            - Adjustment: {random.choice(['-₹500', '+₹250', 'Credit Applied'])}
            - New Balance: ₹{int(mock_data['bill_overview']['Current Balance'].replace('₹', '').replace('.00', '')) + random.randint(-500, 250)}.00
            - Reason: {random.choice(['Service Credit', 'Billing Error Correction', 'Loyalty Discount'])}
            """
        }
    ]
    
    # Create a container to hold action results
    result_container = st.container()
    
    for i in range(0, len(actions), 3):
        cols = st.columns(3)
        for j, action in enumerate(actions[i:i+3]):
            with cols[j]:
                st.markdown(f"""
                <div class="widget-card" style="text-align: center; height: 300px;">
                    <div style="font-size: 3em; margin-bottom: 10px;">{action['icon']}</div>
                    <h3>{action['name']}</h3>
                    <p>{action['description']}</p>
                """, unsafe_allow_html=True)
                
                # Use Streamlit button with unique key
                if st.button(f"Execute {action['name']}", key=f"action_{action['name']}"):
                    with result_container:
                        st.markdown(f"### 🔧 {action['name']} Action Result")
                        st.code(action['mock_response'], language='text')
                        # Add a visual indicator
                        st.success("Action completed successfully!")

# --- Main Application ---
def main():
    # Page Configuration
    st.set_page_config(
        page_title="Telecom CS Agent Desktop", 
        page_icon="📞", 
        layout="wide"
    )
    
    # Apply Custom Styling
    apply_custom_styling()
    
    # Generate Mock Data
    mock_data = generate_mock_data()
    
    # Title
    st.title("🌐 Telecom Customer Service Agent Desktop")
    
    # Sidebar with Enhanced Design
    with st.sidebar:
        # Render Agent Dashboard in Sidebar
        render_agent_dashboard(mock_data)
        
        # Navigation
        nav_selection = st.radio(
            "Navigate", 
            ["Dashboard", "Customer Tools", "AI Assistance", "Automated Actions"]
        )
    
    # Render Selected View
    if nav_selection == "Dashboard":
        render_dashboard(mock_data)
    elif nav_selection == "Customer Tools":
        render_customer_tools(mock_data)
    elif nav_selection == "AI Assistance":
        render_ai_assistance(mock_data)
    elif nav_selection == "Automated Actions":
        render_automated_actions(mock_data)

if __name__ == "__main__":
    main()