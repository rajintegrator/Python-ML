# !pip install "langchain==0.1.0"  # Use 0.1.0 for LangGraph compatibility
# !pip install "langchain-community==0.0.9"
# !pip install "langchain-core==0.1.5"
# !pip install "langgraph==0.0.15"
# !pip install "SQLAlchemy==2.0.25"
# !pip install "pandas"

import os
import sqlite3
import pandas as pd
from typing import Dict, List, Optional, Union

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import BaseTool
from langchain_core.runnables import chain
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolInvoker

# Use a smaller model to save on resources, and for faster development.
llm = ChatOpenAI(model="gpt-3.5-turbo-0613")  # Or "gpt-4-0613" if you have access

# --- 1. Dummy Data and SQLite Setup ---
# Create a dummy SQLite database and tables for simulating telecom orders and related data.


def setup_database():
    """
    Sets up a dummy SQLite database with tables for telecom orders,
    ESIM profiles, and switch configurations.  Includes functions to
    interact with the database.
    """
    conn = sqlite3.connect("telecom_orders.db")
    cursor = conn.cursor()

    # Create orders table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT,
            service_type TEXT,
            status TEXT,
            issue_type TEXT,
            details TEXT
        )
    """
    )

    # Create esim_profiles table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS esim_profiles (
            esim_id TEXT PRIMARY KEY,
            order_id TEXT,
            profile_status TEXT,
            iccid TEXT
        )
    """
    )

    # Create switch_configs table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS switch_configs (
            config_id INTEGER PRIMARY KEY,
            order_id TEXT,
            switch_name TEXT,
            config_status TEXT,
            vlan_id TEXT
        )
    """
    )

    # Insert dummy data
    orders_data = [
        ("ORD001", "CUST101", "Mobile", "Active", None, "Initial Activation"),
        ("ORD002", "CUST102", "Mobile", "Failed", "eSIM", "eSIM profile not found"),
        ("ORD003", "CUST103", "Fixed Line", "Failed", "Switch", "Switch port blocked"),
        ("ORD004", "CUST104", "Mobile", "Failed", "Not Sent", "Order not sent to activation system"),
        ("ORD005", "CUST105", "Internet", "Pending", None, "Awaiting confirmation"),
        ("ORD006", "CUST106", "Mobile", "Failed", "Unknown", "Unknown issue"),
    ]
    cursor.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", orders_data
    )

    esim_data = [
        ("ESIM001", "ORD002", "Inactive", "1234567890"),
        ("ESIM002", "ORD005", "Active", "0987654321"),
    ]
    cursor.executemany(
        "INSERT INTO esim_profiles VALUES (?, ?, ?, ?)", esim_data
    )

    switch_data = [
        ("1", "ORD003", "SwitchA", "Failed", "100"),
        ("2", "ORD005", "SwitchB", "Active", "200"),
    ]
    cursor.executemany(
        "INSERT INTO switch_configs VALUES (?, ?, ?, ?, ?)", switch_data
    )

    conn.commit()
    conn.close()


# --- 2. Define Tools ---
# Define tools for interacting with the database and performing actions.


class ResubmitOrderTool(BaseTool):
    """Tool to resubmit an order."""

    name = "resubmit_order"
    description = "Resubmits an order for activation.  Requires the order_id."

    def _run(self, order_id: str) -> str:
        """Resubmits the order with the given ID."""
        conn = sqlite3.connect("telecom_orders.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE orders SET status = 'Pending', issue_type = NULL WHERE order_id = ?",
            (order_id,),
        )
        conn.commit()
        conn.close()
        return f"Order {order_id} has been resubmitted."

    def _arun(self, order_id: str) -> str:
        raise NotImplementedError("Async not supported for this tool.")


class ReprovisionESIMTool(BaseTool):
    """Tool to reprovision an eSIM profile."""

    name = "reprovision_esim"
    description = (
        "Reprovisions an eSIM profile. Requires the order_id.  "
        "This will update the eSIM profile status to 'Active'."
    )

    def _run(self, order_id: str) -> str:
        """Reprovisions the eSIM profile for the given order ID."""
        conn = sqlite3.connect("telecom_orders.db")
        cursor = conn.cursor()
        # First, get the esim_id for the order
        cursor.execute(
            "SELECT esim_id FROM esim_profiles WHERE order_id = ?", (order_id,)
        )
        result = cursor.fetchone()
        if result is None:
            conn.close()
            return f"No eSIM profile found for order {order_id}."

        esim_id = result[0]
        cursor.execute(
            "UPDATE esim_profiles SET profile_status = 'Active' WHERE esim_id = ?",
            (esim_id,),
        )
        cursor.execute(
            "UPDATE orders SET status = 'Active', issue_type = NULL WHERE order_id = ?",
            (order_id,),
        )
        conn.commit()
        conn.close()
        return f"eSIM profile for order {order_id} (eSIM ID: {esim_id}) has been reprovisioned."

    def _arun(self, order_id: str) -> str:
        raise NotImplementedError("Async not supported for this tool.")


class ReprovisionSwitchTool(BaseTool):
    """Tool to reprovision a switch configuration."""

    name = "reprovision_switch"
    description = (
        "Reprovisions a switch configuration. Requires the order_id. "
        "This will update the switch configuration status to 'Active'."
    )

    def _run(self, order_id: str) -> str:
        """Reprovisions the switch configuration for the given order ID."""
        conn = sqlite3.connect("telecom_orders.db")
        cursor = conn.cursor()

        # Get switch config for order
        cursor.execute(
            "SELECT config_id FROM switch_configs WHERE order_id = ?", (order_id,)
        )
        result = cursor.fetchone()
        if result is None:
            conn.close()
            return f"No switch configuration found for order {order_id}."
        config_id = result[0]

        cursor.execute(
            "UPDATE switch_configs SET config_status = 'Active' WHERE config_id = ?",
            (config_id,),
        )
        cursor.execute(
            "UPDATE orders SET status = 'Active', issue_type = NULL WHERE order_id = ?",
            (order_id,),
        )

        conn.commit()
        conn.close()
        return f"Switch configuration for order {order_id} (Config ID: {config_id}) has been reprovisioned."

    def _arun(self, order_id: str) -> str:
        raise NotImplementedError("Async not supported for this tool.")


# --- 3. Define Agents and Prompts ---
# Define prompts for each agent.  These prompts guide the LLM in
# determining the appropriate action to take.

# Master Agent Prompt
MASTER_AGENT_PROMPT = PromptTemplate.from_template(
    """
