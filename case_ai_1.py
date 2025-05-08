import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import json

# Set page configuration
st.set_page_config(
    page_title="Case-AI Program",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define Verizon colors
verizon_red = "#CD040B"
verizon_black = "#000000"
verizon_grey = "#F2F2F2"
verizon_light_grey = "#D3D3D3"
verizon_white = "#FFFFFF"

# Custom CSS for Verizon styling
st.markdown("""
<style>
    .main {
        background-color: #F8F9FA;
    }
    .stApp {
        font-family: 'Arial', sans-serif;
    }
    h1, h2, h3 {
        color: #000000;
        font-weight: bold;
    }
    .stButton button {
        background-color: #CD040B;
        color: white;
        border-radius: 4px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #A00309;
    }
    .sidebar .sidebar-content {
        background-color: #F2F2F2;
    }
    .css-18e3th9 {
        padding-top: 1rem;
    }
    .stProgress .st-bo {
        background-color: #CD040B;
    }
    .card {
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .agent-card {
        border-left: 4px solid #CD040B;
        padding-left: 15px;
        margin-bottom: 15px;
    }
    .step-container {
        display: flex;
        flex-direction: column;
        gap: 15px;
        margin-bottom: 20px;
    }
    .header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid #D3D3D3;
        margin-bottom: 20px;
    }
    .confidence-meter {
        height: 10px;
        background-color: #D3D3D3;
        border-radius: 5px;
        margin-top: 5px;
    }
    .confidence-fill {
        height: 100%;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Header with Verizon logo
st.markdown("""
<div style="display: flex; align-items: center; background-color: white; padding: 10px; border-radius: 5px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
    <div style="background-color: #CD040B; color: white; padding: 10px 15px; border-radius: 5px; font-size: 24px; font-weight: bold; margin-right: 15px;">V</div>
    <div>
        <h1 style="margin: 0; color: #000000; font-size: 28px;">Case-AI Program</h1>
        <p style="margin: 0; color: #666666;">Verizon Customer Service Automation</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Mock data for the application
def generate_mock_data():
    # Customer data
    customers = {
        "network": {
            "name": "Sarah Johnson",
            "phone": "555-123-4567",
            "account_id": "VZ87654321",
            "email": "sarah.johnson@email.com",
            "address": "123 Maple Street, Chicago, IL 60007",
            "service_plan": "Unlimited Plus",
            "billing_cycle": "15th of each month",
            "active_since": "March 2019"
        },
        "billing": {
            "name": "Michael Rodriguez",
            "phone": "555-987-6543",
            "account_id": "VZ12345678",
            "email": "michael.rodriguez@email.com",
            "address": "456 Oak Avenue, Atlanta, GA 30303",
            "service_plan": "Unlimited Elite",
            "billing_cycle": "5th of each month",
            "active_since": "January 2021"
        },
        "device": {
            "name": "Emily Chen",
            "phone": "555-789-0123",
            "account_id": "VZ45678901",
            "email": "emily.chen@email.com",
            "address": "789 Pine Drive, Seattle, WA 98101",
            "service_plan": "Unlimited Basic",
            "billing_cycle": "20th of each month",
            "active_since": "July 2020",
            "device": "iPhone 15 Pro"
        }
    }
    
    # Case data
    cases = {
        "network": {
            "case_id": "CS" + str(random.randint(1000000, 9999999)),
            "case_type": "Network Connectivity Issue",
            "priority": "High",
            "status": "Open",
            "created_date": (datetime.now() - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
            "description": "Customer reports frequent network dropouts in their area for the past 3 days. Unable to make calls or use data consistently.",
            "case_notes": [
                {"timestamp": (datetime.now() - timedelta(hours=3, minutes=45)).strftime("%Y-%m-%d %H:%M:%S"), 
                 "agent": "Alex Smith", 
                 "note": "Customer called regarding intermittent network issues. Reports signal dropping multiple times per hour."},
                {"timestamp": (datetime.now() - timedelta(hours=3, minutes=40)).strftime("%Y-%m-%d %H:%M:%S"), 
                 "agent": "Alex Smith", 
                 "note": "Verified customer identity and account details. Confirmed account is in good standing."},
                {"timestamp": (datetime.now() - timedelta(hours=3, minutes=35)).strftime("%Y-%m-%d %H:%M:%S"), 
                 "agent": "Alex Smith", 
                 "note": "Attempted remote diagnostics. Customer's device shows good health but poor signal strength."},
                {"timestamp": (datetime.now() - timedelta(hours=3, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"), 
                 "agent": "Alex Smith", 
                 "note": "Checked network status for customer's area. Found possible tower maintenance in progress."},
                {"timestamp": (datetime.now() - timedelta(hours=3, minutes=25)).strftime("%Y-%m-%d %H:%M:%S"), 
                 "agent": "Alex Smith", 
                 "note": "Created follow-up case for Network Engineering team to investigate further and contact customer with resolution."}
            ]
        },
        "billing": {
            "case_id": "CS" + str(random.randint(1000000, 9999999)),
            "case_type": "Unexpected High Bill",
            "priority": "Medium",
            "status": "Open",
            "created_date": (datetime.now() - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
            "description": "Customer received a bill that is $125 higher than their usual monthly charge. No changes to their plan or usage patterns.",
            "case_notes": [
                {"timestamp": (datetime.now() - timedelta(hours=5, minutes=45)).strftime("%Y-%m-%d %H:%M:%S"), 
                 "agent": "Jessica Taylor", 
                 "note": "Customer called about unexpected increase in their monthly bill. Expressing frustration about the sudden increase without notification."},
                {"timestamp": (datetime.now() - timedelta(hours=5, minutes=40)).strftime("%Y-%m-%d %H:%M:%S"), 
                 "agent": "Jessica Taylor", 
                 "note": "Verified customer identity. Reviewed billing history showing consistent payment of $89.99 for the past 11 months."},
                {"timestamp": (datetime.now() - timedelta(hours=5, minutes=35)).strftime("%Y-%m-%d %H:%M:%S"), 
                 "agent": "Jessica Taylor", 
                 "note": "Current bill shows $214.99 total. Initial review indicates possible international roaming charges, but customer denies travel."},
                {"timestamp": (datetime.now() - timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"), 
                 "agent": "Jessica Taylor", 
                 "note": "Created follow-up case for Billing department to conduct detailed analysis and determine cause of unexpected charges."}
            ]
        },
        "device": {
            "case_id": "CS" + str(random.randint(1000000, 9999999)),
            "case_type": "Device Troubleshooting",
            "priority": "Medium",
            "status": "Open",
            "created_date": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "description": "Customer reports iPhone 15 Pro overheating and rapid battery drain after recent OS update.",
            "case_notes": [
                {"timestamp": (datetime.now() - timedelta(hours=1, minutes=45)).strftime("%Y-%m-%d %H:%M:%S"), 
                 "agent": "David Wilson", 
                 "note": "Customer called regarding iPhone 15 Pro issues. Device overheating and battery draining within 3-4 hours of full charge."},
                {"timestamp": (datetime.now() - timedelta(hours=1, minutes=40)).strftime("%Y-%m-%d %H:%M:%S"), 
                 "agent": "David Wilson", 
                 "note": "Verified customer identity and device information. iPhone 15 Pro purchased 6 months ago, recently updated to iOS 18.2."},
                {"timestamp": (datetime.now() - timedelta(hours=1, minutes=35)).strftime("%Y-%m-%d %H:%M:%S"), 
                 "agent": "David Wilson", 
                 "note": "Guided customer through basic troubleshooting: force restart, checking background app refresh, and battery health (currently at 96%)."},
                {"timestamp": (datetime.now() - timedelta(hours=1, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"), 
                 "agent": "David Wilson", 
                 "note": "Issue persists after basic troubleshooting. Customer reports phone becomes too hot to hold during normal use."},
                {"timestamp": (datetime.now() - timedelta(hours=1, minutes=25)).strftime("%Y-%m-%d %H:%M:%S"), 
                 "agent": "David Wilson", 
                 "note": "Created follow-up case for Technical Support to investigate potential hardware issue and determine if repair/replacement is needed."}
            ]
        }
    }
    
    # Tickets data
    tickets = {
        "network": [
            {
                "ticket_id": "NRB" + str(random.randint(10000, 99999)),
                "system": "NRB (Network Review Board)",
                "status": "In Progress",
                "assigned_to": "Network Engineering Team",
                "created_date": (datetime.now() - timedelta(hours=3, minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
                "description": "Investigate persistent network dropouts in Chicago Loop area affecting customer ID VZ87654321.",
                "updates": [
                    {"timestamp": (datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"), 
                     "update": "Ticket created and assigned to Network Engineering Team."},
                    {"timestamp": (datetime.now() - timedelta(hours=2, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"), 
                     "update": "Initial diagnostic shows intermittent performance on tower CHI-2345. Will conduct full scan."}
                ]
            }
        ],
        "billing": [
            {
                "ticket_id": "PMT" + str(random.randint(10000, 99999)),
                "system": "Payment Hub",
                "status": "In Progress",
                "assigned_to": "Billing Audit Team",
                "created_date": (datetime.now() - timedelta(hours=5, minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
                "description": "Review unexpected charges on account VZ12345678. Monthly bill increased by $125 without apparent service changes.",
                "updates": [
                    {"timestamp": (datetime.now() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"), 
                     "update": "Ticket created and assigned to Billing Audit Team."},
                    {"timestamp": (datetime.now() - timedelta(hours=4, minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
                     "update": "Initial review shows potential international data roaming charges applied to account despite no travel."}
                ]
            },
            {
                "ticket_id": "ITTS" + str(random.randint(10000, 99999)),
                "system": "ITTS (IT Ticketing System)",
                "status": "New",
                "assigned_to": "Billing Systems Team",
                "created_date": (datetime.now() - timedelta(hours=5, minutes=10)).strftime("%Y-%m-%d %H:%M:%S"),
                "description": "Request system audit on billing platform for possible data inconsistency affecting account VZ12345678.",
                "updates": [
                    {"timestamp": (datetime.now() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"), 
                     "update": "Ticket created and assigned to Billing Systems Team."}
                ]
            }
        ],
        "device": [
            {
                "ticket_id": "AYS" + str(random.randint(10000, 99999)),
                "system": "AYS (At Your Service)",
                "status": "In Progress",
                "assigned_to": "Device Support Specialists",
                "created_date": (datetime.now() - timedelta(hours=1, minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
                "description": "iPhone 15 Pro overheating and battery drain post iOS 18.2 update. Assess for hardware/software issue.",
                "updates": [
                    {"timestamp": (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"), 
                     "update": "Ticket created and assigned to Device Support Specialists."},
                    {"timestamp": (datetime.now() - timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"), 
                     "update": "Remote diagnostics initiated. Battery diagnostic test scheduled."}
                ]
            }
        ]
    }
    
    return customers, cases, tickets

customers, cases, tickets = generate_mock_data()

# Main application
def main():
    # Sidebar for selecting the scenario
    st.sidebar.markdown(f"""
    <div style="background-color: {verizon_red}; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
        <h3 style="color: white; margin: 0;">Case-AI Scenarios</h3>
    </div>
    """, unsafe_allow_html=True)
    
    scenario = st.sidebar.radio(
        "Select a scenario to simulate:",
        ["Network Connectivity Issue", "Unexpected High Bill", "Device Troubleshooting"]
    )
    
    scenario_key = None
    if scenario == "Network Connectivity Issue":
        scenario_key = "network"
    elif scenario == "Unexpected High Bill":
        scenario_key = "billing"
    else:
        scenario_key = "device"
    
    st.sidebar.markdown("### Current System Stats")
    col1, col2 = st.sidebar.columns(2)
    col1.metric("Active Cases", random.randint(250, 350))
    col2.metric("Avg Resolution Time", f"{random.randint(2, 4)}h {random.randint(10, 59)}m")
    
    col1, col2 = st.sidebar.columns(2)
    col1.metric("AI-Resolved", f"{random.randint(65, 85)}%")
    col2.metric("Agent Transfer", f"{random.randint(15, 35)}%")
    
    # Main content based on the selected scenario
    st.markdown(f"## Scenario: {scenario}")
    
    # Tabs to organize the workflow
    tab1, tab2, tab3 = st.tabs(["Customer Interaction", "Agentic AI Workflow", "Case Resolution"])
    
    # Tab 1: Customer Interaction
    with tab1:
        customer_interaction_tab(scenario_key)
    
    # Tab 2: Agentic AI Workflow
    with tab2:
        agentic_ai_workflow_tab(scenario_key)
    
    # Tab 3: Case Resolution
    with tab3:
        case_resolution_tab(scenario_key)

def customer_interaction_tab(scenario_key):
    st.markdown("### Customer Interaction Timeline")
    
    # Display customer information
    customer = customers[scenario_key]
    case = cases[scenario_key]
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div class="card">
            <h3>Customer Profile</h3>
            <p><strong>Name:</strong> {customer['name']}</p>
            <p><strong>Phone:</strong> {customer['phone']}</p>
            <p><strong>Account ID:</strong> {customer['account_id']}</p>
            <p><strong>Email:</strong> {customer['email']}</p>
            <p><strong>Service Plan:</strong> {customer['service_plan']}</p>
            <p><strong>Customer Since:</strong> {customer['active_since']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card">
            <h3>Interaction Case #{case['case_id']}</h3>
            <p><strong>Type:</strong> {case['case_type']}</p>
            <p><strong>Priority:</strong> {case['priority']}</p>
            <p><strong>Created:</strong> {case['created_date']}</p>
            <p><strong>Description:</strong> {case['description']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display case notes timeline
    st.markdown("### Case Notes")
    
    for note in case['case_notes']:
        st.markdown(f"""
        <div style="padding: 15px; border-left: 3px solid {verizon_red}; margin-bottom: 10px; background-color: white; border-radius: 5px;">
            <p style="color: #666; font-size: 0.8rem; margin-bottom: 5px;">{note['timestamp']} - <strong>{note['agent']}</strong></p>
            <p style="margin: 0;">{note['note']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Follow-up case creation notification
    st.markdown("### Follow-up Case Creation")
    st.success(f"Follow-up case created successfully. Reference ID: {case['case_id']}-F1")
    
    # Customer notification
    st.markdown("### Customer Notification")
    st.info(f"""
    **Email sent to customer:**
    
    Subject: Verizon Case #{case['case_id']}-F1 - We're Working on Your Request
    
    Dear {customer['name']},
    
    Thank you for contacting Verizon Customer Support. We have created a follow-up case to address your {case['case_type'].lower()}.
    
    Your case reference number is: {case['case_id']}-F1
    
    Our team is actively working to resolve your issue. You will receive updates as we make progress.
    
    Thank you for your patience.
    
    Verizon Customer Support
    """)
    
    # Animation to simulate transition to AI workflow
    st.markdown("### Case Transfer")
    st.warning("Transferring case to Case-AI for automated processing...")
    
    progress = st.progress(0)
    for i in range(101):
        time.sleep(0.01)
        progress.progress(i)

def display_confidence_meter(confidence):
    color = "#4CAF50" if confidence >= 80 else "#FF9800" if confidence >= 60 else "#F44336"
    
    st.markdown(f"""
    <div style="margin-bottom: 15px;">
        <p style="margin-bottom: 5px; font-size: 12px;">AI Confidence: {confidence}%</p>
        <div class="confidence-meter">
            <div class="confidence-fill" style="width: {confidence}%; background-color: {color};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def agentic_ai_workflow_tab(scenario_key):
    st.markdown("### Agentic AI Workflow")
    
    case = cases[scenario_key]
    case_tickets = tickets[scenario_key]
    
    # Case Master Agent Initialization
    st.markdown("""
    <div class="card">
        <h3 style="color: #CD040B;">Case Master Agent</h3>
        <p>Initializing Case-AI workflow for follow-up case processing...</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show AI confidence score
    master_confidence = random.randint(90, 99)
    display_confidence_meter(master_confidence)
    
    st.markdown(f"""
    <div class="card">
        <h4>Intent Analysis</h4>
        <p><strong>Primary Issue:</strong> {case['case_type']}</p>
        <p><strong>Urgency Level:</strong> {case['priority']}</p>
        <p><strong>Required Actions:</strong> Delegate to specialized agents for analysis and resolution</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display the workflow steps
    st.markdown("### Workflow Execution")
    
    # Step 1: Case Notes Agent
    with st.expander("Step 1: Case Notes Agent", expanded=True):
        st.markdown("""
        <h4 style="color: #CD040B;">Case Notes Agent</h4>
        <p>Researching and analyzing case notes to provide comprehensive summary...</p>
        """, unsafe_allow_html=True)
        
        time.sleep(0.5)
        notes_confidence = random.randint(85, 95)
        display_confidence_meter(notes_confidence)
        
        # Generate summary based on scenario
        if scenario_key == "network":
            summary = """
            **Case Summary:**
            - Customer experiencing frequent network dropouts in Chicago Loop area for past 3 days
            - Issue affects both voice calls and data connectivity
            - Device diagnostics show good hardware health but poor signal strength
            - Network Engineering confirmed potential tower maintenance (CHI-2345) in customer's area
            - Customer has been with Verizon since 2019 with no previous connectivity issues
            - Priority recommendation: Expedite tower maintenance completion or provide temporary signal booster
            """
        elif scenario_key == "billing":
            summary = """
            **Case Summary:**
            - Customer's bill increased by $125 compared to consistent previous 11 months ($89.99 → $214.99)
            - Initial system review indicates potential international roaming charges
            - Customer denies any international travel or usage
            - Account has good payment history with no previous billing disputes
            - Preliminary analysis suggests possible system error in charge application
            - Priority recommendation: Complete billing audit and issue immediate credit if error confirmed
            """
        else:  # device
            summary = """
            **Case Summary:**
            - Customer reports iPhone 15 Pro overheating and rapid battery drain (3-4 hours from full charge)
            - Issue began after iOS 18.2 update
            - Battery health reported at 96%, device purchased 6 months ago
            - Basic troubleshooting (force restart, background app refresh, settings review) did not resolve
            - Device becomes "too hot to hold" during normal usage
            - Priority recommendation: Advanced diagnostic scan and determine if hardware replacement needed
            """
        
        st.markdown(summary)
    
    # Step 2: Remarks Agent
    with st.expander("Step 2: Remarks Agent", expanded=True):
        st.markdown("""
        <h4 style="color: #CD040B;">Remarks Agent</h4>
        <p>Analyzing customer interaction patterns and sentiment from previous conversations...</p>
        """, unsafe_allow_html=True)
        
        time.sleep(0.5)
        remarks_confidence = random.randint(80, 90)
        display_confidence_meter(remarks_confidence)
        
        # Generate remarks based on scenario
        if scenario_key == "network":
            remarks = """
            **Conversation Analysis:**
            - Customer displayed increasing frustration throughout the call (sentiment score: negative)
            - Mentioned being a "loyal customer for years" and expectations of reliable service
            - Works from home and network issues are impacting job performance
            - Has previously contacted support twice about similar issues in past week
            - Threatened to switch providers if issue not resolved quickly
            - Recommended approach: Empathetic response with concrete timeline and compensation offer
            """
        elif scenario_key == "billing":
            remarks = """
            **Conversation Analysis:**
            - Customer initially confused but became frustrated when charges couldn't be immediately explained
            - Mentioned being on fixed income and unexpected charge causing financial hardship
            - Has recommended Verizon to family members (potential brand advocate)
            - Requested immediate resolution and bill adjustment
            - Mentioned considering consumer protection bureau if not resolved
            - Recommended approach: Priority handling with transparent explanation and goodwill credit
            """
        else:  # device
            remarks = """
            **Conversation Analysis:**
            - Customer was calm but concerned about device safety (mentioned read about battery fire incidents)
            - Recently purchased AppleCare+ but prefers not to use it if Verizon can resolve
            - Has multiple lines on account (family plan with 4 devices)
            - First time experiencing hardware issues with Verizon device
            - Expressed appreciation for agent's troubleshooting attempts
            - Recommended approach: Reassurance about safety with expedited resolution options
            """
        
        st.markdown(remarks)
    
    # Step 3: Ticketing Agent
    with st.expander("Step 3: Ticketing Agent", expanded=True):
        st.markdown("""
        <h4 style="color: #CD040B;">Ticketing Agent</h4>
        <p>Orchestrating and consolidating ticketing system information across platforms...</p>
        """, unsafe_allow_html=True)
        
        time.sleep(0.5)
        ticketing_confidence = random.randint(82, 92)
        display_confidence_meter(ticketing_confidence)
        
        # Display tickets
        st.markdown("**Associated Tickets:**")
        
        for ticket in case_tickets:
            st.markdown(f"""
            <div style="padding: 15px; border-left: 3px solid #1E88E5; margin-bottom: 15px; background-color: white; border-radius: 5px;">
                <h5 style="margin-top: 0;">{ticket['system']} - Ticket #{ticket['ticket_id']}</h5>
                <p><strong>Status:</strong> {ticket['status']}</p>
                <p><strong>Assigned To:</strong> {ticket['assigned_to']}</p>
                <p><strong>Created:</strong> {ticket['created_date']}</p>
                <p><strong>Description:</strong> {ticket['description']}</p>
                <h6 style="margin-bottom: 5px;">Updates:</h6>
                <ul style="margin-top: 0; padding-left: 20px;">
                    {' '.join(f'<li><strong>{update["timestamp"]}:</strong> {update["update"]}</li>' for update in ticket['updates'])}
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Ticket orchestration
        st.markdown("**Ticket Orchestration:**")
        
        if scenario_key == "network":
            orchestration = """
            - Cross-referenced NRB ticket with ongoing maintenance schedule
            - Identified 3 similar customer reports in same area code within past 24 hours
            - Escalated priority based on pattern recognition
            - Set automated monitoring for tower CHI-2345 status changes
            - Scheduled automated ticket updates for engineering milestones
            """
        elif scenario_key == "billing":
            orchestration = """
            - Synchronized Payment Hub and ITTS tickets for coordinated investigation
            - Set dependency chain to ensure billing audit completes before system audit
            - Flagged account for bill protection to prevent automatic payment processing
            - Set verification checkpoints to validate all line items
            - Scheduled 24-hour review cycle until resolution
            """
        else:  # device
            orchestration = """
            - Linked AYS ticket with device warranty system
            - Created automatic data capture job for device diagnostics
            - Set conditional workflow to evaluate hardware vs software issue path
            - Established secure channel for remote diagnostics session
            - Scheduled follow-up diagnostics after 24 hours of monitoring
            """
        
        st.markdown(orchestration)
    
    # Step 4: Validation Agent
    with st.expander("Step 4: Validation Agent", expanded=True):
        st.markdown("""
        <h4 style="color: #CD040B;">Validation Agent</h4>
        <p>Validating ticket information against case notes and issue description...</p>
        """, unsafe_allow_html=True)
        
        time.sleep(0.5)
        validation_confidence = random.randint(85, 95)
        display_confidence_meter(validation_confidence)
        
        # Generate validation report
        if scenario_key == "network":
            validation = """
            **Validation Report:**
            - ✅ Case notes accurately describe customer-reported symptoms
            - ✅ NRB ticket correctly identifies affected tower and service area
            - ✅ Network diagnostic data confirms intermittent service aligned with customer report
            - ✅ Tower maintenance schedule verified against network operations database
            - ✅ Customer account history confirms no previous similar issues
            - ✅ Ticket priority (High) appropriate based on impact assessment
            
            **Data Consistency Score:** 94%
            """
        elif scenario_key == "billing":
            validation = """
            **Validation Report:**
            - ✅ Case notes accurately capture billing discrepancy amount ($125)
            - ✅ Payment Hub ticket correctly addresses the billing review requirement
            - ✅ ITTS ticket appropriately requests system audit for data inconsistency
            - ❌ International roaming charges need additional verification (flagged)
            - ✅ Customer account history confirms consistent billing pattern before incident
            - ✅ Ticket priority (Medium) appropriate based on financial impact assessment
            
            **Data Consistency Score:** 89%
            """
        else:  # device
            validation = """
            **Validation Report:**
            - ✅ Case notes accurately describe device symptoms (overheating, battery drain)
            - ✅ AYS ticket correctly identifies device model and iOS version
            - ✅ Device diagnostic data confirms battery health at 96%
            - ✅ Update history confirms recent iOS 18.2 installation timing
            - ❌ Need additional data on app usage patterns during overheating (flagged)
            - ✅ Ticket priority (Medium) appropriate based on impact assessment
            
            **Data Consistency Score:** 91%
            """
        
        st.markdown(validation)
    
    # Step 5: Research Agent
    with st.expander("Step 5: Research Agent", expanded=True):
        st.markdown("""
        <h4 style="color: #CD040B;">Research Agent</h4>
        <p>Researching case, ticket, and customer history for context and pattern matching...</p>
        """, unsafe_allow_html=True)
        
        time.sleep(0.5)
        research_confidence = random.randint(80, 90)
        display_confidence_meter(research_confidence)
        
        # Generate research findings
        if scenario_key == "network":
            research = """
            **Research Findings:**
            - Found 17 similar cases reported in customer's zip code in past 72 hours
            - Network performance data shows 23% degradation in affected area
            - Tower CHI-2345 maintenance scheduled for completion within 24 hours
            - Customer account shows consistently high data usage (top 15% of users)
            - No known device-specific issues with customer's phone model
            - Previous network tickets in area resolved within avg 2.7 days
            
            **Knowledge Base Match:** Similar incident recorded 3 months ago during previous tower upgrade
            """
        elif scenario_key == "billing":
            research = """
            **Research Findings:**
            - System-wide billing anomaly reports increased by 8% this billing cycle
            - 3 other customers reported similar international charges without travel
            - Database query shows possible rate code error affecting select accounts
            - Customer payment history shows 100% on-time payments
            - Previous billing adjustment made 14 months ago (unrelated service credit)
            - Account flagged for retention monitoring due to competitive service area
            
            **Knowledge Base Match:** Similar billing system error recorded during last software update (resolved with credit)
            """
        else:  # device
            research = """
            **Research Findings:**
            - 43 similar cases reported for iPhone 15 Pro + iOS 18.2 combination
            - Apple support database confirms known issue with background processes
            - Device diagnostics show 5 apps consuming abnormal battery (Maps, Photos, Mail, Instagram, Spotify)
            - Customer has completed 2 of 4 recommended troubleshooting steps
            - Previous case resolved successfully (network configuration, 8 months ago)
            - Device is eligible for replacement if hardware issue confirmed
            
            **Knowledge Base Match:** Apple technical bulletin #TB-2317 describes similar symptoms with software resolution available
            """
        
        st.markdown(research)
    
    # Step 6: Communication Agent
    with st.expander("Step 6: Communication Agent", expanded=True):
        st.markdown("""
        <h4 style="color: #CD040B;">Communication Agent</h4>
        <p>Preparing and sending customer update notifications...</p>
        """, unsafe_allow_html=True)
        
        time.sleep(0.5)
        comm_confidence = random.randint(88, 98)
        display_confidence_meter(comm_confidence)
        
        customer = customers[scenario_key]
        
        # Generate communication updates
        if scenario_key == "network":
            communication = f"""
            **Customer Communication Sent:**
            
            **Email Update (Auto-generated):**
            Subject: Update on Your Verizon Case #{case['case_id']}-F1
            
            Dear {customer['name']},
            
            We wanted to update you on your recent network connectivity issue. Our Network Engineering team has identified that tower maintenance in your area is affecting service. The maintenance is scheduled to complete within 24 hours, which should fully restore your service.
            
            In the meantime, we've found that using WiFi calling when possible may help maintain connection quality. If you're continuing to experience issues after tomorrow, please let us know.
            
            Your case is our priority, and we'll send another update when the maintenance is complete.
            
            Thank you for your patience,
            Verizon Customer Support
            
            **SMS Update (Auto-generated):**
            Verizon: We're working on the network issue in your area (Case #{case['case_id']}-F1). Tower maintenance should be complete within 24hrs. Reply HELP for assistance.
            """
        elif scenario_key == "billing":
            communication = f"""
            **Customer Communication Sent:**
            
            **Email Update (Auto-generated):**
            Subject: Update on Your Verizon Billing Case #{case['case_id']}-F1
            
            Dear {customer['name']},
            
            We're actively investigating the unexpected charges on your recent bill. Our Billing Audit Team has identified potential incorrectly applied international charges and is working to verify and resolve this discrepancy.
            
            Rest assured, if these charges are confirmed to be in error, they will be removed from your bill and any necessary adjustments will be made. We expect to complete our investigation within 2 business days.
            
            We appreciate your patience while we resolve this matter.
            
            Sincerely,
            Verizon Customer Support
            
            **SMS Update (Auto-generated):**
            Verizon: We're investigating the billing issue on your account (Case #{case['case_id']}-F1). Expect resolution within 2 business days. Reply HELP for assistance.
            """
        else:  # device
            communication = f"""
            **Customer Communication Sent:**
            
            **Email Update (Auto-generated):**
            Subject: Update on Your iPhone Issue Case #{case['case_id']}-F1
            
            Dear {customer['name']},
            
            Our Device Support team is actively working on your iPhone 15 Pro overheating and battery drain issue. We've identified this as a known issue related to the recent iOS 18.2 update affecting several users.
            
            We're conducting remote diagnostics on your device and have found some background apps that may be contributing to the problem. We'll be providing specific steps to address these issues within the next 24 hours.
            
            If the software solutions don't resolve the issue, we'll evaluate hardware replacement options under your warranty.
            
            Thank you for your patience,
            Verizon Customer Support
            
            **SMS Update (Auto-generated):**
            Verizon: We're working on your iPhone issue (Case #{case['case_id']}-F1). Remote diagnostics in progress. Check email for details. Reply HELP for assistance.
            """
        
        st.markdown(communication)
    
    # Step 7: Case Resolver Agent
    with st.expander("Step 7: Case Resolver Agent", expanded=True):
        st.markdown("""
        <h4 style="color: #CD040B;">Case Resolver Agent</h4>
        <p>Attempting automated case resolution based on collected intelligence...</p>
        """, unsafe_allow_html=True)
        
        time.sleep(0.5)
        
        # Generate resolution attempt with different confidence levels based on scenario
        if scenario_key == "network":
            resolver_confidence = random.randint(70, 80)
            display_confidence_meter(resolver_confidence)
            
            resolution = """
            **Resolution Attempt:**
            - Verified tower CHI-2345 maintenance schedule (completion expected in 18 hours)
            - Confirmed no alternative tower capacity available for temporary routing
            - Applied courtesy account credit ($20) for service disruption
            - Set automated verification check for service restoration
            - Created SMS alert for customer when full service restored
            
            **AI Resolution Assessment:** Partial resolution possible (maintenance completion required)
            **Recommendation:** Transfer to human agent for additional service accommodation options
            """
            
            st.markdown(resolution)
            st.warning("Confidence below threshold for full automated resolution. Preparing for human agent transfer...")
            
        elif scenario_key == "billing":
            resolver_confidence = random.randint(85, 95)
            display_confidence_meter(resolver_confidence)
            
            resolution = """
            **Resolution Attempt:**
            - Confirmed system error in international roaming charge application
            - Identified 27 other affected accounts with same error pattern
            - Applied full credit ($125) to reverse erroneous charges
            - Generated corrected bill and set for immediate delivery
            - Added account note to prevent recurrence next billing cycle
            - Initiated system fix request (ticket #SYS-78934)
            
            **AI Resolution Assessment:** Full resolution achieved
            **Recommendation:** Send confirmation to customer with resolution details
            """
            
            st.markdown(resolution)
            st.success("Full resolution achieved through automated workflow. No human agent required.")
            
        else:  # device
            resolver_confidence = random.randint(60, 70)
            display_confidence_meter(resolver_confidence)
            
            resolution = """
            **Resolution Attempt:**
            - Confirmed issue matches known iOS 18.2 problem pattern
            - Generated custom troubleshooting steps for customer's specific app usage
            - Prepared backup/restore instructions if settings reset needed
            - Unable to confirm if hardware replacement needed without further diagnostics
            - Cannot remotely implement required OS-level changes
            
            **AI Resolution Assessment:** Partial resolution only (customer action required)
            **Recommendation:** Transfer to technical support specialist for guided resolution
            """
            
            st.markdown(resolution)
            st.warning("Confidence below threshold for full automated resolution. Preparing for human agent transfer...")
    
    # Display timeline summary
    st.markdown("### Agentic AI Workflow Timeline")
    
    # Create simulated timeline data
    timeline_data = []
    base_time = datetime.now() - timedelta(minutes=60)
    
    stages = [
        "Case Master Agent: Intent Analysis", 
        "Case Notes Agent: Research & Summary", 
        "Remarks Agent: Conversation Analysis",
        "Ticketing Agent: System Orchestration",
        "Validation Agent: Data Verification",
        "Research Agent: Knowledge Exploration",
        "Communication Agent: Customer Update",
        "Case Resolver Agent: Resolution Attempt"
    ]
    
    durations = [random.randint(30, 120) for _ in range(len(stages))]
    cumulative_time = 0
    
    for i, (stage, duration) in enumerate(zip(stages, durations)):
        start_time = base_time + timedelta(seconds=cumulative_time)
        end_time = start_time + timedelta(seconds=duration)
        timeline_data.append({
            "Stage": stage,
            "Start": start_time,
            "End": end_time,
            "Duration (sec)": duration
        })
        cumulative_time += duration
    
    # Convert to DataFrame
    df_timeline = pd.DataFrame(timeline_data)
    
    # Display the timeline as a table
    st.dataframe(df_timeline[["Stage", "Start", "End", "Duration (sec)"]], hide_index=True)
    
    # Calculate and display total processing time
    total_seconds = sum(durations)
    minutes, seconds = divmod(total_seconds, 60)
    st.markdown(f"**Total AI Processing Time:** {minutes} minutes, {seconds} seconds")
    
    # Calculate and display time savings
    human_time = random.randint(25, 40)
    time_saved = human_time - (total_seconds / 60)
    time_saved_percent = (time_saved / human_time) * 100
    
    st.markdown(f"""
    <div style="background-color: #E8F5E9; padding: 15px; border-radius: 5px; margin-top: 20px;">
        <h4 style="margin-top: 0; color: #2E7D32;">Efficiency Analysis</h4>
        <p><strong>Traditional Processing Time (estimate):</strong> {human_time} minutes</p>
        <p><strong>AI Processing Time:</strong> {minutes} minutes, {seconds} seconds</p>
        <p><strong>Time Saved:</strong> {time_saved:.1f} minutes ({time_saved_percent:.1f}%)</p>
    </div>
    """, unsafe_allow_html=True)

def case_resolution_tab(scenario_key):
    st.markdown("### Case Resolution Dashboard")
    
    case = cases[scenario_key]
    customer = customers[scenario_key]
    
    # Case status overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Case Status", "Resolved" if scenario_key == "billing" else "In Progress")
    with col2:
        st.metric("Resolution Time", f"{random.randint(1, 3)}h {random.randint(10, 59)}m")
    with col3:
        st.metric("AI Confidence", f"{random.randint(85, 95)}%")
    
    # Case resolution path
    if scenario_key == "billing":
        # Fully resolved by AI
        st.markdown("""
        <div class="card" style="border-left: 4px solid #4CAF50;">
            <h3 style="color: #4CAF50;">✅ Fully Resolved by AI</h3>
            <p>This case was successfully resolved through automated processes without human intervention.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Resolution Summary")
        st.markdown(f"""
        The billing issue for {customer['name']} has been fully resolved. The system identified erroneously applied international roaming charges of $125 that were incorrectly assigned to the customer's account. These charges have been reversed, and a corrected bill has been generated and sent to the customer.
        
        Additionally, a system fix request (ticket #SYS-78934) has been initiated to prevent similar errors from occurring in the future, and 27 other affected accounts have been identified for similar resolution.
        """)
        
        st.markdown("### Resolution Communication")
        st.info(f"""
        **Email sent to customer:**
        
        Subject: Resolution: Your Verizon Billing Case #{case['case_id']}-F1
        
        Dear {customer['name']},
        
        Good news! We've completed our investigation of the unexpected charges on your recent bill and have identified them as incorrectly applied international roaming charges.
        
        We've taken the following actions to resolve this issue:
        
        1. Removed the incorrect charges ($125) from your account
        2. Generated a corrected bill (available now in your online account)
        3. Added a note to your account to prevent this issue from recurring
        
        Your next bill will reflect the correct amount of $89.99, consistent with your normal monthly charges. We apologize for any inconvenience this may have caused and appreciate your patience while we resolved this matter.
        
        If you have any further questions or concerns, please don't hesitate to contact us.
        
        Thank you for being a valued Verizon customer.
        
        Sincerely,
        Verizon Customer Support
        """)
        
    else:
        # Human-in-the-loop required
        st.markdown("""
        <div class="card" style="border-left: 4px solid #FF9800;">
            <h3 style="color: #FF9800;">👤 Human-in-the-Loop Required</h3>
            <p>This case requires human intervention for complete resolution.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Agent Transfer Status")
        
        if scenario_key == "network":
            st.markdown(f"""
            The network connectivity issue for {customer['name']} requires human intervention due to the following factors:
            
            1. Tower maintenance is still in progress (estimated completion: 18 hours)
            2. No alternative tower routing options are available for immediate resolution
            3. Customer has expressed frustration and may require additional account accommodations
            
            The case has been escalated to a Network Specialist with all AI-gathered intelligence for expedited handling.
            """)
            
            st.warning("Customer has been transferred to Network Specialist Team. Average wait time: 3 minutes")
            
        else:  # device
            st.markdown(f"""
            The device troubleshooting issue for {customer['name']} requires human intervention due to the following factors:
            
            1. Remote diagnostics confirm software-related causes, but require customer-side actions
            2. Complex troubleshooting steps need guided implementation
            3. Potential hardware assessment may be required if software solutions fail
            
            The case has been escalated to a Device Support Specialist with all AI-gathered intelligence for guided resolution.
            """)
            
            st.warning("Customer has been transferred to Device Support Specialist Team. Average wait time: 5 minutes")
    
    # Display case champion efficiency metrics
    st.markdown("### Case Champion Efficiency Impact")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Generate data for time comparison chart
        categories = ['Research', 'Analysis', 'Documentation', 'Resolution', 'Communication']
        traditional_time = [random.randint(5, 15) for _ in range(5)]
        ai_assisted_time = [int(t * random.uniform(0.2, 0.5)) for t in traditional_time]
        
        # Create the comparison bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=categories,
            x=traditional_time,
            name='Traditional Process',
            orientation='h',
            marker=dict(color='#9E9E9E')
        ))
        fig.add_trace(go.Bar(
            y=categories,
            x=ai_assisted_time,
            name='Case-AI Assisted',
            orientation='h',
            marker=dict(color=verizon_red)
        ))
        
        fig.update_layout(
            title='Time Spent (minutes)',
            barmode='group',
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Generate data for resolution funnel
        all_cases = 100
        ai_processed = int(all_cases * random.uniform(0.9, 1.0))
        ai_resolved = int(ai_processed * random.uniform(0.7, 0.8))
        human_resolved = ai_processed - ai_resolved
        not_processed = all_cases - ai_processed
        
        # Create the funnel chart
        fig = go.Figure(go.Funnel(
            y = ['Total Cases', 'AI Processed', 'AI Resolved', 'Human Resolved'],
            x = [all_cases, ai_processed, ai_resolved, human_resolved],
            textinfo = "value+percent initial",
            marker = {"color": [verizon_grey, verizon_light_grey, verizon_red, "#1E88E5"]}
        ))
        
        fig.update_layout(
            title='Case Resolution Funnel',
            height=350,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Overall impact metrics
    st.markdown("### Overall Case-AI Program Impact")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Average Resolution Time", "4h 12m", "-65%")
    with col2:
        st.metric("Agent Efficiency", "+82%", "↑")
    with col3:
        st.metric("Customer Satisfaction", "94%", "+12%")
    with col4:
        st.metric("Operational Cost", "-35%", "↓")
    
    # Add a feedback section
    st.markdown("### Case Champion Feedback")
    
    if scenario_key == "billing":
        st.markdown("""
        <div style="background-color: #F0F8FF; padding: 15px; border-radius: 5px; border-left: 4px solid #1E88E5;">
            <p><strong>Case Champion:</strong> Jennifer Martinez</p>
            <p><i>"The Case-AI system resolved this billing issue completely without my intervention. The system correctly identified the erroneous international charges, applied the appropriate credit, and communicated effectively with the customer. The detailed AI analysis saved me at least 25 minutes of research time, and the automated resolution was exactly what I would have done. This is a perfect example of how AI can handle routine billing discrepancies."</i></p>
            <p><strong>Rating:</strong> ⭐⭐⭐⭐⭐ (5/5)</p>
        </div>
        """, unsafe_allow_html=True)
    elif scenario_key == "network":
        st.markdown("""
        <div style="background-color: #F0F8FF; padding: 15px; border-radius: 5px; border-left: 4px solid #1E88E5;">
            <p><strong>Case Champion:</strong> Marcus Johnson</p>
            <p><i>"Case-AI provided exceptional preprocessing for this network issue. When the case was transferred to me, I had immediate access to the tower maintenance schedule, affected area statistics, and customer sentiment analysis. This allowed me to quickly offer the customer a temporary hotspot device while tower maintenance completes. The AI correctly identified that human intervention was needed but saved me about 15 minutes of research and documentation time."</i></p>
            <p><strong>Rating:</strong> ⭐⭐⭐⭐ (4/5)</p>
        </div>
        """, unsafe_allow_html=True)
    else:  # device
        st.markdown("""
        <div style="background-color: #F0F8FF; padding: 15px; border-radius: 5px; border-left: 4px solid #1E88E5;">
            <p><strong>Case Champion:</strong> Aisha Washington</p>
            <p><i>"The Case-AI system correctly identified this as a known iOS issue and provided me with the Apple technical bulletin reference. This saved significant research time. When the customer was transferred to me, I already had the complete device history, diagnostic results, and specific apps causing the issue. I was able to immediately guide the customer through the advanced troubleshooting steps without having to run preliminary diagnostics. The AI handoff was smooth and contextual."</i></p>
            <p><strong>Rating:</strong> ⭐⭐⭐⭐ (4/5)</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Process improvement recommendations
    st.markdown("### Process Improvement Recommendations")
    
    if scenario_key == "billing":
        st.markdown("""
        1. **System Integration:** Enhance integration between Payment Hub and billing system to automatically flag anomalous charges
        2. **Pattern Detection:** Implement proactive monitoring for billing anomalies affecting multiple customers
        3. **Auto-Resolution:** Extend automatic credit authority for similar verified billing errors
        """)
    elif scenario_key == "network":
        st.markdown("""
        1. **Predictive Notifications:** Implement proactive customer notifications before planned tower maintenance
        2. **Alternative Routing:** Develop automatic temporary routing to nearby towers during maintenance
        3. **Service Credits:** Authorize AI to offer standardized compensation for service disruptions
        """)
    else:  # device
        st.markdown("""
        1. **Knowledge Integration:** Faster synchronization with manufacturer technical bulletins
        2. **Guided Troubleshooting:** Develop interactive step-by-step guidance for complex device issues
        3. **Diagnostic Expansion:** Enhance remote diagnostic capabilities to identify hardware vs software issues more conclusively
        """)
    
    # Add disposition tracking
    st.markdown("### Disposition Tracker")
    
    disposition_data = {
        "billing": {
            "Case Type": "Billing Issue",
            "Root Cause": "System Error - International Roaming Charges",
            "Resolution Method": "Automatic Credit Application",
            "Resolution Time": "1h 37m",
            "Customer Contacted": "Yes - Email & SMS",
            "Follow-up Required": "No",
            "Satisfaction Survey Sent": "Yes",
            "Knowledge Base Updated": "Yes - Article #KB-7823"
        },
        "network": {
            "Case Type": "Network Connectivity",
            "Root Cause": "Tower Maintenance - CHI-2345",
            "Resolution Method": "Human Agent - Temporary Solution Provided",
            "Resolution Time": "2h 15m (ongoing)",
            "Customer Contacted": "Yes - Email & SMS",
            "Follow-up Required": "Yes - 24h",
            "Satisfaction Survey Sent": "Pending Resolution",
            "Knowledge Base Updated": "No"
        },
        "device": {
            "Case Type": "Device Troubleshooting",
            "Root Cause": "Software Issue - iOS 18.2 Update",
            "Resolution Method": "Human Agent - Guided Troubleshooting",
            "Resolution Time": "2h 42m (ongoing)",
            "Customer Contacted": "Yes - Email & SMS",
            "Follow-up Required": "Yes - 48h",
            "Satisfaction Survey Sent": "Pending Resolution",
            "Knowledge Base Updated": "In Progress"
        }
    }
    
    df_disposition = pd.DataFrame([disposition_data[scenario_key]]).T.reset_index()
    df_disposition.columns = ["Metric", "Value"]
    
    st.table(df_disposition)

def main():
    # Sidebar for selecting the scenario
    st.sidebar.markdown(f"""
    <div style="background-color: {verizon_red}; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
        <h3 style="color: white; margin: 0;">Case-AI Scenarios</h3>
    </div>
    """, unsafe_allow_html=True)
    
    scenario = st.sidebar.radio(
        "Select a scenario to simulate:",
        ["Network Connectivity Issue", "Unexpected High Bill", "Device Troubleshooting"]
    )
    
    scenario_key = None
    if scenario == "Network Connectivity Issue":
        scenario_key = "network"
    elif scenario == "Unexpected High Bill":
        scenario_key = "billing"
    else:
        scenario_key = "device"
    
    st.sidebar.markdown("### Current System Stats")
    col1, col2 = st.sidebar.columns(2)
    col1.metric("Active Cases", random.randint(250, 350))
    col2.metric("Avg Resolution Time", f"{random.randint(2, 4)}h {random.randint(10, 59)}m")
    
    col1, col2 = st.sidebar.columns(2)
    col1.metric("AI-Resolved", f"{random.randint(65, 85)}%")
    col2.metric("Agent Transfer", f"{random.randint(15, 35)}%")
    
    # Main content based on the selected scenario
    st.markdown(f"## Scenario: {scenario}")
    
    # Tabs to organize the workflow
    tab1, tab2, tab3 = st.tabs(["Customer Interaction", "Agentic AI Workflow", "Case Resolution"])
    
    # Tab 1: Customer Interaction
    with tab1:
        customer_interaction_tab(scenario_key)
    
    # Tab 2: Agentic AI Workflow
    with tab2:
        agentic_ai_workflow_tab(scenario_key)
    
    # Tab 3: Case Resolution
    with tab3:
        case_resolution_tab(scenario_key)

if __name__ == "__main__":
    main()