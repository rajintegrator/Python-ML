# !pip install langgraph langchain-core sqlalchemy

import sqlite3
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama  # Example using Ollama

# Create dummy SQLite database
conn = sqlite3.connect('telecom.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        customer_id TEXT,
        activation_status TEXT,
        esim_status TEXT,
        switch_status TEXT,
        issue_type TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS fallouts (
        fallout_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT,
        resolution_type TEXT,
        status TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# Sample data
orders = [
    ('ORD123', 'CUST001', 'not_sent', 'active', 'ok', 'activation_issue'),
    ('ORD456', 'CUST002', 'sent', 'failed', 'ok', 'esim_issue'),
    ('ORD789', 'CUST003', 'sent', 'active', 'error', 'switch_issue'),
    ('ORD999', 'CUST004', 'sent', 'active', 'ok', 'unknown_issue')
]

cursor.executemany('INSERT INTO orders VALUES (?,?,?,?,?,?)', orders)
conn.commit()

# Define tools for agents
class TelecomTools:
    @staticmethod
    def check_activation_status(order_id: str) -> str:
        cursor.execute('SELECT activation_status FROM orders WHERE order_id = ?', (order_id,))
        return cursor.fetchone()[0]

    @staticmethod
    def mark_for_resubmission(order_id: str) -> str:
        cursor.execute('UPDATE orders SET activation_status = "pending" WHERE order_id = ?', (order_id,))
        conn.commit()
        return f"Order {order_id} marked for resubmission"

    @staticmethod
    def check_esim_status(order_id: str) -> str:
        cursor.execute('SELECT esim_status FROM orders WHERE order_id = ?', (order_id,))
        return cursor.fetchone()[0]

    @staticmethod
    def reprovision_esim(order_id: str) -> str:
        cursor.execute('UPDATE orders SET esim_status = "reprovisioned" WHERE order_id = ?', (order_id,))
        conn.commit()
        return f"eSIM reprovisioned for {order_id}"

    @staticmethod
    def check_switch_status(order_id: str) -> str:
        cursor.execute('SELECT switch_status FROM orders WHERE order_id = ?', (order_id,))
        return cursor.fetchone()[0]

    @staticmethod
    def reprovision_switch(order_id: str) -> str:
        cursor.execute('UPDATE orders SET switch_status = "reconfigured" WHERE order_id = ?', (order_id,))
        conn.commit()
        return f"Switch reconfigured for {order_id}"

# Define agent states
class AgentState(TypedDict):
    order_id: str
    problem: str
    resolution: Annotated[str, "Final resolution details"]
    next_step: Literal["resubmission", "esim", "switch", "human", "completed"]

# Initialize model (using generic model)
model = ChatOllama(model="llama2", temperature=0)

# Master Agent
master_prompt = ChatPromptTemplate.from_messages([
    ("system", """Analyze the telecom order issue and route to proper resolver. Available data:
    Activation Status: {activation_status}
    eSIM Status: {esim_status}
    Switch Status: {switch_status}
    
    Respond ONLY with one of: resubmission, esim, switch, human"""),
])

def master_agent(state: AgentState):
    tools = TelecomTools()
    order_id = state["order_id"]
    
    activation_status = tools.check_activation_status(order_id)
    esim_status = tools.check_esim_status(order_id)
    switch_status = tools.check_switch_status(order_id)
    
    response = model.invoke(master_prompt.format(
        order_id=order_id,
        activation_status=activation_status,
        esim_status=esim_status,
        switch_status=switch_status
    ))
    
    return {"next_step": response.content.strip().lower()}

# Resubmission Agent
resubmission_prompt = ChatPromptTemplate.from_messages([
    ("system", """Handle activation not sent issue for order {order_id}. 
    Check activation status and resubmit if needed.""")
])

def resubmission_agent(state: AgentState):
    tools = TelecomTools()
    order_id = state["order_id"]
    
    current_status = tools.check_activation_status(order_id)
    if current_status == "not_sent":
        result = tools.mark_for_resubmission(order_id)
        return {"resolution": result, "next_step": "completed"}
    return {"resolution": "No action needed", "next_step": "completed"}

# eSIM Agent
esim_prompt = ChatPromptTemplate.from_messages([
    ("system", """Handle eSIM provisioning issues for order {order_id}. 
    Check eSIM status and reprovision if needed.""")
])

def esim_agent(state: AgentState):
    tools = TelecomTools()
    order_id = state["order_id"]
    
    current_status = tools.check_esim_status(order_id)
    if current_status == "failed":
        result = tools.reprovision_esim(order_id)
        return {"resolution": result, "next_step": "completed"}
    return {"resolution": "No eSIM action needed", "next_step": "completed"}

# Switch Agent
switch_prompt = ChatPromptTemplate.from_messages([
    ("system", """Handle switch configuration issues for order {order_id}. 
    Check switch status and reconfigure if needed.""")
])

def switch_agent(state: AgentState):
    tools = TelecomTools()
    order_id = state["order_id"]
    
    current_status = tools.check_switch_status(order_id)
    if current_status == "error":
        result = tools.reprovision_switch(order_id)
        return {"resolution": result, "next_step": "completed"}
    return {"resolution": "No switch action needed", "next_step": "completed"}

# Human Review
def human_review(state: AgentState):
    return {"resolution": "Escalated to human team", "next_step": "completed"}

# Build LangGraph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("master", master_agent)
workflow.add_node("resubmission", resubmission_agent)
workflow.add_node("esim", esim_agent)
workflow.add_node("switch", switch_agent)
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

for agent in ["resubmission", "esim", "switch", "human"]:
    workflow.add_edge(agent, END)

# Compile the graph
app = workflow.compile()

# Visualize the graph (requires graphviz)
from langgraph.graph import END
from IPython.display import Image

Image(app.get_graph().draw_mermaid_png())

# Test the workflow
def run_test(order_id):
    print(f"\nProcessing order {order_id}:")
    for step in app.stream({"order_id": order_id, "resolution": "", "next_step": ""}):
        for key, value in step.items():
            print(f"{key}: {value}")
    print("="*50)

# Test cases
run_test("ORD123")  # Should go to resubmission
run_test("ORD456")  # Should go to eSIM
run_test("ORD789")  # Should go to switch
run_test("ORD999")  # Should go to human