You are a master agent responsible for analyzing telecom orders and routing them to the appropriate agent for handling fallouts.
Here is the order data:
Order ID: {order_id}
Customer ID: {customer_id}
Service Type: {service_type}
Status: {status}
Issue Type: {issue_type}
Details: {details}

Based on the order data, determine the type of issue and route the order to the appropriate agent.
If the issue_type is 'Not Sent', route to the Resubmit Order Agent.
If the issue_type is 'eSIM', route to the Reprovision eSIM Agent.
If the issue_type is 'Switch', route to the Reprovision Switch Agent.
If the issue_type is 'Unknown' or not recognized, route to the Human in the Loop.
Respond only with the agent name.  Do not include any other text.
"""
)

# Resubmit Order Agent Prompt
RESUBMIT_ORDER_PROMPT = PromptTemplate.from_template(
    """
You are an agent responsible for resubmitting orders that were not sent for activation.
Here is the order data:
Order ID: {order_id}
Customer ID: {customer_id}
Service Type: {service_type}
Status: {status}
Issue Type: {issue_type}
Details: {details}

Resubmit the order and update the status.
Use the resubmit_order tool.
Respond with the output of the tool.
"""
)

# Reprovision eSIM Agent Prompt
REPROVISION_ESIM_PROMPT = PromptTemplate.from_template(
    """
You are an agent responsible for reprovisioning eSIM profiles.
Here is the order data:
Order ID: {order_id}
Customer ID: {customer_id}
Service Type: {service_type}
Status: {status}
Issue Type: {issue_type}
Details: {details}

Reprovision the eSIM profile for the order.
Use the reprovision_esim tool.
Respond with the output of the tool.
"""
)

# Reprovision Switch Agent Prompt
REPROVISION_SWITCH_PROMPT = PromptTemplate.from_template(
    """
