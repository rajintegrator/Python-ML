import streamlit as st
import random
import time
from datetime import datetime, timedelta

# --- Session State Initialization ---
if 'active_tool' not in st.session_state:
    st.session_state.active_tool = None

# --- Helper Functions ---
def generate_random_datetime(start_date, end_date):
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
    customer_id = f"TEL{random.randint(100000, 999999)}"
    customer_name = f"{random.choice(['Alice', 'Bob', 'Charlie', 'David', 'Emma'])} {random.choice(['J.', 'M.', 'S.'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'])}"
    
    return {
        "customer_id": customer_id,
        "customer_name": customer_name,
        "agent_name": random.choice(["Sarah", "Michael", "Emily", "James"]),
        "account_status": random.choice(["Active", "Suspended", "Pending Verification"]),
        "contact_info": {
            "phone": f"+91-{random.randint(7000000000, 9999999999)}",
            "email": f"{customer_name.split()[0].lower()}@example.com"
        },
        "order_statuses": [
            "Pending Verification", "Processing", "Shipped", 
            "Out for Delivery", "Delivered", "Installation Scheduled", 
            "Completed", "Cancelled"
        ],
        "tracking_details": {
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
        },
        "troubleshooting_steps": {
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
        },
        "appointments": [
            {
                "appt_id": f"APT{random.randint(1000, 9999)}",
                "date": (datetime.now() + timedelta(days=random.randint(1, 10))).strftime("%Y-%m-%d"),
                "time": f"{random.randint(9, 17):02d}:00 - {random.randint(9, 17)+2:02d}:00",
                "type": random.choice(["Installation", "Repair", "Consultation"]),
                "status": random.choice(["Scheduled", "Pending Confirmation"]),
                "technician": f"{random.choice(['John', 'Jane', 'Mike', 'Sarah'])} {random.choice(['Doe', 'Smith', 'Johnson'])}"
            } for _ in range(3)
        ],
        "equipment_compatibility": {
            "Fiber Home Basic": ["FH-M2000 (Modem)", "WRT-300 (Router)"],
            "High-Speed Internet & TV Bundle": ["GH-X5000 (Modem/Router Combo)", "STB-HD-01 (HD Set-Top Box)"],
            "Premium Mobile & Broadband": [
                "Nokia G400 5G (Device)", 
                "FH-M2500 (Modem)", 
                "Linksys AX1800 (Router)"
            ]
        },
        "recent_activity": [
            {
                "timestamp": generate_random_datetime(
                    datetime.now() - timedelta(days=30),
                    datetime.now()
                ),
                "type": random.choice(["Call", "SMS", "Data Usage", "Payment", "Website Visit"]),
                "details": random.choice([
                    "Customer inquired about data usage",
                    "Reminder for upcoming bill payment",
                    "Used 15 GB of 50 GB data allowance",
                    "Payment received",
                    "Viewed upgrade options"
                ])
            } for _ in range(5)
        ],
        "bill_overview": {
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
        },
        "promotions": [
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
    }

# --- UI Styling Function ---
def apply_custom_styling():
    st.markdown("""
    <style>
    .stApp {
        background-color: #f4f6f9;
        font-family: 'Inter', sans-serif;
    }
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
    .stExpander {
        border-radius: 12px;
        overflow: hidden;
    }
    .sidebar-profile {
        background: linear-gradient(135deg, #3498db, #2980b9);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .sidebar-profile h3 {
        margin: 0 0 10px 0;
    }
    .sidebar-profile p {
        margin: 5px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- AI Query Processing ---
def process_ai_query(query, mock_data):
    query = query.lower()
    if "activation" in query:
        return f"""
        🚨 Activation Issue Detected
        Customer: {mock_data['customer_name']}
        Account Status: {mock_data['account_status']}
        Recommendation: 
        1. Verify device compatibility
        2. Check for pending orders
        3. Confirm service address
        """
    elif "billing" in query:
        return f"""
        💰 Billing Inquiry
        Current Balance: {mock_data['bill_overview']['Current Balance']}
        Due Date: {mock_data['bill_overview']['Due Date']}
        Last Payment: {mock_data['bill_overview']['Last Payment']}
        """
    elif "troubleshoot" in query:
        issue_type = random.choice(list(mock_data['troubleshooting_steps'].keys()))
        return f"""
        🔧 Troubleshooting Guidance for {issue_type}:
        {chr(10).join(mock_data['troubleshooting_steps'][issue_type])}
        """
    else:
        return "Please select a predefined query or describe the issue in more detail"

# --- Main Application ---
def main():
    st.set_page_config(
        page_title="Telecom CS Agent Desktop", 
        page_icon="📞", 
        layout="wide"
    )
    apply_custom_styling()
    mock_data = generate_mock_data()
    
    # Enhanced Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-profile">
            <h3>👤 Agent Dashboard</h3>
            <p>Agent: {mock_data['agent_name']}</p>
            <p>Shift: 09:00 - 18:00 IST</p>
            <hr style="border:1px solid white; margin: 15px 0;">
            <h3>Customer Profile</h3>
            <p>Name: {mock_data['customer_name']}</p>
            <p>ID: {mock_data['customer_id']}</p>
            <p>Status: {mock_data['account_status']}</p>
            <p>Phone: {mock_data['contact_info']['phone']}</p>
            <p>Email: {mock_data['contact_info']['email']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        nav_selection = st.radio(
            "Navigate", 
            ["Dashboard", "Customer Tools", "AI Assistance", "Automated Actions"],
            index=0
        )

    if nav_selection == "Dashboard":
        render_dashboard(mock_data)
    elif nav_selection == "Customer Tools":
        render_customer_tools(mock_data)
    elif nav_selection == "AI Assistance":
        render_ai_assistance(mock_data)
    elif nav_selection == "Automated Actions":
        render_automated_actions(mock_data)

def render_dashboard(mock_data):
    st.header("🏠 Customer Service Dashboard")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container():
            st.markdown("""
            <div class="widget-card">
                <div class="widget-header">
                    <h3>📦 Active Orders</h3>
                </div>
                <p>Total Active: <strong>3</strong></p>
                <p>Processing: <strong>2</strong></p>
                <p>Scheduled: <strong>1</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
    with col2:
        with st.container():
            st.markdown("""
            <div class="widget-card">
                <div class="widget-header">
                    <h3>🛠️ Support Tickets</h3>
                </div>
                <p>Open Tickets: <strong>15</strong></p>
                <p>Resolved Today: <strong>8</strong></p>
                <p>Average Resolution Time: <strong>2.5 hrs</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
    with col3:
        with st.container():
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
    st.header("🛠️ Customer Service Tools")
    
    tools = [
        {
            "name": "Order Tracking", 
            "icon": "📦", 
            "description": "Track customer orders",
            "content": f"""
                <div class="widget-card">
                    <input type="text" placeholder="Enter Order ID" style="padding: 8px; width: 100%; margin: 10px 0;">
                    <button onclick="alert('Tracking order...')">Track Order</button>
                    <div style="margin-top: 15px;">
                        <p>Latest Order Status:</p>
                        <p>ORD{random.randint(100000,999999)} - {random.choice(mock_data['order_statuses'])}</p>
                    </div>
                </div>
            """
        },
        {
            "name": "Troubleshooting", 
            "icon": "⚙️", 
            "description": "Resolve technical issues",
            "content": f"""
                <div class="widget-card">
                    <select style="padding: 8px; width: 100%; margin: 10px 0;">
                        <option>Select Issue Type</option>
                        <option>No Internet</option>
                        <option>Slow Connection</option>
                    </select>
                    <button onclick="alert('Running diagnostics...')">Run Diagnostics</button>
                    <div style="margin-top: 15px;">
                        <p>Recommended Steps:</p>
                        <p>1. {mock_data['troubleshooting_steps']['No Internet'][0]}</p>
                    </div>
                </div>
            """
        },
        {
            "name": "Appointments", 
            "icon": "📅", 
            "description": "Manage service appointments",
            "content": f"""
                <div class="widget-card">
                    <input type="date" style="padding: 8px; width: 100%; margin: 10px 0;">
                    <select style="padding: 8px; width: 100%; margin: 10px 0;">
                        <option>Select Time Slot</option>
                        <option>09:00-11:00</option>
                        <option>13:00-15:00</option>
                    </select>
                    <button onclick="alert('Appointment booked!')">Schedule</button>
                    <div style="margin-top: 15px;">
                        <p>Upcoming Appointment:</p>
                        <p>{mock_data['appointments'][0]['date']} - {mock_data['appointments'][0]['time']}</p>
                    </div>
                </div>
            """
        },
        {
            "name": "Equipment Check", 
            "icon": "🔌", 
            "description": "Verify device compatibility",
            "content": f"""
                <div class="widget-card">
                    <input type="text" placeholder="Enter Device Model" style="padding: 8px; width: 100%; margin: 10px 0;">
                    <button onclick="alert('Checking compatibility...')">Check</button>
                    <div style="margin-top: 15px;">
                        <p>Compatible Devices:</p>
                        <p>{mock_data['equipment_compatibility']['Premium Mobile & Broadband'][0]}</p>
                    </div>
                </div>
            """
        },
        {
            "name": "Activity Log", 
            "icon": "📊", 
            "description": "View recent interactions",
            "content": f"""
                <div class="widget-card">
                    <p>Last 3 Activities:</p>
                    <ul>
                        <li>{mock_data['recent_activity'][0]['timestamp']}: {mock_data['recent_activity'][0]['details']}</li>
                        <li>{mock_data['recent_activity'][1]['timestamp']}: {mock_data['recent_activity'][1]['details']}</li>
                        <li>{mock_data['recent_activity'][2]['timestamp']}: {mock_data['recent_activity'][2]['details']}</li>
                    </ul>
                </div>
            """
        },
        {
            "name": "Billing Details", 
            "icon": "💰", 
            "description": "Access billing information",
            "content": f"""
                <div class="widget-card">
                    <p>Current Balance: {mock_data['bill_overview']['Current Balance']}</p>
                    <p>Due Date: {mock_data['bill_overview']['Due Date']}</p>
                    <button onclick="alert('Payment link sent!')">Send Payment Link</button>
                </div>
            """
        }
    ]

    for i in range(0, len(tools), 3):
        cols = st.columns(3)
        for j, tool in enumerate(tools[i:i+3]):
            with cols[j]:
                with st.expander(f"{tool['icon']} {tool['name']}"):
                    st.markdown(tool['content'], unsafe_allow_html=True)

def render_ai_assistance(mock_data):
    st.header("🤖 AI-Powered Assistance")
    
    # Predefined query selection
    query_type = st.selectbox("Common Issues", [
        "Select Issue",
        "Activation Problem",
        "Billing Inquiry",
        "Connection Issues",
        "Device Compatibility",
        "Service Interruption"
    ])
    
    # Custom query input
    custom_query = st.text_area("Or describe the issue:")
    
    if st.button("Process Query"):
        with st.spinner("Processing..."):
            time.sleep(1)
            response = process_ai_query(query_type + " " + custom_query, mock_data)
            st.success("AI Response:")
            st.info(response)
            
            # Actionable buttons
            if "activation" in response.lower():
                if st.button("Resolve Activation Issue"):
                    st.success("Activation successful! New status: Active")
            elif "billing" in response.lower():
                if st.button("Generate Payment Plan"):
                    st.info("Payment plan created: 3 installments of ₹666.67")

def render_automated_actions(mock_data):
    st.header("⚙️ Automated Service Actions")
    
    actions = [
        {
            "name": "Activate Service",
            "icon": "🔥",
            "content": """
                <div class="widget-card">
                    <p>Service Activation</p>
                    <button onclick="alert('Service activated!')">Execute</button>
                    <div style="margin-top: 10px;">
                        <p>Status: <span style="color: green;">Ready</span></p>
                    </div>
                </div>
            """
        },
        {
            "name": "Cancel Service",
            "icon": "🚫",
            "content": """
                <div class="widget-card">
                    <p>Service Termination</p>
                    <button onclick="alert('Service cancellation initiated')">Execute</button>
                    <div style="margin-top: 10px;">
                        <p>Confirmation: <span style="color: red;">Pending</span></p>
                    </div>
                </div>
            """
        },
        {
            "name": "Send Reminder",
            "icon": "📧",
            "content": """
                <div class="widget-card">
                    <input type="text" placeholder="Enter message" style="padding: 8px; width: 100%; margin: 10px 0;">
                    <button onclick="alert('Reminder sent!')">Send</button>
                    <div style="margin-top: 10px;">
                        <p>Last reminder sent: 2023-12-10 14:30:00</p>
                    </div>
                </div>
            """
        },
        {
            "name": "Update Details",
            "icon": "🔄",
            "content": """
                <div class="widget-card">
                    <select style="padding: 8px; width: 100%; margin: 10px 0;">
                        <option>Select Field to Update</option>
                        <option>Contact Number</option>
                        <option>Address</option>
                    </select>
                    <button onclick="alert('Details updated!')">Update</button>
                </div>
            """
        },
        {
            "name": "Run Diagnostics",
            "icon": "🔍",
            "content": """
                <div class="widget-card">
                    <p>Network Health Check</p>
                    <button onclick="alert('Diagnostics complete')">Run</button>
                    <div style="margin-top: 10px;">
                        <p>Status: <span style="color: green;">Optimal</span></p>
                    </div>
                </div>
            """
        },
        {
            "name": "Billing Adjustment",
            "icon": "💸",
            "content": """
                <div class="widget-card">
                    <input type="number" placeholder="Enter adjustment amount" style="padding: 8px; width: 100%; margin: 10px 0;">
                    <button onclick="alert('Adjustment applied!')">Apply</button>
                    <div style="margin-top: 10px;">
                        <p>New Balance: ₹1,500.00</p>
                    </div>
                </div>
            """
        }
    ]

    for i in range(0, len(actions), 3):
        cols = st.columns(3)
        for j, action in enumerate(actions[i:i+3]):
            with cols[j]:
                with st.expander(f"{action['icon']} {action['name']}"):
                    st.markdown(action['content'], unsafe_allow_html=True)

if __name__ == "__main__":
    main()