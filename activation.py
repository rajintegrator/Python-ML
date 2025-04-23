# Telecom Activation Fallout Management with LangGraph
# A comprehensive multi-agent system for detecting and resolving telecom activation issues

import os
import json
import sqlite3
import uuid
import pandas as pd
import datetime
from typing import Dict, List, Tuple, Any, Annotated, TypedDict, Literal, Optional, Union
from enum import Enum
import random
import time

# Import necessary LangGraph libraries
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint import JsonCheckpointRegistry

# For visualization
import networkx as nx
import matplotlib.pyplot as plt
from IPython.display import display, HTML, Markdown, Image

# For OpenAI integration
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, FunctionMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph.message import add_messages
from langchain_core.tools import Tool

# Constants
DB_NAME = "telecom_orders.db"

# ==============================
# Part 1: Create SQLite Database
# ==============================

def initialize_database():
    """Initialize SQLite database with telecom order tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create Orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL,
        service_type TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        fallout_reason TEXT,
        resolved_by TEXT,
        resolution_time TEXT
    )
    ''')
    
    # Create Customers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        customer_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        address TEXT NOT NULL
    )
    ''')
    
    # Create eSIM table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS esims (
        esim_id TEXT PRIMARY KEY,
        order_id TEXT NOT NULL,
        iccid TEXT NOT NULL,
        eid TEXT NOT NULL,
        status TEXT NOT NULL,
        profile_status TEXT,
        activation_code TEXT,
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
    )
    ''')
    
    # Create Switch table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS switches (
        switch_id TEXT PRIMARY KEY,
        order_id TEXT NOT NULL,
        switch_name TEXT NOT NULL,
        port_id TEXT NOT NULL,
        config_status TEXT NOT NULL,
        last_updated TEXT NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
    )
    ''')
    
    # Create Order Log table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_logs (
        log_id TEXT PRIMARY KEY,
        order_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        description TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
    )
    ''')
    
    conn.commit()
    conn.close()
    
    print("Database initialized successfully.")

# ============================
# Part 2: Mock Data Generation
# ============================

def generate_mock_data(num_orders=50):
    """Generate mock data for telecom orders."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("DELETE FROM order_logs")
    cursor.execute("DELETE FROM switches")
    cursor.execute("DELETE FROM esims")
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM customers")
    
    # Generate customers
    customers = []
    for i in range(20):
        customer_id = f"CUST-{uuid.uuid4().hex[:8]}"
        name = f"Customer {i+1}"
        email = f"customer{i+1}@example.com"
        phone = f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        address = f"{random.randint(100, 9999)} Main St, City {i%10+1}"
        
        cursor.execute(
            "INSERT INTO customers VALUES (?, ?, ?, ?, ?)",
            (customer_id, name, email, phone, address)
        )
        customers.append(customer_id)
    
    # Generate orders and related entities
    fallout_types = [
        "NOT_SENT_FOR_ACTIVATION", 
        "ESIM_ISSUE", 
        "SWITCH_ISSUE", 
        "OTHER_ISSUE",
        None  # No issue
    ]
    
    service_types = ["Mobile", "Internet", "TV", "Bundle"]
    statuses = ["Completed", "Failed", "In Progress", "Pending"]
    
    for i in range(num_orders):
        # Create order
        order_id = f"ORD-{uuid.uuid4().hex[:8]}"
        customer_id = random.choice(customers)
        service_type = random.choice(service_types)
        
        # Determine if order will have fallout
        has_fallout = random.random() < 0.6  # 60% chance of fallout
        status = "Failed" if has_fallout else random.choice(["Completed", "In Progress", "Pending"])
        
        # Set fallout reason if applicable
        fallout_reason = None
        if has_fallout:
            fallout_reason = random.choice(fallout_types[:-1])  # Exclude 'None' option
        
        created_at = (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30))).isoformat()
        updated_at = (datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 10))).isoformat()
        
        # Add some resolved cases
        resolved_by = None
        resolution_time = None
        if has_fallout and random.random() < 0.3:  # 30% of fallouts are resolved
            resolvers = ["resubmission_agent", "esim_agent", "switch_agent", "human_agent"]
            resolved_by = resolvers[fallout_types.index(fallout_reason)]
            resolution_time = (datetime.datetime.now() - datetime.timedelta(hours=random.randint(1, 24))).isoformat()
            status = "Completed"
        
        cursor.execute(
            "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (order_id, customer_id, service_type, status, created_at, updated_at, 
             fallout_reason, resolved_by, resolution_time)
        )
        
        # Create eSIM if applicable
        if service_type == "Mobile" or service_type == "Bundle":
            esim_id = f"ESIM-{uuid.uuid4().hex[:8]}"
            iccid = ''.join(random.choices('0123456789', k=20))
            eid = ''.join(random.choices('0123456789ABCDEF', k=32))
            
            # Set eSIM status based on fallout
            esim_status = "Active"
            profile_status = "Installed"
            
            if fallout_reason == "ESIM_ISSUE":
                esim_status = "Failed"
                profile_status = random.choice(["Download Failed", "Installation Failed", "Activation Failed"])
            
            activation_code = f"LPA:{uuid.uuid4().hex}" if esim_status == "Active" else None
            
            cursor.execute(
                "INSERT INTO esims VALUES (?, ?, ?, ?, ?, ?, ?)",
                (esim_id, order_id, iccid, eid, esim_status, profile_status, activation_code)
            )
        
        # Create switch configuration if applicable
        if service_type == "Internet" or service_type == "TV" or service_type == "Bundle":
            switch_id = f"SW-{uuid.uuid4().hex[:8]}"
            switch_name = random.choice(["SW-NORTH", "SW-SOUTH", "SW-EAST", "SW-WEST"])
            port_id = f"PORT-{random.randint(1, 48)}"
            
            # Set switch status based on fallout
            config_status = "Configured"
            
            if fallout_reason == "SWITCH_ISSUE":
                config_status = random.choice(["Config Failed", "Port Error", "Route Failed"])
            
            last_updated = (datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 5))).isoformat()
            
            cursor.execute(
                "INSERT INTO switches VALUES (?, ?, ?, ?, ?, ?)",
                (switch_id, order_id, switch_name, port_id, config_status, last_updated)
            )
        
        # Generate some order logs
        log_events = [
            ("ORDER_CREATED", "Order was created in the system"),
            ("VALIDATION_PASSED", "Order passed validation checks"),
            ("PAYMENT_PROCESSED", "Payment was successfully processed"),
            ("ACTIVATION_STARTED", "Service activation process started")
        ]
        
        if has_fallout:
            if fallout_reason == "NOT_SENT_FOR_ACTIVATION":
                log_events.append(("ACTIVATION_FAILED", "Order was not sent for activation due to system error"))
            elif fallout_reason == "ESIM_ISSUE":
                log_events.append(("ESIM_FAILED", "eSIM profile download or installation failed"))
            elif fallout_reason == "SWITCH_ISSUE":
                log_events.append(("SWITCH_CONFIG_FAILED", "Switch configuration failed"))
            else:
                log_events.append(("UNKNOWN_ERROR", "An unknown error occurred during activation"))
                
            if resolved_by:
                resolution_event = {
                    "resubmission_agent": ("ORDER_RESUBMITTED", "Order was successfully resubmitted"),
                    "esim_agent": ("ESIM_REPROVISIONED", "eSIM was successfully reprovisioned"),
                    "switch_agent": ("SWITCH_RECONFIGURED", "Switch was successfully reconfigured"),
                    "human_agent": ("MANUAL_RESOLUTION", "Issue was manually resolved by human agent")
                }
                log_events.append(resolution_event[resolved_by])
        else:
            log_events.append(("ACTIVATION_COMPLETED", "Service was successfully activated"))
        
        for event_type, description in log_events:
            log_id = f"LOG-{uuid.uuid4().hex[:8]}"
            log_time = (datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 10), 
                                                    hours=random.randint(0, 23))).isoformat()
            
            cursor.execute(
                "INSERT INTO order_logs VALUES (?, ?, ?, ?, ?)",
                (log_id, order_id, event_type, description, log_time)
            )
    
    conn.commit()
    conn.close()
    
    print(f"Generated {num_orders} mock orders with related data.")