You are an agent responsible for reprovisioning switch configurations.
Here is the order data:
Order ID: {order_id}
Customer ID: {customer_id}
Service Type: {service_type}
Status: {status}
Issue Type: {issue_type}
Details: {details}

Reprovision the switch configuration for the order.
Use the reprovision_switch tool.
Respond with the output of the tool.
"""
)

# Human in the Loop Prompt
HUMAN_IN_THE_LOOP_PROMPT = PromptTemplate.from_template(
    """
The order requires human intervention. Please investigate the following order:
Order ID: {order_id}
Customer ID: {customer_id}
Service Type: {service_type}
Status: {status}
Issue Type: {issue_type}
Details: {details}

Provide a summary of the issue and suggest possible next steps.
"""
)


# --- 4. Define Agents ---
# Create the agents using the LLM and prompts.  Include a ToolInvoker
# for each agent that needs to use tools.

# Master Agent (No tools)
master_agent = (
    {"order_id": lambda x: x["order_id"],
     "customer_id": lambda x: x["customer_id"],
     "service_type": lambda x: x["service_type"],
     "status": lambda x: x["status"],
     "issue_type": lambda x: x["issue_type"],
     "details": lambda x: x["details"],
     }
    | MASTER_AGENT_PROMPT
    | llm
)

# Resubmit Order Agent
resubmit_order_agent = (
    {"order_id": lambda x: x["order_id"],
     "customer_id": lambda x: x["customer_id"],
     "service_type": lambda x: x["service_type"],
     "status": lambda x: x["status"],
     "issue_type": lambda x: x["issue_type"],
     "details": lambda x: x["details"],
     }
    | RESUBMIT_ORDER_PROMPT
    | llm
    | ToolInvoker(tools=[ResubmitOrderTool()])
)

# Reprovision eSIM Agent
reprovision_esim_agent = (
    {"order_id": lambda x: x["order_id"],
     "customer_id": lambda x: x["customer_id"],
     "service_type": lambda x: x["service_type"],
     "status": lambda x: x["status"],
     "issue_type": lambda x: x["issue_type"],
     "details": lambda x: x["details"],
     }
    | REPROVISION_ESIM_PROMPT
    | llm
    | ToolInvoker(tools=[ReprovisionESIMTool()])
)

# Reprovision Switch Agent
reprovision_switch_agent = (
    {"order_id": lambda x: x["order_id"],
     "customer_id": lambda x: x["customer_id"],
     "service_type": lambda x: x["service_type"],
     "status": lambda x: x["status"],
     "issue_type": lambda x: x["issue_type"],
     "details": lambda x: x["details"],
     }
    | REPROVISION_SWITCH_PROMPT
    | llm
    | ToolInvoker(tools=[ReprovisionSwitchTool()])
)

# Human in the Loop Agent
human_in_the_loop_agent = (
    {"order_id": lambda x: x["order_id"],
     "customer_id": lambda x: x["customer_id"],
     "service_type": lambda x: x["service_type"],
     "status": lambda x: x["status"],
     "issue_type": lambda x: x["issue_type"],
     "details": lambda x: x["details"],
     }
    | HUMAN_IN_THE_LOOP_PROMPT
    | llm
)


# --- 5. Define Graph State ---
# Define the state of the graph.  This includes the input and any intermediate state.
class GraphState(TypedDict):
    order_id: str
    customer_id: str
    service_type: str
    status: str
    issue_type: str
    details: str
    agent: str
    messages: List[BaseMessage]


# --- 6. Define Graph Edges ---
# Define the edges of the graph.  These determine the flow of execution.
def should_route(state: GraphState) -> str:
    """
    Determines which agent to route to based on the current state.
    """
    agent = state["agent"]
    if agent == "Resubmit Order Agent":
        return "resubmit_order"
    elif agent == "Reprovision eSIM Agent":
        return "reprovision_esim"
    elif agent == "Reprovision Switch Agent":
        return "reprovision_switch"
    elif agent == "Human in the Loop Agent":
        return "human_in_the_loop"
    else:
        return "master"  # Default to master agent


# --- 7. Build Graph ---
# Build the graph.  This involves creating a StateGraph and adding nodes and edges.
def build_graph():
    """
    Builds the LangGraph graph for handling telecom activation fallouts.
    """
    graph = StateGraph(GraphState)

    # Add nodes
    graph.add_node("master", master_agent)
    graph.add_node("resubmit_order", resubmit_order_agent)
    graph.add_node("reprovision_esim", reprovision_esim_agent)
    graph.add_node("reprovision_switch", reprovision_switch_agent)
    graph.add_node("human_in_the_loop", human_in_the_loop_agent)

    # Add edges
    graph.add_edge("master", "route")
    graph.add_edge("resubmit_order", END)
    graph.add_edge("reprovision_esim", END)
    graph.add_edge("reprovision_switch", END)
    graph.add_edge("human_in_the_loop", END)

    # Add conditional edge
    graph.add_conditional_edges(
        "route",
        should_route,
        {
            "resubmit_order": "resubmit_order",
            "reprovision_esim": "reprovision_esim",
            "reprovision_switch": "reprovision_switch",
            "human_in_the_loop": "human_in_the_loop",
            "master": "master",  # Add a self-loop back to master
        },
    )

    graph.set_entry_point("master")
    return graph


# --- 8. Run Graph ---
# Run the graph with sample data.
def run_graph(order_data: Dict):
    """Runs the LangGraph graph with the given order data."""
    graph = build_graph()
    chain = graph.to_runnable()
    result = chain.invoke(order_data)
    return result


# --- 9. Main ---
# Main function to set up the database and run the graph with sample data.
if __name__ == "__main__":
    setup_database()  # Initialize the database
    # Get a sample order that has a 'eSIM' issue.
    conn = sqlite3.connect("telecom_orders.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE issue_type = 'eSIM' LIMIT 1")
    order_data_row = cursor.fetchone()
    conn.close()

    if order_data_row:
        order_data = {
            "order_id": order_data_row[0],
            "customer_id": order_data_row[1],
            "service_type": order_data_row[2],
            "status": order_data_row[3],
            "issue_type": order_data_row[4],
            "details": order_data_row[5],
        }
        print("Running graph with order data:", order_data)
        result = run_graph(order_data)
        print("Graph execution result:", result)
    else:
        print("No order with 'eSIM' issue found to test.")

    # Get a sample order that has a 'Switch' issue.
    conn = sqlite3.connect("telecom_orders.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE issue_type = 'Switch' LIMIT 1")
    order_data_row = cursor.fetchone()
    conn.close()

    if order_data_row:
        order_data = {
            "order_id": order_data_row[0],
            "customer_id": order_data_row[1],
            "service_type": order_data_row[2],
            "status": order_data_row[3],
            "issue_type": order_data_row[4],
            "details": order_data_row[5],
        }
        print("\nRunning graph with order data:", order_data)
        result = run_graph(order_data)
        print("Graph execution result:", result)
    else:
        print("No order with 'Switch' issue found to test.")

    # Get a sample order that has a 'Not Sent' issue.
    conn = sqlite3.connect("telecom_orders.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE issue_type = 'Not Sent' LIMIT 1")
    order_data_row = cursor.fetchone()
    conn.close()

    if order_data_row:
        order_data = {
            "order_id": order_data_row[0],
            "customer_id": order_data_row[1],
            "service_type": order_data_row[2],
            "status": order_data_row[3],
            "issue_type": order_data_row[4],
            "details": order_data_row[5],
        }
        print("\nRunning graph with order data:", order_data)
        result = run_graph(order_data)
        print("Graph execution result:", result)
    else:
        print("No order with 'Not Sent' issue found to test.")

    # Get a sample order that has an 'Unknown' issue.
    conn = sqlite3.connect("telecom_orders.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE issue_type = 'Unknown' LIMIT 1")
    order_data_row = cursor.fetchone()
    conn.close()

    if order_data_row:
        order_data = {
            "order_id": order_data_row[0],
            "customer_id": order_data_row[1],
            "service_type": order_data_row[2],
            "status": order_data_row[3],
            "issue_type": order_data_row[4],
            "details": order_data_row[5],
        }
        print("\nRunning graph with order data:", order_data)
        result = run_graph(order_data)
        print("Graph execution result:", result)
    else:
        print("No order with 'Unknown' issue found to test.")
