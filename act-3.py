# !pip install langgraph langchain-core sqlalchemy

import sqlite3
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama

# ========== Enhanced Database Setup ==========
conn = sqlite3.connect('telecom.db')
cursor = conn.cursor()

# Create tables with additional status tracking
cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        customer_id TEXT,
        activation_status TEXT CHECK(activation_status IN ('not_sent', 'sent', 'pending', 'failed')),
        esim_status TEXT CHECK(esim_status IN ('active', 'failed', 'reprovisioned')),
        switch_status TEXT CHECK(switch_status IN ('ok', 'error', 'reconfigured')),
        issue_type TEXT,
        last_modified DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS fallouts (
        fallout_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT,
        resolution_type TEXT,
        status TEXT CHECK(status IN ('open', 'resolved', 'validation_failed')),
        validation_attempts INTEGER DEFAULT 0,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# Sample data with realistic scenarios
orders = [
    ('ORD123', 'CUST001', 'not_sent', 'active', 'ok', 'activation_issue'),
    ('ORD456', 'CUST002', 'sent', 'failed', 'ok', 'esim_issue'),
    ('ORD789', 'CUST003', 'sent', 'active', 'error', 'switch_issue'),
    ('ORD999', 'CUST004', 'sent', 'active', 'ok', 'unknown_issue'),
    ('ORD555', 'CUST005', 'sent', 'failed', 'error', 'complex_issue')
]

cursor.executemany('INSERT INTO orders VALUES (?,?,?,?,?,?)', orders)
conn.commit()

# ========== Enhanced Telecom Tools ==========
class TelecomTools:
    @staticmethod
    def get_full_status(order_id: str) -> dict:
        cursor.execute('''
            SELECT activation_status, esim_status, switch_status 
            FROM orders WHERE order_id = ?
        ''', (order_id,))
        result = cursor.fetchone()
        return {
            'activation': result[0],
            'esim': result[1],
            'switch': result[2]
        }

    @staticmethod
    def mark_for_resubmission(order_id: str) -> str:
        cursor.execute('''
            UPDATE orders 
            SET activation_status = 'pending', 
                last_modified = CURRENT_TIMESTAMP 
            WHERE order_id = ?
        ''', (order_id,))
        conn.commit()
        return f"Order {order_id} marked for resubmission"

    @staticmethod
    def reprovision_esim(order_id: str) -> str:
        cursor.execute('''
            UPDATE orders 
            SET esim_status = 'reprovisioned',
                last_modified = CURRENT_TIMESTAMP 
            WHERE order_id = ?
        ''', (order_id,))
        conn.commit()
        return f"eSIM reprovisioned for {order_id}"

    @staticmethod
    def reprovision_switch(order_id: str) -> str:
        cursor.execute('''
            UPDATE orders 
            SET switch_status = 'reconfigured',
                last_modified = CURRENT_TIMESTAMP 
            WHERE order_id = ?
        ''', (order_id,))
        conn.commit()
        return f"Switch reconfigured for {order_id}"

    @staticmethod
    def log_fallout(order_id: str, resolution_type: str):
        cursor.execute('''
            INSERT INTO fallouts (order_id, resolution_type, status)
            VALUES (?, ?, 'open')
        ''', (order_id, resolution_type))
        conn.commit()

# ========== Enhanced Agent State ==========
class AgentState(TypedDict):
    order_id: str
    problem: str
    resolution: Annotated[str, "Resolution details"]
    next_step: Literal["resubmission", "esim", "switch", "human", "validation", "completed"]
    validation_result: Annotated[str, "Validation outcome"]
    retry_count: int

# Initialize model
model = ChatOllama(model="llama2", temperature=0.2)

# ========== Master Agent with LLM Reasoning ==========
master_prompt = ChatPromptTemplate.from_messages([
    ("system", """Analyze telecom order {order_id} issues and route appropriately.
    
    Current Status:
    Activation: {activation_status}
    eSIM: {esim_status}
    Switch: {switch_status}
    
    Consider historical data and system dependencies. Provide detailed reasoning before final decision.
    """),
    ("user", "Respond ONLY with format:\nReasoning: <analysis>\nDecision: [resubmission/esim/switch/human]")
])

def master_agent(state: AgentState):
    tools = TelecomTools()
    order_id = state["order_id"]
    
    status = tools.get_full_status(order_id)
    tools.log_fallout(order_id, "initial_detection")
    
    response = model.invoke(master_prompt.format(
        order_id=order_id,
        activation_status=status['activation'],
        esim_status=status['esim'],
        switch_status=status['switch']
    ))
    
    # Parse LLM response
    reasoning, decision = "No reasoning provided", "human"
    if 'Decision:' in response.content:
        parts = response.content.split('Decision:')
        reasoning = parts[0].replace('Reasoning:', '').strip()
        decision = parts[1].strip().lower()[1:-1]  # Remove brackets
    
    return {
        "next_step": decision if decision in ["resubmission", "esim", "switch"] else "human",
        "problem": reasoning
    }

# ========== Validation Agent ==========
validation_prompt = ChatPromptTemplate.from_messages([
    ("system", """Validate resolution for {order_id}:
    
    Expected Fix: {expected_fix}
    Actual Status:
    Activation: {activation_status}
    eSIM: {esim_status}
    Switch: {switch_status}
    
    Determine if fix was successful. Consider system dependencies.
    Respond with: [success/retry/human]""")
])

def validation_agent(state: AgentState):
    tools = TelecomTools()
    order_id = state["order_id"]
    status = tools.get_full_status(order_id)
    
    response = model.invoke(validation_prompt.format(
        order_id=order_id,
        expected_fix=state["resolution"],
        activation_status=status['activation'],
        esim_status=status['esim'],
        switch_status=status['switch']
    ))
    
    decision = "human"  # default
    if ']' in response.content:
        decision = response.content.split(']')[0][-1].strip().lower()
    
    # Update fallout log
    cursor.execute('''
        UPDATE fallouts 
        SET validation_attempts = validation_attempts + 1,
            status = CASE WHEN ? = 'success' THEN 'resolved' ELSE 'validation_failed'
        WHERE order_id = ?
    ''', (decision, order_id))
    conn.commit()
    
    return {
        "next_step": "completed" if decision == "success" else "human",
        "validation_result": response.content
    }

# ========== Enhanced Specialized Agents ==========
def resubmission_agent(state: AgentState):
    tools = TelecomTools()
    order_id = state["order_id"]
    result = tools.mark_for_resubmission(order_id)
    return {"resolution": result, "next_step": "validation"}

def esim_agent(state: AgentState):
    tools = TelecomTools()
    order_id = state["order_id"]
    result = tools.reprovision_esim(order_id)
    return {"resolution": result, "next_step": "validation"}

def switch_agent(state: AgentState):
    tools = TelecomTools()
    order_id = state["order_id"]
    result = tools.reprovision_switch(order_id)
    return {"resolution": result, "next_step": "validation"}

# ========== Enhanced Human Review ==========
def human_review(state: AgentState):
    order_id = state["order_id"]
    print(f"\nHuman intervention needed for {order_id}")
    print(f"Issue: {state['problem']}")
    print(f"Validation result: {state.get('validation_result', '')}")
    
    action = input("Choose action: (1) Approve fix (2) Manual override (3) Escalate: ")
    cursor.execute('''
        UPDATE fallouts 
        SET status = CASE 
            WHEN ? = '1' THEN 'resolved' 
            ELSE 'validation_failed' 
        END
        WHERE order_id = ?
    ''', (action, order_id))
    conn.commit()
    
    return {"resolution": f"Human action: {action}", "next_step": "completed"}

# ========== Updated Workflow ==========
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("master", master_agent)
workflow.add_node("resubmission", resubmission_agent)
workflow.add_node("esim", esim_agent)
workflow.add_node("switch", switch_agent)
workflow.add_node("validation", validation_agent)
workflow.add_node("human", human_review)

# Set up edges
workflow.set_entry_point("master")

workflow.add_conditional_edges(
    "master",
    lambda state: state["next_step"],
    {
        "resubmission": "resubmission",
        "esim": "esim",
        "switch": "switch",
        "human": "human"
    }
)

# Connect agents to validation
for agent in ["resubmission", "esim", "switch"]:
    workflow.add_edge(agent, "validation")

# Validation outcomes
workflow.add_conditional_edges(
    "validation",
    lambda state: state["next_step"],
    {
        "completed": END,
        "human": "human"
    }
)

workflow.add_edge("human", END)

# Compile the graph
app = workflow.compile()

# ========== Enhanced Test Execution ==========
def run_test(order_id):
    print(f"\n🔍 Processing {order_id}")
    state = {"order_id": order_id, "retry_count": 0}
    
    for step in app.stream(state):
        print(f"\nSTEP: {step['next_step']}")
        print(f"RESOLUTION: {step.get('resolution', '')}")
        if 'validation_result' in step:
            print(f"VALIDATION: {step['validation_result']}")
        
        # Show current DB status
        status = TelecomTools.get_full_status(order_id)
        print(f"CURRENT STATUS: {status}")
    
    print("\nFINAL FALLOUT RECORD:")
    display(pd.read_sql(f"SELECT * FROM fallouts WHERE order_id = '{order_id}'", conn))
    print("="*50)

# Test cases
run_test("ORD123")  # Activation issue
run_test("ORD456")  # eSIM issue 
run_test("ORD789")  # Switch issue
run_test("ORD999")  # Human intervention
run_test("ORD555")  # Complex case

# Visualize
from IPython.display import Image
Image(app.get_graph().draw_mermaid_png())