# ===============================
# Part 3: SQLite Tools and APIs
# ===============================

class TelecomAPI:
    """Provides API access to the telecom database."""
    
    @staticmethod
    def get_connection():
        """Get a connection to the SQLite database."""
        return sqlite3.connect(DB_NAME)
    
    @staticmethod
    def get_failed_orders(limit=10):
        """Get list of failed orders."""
        conn = TelecomAPI.get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT o.order_id, o.customer_id, c.name, o.service_type, o.fallout_reason, o.created_at
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.status = 'Failed' AND o.resolved_by IS NULL
        ORDER BY o.created_at DESC
        LIMIT ?
        """
        
        cursor.execute(query, (limit,))
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    @staticmethod
    def get_order_details(order_id):
        """Get detailed information about an order."""
        conn = TelecomAPI.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get order and customer info
        query = """
        SELECT o.*, c.name, c.email, c.phone, c.address
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_id = ?
        """
        
        cursor.execute(query, (order_id,))
        order_data = dict(cursor.fetchone())
        
        # Get eSIM info if exists
        cursor.execute("SELECT * FROM esims WHERE order_id = ?", (order_id,))
        esim_row = cursor.fetchone()
        if esim_row:
            order_data['esim'] = dict(esim_row)
        
        # Get switch info if exists
        cursor.execute("SELECT * FROM switches WHERE order_id = ?", (order_id,))
        switch_row = cursor.fetchone()
        if switch_row:
            order_data['switch'] = dict(switch_row)
        
        # Get order logs
        cursor.execute("""
            SELECT * FROM order_logs 
            WHERE order_id = ? 
            ORDER BY created_at ASC
        """, (order_id,))
        logs = [dict(row) for row in cursor.fetchall()]
        order_data['logs'] = logs
        
        conn.close()
        return order_data
    
    @staticmethod
    def update_order_status(order_id, status, fallout_reason=None, resolved_by=None):
        """Update order status and related fields."""
        conn = TelecomAPI.get_connection()
        cursor = conn.cursor()
        
        resolution_time = None
        if resolved_by:
            resolution_time = datetime.datetime.now().isoformat()
        
        query = """
        UPDATE orders
        SET status = ?, 
            fallout_reason = ?,
            resolved_by = ?,
            resolution_time = ?,
            updated_at = ?
        WHERE order_id = ?
        """
        
        cursor.execute(
            query, 
            (status, fallout_reason, resolved_by, resolution_time, datetime.datetime.now().isoformat(), order_id)
        )
        
        conn.commit()
        conn.close()
        return {"success": cursor.rowcount > 0, "order_id": order_id}
    
    @staticmethod
    def resubmit_order(order_id):
        """Resubmit an order for activation."""
        conn = TelecomAPI.get_connection()
        cursor = conn.cursor()
        
        # First check if order exists and is in failed state
        cursor.execute("SELECT status, fallout_reason FROM orders WHERE order_id = ?", (order_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return {"success": False, "message": "Order not found"}
        
        status, fallout_reason = result
        
        if status != "Failed":
            conn.close()
            return {"success": False, "message": f"Order is not in Failed state. Current status: {status}"}
        
        if fallout_reason != "NOT_SENT_FOR_ACTIVATION":
            conn.close()
            return {"success": False, "message": f"Order fallout reason is not NOT_SENT_FOR_ACTIVATION. Actual reason: {fallout_reason}"}
        
        # Update order status
        TelecomAPI.update_order_status(order_id, "Completed", None, "resubmission_agent")
        
        # Add log entry
        log_id = f"LOG-{uuid.uuid4().hex[:8]}"
        cursor.execute(
            "INSERT INTO order_logs VALUES (?, ?, ?, ?, ?)",
            (log_id, order_id, "ORDER_RESUBMITTED", "Order was successfully resubmitted for activation", 
             datetime.datetime.now().isoformat())
        )
        
        conn.commit()
        conn.close()
        
        # Simulate processing time
        time.sleep(0.5)
        
        return {
            "success": True,
            "order_id": order_id,
            "message": "Order successfully resubmitted for activation"
        }
    
    @staticmethod
    def reprovision_esim(order_id):
        """Reprovision eSIM for an order."""
        conn = TelecomAPI.get_connection()
        cursor = conn.cursor()
        
        # First check if order exists and has eSIM issue
        cursor.execute("SELECT status, fallout_reason FROM orders WHERE order_id = ?", (order_id,))
        order_result = cursor.fetchone()
        
        if not order_result:
            conn.close()
            return {"success": False, "message": "Order not found"}
        
        status, fallout_reason = order_result
        
        if status != "Failed":
            conn.close()
            return {"success": False, "message": f"Order is not in Failed state. Current status: {status}"}
        
        if fallout_reason != "ESIM_ISSUE":
            conn.close()
            return {"success": False, "message": f"Order fallout reason is not ESIM_ISSUE. Actual reason: {fallout_reason}"}
        
        # Check if eSIM exists
        cursor.execute("SELECT esim_id, iccid, eid FROM esims WHERE order_id = ?", (order_id,))
        esim_result = cursor.fetchone()
        
        if not esim_result:
            conn.close()
            return {"success": False, "message": "No eSIM found for this order"}
        
        esim_id, iccid, eid = esim_result
        
        # Generate new activation code
        new_activation_code = f"LPA:{uuid.uuid4().hex}"
        
        # Update eSIM status
        cursor.execute(
            "UPDATE esims SET status = ?, profile_status = ?, activation_code = ? WHERE esim_id = ?",
            ("Active", "Installed", new_activation_code, esim_id)
        )
        
        # Update order status
        TelecomAPI.update_order_status(order_id, "Completed", None, "esim_agent")
        
        # Add log entry
        log_id = f"LOG-{uuid.uuid4().hex[:8]}"
        cursor.execute(
            "INSERT INTO order_logs VALUES (?, ?, ?, ?, ?)",
            (log_id, order_id, "ESIM_REPROVISIONED", 
             f"eSIM was successfully reprovisioned with new activation code", 
             datetime.datetime.now().isoformat())
        )
        
        conn.commit()
        conn.close()
        
        # Simulate processing time
        time.sleep(0.7)
        
        return {
            "success": True,
            "order_id": order_id,
            "esim_id": esim_id,
            "new_activation_code": new_activation_code,
            "message": "eSIM successfully reprovisioned"
        }
    
    @staticmethod
    def reconfigure_switch(order_id):
        """Reconfigure switch for an order."""
        conn = TelecomAPI.get_connection()
        cursor = conn.cursor()
        
        # First check if order exists and has switch issue
        cursor.execute("SELECT status, fallout_reason FROM orders WHERE order_id = ?", (order_id,))
        order_result = cursor.fetchone()
        
        if not order_result:
            conn.close()
            return {"success": False, "message": "Order not found"}
        
        status, fallout_reason = order_result
        
        if status != "Failed":
            conn.close()
            return {"success": False, "message": f"Order is not in Failed state. Current status: {status}"}
        
        if fallout_reason != "SWITCH_ISSUE":
            conn.close()
            return {"success": False, "message": f"Order fallout reason is not SWITCH_ISSUE. Actual reason: {fallout_reason}"}
        
        # Check if switch exists
        cursor.execute("SELECT switch_id, switch_name, port_id FROM switches WHERE order_id = ?", (order_id,))
        switch_result = cursor.fetchone()
        
        if not switch_result:
            conn.close()
            return {"success": False, "message": "No switch configuration found for this order"}
        
        switch_id, switch_name, port_id = switch_result
        
        # Update switch status
        cursor.execute(
            "UPDATE switches SET config_status = ?, last_updated = ? WHERE switch_id = ?",
            ("Configured", datetime.datetime.now().isoformat(), switch_id)
        )
        
        # Update order status
        TelecomAPI.update_order_status(order_id, "Completed", None, "switch_agent")
        
        # Add log entry
        log_id = f"LOG-{uuid.uuid4().hex[:8]}"
        cursor.execute(
            "INSERT INTO order_logs VALUES (?, ?, ?, ?, ?)",
            (log_id, order_id, "SWITCH_RECONFIGURED", 
             f"Switch {switch_name} port {port_id} was successfully reconfigured", 
             datetime.datetime.now().isoformat())
        )
        
        conn.commit()
        conn.close()
        
        # Simulate processing time
        time.sleep(0.6)
        
        return {
            "success": True,
            "order_id": order_id,
            "switch_id": switch_id,
            "switch_name": switch_name,
            "port_id": port_id,
            "message": "Switch successfully reconfigured"
        }
    
    @staticmethod
    def mark_for_human_intervention(order_id, notes=None):
        """Mark an order for human intervention."""
        conn = TelecomAPI.get_connection()
        cursor = conn.cursor()
        
        # Check if order exists
        cursor.execute("SELECT status FROM orders WHERE order_id = ?", (order_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return {"success": False, "message": "Order not found"}
        
        # Add log entry with notes
        log_id = f"LOG-{uuid.uuid4().hex[:8]}"
        description = "Order marked for human intervention"
        if notes:
            description += f": {notes}"
            
        cursor.execute(
            "INSERT INTO order_logs VALUES (?, ?, ?, ?, ?)",
            (log_id, order_id, "HUMAN_INTERVENTION_NEEDED", description, datetime.datetime.now().isoformat())
        )
        
        # Update order status
        updated_at = datetime.datetime.now().isoformat()
        cursor.execute(
            "UPDATE orders SET updated_at = ? WHERE order_id = ?",
            (updated_at, order_id)
        )
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "order_id": order_id,
            "message": "Order marked for human intervention",
            "notes": notes
        }

# Convert API methods to tools
def get_failed_orders_tool(limit=10):
    """Tool to get failed orders."""
    return TelecomAPI.get_failed_orders(limit)

def get_order_details_tool(order_id):
    """Tool to get order details."""
    return TelecomAPI.get_order_details(order_id)

def resubmit_order_tool(order_id):
    """Tool to resubmit an order."""
    return TelecomAPI.resubmit_order(order_id)

def reprovision_esim_tool(order_id):
    """Tool to reprovision an eSIM."""
    return TelecomAPI.reprovision_esim(order_id)

def reconfigure_switch_tool(order_id):
    """Tool to reconfigure a switch."""
    return TelecomAPI.reconfigure_switch(order_id)

def mark_for_human_intervention_tool(order_id, notes=None):
    """Tool to mark an order for human intervention."""
    return TelecomAPI.mark_for_human_intervention(order_id, notes)

# ==============================
# Part 4: Define Agent Structure
# ==============================

# First, we'll define the tools for each agent
telecom_tools = [
    Tool(
        name="get_failed_orders",
        description="Get a list of failed orders that need resolution",
        func=get_failed_orders_tool,
        args_schema={"limit": int}
    ),
    Tool(
        name="get_order_details",
        description="Get detailed information about a specific order",
        func=get_order_details_tool,
        args_schema={"order_id": str}
    ),
    Tool(
        name="resubmit_order",
        description="Resubmit an order that was not sent for activation",
        func=resubmit_order_tool,
        args_schema={"order_id": str}
    ),
    Tool(
        name="reprovision_esim",
        description="Reprovision an eSIM that had provisioning issues",
        func=reprovision_esim_tool,
        args_schema={"order_id": str}
    ),
    Tool(
        name="reconfigure_switch",
        description="Reconfigure a switch that had configuration issues",
        func=reconfigure_switch_tool,
        args_schema={"order_id": str}
    ),
    Tool(
        name="mark_for_human_intervention",
        description="Mark an order for human intervention when automated resolution isn't possible",
        func=mark_for_human_intervention_tool,
        args_schema={"order_id": str, "notes": str}
    )
]

tool_executor = ToolExecutor(telecom_tools)

# Define LLM
llm = ChatOpenAI(temperature=0, model="gpt-4")

# Define system prompts for each agent
master_agent_prompt = """
You are the Master Telecom Agent responsible for analyzing telecom order fallouts and routing them to specialized agents.

