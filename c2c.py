import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Activation Arena",
    page_icon="📱",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .agent-box {
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .orchestrator {
        background-color: #f0f8ff;
        border-left: 5px solid #1e90ff;
    }
    .resolver {
        background-color: #f0fff0;
        border-left: 5px solid #32cd32;
    }
    .error {
        background-color: #fff0f0;
        border-left: 5px solid #ff6347;
    }
    .human {
        background-color: #fff8f0;
        border-left: 5px solid #ffa500;
    }
    .success {
        background-color: #f0fff0;
        border-left: 5px solid #008000;
    }
    .stProgress .st-bo {
        background-color: #1e90ff;
    }
    .log-message {
        padding: 5px 10px;
        margin: 5px 0;
        border-radius: 3px;
    }
    .log-info {
        background-color: #e6f7ff;
        border-left: 3px solid #1890ff;
    }
    .log-success {
        background-color: #e6ffe6;
        border-left: 3px solid #52c41a;
    }
    .log-error {
        background-color: #fff1f0;
        border-left: 3px solid #ff4d4f;
    }
    .log-warning {
        background-color: #fffbe6;
        border-left: 3px solid #faad14;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("📱 Activation Arena")
st.subheader("Agentic AI-powered Solution for Activation Issues")

st.markdown("""
This system demonstrates the future state of telecom activation issue resolution using agentic AI. 
It helps retail store representatives quickly diagnose and fix activation issues without requiring
deep technical knowledge of backend systems.
""")

# Create session state variables if they don't exist
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'current_phase' not in st.session_state:
    st.session_state.current_phase = "input"
if 'selected_scenario' not in st.session_state:
    st.session_state.selected_scenario = None
if 'human_intervention' not in st.session_state:
    st.session_state.human_intervention = False
if 'human_response' not in st.session_state:
    st.session_state.human_response = None
if 'issue_resolved' not in st.session_state:
    st.session_state.issue_resolved = False
if 'simulation_complete' not in st.session_state:
    st.session_state.simulation_complete = False
if 'progress_value' not in st.session_state:
    st.session_state.progress_value = 0
if 'transaction_details' not in st.session_state:
    st.session_state.transaction_details = {}

# Reset Button (Always visible)
if st.sidebar.button("Reset Application"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Mock data for scenarios
scenarios = {
    "scenario1": {
        "customer_id": "CUST123456",
        "mtn": "1234567890",
        "issue_type": "NFSA",
        "description": "Order created but activation request not sent to network",
        "resolver": "NFSA Resolver",
        "requires_human": False,
        "transaction_details": {
            "order_id": "ORD987654321",
            "sim_iccid": "89014103211118510720",
            "plan_code": "UNLIMITED-5G",
            "device_imei": "359072061304313",
            "activation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "order_source": "Retail Store #17834",
            "account_type": "Consumer Postpaid"
        },
        "checks": [
            {"name": "Order Status Check", "result": "CREATED", "status": "success"},
            {"name": "Activation Status Check", "result": "NOT_SENT", "status": "error"},
            {"name": "SIM Card Validation", "result": "VALID", "status": "success"},
            {"name": "Network Connectivity", "result": "AVAILABLE", "status": "success"},
        ],
        "resolution_steps": [
            "Retrieving order details from CRM",
            "Verifying SIM card ICCID in inventory system",
            "Creating activation packet for network provisioning",
            "Submitting activation request to network gateway",
            "Confirming activation signal received by network",
            "Updating order status in CRM to 'ACTIVATION_PENDING'",
            "Verifying activation completion in network system"
        ]
    },
    "scenario2": {
        "customer_id": "CUST789012",
        "mtn": "9876543210",
        "issue_type": "Device Payment Plan",
        "description": "Device payment plan verification failed",
        "resolver": "Device Payment Plan Resolver",
        "requires_human": True,
        "human_intervention_point": 3,
        "human_intervention_reason": "Credit check requires manual verification due to recent address change",
        "transaction_details": {
            "order_id": "ORD458721093",
            "device_type": "iPhone 16 Pro",
            "device_imei": "353879234102475",
            "plan_term": "24 months",
            "monthly_payment": "$32.50",
            "total_financed": "$780.00",
            "credit_application_id": "CR-78934-AX",
            "address_change_date": (datetime.now() - pd.Timedelta(days=15)).strftime("%Y-%m-%d")
        },
        "checks": [
            {"name": "Order Status Check", "result": "CREATED", "status": "success"},
            {"name": "Device Payment Plan Status", "result": "PENDING_VERIFICATION", "status": "error"},
            {"name": "Credit Check Status", "result": "MANUAL_REVIEW", "status": "warning"},
            {"name": "Device Inventory Check", "result": "IN_STOCK", "status": "success"},
        ],
        "resolution_steps": [
            "Retrieving customer payment plan details",
            "Verifying device eligibility for selected plan",
            "Running credit check through financial system",
            "Awaiting customer service agent review for credit verification",
            "Processing payment plan authorization",
            "Linking device to customer account",
            "Updating billing system with payment plan details"
        ],
        "after_human_approval_steps": [
            "Manually verified customer address history in credit system",
            "Applied approval override to credit check",
            "Processing payment plan authorization with approved status",
            "Linking device to customer account with verified financial status",
            "Updating billing system with complete payment plan details",
            "Marking device payment plan as ACTIVE in CRM",
            "Generating customer payment plan confirmation"
        ]
    },
    "scenario3": {
        "customer_id": "CUST345678",
        "mtn": "5556667777",
        "issue_type": "MTAS Switch Error",
        "description": "Mobile Telephone Administration System switch error preventing activation",
        "resolver": "MTAS Switch Error Resolver",
        "requires_human": False,
        "transaction_details": {
            "order_id": "ORD234567890",
            "sim_iccid": "89014103276395104582",
            "switch_id": "MTAS-SWITCH-54",
            "error_code": "ERROR_CODE_4532",
            "error_description": "Network routing misconfiguration",
            "system_version": "MTAS v7.3.2",
            "operator_id": "SYS-AUTO-12"
        },
        "checks": [
            {"name": "Order Status Check", "result": "CREATED", "status": "success"},
            {"name": "Activation Status Check", "result": "FAILED", "status": "error"},
            {"name": "MTAS Switch Status", "result": "ERROR_CODE_4532", "status": "error"},
            {"name": "Network Routing Check", "result": "MISCONFIGURED", "status": "error"},
        ],
        "resolution_steps": [
            "Identifying MTAS switch error code 4532",
            "Running diagnostic on switch configuration",
            "Clearing cached routing information",
            "Resetting switch port assignment",
            "Reconfiguring network routing parameters",
            "Testing connection through alternate switch path",
            "Confirming proper routing configuration"
        ]
    },
    "scenario4": {
        "customer_id": "CUST901234",
        "mtn": "3334445555",
        "issue_type": "eSIM Activation",
        "description": "eSIM profile download failed on device",
        "resolver": "MLMO-eSim Issue Resolver",
        "requires_human": False,
        "transaction_details": {
            "order_id": "ORD543219876",
            "esim_profile_id": "ESIM-73628495",
            "device_model": "Pixel 8 Pro",
            "device_os": "Android 15",
            "activation_code": "LPA:1$smdpplus.provider.com$9-8KH12-SDKL8-30XB",
            "profile_status": "GENERATED",
            "mlmo_server": "esim-server-03.provider.com"
        },
        "checks": [
            {"name": "Order Status Check", "result": "CREATED", "status": "success"},
            {"name": "eSIM Profile Status", "result": "GENERATED", "status": "success"},
            {"name": "MLMO Connectivity", "result": "ERROR", "status": "error"},
            {"name": "Device Compatibility", "result": "COMPATIBLE", "status": "success"},
        ],
        "resolution_steps": [
            "Verifying eSIM profile generation in MLMO system",
            "Checking device compatibility with eSIM technology",
            "Resetting connection to MLMO server",
            "Regenerating eSIM activation code",
            "Creating secure download channel",
            "Pushing eSIM profile to device",
            "Confirming profile installation on device"
        ]
    },
    "scenario5": {
        "customer_id": "CUST567890",
        "mtn": "7778889999",
        "issue_type": "Port-In Validation",
        "description": "Number port-in verification failed from previous carrier",
        "resolver": "Port-In Verification Resolver",
        "requires_human": True,
        "human_intervention_point": 2,
        "human_intervention_reason": "Account name mismatch with previous carrier records",
        "transaction_details": {
            "order_id": "ORD678905432",
            "port_request_id": "PORT-67890-54321",
            "previous_carrier": "Competitor Mobile",
            "account_number": "AC-674839201",
            "pin_code": "1234",
            "submitted_name": "J Smith",
            "carrier_name": "John A. Smith",
            "port_submission_date": datetime.now().strftime("%Y-%m-%d"),
            "requested_port_date": (datetime.now() + pd.Timedelta(days=2)).strftime("%Y-%m-%d")
        },
        "checks": [
            {"name": "Order Status Check", "result": "CREATED", "status": "success"},
            {"name": "Port Request Status", "result": "REJECTED", "status": "error"},
            {"name": "Account Validation", "result": "MISMATCH", "status": "error"},
            {"name": "Previous Carrier Check", "result": "AVAILABLE", "status": "success"},
        ],
        "resolution_steps": [
            "Retrieving port request details from Number Portability Administration Center",
            "Validating customer information against previous carrier records",
            "Correcting account name discrepancy in port request",
            "Updating authorization information",
            "Resubmitting port request with corrected information",
            "Confirming acceptance by donor carrier",
            "Scheduling port completion date"
        ],
        "after_human_approval_steps": [
            "Updating customer name from 'J Smith' to 'John A. Smith' in port request",
            "Re-validating customer information with updated name data",
            "Updating authorization information with corrected account details",
            "Resubmitting port request to Number Portability Administration Center",
            "Receiving acceptance confirmation from donor carrier",
            "Setting port completion date in system",
            "Sending confirmation notification to customer"
        ]
    }
}

# Function to add log entries
def add_log(agent, message, log_type="info"):
    st.session_state.logs.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "agent": agent,
        "message": message,
        "type": log_type
    })

# Demo scenario selector (hidden in production)
with st.expander("Demo Controls (For Testing Only)"):
    selected_demo = st.selectbox(
        "Choose a demo scenario",
        options=list(scenarios.keys()),
        format_func=lambda x: f"{scenarios[x]['customer_id']} - {scenarios[x]['issue_type']}"
    )
    
    if st.button("Load Demo Scenario"):
        st.session_state.selected_scenario = selected_demo
        demo_data = scenarios[selected_demo]
        st.session_state.customer_id = demo_data["customer_id"]
        st.session_state.mtn = demo_data["mtn"]
        st.rerun()

# Input form
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        customer_id = st.text_input("Customer ID", 
                                    key="customer_id_input",
                                    value=st.session_state.get("customer_id", ""))
    
    with col2:
        mtn = st.text_input("Mobile Telephone Number (MTN)", 
                           key="mtn_input",
                           value=st.session_state.get("mtn", ""))
    
    start_processing = st.button("Process Activation", disabled=st.session_state.processing)
    if start_processing:
        if customer_id and mtn:
            st.session_state.customer_id = customer_id
            st.session_state.mtn = mtn
            st.session_state.processing = True
            st.session_state.logs = []
            st.session_state.current_phase = "orchestrator"
            st.session_state.human_intervention = False
            st.session_state.issue_resolved = False
            st.session_state.simulation_complete = False
            st.session_state.progress_value = 0
            
            # Select a random scenario if none is preselected
            if not st.session_state.selected_scenario:
                st.session_state.selected_scenario = random.choice(list(scenarios.keys()))
            
            # Store transaction details
            scenario = scenarios[st.session_state.selected_scenario]
            st.session_state.transaction_details = scenario.get("transaction_details", {})
            
            # Add initial log entry
            add_log("System", f"Received activation verification request for Customer ID: {customer_id}, MTN: {mtn}", "info")
            st.rerun()
        else:
            st.error("Please enter both Customer ID and MTN")

# State management functions
def reset_simulation():
    st.session_state.processing = False
    st.session_state.logs = []
    st.session_state.current_phase = "input"
    st.session_state.selected_scenario = None
    st.session_state.human_intervention = False
    st.session_state.human_response = None
    st.session_state.issue_resolved = False
    st.session_state.customer_id = ""
    st.session_state.mtn = ""
    st.session_state.simulation_complete = False
    st.session_state.progress_value = 0
    st.session_state.transaction_details = {}

def advance_to_phase(phase, issue_resolved=False):
    st.session_state.current_phase = phase
    if phase == "complete":
        st.session_state.simulation_complete = True
        st.session_state.issue_resolved = issue_resolved
    st.rerun()

# Display processing area when processing is active
if st.session_state.processing:
    # Get the scenario data
    scenario = scenarios[st.session_state.selected_scenario]
    
    # Display the current status/phase
    current_status_col1, current_status_col2 = st.columns([3, 1])
    
    with current_status_col1:
        if st.session_state.current_phase == "orchestrator":
            st.subheader("🧠 Orchestrator Agent")
            st.info("Analyzing issue and routing to appropriate resolver")
        elif st.session_state.current_phase == "resolver":
            st.subheader(f"🔧 {scenario['resolver']}")
            st.success(f"Working on resolving: {scenario['description']}")
        elif st.session_state.current_phase == "human":
            st.subheader("👤 Human Agent Intervention Required")
            st.warning(f"Awaiting human agent decision: {scenario.get('human_intervention_reason', 'Manual intervention required')}")
        elif st.session_state.current_phase == "complete":
            st.subheader("✅ Resolution Complete")
            if st.session_state.issue_resolved:
                st.success("Activation issue successfully resolved!")
            else:
                st.error("Activation issue could not be automatically resolved. Ticket created for further investigation.")
    
    with current_status_col2:
        if st.session_state.current_phase == "complete":
            if st.button("New Request"):
                reset_simulation()
                st.rerun()
        else:
            # Reset button during processing
            if st.button("Cancel Process"):
                reset_simulation()
                st.rerun()
    
    # Display progress bar
    if st.session_state.current_phase not in ["complete", "human"]:
        progress_bar = st.progress(st.session_state.progress_value)
        latest_status = st.empty()
    
    # Display log section
    st.markdown("### System Logs")
    log_container = st.container()
    
    with log_container:
        for log in st.session_state.logs:
            css_class = f"log-{log['type']}"
            st.markdown(f"""
            <div class="log-message {css_class}">
                <small>{log['timestamp']}</small> - <strong>{log['agent']}</strong>: {log['message']}
            </div>
            """, unsafe_allow_html=True)
    
    # Orchestrator phase simulation
    if st.session_state.current_phase == "orchestrator" and not st.session_state.simulation_complete:
        # Display checks being performed
        with st.expander("System Checks", expanded=True):
            checks_df = pd.DataFrame(scenario["checks"])
            
            # Create formatted dataframe for display
            for i, check in enumerate(checks_df.iterrows()):
                status_color = "green" if check[1]["status"] == "success" else "red" if check[1]["status"] == "error" else "orange"
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f0f0f0;">
                    <div>{check[1]["name"]}</div>
                    <div style="color: {status_color}; font-weight: bold;">{check[1]["result"]}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Add to logs and update progress
                time.sleep(0.5)
                progress_value = (i + 1) / len(checks_df)
                st.session_state.progress_value = progress_value
                progress_bar.progress(progress_value)
                add_log("Orchestrator", f"Performed {check[1]['name']}: {check[1]['result']}", 
                       log_type="success" if check[1]["status"] == "success" else "error")
                latest_status.info(f"Performing check: {check[1]['name']}")
        
        # Finish orchestrator phase and move to resolver
        time.sleep(1)
        add_log("Orchestrator", f"Analysis complete. Issue identified: {scenario['description']}", "warning")
        add_log("System", f"Routing to {scenario['resolver']} for resolution", "info")
        advance_to_phase("resolver")
    
    # Resolver phase simulation
    elif st.session_state.current_phase == "resolver" and not st.session_state.simulation_complete:
        # Reset progress only at the beginning, not when coming back from human intervention
        if st.session_state.progress_value >= 1.0 and not st.session_state.get("human_response"):
            st.session_state.progress_value = 0
        
        # Determine which resolution steps to use
        resolution_steps = scenario["resolution_steps"]
        
        # If we're coming from human approval, use the alternate steps if available
        if st.session_state.get("human_response") == "approved" and "after_human_approval_steps" in scenario:
            resolution_steps = scenario["after_human_approval_steps"]
            
        # Show resolution steps being executed
        with st.expander("Resolution Process", expanded=True):
            # Initialize progress tracking
            total_steps = len(resolution_steps)
            
            # Determine starting point - if coming from human intervention
            start_index = 0
            if st.session_state.get("human_response") == "approved":
                # Start from the beginning of the human approval steps
                st.session_state.progress_value = 0
                # Log resumption of process
                add_log(scenario["resolver"], "Resuming resolution process after human approval", "info")
            
            # Process each remaining resolution step
            for i in range(start_index, len(resolution_steps)):
                step = resolution_steps[i]
                
                # Check if we need human intervention at this step
                if scenario.get("requires_human", False) and i == scenario.get("human_intervention_point", 0) and not st.session_state.get("human_response"):
                    latest_status.warning(f"Human intervention required: {scenario.get('human_intervention_reason', 'Manual intervention required')}")
                    add_log(scenario["resolver"], f"Process paused: {scenario.get('human_intervention_reason', 'Manual intervention required')}", "warning")
                    st.session_state.human_intervention = True
                    advance_to_phase("human")
                    break
                
                # Display and log the current step
                st.markdown(f"""
                <div style="display: flex; align-items: center; padding: 8px 0; border-bottom: 1px solid #f0f0f0;">
                    <div style="margin-right: 10px;">▶️</div>
                    <div>{step}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Simulate processing
                time.sleep(0.7)
                progress_value = (i + 1) / total_steps
                st.session_state.progress_value = progress_value
                progress_bar.progress(progress_value)
                add_log(scenario["resolver"], f"Executed: {step}", "success")
                latest_status.info(f"Processing: {step}")
            
            # If we've completed all steps, mark as complete
            if st.session_state.progress_value >= 0.99:
                time.sleep(1)
                add_log(scenario["resolver"], f"Resolution complete: {scenario['description']}", "success")
                
                # Add final completion message based on the scenario
                if scenario['issue_type'] == "Device Payment Plan":
                    add_log("System", "✅ Transaction completed: Device payment plan successfully verified and activated", "success")
                elif scenario['issue_type'] == "Port-In Validation":
                    add_log("System", "✅ Transaction completed: Port-in request accepted by previous carrier", "success")
                elif scenario['issue_type'] == "NFSA":
                    add_log("System", "✅ Transaction completed: Activation request successfully sent to network", "success")
                elif scenario['issue_type'] == "MTAS Switch Error":
                    add_log("System", "✅ Transaction completed: Switch error resolved and activation completed", "success")
                elif scenario['issue_type'] == "eSIM Activation":
                    add_log("System", "✅ Transaction completed: eSIM profile successfully downloaded to device", "success")
                else:
                    add_log("System", "✅ Transaction completed: Activation issue successfully resolved", "success")
                    
                advance_to_phase("complete", issue_resolved=True)
    
    # Human intervention phase
    elif st.session_state.current_phase == "human" and not st.session_state.simulation_complete:
        # Display human intervention UI
        st.markdown("### Human Agent Interface")
        
        with st.container():
            st.markdown(f"""
            <div class="agent-box human">
                <h4>Customer Service Agent Review Required</h4>
                <p><strong>Issue:</strong> {scenario['description']}</p>
                <p><strong>Reason for escalation:</strong> {scenario.get('human_intervention_reason', 'Manual intervention required')}</p>
                <p><strong>Customer:</strong> {st.session_state.customer_id}</p>
                <p><strong>MTN:</strong> {st.session_state.mtn}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display transaction details
            with st.expander("Transaction Details", expanded=True):
                if st.session_state.transaction_details:
                    for key, value in st.session_state.transaction_details.items():
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #f0f0f0;">
                            <div><strong>{key.replace('_', ' ').title()}:</strong></div>
                            <div>{value}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No additional transaction details available")
            
            # Show agent options
            st.write("Please review and choose an action:")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Approve and Continue Processing"):
                    add_log("Human Agent", "Review complete: Approved continuation of automated processing", "success")
                    st.session_state.human_response = "approved"
                    st.session_state.human_intervention = True
                    
                    # If this was a Port-In scenario, show what was fixed
                    if scenario['issue_type'] == "Port-In Validation":
                        add_log("Human Agent", "Updated account name from 'J Smith' to 'John A. Smith' to match carrier records", "info")
                    # If this was a Device Payment Plan scenario, show verification
                    elif scenario['issue_type'] == "Device Payment Plan":
                        add_log("Human Agent", "Manually verified address change and approved credit application", "info")
                    
                    advance_to_phase("resolver")
            
            with col2:
                if st.button("Reject and Create Manual Ticket"):
                    add_log("Human Agent", "Review complete: Creating manual ticket for further investigation", "warning")
                    st.session_state.human_response = "rejected"
                    advance_to_phase("complete", issue_resolved=False)
            
            with col3:
                if st.button("Request Customer Callback"):
                    add_log("Human Agent", "Review complete: Additional information needed from customer", "warning")
                    st.session_state.human_response = "callback"
                    advance_to_phase("complete", issue_resolved=False)
            
            # Option to add notes
            notes = st.text_area("Agent Notes (optional)")
            if notes:
                if st.button("Add Notes"):
                    add_log("Human Agent", f"Notes added: {notes}", "info")
                    st.rerun()
    
    # Complete phase - show results
    elif st.session_state.current_phase == "complete":
        # Show final results and summary
        with st.container():
            if st.session_state.issue_resolved:
                st.markdown(f"""
                <div class="agent-box success">
                    <h4>✅ Activation Issue Successfully Resolved</h4>
                    <p><strong>Customer ID:</strong> {st.session_state.customer_id}</p>
                    <p><strong>MTN:</strong> {st.session_state.mtn}</p>
                    <p><strong>Issue Type:</strong> {scenario['issue_type']}</p>
                    <p><strong>Resolution:</strong> {scenario['description']} has been successfully resolved.</p>
                    <p><strong>Resolver Agent:</strong> {scenario['resolver']}</p>
                    <p><strong>Resolution Time:</strong> {random.randint(15, 120)} seconds</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display transaction details
                with st.expander("Transaction Details", expanded=True):
                    # Add transaction completion details
                    completion_details = {
                        "transaction_id": f"TX-{random.randint(10000000, 99999999)}",
                        "completion_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "activation_status": "ACTIVE",
                        "confirmation_code": f"CONF-{random.randint(100000, 999999)}"
                    }
                    
                    all_details = {**st.session_state.transaction_details, **completion_details}
                    
                    for key, value in all_details.items():
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #f0f0f0;">
                            <div><strong>{key.replace('_', ' ').title()}:</strong></div>
                            <div>{value}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Display next steps
                st.info("The system has notified the customer via SMS that their activation is complete.")
            else:
                ticket_id = f"T-{random.randint(100000, 999999)}"
                
                st.markdown(f"""
                <div class="agent-box error">
					<h4>⚠️ Manual Intervention Required</h4>
                    <p><strong>Customer ID:</strong> {st.session_state.customer_id}</p>
                    <p><strong>MTN:</strong> {st.session_state.mtn}</p>
                    <p><strong>Issue Type:</strong> {scenario['issue_type']}</p>
                    <p><strong>Status:</strong> {
                        "Additional customer information required." if st.session_state.human_response == "callback" else
                        "Automated resolution unsuccessful. Ticket has been created for manual processing."
                    }</p>
                    <p><strong>Ticket ID:</strong> {ticket_id}</p>
                    <p><strong>Priority:</strong> {random.choice(["High", "Medium"])}</p>
                    <p><strong>Assigned To:</strong> {random.choice(["Tier 2 Support", "Activation Specialist Team", "Account Management Team"])}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display escalation details
                with st.expander("Escalation Details", expanded=True):
                    escalation_details = {
                        "ticket_id": ticket_id,
                        "created_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "estimated_resolution": random.choice(["4 hours", "8 hours", "24 hours"]),
                        "resolution_channel": random.choice(["Call", "Email", "SMS"]),
                        "notification_sent": "Yes"
                    }
                    
                    all_details = {**st.session_state.transaction_details, **escalation_details}
                    
                    for key, value in all_details.items():
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #f0f0f0;">
                            <div><strong>{key.replace('_', ' ').title()}:</strong></div>
                            <div>{value}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Display next steps
                if st.session_state.human_response == "callback":
                    st.warning("The customer will be contacted for additional information. A callback is scheduled.")
                else:
                    st.warning("The customer should be informed that their activation requires additional processing time.")
        
        # Show summary metrics
        st.markdown("### Resolution Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            resolution_time = random.randint(15, 120) if st.session_state.issue_resolved else random.randint(30, 180)
            st.metric("Resolution Time", f"{resolution_time} sec", 
                     delta=f"-{random.randint(70, 85)}%" if st.session_state.issue_resolved else f"-{random.randint(40, 60)}%", 
                     delta_color="normal", help="Compared to manual process average of 180 seconds")
                     
        with col2:
            human_time = random.randint(0, 90) if st.session_state.human_intervention else 0
            st.metric("Human Intervention Time", f"{human_time} sec",
                     delta=None)
        
        with col3:
            automated_percentage = 100 if not st.session_state.human_intervention else int((resolution_time - human_time) / resolution_time * 100)
            st.metric("Automation Percentage", f"{automated_percentage}%",
                     delta=f"+{automated_percentage}%" if automated_percentage > 0 else None,
                     delta_color="normal")
        
        # Add option to return to start
        if st.button("Process New Request"):
            reset_simulation()
            st.rerun()

# Add footer
st.markdown("---")
st.markdown("""
<div style="text-align: center">
    <p>Telecom Activation Resolution System - AI-powered activation management</p>
    <p><small>This is a simulation for demonstration purposes only</small></p>
</div>
""", unsafe_allow_html=True)