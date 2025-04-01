import streamlit as st
import time
import random
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from PIL import Image
import re # For tokenization simulation

# --- Page Configuration (Must be the first Streamlit command) ---
st.set_page_config(
    page_title="AIVA - Polished Sim",
    page_icon="🌟", # Changed icon
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    /* General */
    .main { background-color: #f8f9fa; }
    .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
    h1, h2, h3 { color: #2c3e50; }
    /* Reduce space below main title/caption */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlockBorderWrapper"] {
        padding-top: 0.5rem; /* Adjust as needed */
    }


    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #e9ecef; padding-top: 1rem;}
    [data-testid="stSidebar"] h2 { color: #0d6efd; margin-bottom: 0; font-size: 1.5rem;} /* Sidebar Title */
    [data-testid="stSidebar"] .stMarkdown p { margin-bottom: 0.3rem; }
    [data-testid="stSidebar"] strong { color: #343a40; }
    [data-testid="stSidebar"] .stButton button { background-color: #6c757d; color: white; width: 100%; margin-top: 10px;} /* Reset Button */
    [data-testid="stSidebar"] .stButton button:hover { background-color: #dc3545; color: white; } /* Reset hover color */


    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 2px solid #dee2e6;}
    .stTabs [data-baseweb="tab"] {
        height: 45px; border-radius: 6px 6px 0 0; padding: 10px 16px; background-color: #e9ecef;
        border: 1px solid #dee2e6; border-bottom: none; color: #495057;
    }
    .stTabs [aria-selected="true"] { background-color: #0d6efd; color: white; border-color: #0d6efd; }
    /* Content padding - Reduced top padding within tabs */
    .stTabs [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] > div:first-child { padding-top: 10px; }

    /* Cards & Boxes */
    /* Card starts immediately, no extra top margin */
    .info-card { background-color: #ffffff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.08); margin-bottom: 15px; border: 1px solid #e0e0e0; margin-top: 0;}
    .analysis-box { background-color: #fdfdfe; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
    .analysis-title { font-weight: 600; color: #0d6efd; margin-bottom: 10px; font-size: 1.1em; }
    .summary-box { background-color: #e6f7ff; border: 1px solid #91d5ff; padding: 15px; border-radius: 8px; margin-bottom: 20px;}
    .nlu-step-box { border: 1px dashed #0d6efd; background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 10px; }

    /* Messages & Badges */
    .aiva-response-box { background-color: #e6f0ff; border-left: 5px solid #0d6efd; padding: 15px; border-radius: 5px; margin: 15px 0; }
    .user-input-box { background-color: #f1f3f5; border: 1px solid #dee2e6; padding: 10px; border-radius: 5px; margin-bottom: 15px; font-style: italic;}
    .transcript { background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px; border: 1px solid #dee2e6; font-style: italic; font-size: 0.95em; max-height: 150px; overflow-y: auto;}
    .badge { display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 0.8em; font-weight: 600; margin: 0 2px;}
    .badge-blue { background-color: #cfe2ff; color: #0d6efd; border: 1px solid #9ec5fe;}
    .badge-green { background-color: #d1e7dd; color: #155724; border: 1px solid #a3cfbb;}
    .badge-orange { background-color: #fff3cd; color: #856404; border: 1px solid #ffe69c;}
    .badge-red { background-color: #f8d7da; color: #721c24; border: 1px solid #f1aeb5;}
    .badge-grey { background-color: #e9ecef; color: #495057; border: 1px solid #ced4da;}
    .highlight { background-color: #fff3cd; padding: 0.1em 0.3em; border-radius: 3px; font-weight: bold; color: #856404;}

    /* Chat Simulation */
    .chat-container { background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-top: 15px; max-height: 400px; overflow-y: auto;}
    .chat-message { padding: 8px 12px; border-radius: 15px; margin-bottom: 8px; max-width: 85%; line-height: 1.4; font-size: 0.95em; }
    .user-message { background-color: #e9ecef; margin-left: auto; border-bottom-right-radius: 5px; color: #343a40;}
    .aiva-message { background-color: #cfe2ff; margin-right: auto; border-bottom-left-radius: 5px; color: #0a58ca;}
    .message-time { font-size: 0.75em; color: #6c757d; text-align: right; margin-top: 3px; }

    /* Buttons & Inputs */
    .stButton button { border-radius: 20px; padding: 8px 20px; font-weight: 500; border: none; transition: all 0.2s; }
    .stButton button:hover { filter: brightness(110%); }
    /* Primary Button Color */
    .stButton button:not(:hover) { background-color: #0d6efd; color: white; }

    /* Expander */
    .stExpander { border: 1px solid #dee2e6; border-radius: 8px; background-color: #ffffff; margin-bottom: 15px; }
    .stExpander header { font-weight: 600; color: #0d6efd;}

    /* Progress */
    .stProgress > div > div > div > div { background-color: #0d6efd; } /* Progress bar color */

    /* Icons */
    .icon { font-size: 1.2em; margin-right: 5px; vertical-align: middle; }

</style>
""", unsafe_allow_html=True)


# --- Helper Functions ---

# Simplified processing simulation
def show_processing_simple(label, steps=5, key_suffix=""):
    # Use st.spinner for a cleaner look
    with st.spinner(f"⚙️ {label}..."):
        time.sleep(random.uniform(0.1, 0.3) * steps / 5)
    return True

# Chat message function (no change needed)
def chat_message(content, sender="aiva", time_str=None):
    if time_str is None:
        time_str = time.strftime("%H:%M")
    message_class = "aiva-message" if sender == "aiva" else "user-message"
    return f"""
    <div class="chat-message {message_class}">
        {content}
        <div class="message-time">{time_str}</div>
    </div>
    """

# Function to reset the session state
def reset_session_state():
    keys_to_reset = [
        "issue_submitted_any", "submitted_modality", "submitted_issue_text",
        "simulated_transcript", "is_recording_cust", "audio_stopped",
        "customer_input_method", "cust_rating", "cust_final_reply",
        # Add any other state keys used if necessary
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
    # Re-initialize defaults
    st.session_state.issue_submitted_any = False
    st.session_state.submitted_modality = "N/A"
    st.session_state.submitted_issue_text = ""

# --- Sample Data ---
customer_data = { "name": "Sarah Parker", "phone": "785-321-4690", "customer_since": "2 years", "tier": "Premium", "plan": "Unlimited Data & Talk", "monthly_bill": "$75.99", "last_payment": "March 15, 2025", "devices": "iPhone 15 Pro", "avg_data_usage": "15.3 GB/month"}
def generate_network_data():
    dates = pd.date_range(start='2025-03-01', end='2025-03-31', freq='D')
    speeds = [random.uniform(80, 120) for _ in range(25)] + [random.uniform(5, 20) for _ in range(len(dates) - 25)]
    random.shuffle(speeds)
    return pd.DataFrame({ 'Date': dates, 'Download Speed (Mbps)': speeds, 'Upload Speed (Mbps)': [s * random.uniform(0.1, 0.3) for s in speeds] })
network_df = generate_network_data()
audio_transcript_text = "I've been with Visible for two years now, and usually it's pretty good for the price. But lately, my data speeds have been absolutely terrible! I'm paying for unlimited data, but I can barely load a webpage, let alone stream a video. I've tried restarting my phone, toggling airplane mode, and even resetting my network settings, but nothing seems to help. And to top it off, I contacted support through the app three days ago, and I still haven't heard back! I'm starting to think about switching providers if this keeps up."
sample_issue_for_text = audio_transcript_text # Use the same text for the default text area input

intent_classification_results = { "Network Issue": 0.78, "Billing Complaint": 0.12, "Service Quality": 0.08 }
context_enrichment_results = { "Customer Sentiment": "Negative (0.82)", "Issue Priority": "High", "Previous Issues": "None (6mo)", "Churn Risk": "Medium (0.65)", "Area Network Status": "Maintenance MNT-2345", "Device Compatible": "✅ Yes" }
agent_assignment = { "Agent": "AIVA-Network-Pro", "Type": "AI", "Confidence": 0.95 }
resolution_plan_summary = "Diagnose line > Check config > Apply remote fix > Offer credit > Schedule follow-up."
resolution_plan_detailed = [ "Acknowledge & Empathize", "Verify Account", "Check Area Network Status", "Run Remote Diagnostics", "Identify Config Error", "Trigger Re-provisioning", "Confirm Resolution", "Apply Compensation", "Offer Follow-up", "Log & Update Record" ]
execution_steps = ["Running Diagnostics", "Applying Config Fix", "Processing Compensation", "Logging & Closing"] # Define execution steps for backend


# --- Initialize Session State ---
if "issue_submitted_any" not in st.session_state: st.session_state.issue_submitted_any = False
if "submitted_modality" not in st.session_state: st.session_state.submitted_modality = "N/A"
if "submitted_issue_text" not in st.session_state: st.session_state.submitted_issue_text = ""
if "simulated_transcript" not in st.session_state: st.session_state.simulated_transcript = ""
if "is_recording_cust" not in st.session_state: st.session_state.is_recording_cust = False
if "audio_stopped" not in st.session_state: st.session_state.audio_stopped = False


# --- Sidebar ---
with st.sidebar:
    st.markdown("## VZ Inc.")
    st.markdown("**AIVA Dashboard**")
    st.caption(f"AI Virtual Assistant | {time.strftime('%a, %b %d, %Y')}")
    st.markdown("---")
    view_mode = st.radio("View Mode", ["Customer View", "Backend View"], horizontal=True)
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
    # Reset Button
    if st.button("🔁 Reset Simulation"):
        reset_session_state()
        st.success("Simulation Reset!")
        st.rerun() # Force immediate rerun after reset

    st.caption("© 2025 VZ Inc.")

# --- Main Content ---
st.title("🌟 AIVA Assistant") # Changed icon

# ====================================
#       CUSTOMER VIEW
# ====================================
if view_mode == "Customer View":

    tabs = st.tabs(["💬 Submit Issue", "📊 Resolution Status"])

    # --- Submit Issue Tab ---
    with tabs[0]:
        st.markdown('<div class="info-card">', unsafe_allow_html=True) # Wrap in card

        if not st.session_state.issue_submitted_any:
            st.markdown("### Report an Issue")
            st.write("Hello Sarah! How can AIVA help you today? Please describe your issue using one of the methods below.")

            input_method = st.radio("Choose input method:", ["Record Audio (Simulated)", "Upload Image", "Text"], horizontal=True, key="customer_input_method")

            # --- Audio Input ---
            if input_method == "Record Audio (Simulated)":
                st.markdown("##### <span class='icon'>🎤</span> Record Your Issue:", unsafe_allow_html=True)
                st.write("Click ▶️ to simulate recording, then ⏹️ to stop.")
                col_rec1, col_rec2 = st.columns([1, 5])
                with col_rec1:
                    if st.button("▶️ Start", key="cust_rec"):
                        st.session_state.is_recording_cust = True
                        st.session_state.audio_stopped = False
                        st.session_state.simulated_transcript = ""
                with col_rec2:
                    if st.button("⏹️ Stop", key="cust_stop"):
                        st.session_state.is_recording_cust = False
                        st.session_state.audio_stopped = True
                        st.session_state.simulated_transcript = audio_transcript_text

                if st.session_state.get('is_recording_cust', False):
                    st.markdown("🔴 Recording... `[-------||| pulsating |||-------]`")

                if st.session_state.get('audio_stopped', False):
                     st.markdown(f"""<div class="transcript"><strong>Simulated Transcript:</strong><br>{st.session_state.simulated_transcript}</div>""", unsafe_allow_html=True)
                     if st.button("Submit Audio Transcript", key="customer_submit_audio"):
                        if show_processing_simple("Processing audio transcript", 4, "audio"): # Check if processing successful
                            st.session_state.issue_submitted_any = True
                            st.session_state.submitted_issue_text = st.session_state.simulated_transcript
                            st.session_state.submitted_modality = "Audio"
                            st.rerun()

            # --- Image Input ---
            elif input_method == "Upload Image":
                st.markdown("##### <span class='icon'>📷</span> Upload Screenshot/Photo:", unsafe_allow_html=True)
                uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "png", "jpeg"], key="customer_img_upload", label_visibility="collapsed")
                if uploaded_file is not None:
                    try:
                        image = Image.open(uploaded_file)
                        st.image(image, caption="Uploaded Image Preview", width=250)
                        if st.button("Submit Image", key="customer_submit_img"):
                            if show_processing_simple("Analyzing image", 5, "img"):
                                extracted_text_sim = "Speed Test: 2.1 Mbps down / 0.8 Mbps up"
                                st.session_state.issue_submitted_any = True
                                st.session_state.submitted_issue_text = f"Image Uploaded. OCR: '{extracted_text_sim}'"
                                st.session_state.submitted_modality = "Image"
                                st.rerun()
                    except Exception as e:
                        st.error(f"Error processing image: {e}")

            # --- Text Input ---
            elif input_method == "Text":
                st.markdown("##### <span class='icon'>⌨️</span> Describe Your Issue:", unsafe_allow_html=True)
                text_input = st.text_area("Please provide details:", sample_issue_for_text, height=120, key="customer_text_input", label_visibility="collapsed")
                if st.button("Submit Text Description", key="customer_submit_text"):
                    if show_processing_simple("Processing text", 3, "text"):
                        st.session_state.issue_submitted_any = True
                        st.session_state.submitted_issue_text = text_input
                        st.session_state.submitted_modality = "Text"
                        st.rerun()

        # --- Show AIVA interaction AFTER submission ---
        else:
            st.markdown("### 💬 AIVA is Assisting You")
            st.markdown(f"""
            <div class="user-input-box">
                <strong>Your Issue ({st.session_state.submitted_modality}):</strong><br>
                "{st.session_state.submitted_issue_text[:200]}{'...' if len(st.session_state.submitted_issue_text)>200 else ''}"
            </div>
            """, unsafe_allow_html=True)

            st.markdown("##### Live Chat Simulation:")
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            # Chat messages... (kept as before)
            st.markdown(chat_message("Hello Sarah! Thanks for reaching out. I understand you're having trouble with slow data speeds.", "aiva", "10:05"), unsafe_allow_html=True)
            st.markdown(chat_message("That sounds frustrating. Let me check your account and the network status in your area right now.", "aiva", "10:05"), unsafe_allow_html=True)
            st.markdown(chat_message("Okay, I see your Premium plan details and confirm recent maintenance (MNT-2345) nearby.", "aiva", "10:06"), unsafe_allow_html=True)
            st.markdown(chat_message("Running diagnostics on your connection now... please wait a moment.", "aiva", "10:06"), unsafe_allow_html=True)
            st.markdown(chat_message("Diagnostics complete. I found a network configuration mismatch likely caused by the maintenance.", "aiva", "10:08"), unsafe_allow_html=True)
            st.markdown(chat_message("Good news! I've applied a remote fix to correct your line configuration. Your speeds should improve within the next ~30 minutes.", "aiva", "10:09"), unsafe_allow_html=True)
            st.markdown(chat_message("For the inconvenience, I've also added a 10% credit to your next bill.", "aiva", "10:09"), unsafe_allow_html=True)
            st.markdown(chat_message("Is there anything else I can help with today?", "aiva", "10:10"), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True) # End chat container

            st.markdown("##### Your Reply:")
            user_reply = st.text_input("Reply to AIVA (Optional)", key="cust_final_reply", label_visibility="collapsed")
            col_reply, col_rate = st.columns([3, 2])
            with col_reply:
                if st.button("Send Reply", key="cust_send_reply"):
                    if user_reply: st.success("Reply sent!")
            with col_rate:
                 rating = st.radio("Rate AIVA:", ["👍 Good", "👌 Okay", "👎 Bad"], horizontal=True, key="cust_rating", index=None)
                 if rating: st.success("Thanks for the feedback!")

        st.markdown('</div>', unsafe_allow_html=True) # End info card

    # --- Resolution Status Tab ---
    with tabs[1]:
        st.markdown('<div class="info-card">', unsafe_allow_html=True) # Wrap in card
        st.markdown("### 📊 Issue Resolution Status")

        if st.session_state.issue_submitted_any:
            st.markdown(f"""
            <div class="summary-box">
                <strong>Case Summary (Ref: #789123)</strong><br>
                <span class="badge badge-red">Network Speed Issue</span> reported via <span class="badge badge-blue">{st.session_state.submitted_modality}</span><br>
                <strong>Status:</strong> <span class="badge badge-green">✔️ Resolved</span><br>
                <strong>Resolution:</strong> Remote Configuration Fix Applied<br>
                <strong>Next Step:</strong> Follow-up Check Scheduled
            </div>
            """, unsafe_allow_html=True)
            with st.expander("View Network Performance Chart"):
                # Chart code... (kept as before)
                st.markdown("##### Network Speed Trend (Last 30 Days)")
                fig_network = go.Figure()
                fig_network.add_trace(go.Scatter(x=network_df['Date'], y=network_df['Download Speed (Mbps)'], mode='lines', name='Download', line=dict(color='#0d6efd')))
                issue_start_date = pd.to_datetime('2025-03-26'); issue_end_date = pd.to_datetime('2025-03-31')
                fig_network.add_vrect(x0=issue_start_date, x1=issue_end_date, fillcolor="rgba(255, 193, 7, 0.2)", line_width=0, annotation_text="Slowdown", annotation_position="top left")
                fig_network.update_layout( height=300, margin=dict(l=20, r=20, t=30, b=20), hovermode="x unified", yaxis_title="Mbps")
                st.plotly_chart(fig_network, use_container_width=True)

            with st.expander("View Resolution Steps Taken by AIVA"):
                st.markdown("##### Key Actions Log:")
                key_steps = ["Verified Account", "Ran Diagnostics", "Identified Config Error", "Applied Remote Fix", "Added Bill Credit", "Scheduled Follow-up"]
                for step in key_steps: st.markdown(f"✔️ {step}")
        else:
            st.info("No active issue submitted yet. Please report an issue first.")
        st.markdown('</div>', unsafe_allow_html=True) # End info card

# ====================================
#       BACKEND VIEW
# ====================================
else: # view_mode == "Backend View"
    st.markdown("## ⚙️ AIVA Backend Processing")
    st.caption("Simulated view of AI analysis and agentic workflow.")

    if not st.session_state.issue_submitted_any:
        st.warning("No issue submitted in Customer View yet.")
    else:
        # Wrap the entire backend content flow in the info-card to remove gap
        st.markdown('<div class="info-card">', unsafe_allow_html=True)

        # --- Step 1: Input & Initial Parse ---
        st.markdown("### 1. Input Received & Parsed")
        st.markdown(f"""
        <div class="user-input-box">
            <strong>Input via:</strong> <span class="badge badge-blue">{st.session_state.submitted_modality}</span> | <strong>Customer:</strong> {customer_data['name']}<br>
            <strong>Raw Input/Transcript:</strong><br>
            <div class="transcript">{st.session_state.submitted_issue_text}</div>
        </div>
        """, unsafe_allow_html=True)
        if show_processing_simple("Parsing/Transcribing Input", 2, "be_parse"): pass # Placeholder for simulation timing
        analysis_text = st.session_state.submitted_issue_text if st.session_state.submitted_issue_text else audio_transcript_text

        st.divider()

        # --- Step 2: NLU Pipeline ---
        st.markdown("### 2. NLU Pipeline Simulation")

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

        # --- Intent Mapping ---
        st.markdown("##### <span class='icon'>➡️</span> Step 2c: Intent Mapping", unsafe_allow_html=True)
        if show_processing_simple("Mapping Keywords to Intent", 2, "be_mapping"):
            st.markdown('<div class="nlu-step-box">', unsafe_allow_html=True)
            st.markdown(f"""
            - Keywords like <span class="highlight">data speeds</span>, <span class="highlight">terrible</span>, <span class="highlight">barely load</span> strongly indicate: **Network Issue** <span class="badge badge-green">High Confidence</span>
            - Keywords like <span class="highlight">support</span>, <span class="highlight">haven't heard back</span> indicate: **Service Complaint** <span class="badge badge-orange">Medium Confidence</span>
            - Keyword <span class="highlight">switching providers</span> indicates: **Churn Risk** <span class="badge badge-red">Flagged</span>
            """, unsafe_allow_html=True)
            st.markdown("**➡️ Primary Derived Intent:** <span class='badge badge-red'>Network Issue</span> (Confidence: 78%)", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.divider()

        # --- Step 3: Context, Agent & Plan ---
        st.markdown("### 3. Context, Agent Assignment & Planning")
        col_agent, col_plan = st.columns(2)
        with col_agent:
            st.markdown("##### Context & Agent")
            if show_processing_simple("Enriching Context", 1, "be_context"): pass
            if show_processing_simple("Selecting Agent", 1, "be_agent"): pass
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
                for i, step in enumerate(resolution_plan_detailed): st.markdown(f"{i+1}. {step}")

        st.divider()

        # --- Step 4: Execution & Outcome ---
        st.markdown("### 4. Execution & Outcome")
        st.markdown("Simulating agent executing the plan step-by-step:")

        # Improved execution steps display
        cols_exec = st.columns(len(execution_steps))
        for i, step_label in enumerate(execution_steps):
            with cols_exec[i]:
                # Run the simulation step
                show_processing_simple(step_label, random.randint(2,4), f"exec_{i}")
                # Display success with the label
                st.success(f"✔️ {step_label}")

        st.markdown("##### Final Outcome")
        st.markdown("""
        <div class="summary-box" style="background-color: #d1e7dd; border-color: #a3cfbb;">
            <strong><span class='icon'>🏁</span> Status:</strong> <span class="badge badge-green">Resolved</span> <br>
            <strong><span class='icon'>🛠️</span> Action Taken:</strong> Remote network re-configuration successful. <br>
            <strong><span class='icon'>💰</span> Compensation:</strong> 10% bill credit applied. <br>
            <strong><span class='icon'>➡️</span> Next Action:</strong> Automated follow-up check scheduled.
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True) # End info card