Your responsibilities:
1. Analyze the order details to determine the cause of fallout.
2. Route the order to the appropriate specialized agent based on the issue type:
   - For "NOT_SENT_FOR_ACTIVATION" issues, route to the Resubmission Agent
   - For "ESIM_ISSUE" issues, route to the eSIM Agent
   - For "SWITCH_ISSUE" issues, route to the Switch Agent
   - For any other issues or unclear cases, route to human intervention

To analyze an order, you should:
1. First gather information using the get_order_details tool to understand the issue
2. Check the fallout_reason field and logs to confirm the issue type
3. Make a determination on the appropriate agent to handle the issue

Be thorough in your analysis and provide a clear explanation of your routing decision.
"""

resubmission_agent_prompt = """
You are the Resubmission Agent responsible for handling orders that were not sent for activation.

Your responsibilities:
1. Verify that the order has a fallout reason of "NOT_SENT_FOR_ACTIVATION"
2. Check the order logs to understand why the activation failed
3. Use the resubmit_order tool to resubmit the order for activation
4. Verify the resubmission was successful

Be thorough in your verification steps before resubmitting the order.
If the issue doesn't appear to be a simple "not sent for activation" problem, recommend human intervention.
"""

esim_agent_prompt = """
You are the eSIM Agent responsible for handling orders with eSIM provisioning issues.

