# -*- coding: utf-8 -*-
import streamlit as st
import time
import random
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from PIL import Image
import re
import datetime

# --- Page Configuration (Must be the first Streamlit command) ---
st.set_page_config(
    page_title="AIVA - Enhanced Sim",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
# Added styles for log formatting and follow-up case
st.markdown("""
<style>
    /* General */
    body { font-family: 'Inter', sans-serif; }
    .main { background-color: #f8f9fa; }
    .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
    h1, h2, h3 { color: #2c3e50; }
    h4 { color: #0d6efd; } /* Make H4 blue */
    h5 { color: #343a40; } /* Darken H5 */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlockBorderWrapper"] {
        padding-top: 0.5rem;
    }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #e9ecef; padding-top: 1rem;}
    [data-testid="stSidebar"] h2 { color: #0d6efd; margin-bottom: 0; font-size: 1.5rem;}
    [data-testid="stSidebar"] .stMarkdown p { margin-bottom: 0.3rem; }
    [data-testid="stSidebar"] strong { color: #343a40; }
    [data-testid="stSidebar"] .stButton button { background-color: #6c757d; color: white; width: 100%; margin-top: 10px; border-radius: 8px; }
    [data-testid="stSidebar"] .stButton button:hover { background-color: #dc3545; color: white; }
    [data-testid="stSidebar"] .stCaption { margin-top: auto; padding-top: 1rem; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 2px solid #dee2e6; }
    .stTabs [data-baseweb="tab"] {
        height: 45px; border-radius: 6px 6px 0 0; padding: 10px 16px; background-color: #e9ecef;
        border: 1px solid #dee2e6; border-bottom: none; color: #495057;
    }
    .stTabs [aria-selected="true"] { background-color: #0d6efd; color: white; border-color: #0d6efd; }
    .stTabs [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] > div:first-child { padding-top: 15px; }

    /* Cards & Boxes */
    .info-card { background-color: #ffffff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.08); margin-bottom: 15px; border: 1px solid #e0e0e0; margin-top: 0; }
    .analysis-box { background-color: #fdfdfe; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
    .analysis-title { font-weight: 600; color: #0d6efd; margin-bottom: 10px; font-size: 1.1em; }
    .summary-box { background-color: #e6f7ff; border: 1px solid #91d5ff; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
    .follow-up-box { background-color: #fff3cd; border: 1px solid #ffe69c; padding: 15px; border-radius: 8px; margin-bottom: 20px; } /* Yellow for follow-up */
    .nlu-step-box { border: 1px dashed #0d6efd; background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 10px; } /* Reverted padding */

    /* Messages & Badges */
    .aiva-response-box { background-color: #e6f0ff; border-left: 5px solid #0d6efd; padding: 15px; border-radius: 5px; margin: 15px 0; }
    .user-input-box { background-color: #f1f3f5; border: 1px solid #dee2e6; padding: 10px; border-radius: 5px; margin-bottom: 15px; font-style: italic; }
    .transcript { background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px; border: 1px solid #dee2e6; font-style: italic; font-size: 0.95em; max-height: 150px; overflow-y: auto; }
    .badge { display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 0.8em; font-weight: 600; margin: 0 2px; }
    .badge-blue { background-color: #cfe2ff; color: #0d6efd; border: 1px solid #9ec5fe; }
    .badge-green { background-color: #d1e7dd; color: #155724; border: 1px solid #a3cfbb; }
    .badge-orange { background-color: #fff3cd; color: #856404; border: 1px solid #ffe69c; }
    .badge-red { background-color: #f8d7da; color: #721c24; border: 1px solid #f1aeb5; }
    .badge-grey { background-color: #e9ecef; color: #495057; border: 1px solid #ced4da; }
    .highlight { background-color: #fff3cd; padding: 0.1em 0.3em; border-radius: 3px; font-weight: bold; color: #856404; }

    /* Chat Simulation */
    .chat-container { background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-top: 15px; max-height: 400px; overflow-y: auto; }
    .chat-message { padding: 8px 12px; border-radius: 15px; margin-bottom: 8px; max-width: 85%; line-height: 1.4; font-size: 0.95em; }
    .user-message { background-color: #e9ecef; margin-left: auto; border-bottom-right-radius: 5px; color: #343a40; }
    .aiva-message { background-color: #cfe2ff; margin-right: auto; border-bottom-left-radius: 5px; color: #0a58ca; }
    .message-time { font-size: 0.75em; color: #6c757d; text-align: right; margin-top: 3px; }

    /* Interaction Log Formatting */
    .log-container { background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-top: 10px; max-height: 400px; overflow-y: auto; font-family: monospace; font-size: 0.9em; }
    .log-entry { padding: 5px 8px; margin-bottom: 3px; border-radius: 4px; line-height: 1.5; word-wrap: break-word; /* Ensure long messages wrap */ }
    .log-entry-AIVA { background-color: #e6f0ff; }
    .log-entry-CUSTOMER { background-color: #f1f3f5; }
    .log-entry-SYSTEM { background-color: #e9ecef; font-style: italic; color: #6c757d; }
    .log-timestamp { font-weight: bold; color: #0d6efd; margin-right: 10px; display: inline-block; /* Prevent wrapping */ white-space: nowrap; }
    .log-sender { font-weight: bold; margin-right: 5px; display: inline-block; }
    .log-sender-AIVA { color: #0a58ca; }
    .log-sender-CUSTOMER { color: #343a40; }
    .log-sender-SYSTEM { color: #6c757d; }
    .log-message { display: inline; } /* Allow message to wrap */


    /* Buttons & Inputs */
    .stButton button { border-radius: 20px; padding: 8px 20px; font-weight: 500; border: none; transition: all 0.2s; }
    .stButton button:hover { filter: brightness(110%); }
    .stButton:not([data-testid="stSidebar"] .stButton) button:not(:hover) { background-color: #0d6efd; color: white; }
    .stButton[key="cust_rec"] button, .stButton[key="cust_stop"] button { background-color: #6c757d; color: white; }
    .stButton[key="cust_rec"] button:hover, .stButton[key="cust_stop"] button:hover { background-color: #5a6268; }
    /* Feedback submit button */
    .stButton[key="submit_feedback_button"] button { background-color: #198754; color: white; } /* Green */
    .stButton[key="submit_feedback_button"] button:hover { background-color: #157347; }


    /* Expander */
    .stExpander { border: 1px solid #dee2e6; border-radius: 8px; background-color: #ffffff; margin-bottom: 15px; }
    .stExpander header { font-weight: 600; color: #0d6efd; }

    /* Progress */
    .stProgress > div > div > div > div { background-color: #0d6efd; }

    /* Icons */
    .icon { font-size: 1.2em; margin-right: 5px; vertical-align: middle; }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---

def get_current_time():
    """Gets the current timestamp for logging."""
    return datetime.datetime.now().strftime("%H:%M:%S")

def generate_case_id(prefix="CASE"):
    """Generates a random alphanumeric case ID."""
    return f"{prefix}-{random.randint(100000, 999999)}"

# Simplified processing simulation
def show_processing_simple(label, steps=5, key_suffix=""):
    """Displays a spinner for a short duration to simulate processing."""
    with st.spinner(f"⚙️ {label}..."):
        time.sleep(random.uniform(0.1, 0.3) * steps / 5)
    return True

# Chat message function
def chat_message(content, sender="aiva", time_str=None):
    """Formats a chat message with appropriate styling."""
    if time_str is None:
        time_str = get_current_time()[:5] # Just HH:MM for chat display
    message_class = "aiva-message" if sender == "aiva" else "user-message"
    # Basic sanitization for HTML display
    safe_content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"""
    <div class="chat-message {message_class}">
        {safe_content}
        <div class="message-time">{time_str}</div>
    </div>
    """

# Function to add log entry (stores structured data)
def add_log_entry(sender, message):
    """Adds a structured entry to the interaction log."""
    if "interaction_log" not in st.session_state:
        st.session_state.interaction_log = []
    timestamp = get_current_time()
    # Ensure sender is uppercase for consistency
    sender_upper = sender.upper()
    st.session_state.interaction_log.append({"timestamp": timestamp, "sender": sender_upper, "message": message})

# Function to format a single log entry for HTML display (used in Backend View)
def format_log_entry_html(log_entry):
    """Formats a single structured log entry into an HTML string for display."""
    sender = log_entry.get('sender', 'UNKNOWN') # Use .get for safety
    timestamp = log_entry.get('timestamp', '??:??:??')
    message = log_entry.get('message', '')

    sender_class = f"log-sender-{sender}"
    entry_class = f"log-entry-{sender}"

    # Basic sanitization for HTML display
    safe_message = message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Ensure the HTML structure is simple and valid
    return f"""
    <div class="log-entry {entry_class}">
        <span class="log-timestamp">{timestamp}</span>
        <span class="log-sender {sender_class}">{sender}:</span>
        <span class="log-message">{safe_message}</span>
    </div>
    """

# Function to reset the session state
def reset_session_state():
    """Clears specific keys from the session state and reinitializes defaults."""
    keys_to_reset = [
        "issue_submitted_any", "submitted_modality", "submitted_issue_text",
        "simulated_transcript", "is_recording_cust", "audio_stopped",
        "customer_input_method", "cust_rating", "cust_final_reply",
        "human_agent_requested", "interaction_log", "case_escalated",
        "interaction_case_id", "follow_up_case_id", "human_agent_details",
        "human_agent_details_submitted", "cust_rating_value",
        "aiva_chat_logged", # Flag to prevent re-logging AIVA chat with delays
        "cust_feedback_text", # New for feedback comment
        "feedback_submitted" # Flag for feedback submission
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
    # Reinitialize defaults
    st.session_state.issue_submitted_any = False
    st.session_state.submitted_modality = "N/A"
    st.session_state.submitted_issue_text = ""
    st.session_state.human_agent_requested = None # None = choice not made, True = yes, False = no
    st.session_state.case_escalated = False # For potential future auto-escalation logic
    st.session_state.interaction_log = []
    st.session_state.interaction_case_id = None
    st.session_state.follow_up_case_id = None
    st.session_state.human_agent_details = ""
    st.session_state.human_agent_details_submitted = False
    st.session_state.cust_rating_value = None
    st.session_state.aiva_chat_logged = False
    st.session_state.cust_feedback_text = "" # Store the text feedback
    st.session_state.feedback_submitted = False


# --- Sample Data ---
customer_data = {
    "name": "Sarah Parker",
    "phone": "785-321-4690",
    "customer_since": "2 years",
    "tier": "Premium",
    "plan": "Unlimited Data & Talk",
    "monthly_bill": "$75.99",
    "last_payment": "March 15, 2025",
    "devices": "iPhone 15 Pro",
    "avg_data_usage": "15.3 GB/month"
}

def generate_network_data():
    """Generates sample network speed data with a simulated dip."""
    dates = pd.date_range(start='2025-03-01', end='2025-03-31', freq='D')
    normal_speeds = [random.uniform(80, 120) for _ in range(25)]
    dip_speeds = [random.uniform(5, 20) for _ in range(len(dates) - 25)]
    speeds = normal_speeds + dip_speeds
    random.shuffle(speeds[:25])
    random.shuffle(speeds[25:])
    return pd.DataFrame({
        'Date': dates,
        'Download Speed (Mbps)': speeds,
        'Upload Speed (Mbps)': [s * random.uniform(0.1, 0.3) for s in speeds]
    })

network_df = generate_network_data()

# Use the provided sample data structures directly
audio_transcript_text = ("I've been with Visible for two years now, and usually it's pretty good for the price. "
"This data speed issue has now become a serious problem. I'm paying for unlimited data, but I can barely load a webpage or stream a video. "
"I've tried restarting my phone, toggling airplane mode and even resetting my network settings. "
"And to add, I contacted support through the app three days ago, and I still haven't heard back! "
"I'm starting to consider switching providers if this persists.")

sample_issue_for_text = audio_transcript_text

intent_classification_results = {
    "Network Issue": 0.78,
    "Billing Complaint": 0.12,
    "Service Quality": 0.08,
    "Churn Intent": 0.65 # Added based on context enrichment
}

context_enrichment_results = {
    "Customer Sentiment": "Negative (0.82)",
    "Issue Priority": "High",
    "Previous Issues": "None (6mo)",
    "Churn Risk": "Medium (0.65)", # Matches Churn Intent score
    "Area Network Status": "Maintenance MNT-2345",
    "Device Compatible": "✅ Yes"
}

agent_assignment = {
    "Agent": "AIVA-Network-Pro",
    "Type": "AI",
    "Confidence": 0.95
}

resolution_plan_summary = "Diagnose line > Check config > Apply remote fix > Offer credit > Schedule follow-up."
resolution_plan_detailed = [
    "Acknowledge & Empathize", "Verify Account", "Check Area Network Status",
    "Run Remote Diagnostics", "Identify Config Error", "Trigger Re-provisioning",
    "Confirm Resolution", "Apply Compensation", "Offer Follow-up", "Log & Update Record"
]
execution_steps = ["Running Diagnostics", "Applying Config Fix", "Processing Compensation", "Logging & Closing"]

# --- Initialize Session State ---
if "issue_submitted_any" not in st.session_state:
    reset_session_state()

# --- Sidebar ---
with st.sidebar:
    st.markdown("## VZ Inc.")
    st.markdown("**AIVA Dashboard**")
    st.caption(f"AI Virtual Assistant | {datetime.datetime.now().strftime('%a, %b %d, %Y')}")
    st.markdown("---")
    view_mode = st.radio("View Mode", ["Customer View", "Backend View"], horizontal=True, key="view_mode_radio")
    st.markdown("---")
    st.markdown("#### Customer Info")
    st.markdown(f"**Name:** {customer_data['name']}")
    st.markdown(f"**Phone:** {customer_data['phone']}")
    st.markdown(f"**Tier:** <span class='badge badge-orange'>{customer_data['tier']}</span>", unsafe_allow_html=True)
    st.markdown(f"**Plan:** {customer_data['plan']}")
    st.markdown(f"**Member Since:** {customer_data['customer_since']}")
    st.markdown("---")
    if view_mode == "Backend View":
        st.markdown("#### System Status")
        statuses = ["API OK ✅", "NLU OK ✅", "CRM OK ✅", "Agents Ready ✅"]
        st.markdown(" ".join([f"<span class='badge badge-grey'>{s}</span>" for s in statuses]), unsafe_allow_html=True)
        st.markdown("---")

    st.markdown('<div style="margin-top: 20px;">', unsafe_allow_html=True)
    if st.button("🔁 Reset Simulation"):
        reset_session_state()
        st.success("Simulation Reset!")
        time.sleep(1)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.caption("© 2025 VZ Inc.")

# --- Main Content ---
st.title("🌟 AIVA Assistant")

# ====================================
#        CUSTOMER VIEW
# ====================================
if view_mode == "Customer View":
    tabs = st.tabs(["💬 Submit Issue / Chat", "📊 Resolution Status"])

    # --- Submit Issue / Chat Tab ---
    with tabs[0]:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        if not st.session_state.issue_submitted_any:
            st.markdown("### Report an Issue")
            st.write(f"Hello {customer_data['name']}! How can AIVA help you today? Please describe your issue using one of the methods below.")

            input_method = st.radio("Choose input method:", ["Record Audio (Simulated)", "Upload Image", "Text"], horizontal=True, key="customer_input_method")

            # Common submission logic
            def handle_submission(modality, text):
                 if show_processing_simple(f"Processing {modality} input", 4 if modality == "Audio" else 3, modality.lower()):
                    st.session_state.issue_submitted_any = True
                    st.session_state.submitted_issue_text = text
                    st.session_state.submitted_modality = modality
                    # Generate Interaction Case ID here
                    st.session_state.interaction_case_id = generate_case_id("INT")
                    add_log_entry("SYSTEM", f"Interaction Case {st.session_state.interaction_case_id} created.")
                    # Log the actual customer input
                    add_log_entry("CUSTOMER", f"({modality}) {text}")
                    st.rerun()

            # --- Audio Input ---
            if input_method == "Record Audio (Simulated)":
                st.markdown("##### <span class='icon'>🎤</span> Record Your Issue:", unsafe_allow_html=True)
                st.write("Click ▶️ to simulate recording, then ⏹️ to stop.")
                col_rec1, col_rec2, col_rec3 = st.columns([1, 1, 4])
                with col_rec1:
                    if st.button("▶️ Start", key="cust_rec"):
                        st.session_state.is_recording_cust = True
                        st.session_state.audio_stopped = False
                        st.session_state.simulated_transcript = ""
                        st.rerun()
                with col_rec2:
                    if st.button("⏹️ Stop", key="cust_stop", disabled=not st.session_state.get('is_recording_cust', False)):
                        st.session_state.is_recording_cust = False
                        st.session_state.audio_stopped = True
                        st.session_state.simulated_transcript = audio_transcript_text
                        st.rerun()

                if st.session_state.get('is_recording_cust', False):
                    st.markdown("🔴 Recording... `[-------||| pulsating |||-------]`")
                if st.session_state.get('audio_stopped', False):
                    st.markdown(f"""<div class="transcript"><strong>Simulated Transcript:</strong><br>{st.session_state.simulated_transcript}</div>""", unsafe_allow_html=True)
                    if st.button("Submit Audio Transcript", key="customer_submit_audio"):
                         # Use the actual transcript text for submission
                         handle_submission("Audio", st.session_state.simulated_transcript)

            # --- Image Input ---
            elif input_method == "Upload Image":
                st.markdown("##### <span class='icon'>📷</span> Upload Screenshot/Photo:", unsafe_allow_html=True)
                uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "png", "jpeg"], key="customer_img_upload", label_visibility="collapsed")
                if uploaded_file is not None:
                    try:
                        image = Image.open(uploaded_file)
                        st.image(image, caption="Uploaded Image Preview", width=250)
                        if st.button("Submit Image", key="customer_submit_img"):
                            extracted_text_sim = "Speed Test: 2.1 Mbps down / 0.8 Mbps up"
                            submission_text = f"Image Uploaded. OCR: '{extracted_text_sim}'"
                            handle_submission("Image", submission_text)
                    except Exception as e:
                        st.error(f"Error processing image: {e}")

            # --- Text Input ---
            elif input_method == "Text":
                st.markdown("##### <span class='icon'>⌨️</span> Describe Your Issue:", unsafe_allow_html=True)
                text_input = st.text_area("Please provide details:", sample_issue_for_text, height=120, key="customer_text_input", label_visibility="collapsed")
                if st.button("Submit Text Description", key="customer_submit_text"):
                    if text_input:
                        handle_submission("Text", text_input)
                    else:
                        st.warning("Please enter your issue description before submitting.")

        else:
            # --- After Issue Submission ---
            st.markdown(f"### 💬 AIVA Assistance (Case: {st.session_state.interaction_case_id})")
            st.markdown(f"""
            <div class="user-input-box">
                <strong>Your Issue ({st.session_state.submitted_modality}):</strong><br>
                "{st.session_state.submitted_issue_text[:200]}{'...' if len(st.session_state.submitted_issue_text)>200 else ''}"
            </div>
            """, unsafe_allow_html=True)

            st.markdown("##### Live Chat Simulation:")

            # Live chat simulation messages (AIVA part)
            chat_messages_aiva = [
                f"Hello {customer_data['name']}! Thanks for reaching out regarding Case {st.session_state.interaction_case_id}. I understand you're having trouble with slow data speeds.",
                "That sounds frustrating. Let me check your account and your network status in your area right now.",
                f"I see your {customer_data['tier']} plan details and note a recent maintenance ({context_enrichment_results['Area Network Status']}) nearby.",
                "Running diagnostics on your connection now... please wait a moment.",
                "Diagnostics complete. Our analysis indicates a configuration mismatch likely due to the maintenance.",
                "Good news! I've applied a remote fix to correct your line configuration. Your speeds should improve within ~30 minutes.",
                "For the inconvenience, a 10% credit has been applied to your next bill.",
                "Would you still like to speak to a human agent for further assistance?"
            ]

            # --- CORRECTED: Add AIVA messages to log with delays if not already logged ---
            if not st.session_state.aiva_chat_logged:
                # Use an empty container to show messages appearing one by one
                chat_placeholder = st.empty()
                current_chat_html = ""
                # Display existing CUSTOMER message first
                for entry in filter(lambda x: x['sender'] == 'CUSTOMER', st.session_state.interaction_log):
                     current_chat_html += chat_message(entry['message'], sender=entry['sender'].lower(), time_str=entry['timestamp'][:5])

                with chat_placeholder.container():
                    st.markdown('<div class="chat-container" id="chat-container-dynamic">', unsafe_allow_html=True)
                    st.markdown(current_chat_html, unsafe_allow_html=True) # Show initial customer message
                    st.markdown('</div>', unsafe_allow_html=True)

                # Add AIVA messages with delays
                for i, msg in enumerate(chat_messages_aiva):
                    # Simulate delay - longer for diagnostics
                    delay = random.uniform(0.8, 1.5)
                    if "diagnostics" in msg.lower():
                        delay = random.uniform(2.0, 3.0)
                    elif "applied a remote fix" in msg.lower():
                         delay = random.uniform(1.5, 2.5)

                    time.sleep(delay)
                    add_log_entry("AIVA", msg) # This captures the timestamp *after* the delay

                    # Update the chat display dynamically
                    current_chat_html = ""
                    for entry in filter(lambda x: x['sender'] in ['CUSTOMER', 'AIVA'], st.session_state.interaction_log):
                         current_chat_html += chat_message(entry['message'], sender=entry['sender'].lower(), time_str=entry['timestamp'][:5])

                    # Update the placeholder content
                    with chat_placeholder.container():
                        st.markdown('<div class="chat-container" id="chat-container-dynamic">', unsafe_allow_html=True)
                        st.markdown(current_chat_html, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                st.session_state.aiva_chat_logged = True # Mark as logged
                st.rerun() # Rerun once after all messages are logged to finalize display

            else:
                # If already logged, just display the full chat history statically
                st.markdown('<div class="chat-container" id="chat-container-static">', unsafe_allow_html=True)
                chat_html = ""
                for entry in filter(lambda x: x['sender'] in ['CUSTOMER', 'AIVA'], st.session_state.interaction_log):
                    chat_html += chat_message(entry['message'], sender=entry['sender'].lower(), time_str=entry['timestamp'][:5])
                st.markdown(chat_html, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)


            # --- Human Agent Request Section ---
            st.markdown("---") # Separator
            st.markdown("##### Need More Help?")

            # State 1: Ask if human agent is needed
            if st.session_state.human_agent_requested is None:
                human_option = st.radio("Would you like to connect to a human agent?", ["No, AIVA resolved my issue.", "Yes, please connect me."], key="human_option", index=0)
                if st.button("Confirm Choice", key="confirm_human_choice"):
                    if "Yes" in human_option:
                        st.session_state.human_agent_requested = True # Mark intent
                    else:
                        st.session_state.human_agent_requested = False # Mark choice
                        add_log_entry("SYSTEM", "Customer confirmed issue resolved by AIVA.")
                    st.rerun()

            # State 2: Human agent requested, ask for details
            elif st.session_state.human_agent_requested is True and not st.session_state.human_agent_details_submitted:
                 st.info("You've requested to speak with a human agent. Please provide any additional details below that might help them understand your situation better.")
                 details_input = st.text_area("Additional details for the human agent (Optional):", key="human_agent_details_input", height=100)
                 if st.button("Submit Details & Proceed", key="submit_human_details"):
                     st.session_state.human_agent_details = details_input if details_input else "No additional details provided."
                     st.session_state.human_agent_details_submitted = True # Mark details as submitted
                     # Now generate follow-up case ID and log escalation with details
                     st.session_state.follow_up_case_id = generate_case_id("FLW")
                     add_log_entry("SYSTEM", f"Human agent requested by customer. Follow-up Case {st.session_state.follow_up_case_id} created.")
                     add_log_entry("CUSTOMER", f"(Details for Agent) {st.session_state.human_agent_details}")
                     st.rerun()

            # State 3: Human agent requested, details submitted
            elif st.session_state.human_agent_requested is True and st.session_state.human_agent_details_submitted:
                 st.markdown(f"""
                 <div class="aiva-response-box">
                     Thank you. Your request (Follow-up Case: {st.session_state.follow_up_case_id}) is being routed to a human agent along with your provided details. They will contact you shortly or review your case.
                 </div>
                 """, unsafe_allow_html=True)
                 st.markdown(f"""
                 <div class="user-input-box" style="font-style: normal;">
                     <strong>Details provided for agent:</strong><br>
                     "{st.session_state.human_agent_details}"
                 </div>
                 """, unsafe_allow_html=True)


            # --- CORRECTED: State 4: Human agent declined - Feedback Section ---
            elif st.session_state.human_agent_requested is False:
                 if not st.session_state.feedback_submitted:
                     st.markdown('<div class="aiva-response-box">Thank you for confirming! We appreciate your feedback. Please feel free to rate your experience with AIVA below.</div>', unsafe_allow_html=True)
                     st.markdown("##### Rate AIVA & Provide Feedback:")

                     # Rating Radio Buttons
                     rating_options = ["👍 Good", "👌 Okay", "👎 Bad"]
                     # Ensure rating is stored in session state
                     if 'cust_rating_value' not in st.session_state:
                         st.session_state.cust_rating_value = None # Initialize if not present

                     # --- CORRECTED: Radio button index handling ---
                     try:
                         # Find index if value exists, otherwise default to None (no selection)
                         current_rating_index = rating_options.index(st.session_state.cust_rating_value) if st.session_state.cust_rating_value in rating_options else None
                     except ValueError:
                         current_rating_index = None # Should not happen if initialized, but safety check

                     # Use a separate key for the widget to capture its current value
                     current_selection = st.radio(
                         "Rate your experience:",
                         rating_options,
                         horizontal=True,
                         key="cust_rating_widget", # Use a unique key for the widget itself
                         index=current_rating_index
                     )
                     # Update session state based on widget's current value *if* it changed
                     if current_selection != st.session_state.cust_rating_value:
                         st.session_state.cust_rating_value = current_selection
                         # No rerun needed here, just update the state variable

                     # Feedback Text Area
                     feedback_text = st.text_area("Additional Feedback (Optional):", key="cust_feedback_text_input", height=75)

                     # Submit Button
                     if st.button("Submit Feedback", key="submit_feedback_button"):
                         # Use the rating stored in session state
                         rating_to_log = st.session_state.cust_rating_value if st.session_state.cust_rating_value else "Not Rated"
                         # Use the current value from the text area widget
                         feedback_to_log = feedback_text if feedback_text else "No additional feedback."
                         # Store the text feedback in session state as well
                         st.session_state.cust_feedback_text = feedback_to_log

                         add_log_entry("SYSTEM", f"Customer Feedback - Rating: {rating_to_log}, Comment: {feedback_to_log}")
                         st.session_state.feedback_submitted = True
                         st.success("Thank you for your feedback!")
                         time.sleep(1.5)
                         st.rerun()
                 else:
                     # Show message after feedback is submitted
                     st.success("Thank you for your feedback!")


        st.markdown('</div>', unsafe_allow_html=True)  # End info card

    # --- Resolution Status Tab ---
    with tabs[1]:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Issue Resolution Status")
        if st.session_state.issue_submitted_any:
            # --- Main Interaction Case Summary ---
            status_badge = '<span class="badge badge-green">✔️ Resolved by AIVA</span>'
            resolution_text = "Remote Configuration Fix Applied"
            next_step = "Follow-up Check Scheduled"
            if st.session_state.human_agent_requested is True: # Check if escalation happened
                 status_badge = f'<span class="badge badge-orange">⏳ Escalated to Human Agent (See Follow-up Case {st.session_state.follow_up_case_id})</span>'
                 resolution_text = "AIVA applied initial fix. Awaiting human review."
                 next_step = "Human Agent Follow-up"
            elif st.session_state.human_agent_requested is False: # Check if declined
                 status_badge = '<span class="badge badge-green">✔️ Resolved by AIVA (Confirmed by Customer)</span>'

            st.markdown(f"""
            <div class="summary-box">
                <strong>Interaction Case Summary (ID: {st.session_state.interaction_case_id})</strong><br>
                <span class="badge badge-red">Network Speed Issue</span> reported via <span class="badge badge-blue">{st.session_state.submitted_modality}</span><br>
                <strong>Status:</strong> {status_badge}<br>
                <strong>AIVA Resolution Attempt:</strong> {resolution_text}<br>
                <strong>Next Step:</strong> {next_step}
            </div>
            """, unsafe_allow_html=True)

            # --- Follow-up Case Details (Conditional) ---
            if st.session_state.human_agent_requested is True:
                st.markdown("---")
                st.markdown(f"""
                <div class="follow-up-box">
                    <strong>Follow-up Case Details (ID: {st.session_state.follow_up_case_id})</strong><br>
                    <strong>Status:</strong> <span class="badge badge-orange">Pending Human Agent Review</span><br>
                    <strong>Reason for Escalation:</strong> Customer Request<br>
                    <strong>Original Interaction Ref:</strong> {st.session_state.interaction_case_id}<br>
                    <strong>Issue Summary:</strong> {st.session_state.submitted_issue_text[:150]}{'...' if len(st.session_state.submitted_issue_text)>150 else ''}<br>
                    <strong>Additional Details Provided:</strong><br>
                    <div class="transcript" style="max-height: 80px; font-style: normal;">{st.session_state.get("human_agent_details", "N/A")}</div>
                </div>
                """, unsafe_allow_html=True)


            # --- Network Chart (Always Visible After Submission) ---
            with st.expander("View Network Performance Chart"):
                st.markdown("##### Network Speed Trend (Last 30 Days)")
                fig_network = go.Figure()
                fig_network.add_trace(go.Scatter(x=network_df['Date'], y=network_df['Download Speed (Mbps)'], mode='lines+markers', name='Download', line=dict(color='#0d6efd'), marker=dict(size=4)))
                issue_start_date = network_df['Date'][25]
                issue_end_date = network_df['Date'].iloc[-1]
                fig_network.add_vrect(x0=issue_start_date, x1=issue_end_date, fillcolor="rgba(255, 193, 7, 0.2)", line_width=0, annotation_text="Reported Slowdown Period", annotation_position="top left")
                fig_network.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20), hovermode="x unified", yaxis_title="Mbps")
                st.plotly_chart(fig_network, use_container_width=True)

            # --- AIVA Steps (Always Visible After Submission) ---
            with st.expander("View Resolution Steps Taken by AIVA"):
                st.markdown("##### Key Actions Log (AIVA):")
                key_steps = ["Verified Account", "Ran Diagnostics", "Identified Config Error", "Applied Remote Fix", "Added Bill Credit", "Scheduled Follow-up"]
                for step in key_steps:
                    st.markdown(f"✔️ {step}")
                if st.session_state.human_agent_requested:
                    st.markdown("↪️ Escalated to Human Agent (Customer Request)")

        else:
            st.info("No active issue submitted yet. Please report an issue first.")
        st.markdown('</div>', unsafe_allow_html=True)  # End info card

# ====================================
#        BACKEND VIEW
# ====================================
else:  # view_mode == "Backend View"
    st.markdown("## ⚙️ AIVA Backend Processing")
    st.caption("Simulated view of AI analysis and agentic workflow.")
    if not st.session_state.issue_submitted_any:
        st.warning("No issue submitted in Customer View yet.")
    else:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown(f"### Interaction Case: {st.session_state.interaction_case_id}")
        # --- Step 1: Input & Initial Parse ---
        st.markdown("#### 1. Input Received & Parsed") # Use H4 for steps
        st.markdown(f"""
        <div class="user-input-box">
            <strong>Input via:</strong> <span class="badge badge-blue">{st.session_state.submitted_modality}</span> | <strong>Customer:</strong> {customer_data['name']} ({customer_data['tier']})<br>
            <strong>Raw Input/Transcript:</strong><br>
            <div class="transcript">{st.session_state.submitted_issue_text}</div>
        </div>
        """, unsafe_allow_html=True)
        if show_processing_simple("Parsing/Transcribing Input", 2, "be_parse"): pass
        analysis_text = st.session_state.submitted_issue_text if st.session_state.submitted_issue_text else audio_transcript_text

        st.divider()

        # --- Step 2: NLU Pipeline ---
        # --- REVERTED TO USER'S PREFERRED STRUCTURE for 2a, 2b, 2c ---
        st.markdown("#### 2. NLU Pipeline Simulation") # Use H4

        # --- Tokenization ---
        st.markdown("##### <span class='icon'>➡️</span> Step 2a: Tokenization", unsafe_allow_html=True)
        if show_processing_simple("Tokenizing Text", 1, "be_tokenize"):
            tokens = re.findall(r'\b\w+\b', analysis_text.lower())
            st.markdown('<div class="nlu-step-box">', unsafe_allow_html=True)
            st.markdown(f"**Sample Tokens:** `{', '.join(tokens[:15])}...` (Total: {len(tokens)} tokens)")
            st.markdown('</div>', unsafe_allow_html=True)

        # --- Keyword Extraction ---
        st.markdown("##### <span class='icon'>➡️</span> Step 2b: Keyword Extraction", unsafe_allow_html=True)
        if show_processing_simple("Extracting Keywords", 2, "be_keywords"):
            keywords = ["data speeds", "terrible", "unlimited data", "barely load", "stream video", "restarting", "airplane mode", "network settings", "support", "haven't heard back", "switching providers"]
            highlighted_text = analysis_text
            for kw in keywords:
                regex = re.compile(re.escape(kw), re.IGNORECASE)
                highlighted_text = regex.sub(f'<span class="highlight">{kw}</span>', highlighted_text)
            st.markdown('<div class="nlu-step-box">', unsafe_allow_html=True)
            st.markdown("**Identified Keywords/Phrases (Highlighted):**")
            st.markdown(f"<div class='transcript' style='max-height: 100px;'>{highlighted_text}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # --- Intent Mapping (Simplified structure as requested) ---
        st.markdown("##### <span class='icon'>➡️</span> Step 2c: Intent Mapping", unsafe_allow_html=True)
        if show_processing_simple("Mapping Keywords to Intent", 2, "be_mapping"):
            st.markdown('<div class="nlu-step-box">', unsafe_allow_html=True)
            # Simplified display based on user's earlier example structure
            st.markdown(f"""
             - Keywords like <span class="highlight">data speeds</span>, <span class="highlight">terrible</span>, <span class="highlight">barely load</span> strongly indicate: **Network Issue** <span class="badge badge-green">High Confidence</span>
             - Keywords like <span class="highlight">support</span>, <span class="highlight">haven't heard back</span> indicate: **Service Complaint** <span class="badge badge-orange">Medium Confidence</span>
             - Keyword <span class="highlight">switching providers</span> indicates: **Churn Risk** <span class="badge badge-red">Flagged</span>
             """, unsafe_allow_html=True)
            # Determine primary intent based on sample data score
            primary_intent = max(intent_classification_results, key=intent_classification_results.get)
            primary_score = intent_classification_results[primary_intent]
            st.markdown(f"**➡️ Primary Derived Intent:** <span class='badge badge-red'>{primary_intent}</span> (Confidence: {primary_score:.0%})", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.divider()

        # --- Step 3: Context, Agent & Plan ---
        # --- REVERTED TO USER'S PREFERRED STRUCTURE for 3 ---
        st.markdown("#### 3. Context, Agent Assignment & Planning") # Use H4
        col_agent, col_plan = st.columns(2)
        with col_agent:
            st.markdown("##### Context & Agent")
            if show_processing_simple("Enriching Context", 1, "be_context"): pass
            if show_processing_simple("Selecting Agent", 1, "be_agent"): pass
            # Display based on user's earlier example structure
            st.markdown(f"""
            <div class="analysis-box">
                    <strong><span class='icon'>👤</span> Assigned Agent:</strong> <span class="badge badge-blue">{agent_assignment['Agent']} ({agent_assignment['Type']})</span> <br>
                    <strong><span class='icon'>🚦</span> Issue Priority:</strong> <span class="badge badge-red">{context_enrichment_results['Issue Priority']}</span> <br>
                    <strong><span class='icon'>⚠️</span> Churn Risk:</strong> <span class="badge badge-orange">{context_enrichment_results['Churn Risk'].split('(')[0]}</span> <br>
                    <strong><span class='icon'>🔧</span> Area Status:</strong> {context_enrichment_results['Area Network Status']}
            </div>
            """, unsafe_allow_html=True)
        with col_plan:
            st.markdown("##### Resolution Plan")
            if show_processing_simple("Generating Plan", 1, "be_plan"): pass
            st.markdown(f"""
                 <div class="analysis-box">
                     <strong><span class='icon'>🗺️</span> Plan Summary:</strong><br> {resolution_plan_summary}
                 </div>
                 """, unsafe_allow_html=True)
            with st.expander("View Detailed Plan Steps"):
                for i, step in enumerate(resolution_plan_detailed):
                    st.markdown(f"{i+1}. {step}")
        st.divider()

        # --- Step 4: Execution & Outcome ---
        st.markdown("#### 4. Execution & Outcome") # Use H4
        st.markdown("Simulating agent executing the plan step-by-step:")
        exec_placeholder = st.empty()
        exec_status_html = "<div style='display: flex; gap: 10px; flex-wrap: wrap;'>"
        # Simulate steps
        steps_to_execute = execution_steps # Use the full list from sample data

        for i, step_label in enumerate(steps_to_execute):
             # Decide if step should run based on escalation (only affects compensation display later)
             run_step = True
             if "Compensation" in step_label and st.session_state.human_agent_requested is True:
                 run_step = False # Skip simulating compensation if escalated

             if run_step:
                 with exec_placeholder:
                     temp_html = exec_status_html + f"<div class='analysis-box' style='flex: 1; min-width: 150px;'><span class='icon'>⏳</span> Executing: {step_label}...</div>" + "</div>"
                     st.markdown(temp_html, unsafe_allow_html=True)
                     time.sleep(random.uniform(0.5, 1.0))
                 exec_status_html += f"<div class='analysis-box' style='flex: 1; min-width: 150px; background-color: #d1e7dd;'><span class='icon'>✔️</span> Completed: {step_label}</div>"
             else:
                  # Show skipped step if needed (optional)
                  # exec_status_html += f"<div class='analysis-box' style='flex: 1; min-width: 150px; background-color: #e9ecef;'><span class='icon'>⚪</span> Skipped: {step_label}</div>"
                  pass # Or just don't show skipped steps

        exec_placeholder.markdown(exec_status_html + "</div>", unsafe_allow_html=True)

        # --- CORRECTED: Final Outcome (Using User's Preferred Structure) ---
        st.markdown("##### Final Outcome")

        # Determine Status text and badge based on escalation state
        status_icon = "🏁"
        status_badge_class = "badge-green"
        status_text = "Resolved"
        if st.session_state.human_agent_requested is True:
            status_icon = "➡️"
            status_badge_class = "badge-orange"
            status_text = f"Escalated (Follow-up: {st.session_state.follow_up_case_id})"
        elif st.session_state.human_agent_requested is False:
            status_text = "Resolved (Confirmed by Customer)"

        # Use the structure from the user's earlier code example
        # Only the status line is dynamically changed here
        st.markdown(f"""
        <div class="summary-box" style="background-color: {'#fff3cd' if st.session_state.human_agent_requested else '#d1e7dd'}; border-color: {'#ffe69c' if st.session_state.human_agent_requested else '#a3cfbb'};">
            <strong><span class='icon'>{status_icon}</span> Status:</strong> <span class="badge {status_badge_class}">{status_text}</span> <br>
            <strong><span class='icon'>🛠️</span> Action Taken:</strong> Remote network re-configuration successful. <br>
            <strong><span class='icon'>💰</span> Compensation:</strong> 10% bill credit applied. <br>
            <strong><span class='icon'>➡️</span> Next Action:</strong> Automated follow-up check scheduled.
        </div>
        """, unsafe_allow_html=True)


        # --- CORRECTED: Churn Mitigation Section Title ---
        if "Medium" in context_enrichment_results['Churn Risk'] or "High" in context_enrichment_results['Churn Risk'] or st.session_state.human_agent_requested:
             # Renamed Title
             st.markdown("##### <span class='icon'>🛡️</span> Churn Mitigation Section", unsafe_allow_html=True)
             # Build the list items conditionally
             mitigation_items = [
                 "<li>✔️ Offered empathetic acknowledgement of the issue.</li>"
             ]
             if not st.session_state.human_agent_requested:
                 mitigation_items.append("<li>✔️ Applied proactive 10% bill credit for inconvenience.</li>")

             mitigation_items.append("<li>✔️ Clearly offered escalation path to a human agent.</li>")
             if st.session_state.human_agent_requested:
                 mitigation_items.append("<li>✔️ Captured additional customer details for human agent review.</li>")
             mitigation_items.append("<li>✔️ Scheduled automated follow-up network check.</li>")
             # Add feedback to mitigation list if submitted
             if st.session_state.get('feedback_submitted'):
                 rating_fb = st.session_state.cust_rating_value if st.session_state.cust_rating_value else "Not Rated"
                 # Fetch comment from state
                 comment_fb_text = st.session_state.get('cust_feedback_text', '')
                 comment_fb = f" Comment: \"{comment_fb_text}\"" if comment_fb_text and comment_fb_text != "No additional feedback." else ""
                 mitigation_items.append(f"<li>✔️ Logged customer feedback (Rating: {rating_fb}{comment_fb})</li>")


             mitigation_html = f"""
             <div class="analysis-box" style="background-color: #e6f0ff;">
                 The following actions were taken potentially impacting customer trust and churn risk:
                 <ul>
                     {''.join(mitigation_items)}
                 </ul>
             </div>
             """
             st.markdown(mitigation_html, unsafe_allow_html=True)


        # --- CORRECTED: Interaction Case Log (Alternative Rendering) ---
        st.divider()
        st.markdown(f"### Interaction Case Log (ID: {st.session_state.interaction_case_id})")
        st.markdown("<strong>Complete Interaction Flow (Internal View):</strong>", unsafe_allow_html=True)

        # Render each log entry individually using markdown within a styled container
        # Using st.markdown for each entry within the container div
        st.markdown('<div class="log-container">', unsafe_allow_html=True) # Apply container style
        if "interaction_log" in st.session_state and st.session_state.interaction_log:
            for entry_data in st.session_state.interaction_log:
                if isinstance(entry_data, dict):
                    # Generate HTML for this single entry
                    formatted_html_entry = format_log_entry_html(entry_data)
                    # Render this single entry using markdown
                    # This is the crucial part for rendering the HTML correctly
                    st.markdown(formatted_html_entry, unsafe_allow_html=True)
                else:
                    # Fallback for unexpected log format
                    st.markdown(f"<div class='log-entry log-entry-SYSTEM'>Error: Invalid log entry format - {str(entry_data)}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='log-entry log-entry-SYSTEM'>Log is empty.</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True) # Close container style


        st.markdown('</div>', unsafe_allow_html=True)  # End info card