Your responsibilities:
1. Verify that the order has a fallout reason of "ESIM_ISSUE"
2. Check the eSIM details and order logs to understand the specific issue
3. Use the reprovision_esim tool to reprovision the eSIM with a new activation code
4. Verify the reprovisioning was successful and provide the new activation code

Be thorough in your analysis to ensure the issue is with the eSIM profile rather than something else.
If the issue doesn't appear to be a standard eSIM provisioning problem, recommend human intervention.
"""

switch_agent_prompt = """
You are the Switch Agent responsible for handling orders with network switch configuration issues.

Your responsibilities:
1. Verify that the order has a fallout reason of "SWITCH_ISSUE"
2. Check the switch details and order logs to understand the specific configuration issue
3. Use the reconfigure_switch tool to apply the correct configuration to the switch and port
4. Verify the reconfiguration was successful

Be thorough in your analysis to ensure the issue is with the switch configuration rather than something else.
If the issue doesn't appear to be a standard switch configuration problem, recommend human intervention.
"""

human_agent_prompt = """
You are the Human Intervention Agent responsible for handling complex issues that the automated agents cannot resolve.

Your responsibilities:
1. Analyze the order details to understand the complex or unclear issue
2. Document your analysis and why human intervention is needed
3. Use the mark_for_human_intervention tool to flag the order for human review
4. Provide detailed notes to help the human resolver understand the issue

Be thorough in your analysis and provide as much context as possible in your notes to the human team.
"""

# Define the state for our LangGraph application
class AgentState(TypedDict):
    messages: List[Union[HumanMessage, AIMessage, SystemMessage, FunctionMessage]]
    order_id: Optional[str]
    fallout_type: Optional[str]
    resolution_path: Optional[str]
    escalated_to_human: bool
    resolution_status: Literal["PENDING", "RESOLVED", "FAILED"]

# ==============================
# Part 5: Define Agent Functions
# ==============================

def create_agent_prompt(system_prompt):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])
    return prompt

# Define the function for the master agent
def master_agent(state):
    # Extract messages from the state
    messages = state["messages"]
    
    # Create the prompt for the master agent
    master_prompt = create_agent_prompt(master_agent_prompt)
    
    # Generate response using prompt and messages
    response = llm.invoke(master_prompt.invoke({"messages": messages}))
    
    # Update the state with the master agent's response
    new_state = {**state}
    new_state["messages"] = add_messages(messages, response)
    
    # Determine if we need to execute a tool
    if response.tool_calls:
        tool_to_call = response.tool_calls[0]
        
        print(f"Master Agent executing tool: {tool_to_call.name}")
        tool_result = tool_executor.invoke(tool_to_call)
        
        # Add tool response to messages
        function_message = FunctionMessage(
            name=tool_to_call.name,
            content=json.dumps(tool_result),
        )
        new_state["messages"] = add_messages(new_state["messages"], function_message)
        		
		# If we got order details, try to determine fallout type
        if tool_to_call.name == "get_order_details" and "order_id" in tool_to_call.args:
            order_id = tool_to_call.args["order_id"]
            new_state["order_id"] = order_id
            
            # Extract fallout type from the tool result
            if isinstance(tool_result, dict) and "fallout_reason" in tool_result:
                fallout_type = tool_result["fallout_reason"]
                new_state["fallout_type"] = fallout_type
    
    return new_state

# Define the function for the resubmission agent
def resubmission_agent(state):
    # Extract messages from the state
    messages = state["messages"]
    
    # Create the prompt for the resubmission agent
    resubmission_prompt = create_agent_prompt(resubmission_agent_prompt)
    
    # Generate response using prompt and messages
    response = llm.invoke(resubmission_prompt.invoke({"messages": messages}))
    
    # Update the state with the resubmission agent's response
    new_state = {**state}
    new_state["messages"] = add_messages(messages, response)
    
    # Determine if we need to execute a tool
    if response.tool_calls:
        tool_to_call = response.tool_calls[0]
        
        print(f"Resubmission Agent executing tool: {tool_to_call.name}")
        tool_result = tool_executor.invoke(tool_to_call)
        
        # Add tool response to messages
        function_message = FunctionMessage(
            name=tool_to_call.name,
            content=json.dumps(tool_result),
        )
        new_state["messages"] = add_messages(new_state["messages"], function_message)
        
        # Update resolution status based on tool result
        if tool_to_call.name == "resubmit_order" and tool_result.get("success"):
            new_state["resolution_status"] = "RESOLVED"
            new_state["resolution_path"] = "resubmission_agent"
        elif tool_to_call.name == "mark_for_human_intervention":
            new_state["escalated_to_human"] = True
    
    return new_state

# Define the function for the eSIM agent
def esim_agent(state):
    # Extract messages from the state
    messages = state["messages"]
    
    # Create the prompt for the eSIM agent
    esim_prompt = create_agent_prompt(esim_agent_prompt)
    
    # Generate response using prompt and messages
    response = llm.invoke(esim_prompt.invoke({"messages": messages}))
    
    # Update the state with the eSIM agent's response
    new_state = {**state}
    new_state["messages"] = add_messages(messages, response)
    
    # Determine if we need to execute a tool
    if response.tool_calls:
        tool_to_call = response.tool_calls[0]
        
        print(f"eSIM Agent executing tool: {tool_to_call.name}")
        tool_result = tool_executor.invoke(tool_to_call)
        
        # Add tool response to messages
        function_message = FunctionMessage(
            name=tool_to_call.name,
            content=json.dumps(tool_result),
        )
        new_state["messages"] = add_messages(new_state["messages"], function_message)
        
        # Update resolution status based on tool result
        if tool_to_call.name == "reprovision_esim" and tool_result.get("success"):
            new_state["resolution_status"] = "RESOLVED"
            new_state["resolution_path"] = "esim_agent"
        elif tool_to_call.name == "mark_for_human_intervention":
            new_state["escalated_to_human"] = True
    
    return new_state

# Define the function for the switch agent
def switch_agent(state):
    # Extract messages from the state
    messages = state["messages"]
    
    # Create the prompt for the switch agent
    switch_prompt = create_agent_prompt(switch_agent_prompt)
    
    # Generate response using prompt and messages
    response = llm.invoke(switch_prompt.invoke({"messages": messages}))
    
    # Update the state with the switch agent's response
    new_state = {**state}
    new_state["messages"] = add_messages(messages, response)
    
    # Determine if we need to execute a tool
    if response.tool_calls:
        tool_to_call = response.tool_calls[0]
        
        print(f"Switch Agent executing tool: {tool_to_call.name}")
        tool_result = tool_executor.invoke(tool_to_call)
        
        # Add tool response to messages
        function_message = FunctionMessage(
            name=tool_to_call.name,
            content=json.dumps(tool_result),
        )
        new_state["messages"] = add_messages(new_state["messages"], function_message)
        
        # Update resolution status based on tool result
        if tool_to_call.name == "reconfigure_switch" and tool_result.get("success"):
            new_state["resolution_status"] = "RESOLVED"
            new_state["resolution_path"] = "switch_agent"
        elif tool_to_call.name == "mark_for_human_intervention":
            new_state["escalated_to_human"] = True
    
    return new_state

# Define the function for the human intervention agent
def human_agent(state):
    # Extract messages from the state
    messages = state["messages"]
    
    # Create the prompt for the human agent
    human_prompt = create_agent_prompt(human_agent_prompt)
    
    # Generate response using prompt and messages
    response = llm.invoke(human_prompt.invoke({"messages": messages}))
    
    # Update the state with the human agent's response
    new_state = {**state}
    new_state["messages"] = add_messages(messages, response)
    
    # Determine if we need to execute a tool
    if response.tool_calls:
        tool_to_call = response.tool_calls[0]
        
        print(f"Human Intervention Agent executing tool: {tool_to_call.name}")
        tool_result = tool_executor.invoke(tool_to_call)
        
        # Add tool response to messages
        function_message = FunctionMessage(
            name=tool_to_call.name,
            content=json.dumps(tool_result),
        )
        new_state["messages"] = add_messages(new_state["messages"], function_message)
        
        # Update state
        if tool_to_call.name == "mark_for_human_intervention" and tool_result.get("success"):
            new_state["escalated_to_human"] = True
            new_state["resolution_status"] = "PENDING" # Human needs to intervene
    
    return new_state

# ==============================
# Part 6: Define Routing Logic
# ==============================

# Conditional edge for routing based on fallout type
def route_to_specialist(state):
    fallout_type = state.get("fallout_type")
    
    if fallout_type == "NOT_SENT_FOR_ACTIVATION":
        return "resubmission_agent"
    elif fallout_type == "ESIM_ISSUE":
        return "esim_agent"
    elif fallout_type == "SWITCH_ISSUE":
        return "switch_agent"
    else:
        # For any other issue type or if fallout_type is None
        return "human_agent"

# Check if resolution is completed
def is_resolution_completed(state):
    return state.get("resolution_status") == "RESOLVED"

# ==============================
# Part 7: Build the Graph
# ==============================

# Create a new graph
telecom_workflow = StateGraph(AgentState)

# Add nodes to the graph
telecom_workflow.add_node("master_agent", master_agent)
telecom_workflow.add_node("resubmission_agent", resubmission_agent)
telecom_workflow.add_node("esim_agent", esim_agent)
telecom_workflow.add_node("switch_agent", switch_agent)
telecom_workflow.add_node("human_agent", human_agent)

# Define the edges
telecom_workflow.add_edge("master_agent", route_to_specialist)
telecom_workflow.add_conditional_edges(
    "resubmission_agent",
    is_resolution_completed,
    {
        True: END,
        False: "human_agent"
    }
)
telecom_workflow.add_conditional_edges(
    "esim_agent",
    is_resolution_completed,
    {
        True: END,
        False: "human_agent"
    }
)
telecom_workflow.add_conditional_edges(
    "switch_agent",
    is_resolution_completed,
    {
        True: END,
        False: "human_agent"
    }
)
telecom_workflow.add_edge("human_agent", END)

# Set the entrypoint
telecom_workflow.set_entry_point("master_agent")

# Compile the graph
telecom_app = telecom_workflow.compile()

# ==============================
# Part 8: Visualize the Graph
# ==============================

def visualize_graph():
    """Visualize the telecom workflow graph."""
    # Create a directed graph for visualization
    G = nx.DiGraph()
    
    # Add nodes
    G.add_node("master_agent", label="Master Agent")
    G.add_node("resubmission_agent", label="Resubmission Agent")
    G.add_node("esim_agent", label="eSIM Agent") 
    G.add_node("switch_agent", label="Switch Agent")
    G.add_node("human_agent", label="Human Agent")
    G.add_node("END", label="End")
    
    # Add edges
    G.add_edge("master_agent", "resubmission_agent", label="NOT_SENT_FOR_ACTIVATION")
    G.add_edge("master_agent", "esim_agent", label="ESIM_ISSUE")
    G.add_edge("master_agent", "switch_agent", label="SWITCH_ISSUE")
    G.add_edge("master_agent", "human_agent", label="OTHER_ISSUE")
    
    G.add_edge("resubmission_agent", "END", label="Resolved")
    G.add_edge("resubmission_agent", "human_agent", label="Failed")
    
    G.add_edge("esim_agent", "END", label="Resolved")
    G.add_edge("esim_agent", "human_agent", label="Failed")
    
    G.add_edge("switch_agent", "END", label="Resolved")
    G.add_edge("switch_agent", "human_agent", label="Failed")
    
    G.add_edge("human_agent", "END")
    
    # Set up positions
    pos = {
        "master_agent": (0, 0),
        "resubmission_agent": (-3, -2),
        "esim_agent": (-1, -2),
        "switch_agent": (1, -2),
        "human_agent": (3, -2),
        "END": (0, -4)
    }
    
    # Set up node colors
    node_colors = {
        "master_agent": "lightblue",
        "resubmission_agent": "lightgreen",
        "esim_agent": "lightcoral",
        "switch_agent": "lightyellow",
        "human_agent": "lightpink",
        "END": "lightgrey"
    }
    
    # Create figure and draw
    plt.figure(figsize=(14, 10))
    
    # Draw nodes with colors
    for node, color in node_colors.items():
        nx.draw_networkx_nodes(G, pos, nodelist=[node], node_color=color, node_size=2500, alpha=0.8)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.7, edge_color="gray", arrows=True, arrowsize=20)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight="bold")
    
    # Draw edge labels
    edge_labels = nx.get_edge_attributes(G, "label")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
    
    plt.title("Telecom Activation Fallout Management Workflow", fontsize=16)
    plt.axis("off")
    plt.tight_layout()
    plt.show()

# ==============================
# Part 9: Example Run Functions
# ==============================

def run_telecom_workflow(order_id=None):
    """Run the telecom workflow with a specified order ID or get a failed order."""
    # Initialize the database if it doesn't exist
    if not os.path.exists(DB_NAME):
        initialize_database()
        generate_mock_data(50)
    
    # If no order_id is provided, get the first failed order
    if order_id is None:
        failed_orders = TelecomAPI.get_failed_orders(1)
        if not failed_orders:
            print("No failed orders found. Generating more mock data...")
            generate_mock_data(20)
            failed_orders = TelecomAPI.get_failed_orders(1)
        
        if failed_orders:
            order_id = failed_orders[0]["order_id"]
        else:
            print("No failed orders available to process.")
            return
    
    # Get order details to show initial state
    order_details = TelecomAPI.get_order_details(order_id)
    print(f"\n==== Starting workflow for Order ID: {order_id} ====")
    print(f"Customer: {order_details.get('name')}")
    print(f"Service Type: {order_details.get('service_type')}")
    print(f"Fallout Reason: {order_details.get('fallout_reason')}")
    print("=" * 60)
    
    # Define initial inputs for the workflow
    inputs = {
        "messages": [
            HumanMessage(
                content=f"Please analyze and resolve the fallout for order ID {order_id}."
            )
        ],
        "order_id": None,
        "fallout_type": None,
        "resolution_path": None,
        "escalated_to_human": False,
        "resolution_status": "PENDING"
    }
    
    # Execute the workflow
    result = telecom_app.invoke(inputs)
    
    # Check the final state of the order
    updated_order = TelecomAPI.get_order_details(order_id)
    
    print("\n==== Workflow Result ====")
    print(f"Order ID: {order_id}")
    print(f"Final Status: {updated_order.get('status')}")
    print(f"Resolution Path: {result.get('resolution_path')}")
    print(f"Escalated to Human: {result.get('escalated_to_human')}")
    
    # Print the conversation history
    print("\n==== Conversation History ====")
    for message in result["messages"]:
        if isinstance(message, HumanMessage):
            print(f"\nHuman: {message.content}")
        elif isinstance(message, AIMessage):
            print(f"\nAI: {message.content}")
        elif isinstance(message, FunctionMessage):
            print(f"\nFunction ({message.name}): {message.content[:100]}...")
    
    return result

# ==============================
# Part 10: Monitoring Functions
# ==============================

def display_order_statistics():
    """Display statistics about orders in the database."""
    conn = TelecomAPI.get_connection()
    cursor = conn.cursor()
    
    # Get total orders
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]
    
    # Get counts by status
    cursor.execute("SELECT status, COUNT(*) FROM orders GROUP BY status")
    status_counts = cursor.fetchall()
    
    # Get counts by fallout reason
    cursor.execute("SELECT fallout_reason, COUNT(*) FROM orders WHERE fallout_reason IS NOT NULL GROUP BY fallout_reason")
    fallout_counts = cursor.fetchall()
    
    # Get counts by resolver
    cursor.execute("SELECT resolved_by, COUNT(*) FROM orders WHERE resolved_by IS NOT NULL GROUP BY resolved_by")
    resolver_counts = cursor.fetchall()
    
    conn.close()
    
    # Display as DataFrame
    print("\n==== Order Statistics ====")
    print(f"Total Orders: {total_orders}")
    
    print("\nStatus Distribution:")
    status_df = pd.DataFrame(status_counts, columns=["Status", "Count"])
    display(status_df)
    
    print("\nFallout Reason Distribution:")
    fallout_df = pd.DataFrame(fallout_counts, columns=["Fallout Reason", "Count"])
    display(fallout_df)
    
    print("\nResolver Distribution:")
    resolver_df = pd.DataFrame(resolver_counts, columns=["Resolved By", "Count"])
    display(resolver_df)
    
    # Create bar charts
    plt.figure(figsize=(15, 10))
    
    # Status chart
    plt.subplot(2, 2, 1)
    status_df.plot(kind="bar", x="Status", y="Count", ax=plt.gca(), legend=False, color="skyblue")
    plt.title("Order Status Distribution")
    plt.xlabel("Status")
    plt.ylabel("Count")
    
    # Fallout chart
    plt.subplot(2, 2, 2)
    fallout_df.plot(kind="bar", x="Fallout Reason", y="Count", ax=plt.gca(), legend=False, color="salmon")
    plt.title("Fallout Reason Distribution")
    plt.xlabel("Fallout Reason")
    plt.ylabel("Count")
    
    # Resolver chart
    if not resolver_df.empty:
        plt.subplot(2, 2, 3)
        resolver_df.plot(kind="bar", x="Resolved By", y="Count", ax=plt.gca(), legend=False, color="lightgreen")
        plt.title("Resolver Distribution")
        plt.xlabel("Resolved By")
        plt.ylabel("Count")
    
    plt.tight_layout()
    plt.show()

# ==============================
# Part 11: Notebook Demo Main Section
# ==============================

def main():
    """Main function to run the notebook demo."""
    print("Welcome to the Telecom Activation Fallout Management System!")
    print("This system uses LangGraph to orchestrate multiple AI agents to resolve telecom order issues.")
    
    # Initialize database
    if not os.path.exists(DB_NAME):
        print("\nInitializing database with mock data...")
        initialize_database()
        generate_mock_data(50)
    else:
        print("\nDatabase already exists.")
    
    # Visualize the graph
    print("\nVisualizing the agent workflow graph...")
    visualize_graph()
    
    # Display order statistics
    display_order_statistics()
    
    # Run examples for each fallout type
    print("\n==== Running Example Workflows ====")
    
    # Find one order of each fallout type
    conn = TelecomAPI.get_connection()
    cursor = conn.cursor()
    
    # Get one order of each fallout type
    cursor.execute("SELECT order_id FROM orders WHERE fallout_reason = 'NOT_SENT_FOR_ACTIVATION' AND status = 'Failed' LIMIT 1")
    not_sent_order = cursor.fetchone()
    
    cursor.execute("SELECT order_id FROM orders WHERE fallout_reason = 'ESIM_ISSUE' AND status = 'Failed' LIMIT 1")
    esim_order = cursor.fetchone()
    
    cursor.execute("SELECT order_id FROM orders WHERE fallout_reason = 'SWITCH_ISSUE' AND status = 'Failed' LIMIT 1")
    switch_order = cursor.fetchone()
    
    cursor.execute("SELECT order_id FROM orders WHERE fallout_reason = 'OTHER_ISSUE' AND status = 'Failed' LIMIT 1")
    other_order = cursor.fetchone()
    
    conn.close()
    
    # Run examples if orders are found
    if not_sent_order:
        print("\n\n==== Example 1: NOT_SENT_FOR_ACTIVATION Order ====")
        run_telecom_workflow(not_sent_order[0])
    
    if esim_order:
        print("\n\n==== Example 2: ESIM_ISSUE Order ====")
        run_telecom_workflow(esim_order[0])
    
    if switch_order:
        print("\n\n==== Example 3: SWITCH_ISSUE Order ====")
        run_telecom_workflow(switch_order[0])
    
    if other_order:
        print("\n\n==== Example 4: OTHER_ISSUE Order ====")
        run_telecom_workflow(other_order[0])
    
    print("\n\nTelecom Activation Fallout Management demo completed.")

# Run the main function when notebook is executed
if __name__ == "__main__":
    main()