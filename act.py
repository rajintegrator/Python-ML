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
import logging

# Import necessary LangGraph libraries
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
# Note: Checkpoints are useful for persistent state, but removed for simplicity here.
# from langgraph.checkpoint.memory import MemorySaver
# from langgraph.checkpoint import JsonCheckpointRegistry

# For visualization (ensure these are installed: pip install networkx matplotlib)
import networkx as nx
import matplotlib.pyplot as plt
from IPython.display import display, Markdown, Image # Use display for rich output in notebooks

# Import LangChain core components
# ******************************************************************************
# TODO: Replace with your Gemini LLM integration
# from langchain_openai import ChatOpenAI # REMOVED OpenAI specific import
from langchain_core.language_models.chat_models import BaseChatModel # Generic base class
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
# FunctionMessage is deprecated, use ToolMessage instead if using newer LangChain versions
# For compatibility with older examples, we might keep FunctionMessage if ToolMessage causes issues.
# Let's try ToolMessage first as it's the current standard.
from langchain_core.messages import ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph.message import add_messages # Utility to add messages to state
from langchain_core.tools import Tool
from langchain_core.pydantic_v1 import BaseModel, Field # For tool argument schemas

# ******************************************************************************

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
DB_NAME = "telecom_orders_v2.db" # Use a new DB name to avoid conflicts

# ==============================
# Part 1: Create SQLite Database
# ==============================

def initialize_database():
    """Initialize SQLite database with telecom order tables."""
    # Use try...finally to ensure connection is closed
    conn = None
    try:
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
        logging.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logging.error(f"Database initialization failed: {e}")
    finally:
        if conn:
            conn.close()

# ============================
# Part 2: Mock Data Generation
# ============================

def generate_mock_data(num_orders=50):
    """Generate mock data for telecom orders."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Clear existing data (optional, good for rerunning generation)
        logging.info("Clearing existing mock data...")
        cursor.execute("DELETE FROM order_logs")
        cursor.execute("DELETE FROM switches")
        cursor.execute("DELETE FROM esims")
        cursor.execute("DELETE FROM orders")
        cursor.execute("DELETE FROM customers")
        conn.commit() # Commit deletions

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
            "OTHER_ISSUE", # For human intervention
            None  # No issue / Completed successfully initially
        ]
        fallout_weights = [0.2, 0.2, 0.15, 0.05, 0.4] # Adjust weights as needed

        service_types = ["Mobile", "Internet", "TV", "Bundle"]
        statuses = ["Completed", "Failed", "In Progress", "Pending"]

        for i in range(num_orders):
            # Create order
            order_id = f"ORD-{uuid.uuid4().hex[:8]}"
            customer_id = random.choice(customers)
            service_type = random.choice(service_types)

            # Determine fallout type based on weights
            fallout_reason = random.choices(fallout_types, weights=fallout_weights, k=1)[0]
            has_fallout = fallout_reason is not None

            status = "Failed" if has_fallout else random.choice(["Completed", "In Progress", "Pending"])

            created_at = (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30))).isoformat()
            updated_at = (datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 10))).isoformat()

            # Add some resolved cases (only for actual fallouts)
            resolved_by = None
            resolution_time = None
            if has_fallout and random.random() < 0.3:  # 30% of fallouts are already resolved for realism
                resolvers = {
                    "NOT_SENT_FOR_ACTIVATION": "resubmission_agent",
                    "ESIM_ISSUE": "esim_agent",
                    "SWITCH_ISSUE": "switch_agent",
                    "OTHER_ISSUE": "human_agent" # Assume human resolved 'other' issues
                }
                resolved_by = resolvers.get(fallout_reason)
                if resolved_by: # Ensure we have a resolver for the fallout type
                    resolution_time = (datetime.datetime.now() - datetime.timedelta(hours=random.randint(1, 24))).isoformat()
                    status = "Completed" # Mark as completed if resolved

            cursor.execute(
                "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (order_id, customer_id, service_type, status, created_at, updated_at,
                 fallout_reason, resolved_by, resolution_time)
            )

            # Create eSIM if applicable
            if service_type in ["Mobile", "Bundle"]:
                esim_id = f"ESIM-{uuid.uuid4().hex[:8]}"
                iccid = ''.join(random.choices('0123456789', k=20))
                eid = ''.join(random.choices('0123456789ABCDEF', k=32))

                # Set eSIM status based on fallout
                esim_status = "Active"
                profile_status = "Installed"
                activation_code = f"LPA:{uuid.uuid4().hex}"

                if fallout_reason == "ESIM_ISSUE" and status == "Failed": # Only set failed status if order is currently failed
                    esim_status = "Failed"
                    profile_status = random.choice(["Download Failed", "Installation Failed", "Activation Failed"])
                    activation_code = None

                cursor.execute(
                    "INSERT INTO esims VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (esim_id, order_id, iccid, eid, esim_status, profile_status, activation_code)
                )

            # Create switch configuration if applicable
            if service_type in ["Internet", "TV", "Bundle"]:
                switch_id = f"SW-{uuid.uuid4().hex[:8]}"
                switch_name = random.choice(["SW-NORTH", "SW-SOUTH", "SW-EAST", "SW-WEST"])
                port_id = f"PORT-{random.randint(1, 48)}"

                # Set switch status based on fallout
                config_status = "Configured"

                if fallout_reason == "SWITCH_ISSUE" and status == "Failed": # Only set failed status if order is currently failed
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

            if status == "Failed": # Log failure reason if currently failed
                 if fallout_reason == "NOT_SENT_FOR_ACTIVATION":
                    log_events.append(("ACTIVATION_FAILED", "Order was not sent for activation due to system error"))
                 elif fallout_reason == "ESIM_ISSUE":
                    log_events.append(("ESIM_FAILED", f"eSIM profile issue: {profile_status if 'profile_status' in locals() else 'Unknown'}"))
                 elif fallout_reason == "SWITCH_ISSUE":
                    log_events.append(("SWITCH_CONFIG_FAILED", f"Switch configuration failed: {config_status if 'config_status' in locals() else 'Unknown'}"))
                 elif fallout_reason == "OTHER_ISSUE":
                    log_events.append(("UNKNOWN_ERROR", "An unknown error occurred during activation"))

            elif status == "Completed":
                 if resolved_by: # Log resolution if it was resolved
                    resolution_event_map = {
                        "resubmission_agent": ("ORDER_RESUBMITTED", "Order was successfully resubmitted"),
                        "esim_agent": ("ESIM_REPROVISIONED", "eSIM was successfully reprovisioned"),
                        "switch_agent": ("SWITCH_RECONFIGURED", "Switch was successfully reconfigured"),
                        "human_agent": ("MANUAL_RESOLUTION", "Issue was manually resolved by human agent")
                    }
                    event = resolution_event_map.get(resolved_by)
                    if event:
                        log_events.append(event)
                 log_events.append(("ACTIVATION_COMPLETED", "Service was successfully activated")) # Always log completion if status is Completed

            for event_type, description in log_events:
                log_id = f"LOG-{uuid.uuid4().hex[:8]}"
                # Ensure logs are chronologically plausible relative to creation/update times
                log_time = (datetime.datetime.fromisoformat(created_at) + datetime.timedelta(minutes=random.randint(1, 1440))).isoformat()

                cursor.execute(
                    "INSERT INTO order_logs VALUES (?, ?, ?, ?, ?)",
                    (log_id, order_id, event_type, description, log_time)
                )

        conn.commit()
        logging.info(f"Generated {num_orders} mock orders with related data.")

    except sqlite3.Error as e:
        logging.error(f"Mock data generation failed: {e}")
        if conn:
            conn.rollback() # Rollback changes on error
    finally:
        if conn:
            conn.close()

# ===============================
# Part 3: SQLite Tools and APIs
# ===============================

class TelecomAPI:
    """Provides API access to the telecom database."""

    @staticmethod
    def _get_connection():
        """Get a connection to the SQLite database."""
        # Consider adding pooling for high-concurrency scenarios
        return sqlite3.connect(DB_NAME)

    @staticmethod
    def get_failed_orders(limit: int = 10) -> List[Dict]:
        """Get list of failed orders that are not yet resolved."""
        conn = None
        results = []
        try:
            conn = TelecomAPI._get_connection()
            cursor = conn.cursor()
            query = """
            SELECT o.order_id, o.customer_id, c.name, o.service_type, o.fallout_reason, o.created_at
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.status = 'Failed' AND o.resolved_by IS NULL
            ORDER BY o.created_at ASC -- Process older orders first
            LIMIT ?
            """
            cursor.execute(query, (limit,))
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Error getting failed orders: {e}")
        finally:
            if conn:
                conn.close()
        return results

    @staticmethod
    def get_order_details(order_id: str) -> Optional[Dict]:
        """Get detailed information about an order."""
        conn = None
        order_data = None
        try:
            conn = TelecomAPI._get_connection()
            conn.row_factory = sqlite3.Row # Access columns by name
            cursor = conn.cursor()

            # Get order and customer info
            query = """
            SELECT o.*, c.name, c.email, c.phone, c.address
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_id = ?
            """
            cursor.execute(query, (order_id,))
            order_row = cursor.fetchone()

            if not order_row:
                logging.warning(f"Order ID {order_id} not found.")
                return None

            order_data = dict(order_row)

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

        except sqlite3.Error as e:
            logging.error(f"Error getting details for order {order_id}: {e}")
            order_data = None # Ensure None is returned on error
        finally:
            if conn:
                conn.close()
        return order_data

    @staticmethod
    def _add_log_entry(cursor: sqlite3.Cursor, order_id: str, event_type: str, description: str):
        """Helper to add a log entry."""
        log_id = f"LOG-{uuid.uuid4().hex[:8]}"
        cursor.execute(
            "INSERT INTO order_logs VALUES (?, ?, ?, ?, ?)",
            (log_id, order_id, event_type, description, datetime.datetime.now().isoformat())
        )

    @staticmethod
    def update_order_status(order_id: str, status: str, fallout_reason: Optional[str] = None, resolved_by: Optional[str] = None) -> Dict:
        """Update order status and related fields."""
        conn = None
        success = False
        try:
            conn = TelecomAPI._get_connection()
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
            success = cursor.rowcount > 0
            if success:
                 logging.info(f"Order {order_id} status updated to {status} by {resolved_by or 'API'}.")
                 # Add log entry for status update
                 TelecomAPI._add_log_entry(cursor, order_id, "STATUS_UPDATE", f"Status changed to {status}" + (f" by {resolved_by}" if resolved_by else ""))
                 conn.commit() # Commit log entry
            else:
                 logging.warning(f"Failed to update status for order {order_id} (not found or no change).")

        except sqlite3.Error as e:
            logging.error(f"Error updating status for order {order_id}: {e}")
            if conn:
                conn.rollback()
            success = False
        finally:
            if conn:
                conn.close()
        return {"success": success, "order_id": order_id}

    @staticmethod
    def resubmit_order(order_id: str) -> Dict:
        """Resubmit an order for activation."""
        conn = None
        result = {"success": False, "message": "Failed to resubmit order", "order_id": order_id}
        try:
            conn = TelecomAPI._get_connection()
            cursor = conn.cursor()

            # Check order status and reason
            cursor.execute("SELECT status, fallout_reason FROM orders WHERE order_id = ?", (order_id,))
            order_info = cursor.fetchone()

            if not order_info:
                result["message"] = "Order not found"
                return result

            status, fallout_reason = order_info
            if status != "Failed":
                result["message"] = f"Order is not in Failed state. Current status: {status}"
                return result
            if fallout_reason != "NOT_SENT_FOR_ACTIVATION":
                result["message"] = f"Order fallout reason is not NOT_SENT_FOR_ACTIVATION. Actual: {fallout_reason}"
                return result

            # Simulate processing time
            time.sleep(random.uniform(0.3, 0.8))

            # Update order status via the dedicated method
            update_result = TelecomAPI.update_order_status(order_id, "Completed", None, "resubmission_agent")

            if update_result["success"]:
                # Log specific resubmission event (already logged by update_order_status generally)
                # TelecomAPI._add_log_entry(cursor, order_id, "ORDER_RESUBMITTED", "Order was successfully resubmitted for activation")
                # conn.commit() # Already committed in update_order_status if successful
                result = {
                    "success": True,
                    "order_id": order_id,
                    "message": "Order successfully resubmitted for activation and marked as Completed."
                }
                logging.info(result["message"])
            else:
                 result["message"] = "Failed to update order status during resubmission."
                 logging.error(result["message"])


        except sqlite3.Error as e:
            logging.error(f"Error resubmitting order {order_id}: {e}")
            result["message"] = f"Database error during resubmission: {e}"
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
        return result

    @staticmethod
    def reprovision_esim(order_id: str) -> Dict:
        """Reprovision eSIM for an order."""
        conn = None
        result = {"success": False, "message": "Failed to reprovision eSIM", "order_id": order_id}
        try:
            conn = TelecomAPI._get_connection()
            cursor = conn.cursor()

            # Check order status and reason
            cursor.execute("SELECT status, fallout_reason FROM orders WHERE order_id = ?", (order_id,))
            order_info = cursor.fetchone()
            if not order_info:
                result["message"] = "Order not found"
                return result
            status, fallout_reason = order_info
            if status != "Failed":
                result["message"] = f"Order is not in Failed state. Current status: {status}"
                return result
            if fallout_reason != "ESIM_ISSUE":
                result["message"] = f"Order fallout reason is not ESIM_ISSUE. Actual: {fallout_reason}"
                return result

            # Check if eSIM exists
            cursor.execute("SELECT esim_id FROM esims WHERE order_id = ?", (order_id,))
            esim_info = cursor.fetchone()
            if not esim_info:
                result["message"] = "No eSIM found for this order"
                return result
            esim_id = esim_info[0]

            # Simulate processing time
            time.sleep(random.uniform(0.5, 1.0))

            # Generate new activation code
            new_activation_code = f"LPA:{uuid.uuid4().hex}"

            # Update eSIM status
            cursor.execute(
                "UPDATE esims SET status = ?, profile_status = ?, activation_code = ? WHERE esim_id = ?",
                ("Active", "Installed", new_activation_code, esim_id)
            )
            conn.commit() # Commit eSIM update

            # Update order status
            update_result = TelecomAPI.update_order_status(order_id, "Completed", None, "esim_agent")

            if update_result["success"]:
                 # Log specific reprovision event
                 TelecomAPI._add_log_entry(cursor, order_id, "ESIM_REPROVISIONED", f"eSIM {esim_id} reprovisioned. New code: {new_activation_code}")
                 conn.commit() # Commit log entry
                 result = {
                    "success": True,
                    "order_id": order_id,
                    "esim_id": esim_id,
                    "new_activation_code": new_activation_code,
                    "message": "eSIM successfully reprovisioned and order marked as Completed."
                 }
                 logging.info(result["message"])
            else:
                 result["message"] = "Failed to update order status after eSIM reprovisioning."
                 logging.error(result["message"])
                 # Consider rolling back eSIM update if order status update fails? Depends on business logic.
                 # conn.rollback()

        except sqlite3.Error as e:
            logging.error(f"Error reprovisioning eSIM for order {order_id}: {e}")
            result["message"] = f"Database error during eSIM reprovisioning: {e}"
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
        return result

    @staticmethod
    def reconfigure_switch(order_id: str) -> Dict:
        """Reconfigure switch for an order."""
        conn = None
        result = {"success": False, "message": "Failed to reconfigure switch", "order_id": order_id}
        try:
            conn = TelecomAPI._get_connection()
            cursor = conn.cursor()

            # Check order status and reason
            cursor.execute("SELECT status, fallout_reason FROM orders WHERE order_id = ?", (order_id,))
            order_info = cursor.fetchone()
            if not order_info:
                result["message"] = "Order not found"
                return result
            status, fallout_reason = order_info
            if status != "Failed":
                result["message"] = f"Order is not in Failed state. Current status: {status}"
                return result
            if fallout_reason != "SWITCH_ISSUE":
                result["message"] = f"Order fallout reason is not SWITCH_ISSUE. Actual: {fallout_reason}"
                return result

            # Check if switch exists
            cursor.execute("SELECT switch_id, switch_name, port_id FROM switches WHERE order_id = ?", (order_id,))
            switch_info = cursor.fetchone()
            if not switch_info:
                result["message"] = "No switch configuration found for this order"
                return result
            switch_id, switch_name, port_id = switch_info

            # Simulate processing time
            time.sleep(random.uniform(0.4, 0.9))

            # Update switch status
            cursor.execute(
                "UPDATE switches SET config_status = ?, last_updated = ? WHERE switch_id = ?",
                ("Configured", datetime.datetime.now().isoformat(), switch_id)
            )
            conn.commit() # Commit switch update

            # Update order status
            update_result = TelecomAPI.update_order_status(order_id, "Completed", None, "switch_agent")

            if update_result["success"]:
                # Log specific reconfiguration event
                TelecomAPI._add_log_entry(cursor, order_id, "SWITCH_RECONFIGURED", f"Switch {switch_name} port {port_id} reconfigured.")
                conn.commit() # Commit log entry
                result = {
                    "success": True,
                    "order_id": order_id,
                    "switch_id": switch_id,
                    "switch_name": switch_name,
                    "port_id": port_id,
                    "message": "Switch successfully reconfigured and order marked as Completed."
                }
                logging.info(result["message"])
            else:
                 result["message"] = "Failed to update order status after switch reconfiguration."
                 logging.error(result["message"])
                 # Consider rolling back switch update?
                 # conn.rollback()

        except sqlite3.Error as e:
            logging.error(f"Error reconfiguring switch for order {order_id}: {e}")
            result["message"] = f"Database error during switch reconfiguration: {e}"
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
        return result

    @staticmethod
    def mark_for_human_intervention(order_id: str, notes: str) -> Dict:
        """Mark an order for human intervention."""
        conn = None
        result = {"success": False, "message": "Failed to mark for human intervention", "order_id": order_id}
        try:
            conn = TelecomAPI._get_connection()
            cursor = conn.cursor()

            # Check if order exists
            cursor.execute("SELECT status FROM orders WHERE order_id = ?", (order_id,))
            order_info = cursor.fetchone()
            if not order_info:
                result["message"] = "Order not found"
                return result

            # Add log entry with notes
            description = f"Order marked for human intervention. Notes: {notes}"
            TelecomAPI._add_log_entry(cursor, order_id, "HUMAN_INTERVENTION_NEEDED", description)

            # Update order's updated_at timestamp (status remains Failed)
            updated_at = datetime.datetime.now().isoformat()
            cursor.execute(
                "UPDATE orders SET updated_at = ?, resolved_by = ? WHERE order_id = ?", # Mark as resolved by human_agent for tracking
                (updated_at, 'human_agent', order_id)
            )

            conn.commit()
            result = {
                "success": True,
                "order_id": order_id,
                "message": "Order successfully marked for human intervention.",
                "notes": notes
            }
            logging.info(f"Order {order_id} marked for human intervention. Notes: {notes}")

        except sqlite3.Error as e:
            logging.error(f"Error marking order {order_id} for human intervention: {e}")
            result["message"] = f"Database error marking for human intervention: {e}"
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
        return result

# ======================================
# Part 4: Define Tool Schemas and Tools
# ======================================

# Define Pydantic models for tool arguments for better validation and clarity
class GetFailedOrdersInput(BaseModel):
    limit: int = Field(10, description="Maximum number of failed orders to return")

class GetOrderDetailsInput(BaseModel):
    order_id: str = Field(..., description="The unique ID of the order to fetch details for")

class ResubmitOrderInput(BaseModel):
    order_id: str = Field(..., description="The unique ID of the order to resubmit")

class ReprovisionEsimInput(BaseModel):
    order_id: str = Field(..., description="The unique ID of the order whose eSIM needs reprovisioning")

class ReconfigureSwitchInput(BaseModel):
    order_id: str = Field(..., description="The unique ID of the order whose switch needs reconfiguration")

class MarkForHumanInterventionInput(BaseModel):
    order_id: str = Field(..., description="The unique ID of the order to mark for human review")
    notes: str = Field(..., description="Detailed notes explaining why human intervention is required")


# Create LangChain Tools
# Note: Using Pydantic models (args_schema=...) is the modern way
telecom_tools = [
    Tool(
        name="get_failed_orders",
        description="Get a list of recently failed orders that need resolution and are not yet resolved.",
        func=TelecomAPI.get_failed_orders,
        args_schema=GetFailedOrdersInput
    ),
    Tool(
        name="get_order_details",
        description="Get detailed information about a specific order using its ID, including customer info, status, fallout reason, eSIM/switch details (if applicable), and logs.",
        func=TelecomAPI.get_order_details,
        args_schema=GetOrderDetailsInput
    ),
    Tool(
        name="resubmit_order",
        description="Resubmit an order that failed specifically because it was 'NOT_SENT_FOR_ACTIVATION'. This attempts to fix the issue and mark the order as Completed.",
        func=TelecomAPI.resubmit_order,
        args_schema=ResubmitOrderInput
    ),
    Tool(
        name="reprovision_esim",
        description="Reprovision an eSIM for an order that failed specifically due to an 'ESIM_ISSUE'. This attempts to fix the issue, generate a new activation code, and mark the order as Completed.",
        func=TelecomAPI.reprovision_esim,
        args_schema=ReprovisionEsimInput
    ),
    Tool(
        name="reconfigure_switch",
        description="Reconfigure the network switch port for an order that failed specifically due to a 'SWITCH_ISSUE'. This attempts to fix the configuration and mark the order as Completed.",
        func=TelecomAPI.reconfigure_switch,
        args_schema=ReconfigureSwitchInput
    ),
    Tool(
        name="mark_for_human_intervention",
        description="Mark an order for manual review by a human agent. Use this when automated resolution fails or the issue type is 'OTHER_ISSUE' or unclear. Provide detailed notes.",
        func=TelecomAPI.mark_for_human_intervention,
        args_schema=MarkForHumanInterventionInput
    )
]

# Tool Executor will run the tools when called by the LLM
tool_executor = ToolExecutor(telecom_tools)

# ==============================
# Part 5: Define LLM and Prompts
# ==============================

# ******************************************************************************
# TODO: Instantiate your Gemini LLM here
# Replace this placeholder with your actual Gemini Chat Model instance
# Example (replace with actual Gemini client/model setup):
# from langchain_google_genai import ChatGoogleGenerativeAI
# llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)

# Placeholder LLM - replace this!
class PlaceholderChatModel(BaseChatModel):
    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs) -> Any:
        # This is a dummy implementation. Replace with actual LLM call.
        last_message = messages[-1].content if messages else ""
        response_content = f"Placeholder response based on: {last_message[:50]}..."

        # Simulate tool calling based on keywords
        tool_calls = []
        if "details for order" in last_message.lower():
            order_id_match = re.search(r'ORD-[0-9A-Fa-f]{8}', last_message)
            if order_id_match:
                 tool_calls.append({"name": "get_order_details", "args": {"order_id": order_id_match.group(0)}, "id": "tool_call_1"})
        elif "resubmit order" in last_message.lower():
             order_id_match = re.search(r'ORD-[0-9A-Fa-f]{8}', last_message)
             if order_id_match:
                 tool_calls.append({"name": "resubmit_order", "args": {"order_id": order_id_match.group(0)}, "id": "tool_call_2"})
        # Add more dummy tool call logic if needed for testing without a real LLM

        return AIMessage(content=response_content, tool_calls=tool_calls if tool_calls else None)

    async def _agenerate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs) -> Any:
         # Dummy async implementation
        return self._generate(messages, stop, **kwargs)

    @property
    def _llm_type(self) -> str:
        return "placeholder-chat-model"

# Use the placeholder for now
# llm = PlaceholderChatModel()
# IMPORTANT: You MUST replace the above PlaceholderChatModel with your actual Gemini LLM instance.
# For now, we comment it out to avoid errors if no LLM is configured.
# The script will error later if llm is not defined when agents are called.
# Ensure you define 'llm' before running the workflow.
print("WARNING: LLM is not defined. Replace PlaceholderChatModel or uncomment and configure your Gemini LLM.")
llm = None # Explicitly set to None, ensure it's defined before running run_telecom_workflow

# ******************************************************************************


# Define system prompts for each agent
master_agent_prompt = """
You are the Master Telecom Agent, the central dispatcher for analyzing and routing telecom order fallouts.

Your primary goal is to accurately identify the reason for an order failure and route it to the correct specialized agent or to human intervention if necessary.

Follow these steps:
1. Receive the initial request containing an order ID.
2. Use the `get_order_details` tool to fetch comprehensive information about the specified order. Pay close attention to the `status`, `fallout_reason`, and `logs`.
3. Analyze the fetched details:
    - If `fallout_reason` is 'NOT_SENT_FOR_ACTIVATION', determine routing to 'resubmission_agent'.
    - If `fallout_reason` is 'ESIM_ISSUE', determine routing to 'esim_agent'.
    - If `fallout_reason` is 'SWITCH_ISSUE', determine routing to 'switch_agent'.
    - If `fallout_reason` is 'OTHER_ISSUE', or if the reason is unclear/missing despite the order being 'Failed', determine routing to 'human_agent'.
    - If the order status is NOT 'Failed', state that the order doesn't require fallout processing.
4. Respond clearly stating the identified fallout type (or lack thereof) and the determined routing path (e.g., "Routing to esim_agent for ESIM_ISSUE."). Do NOT attempt to resolve the issue yourself. Your sole job is analysis and routing.
"""

resubmission_agent_prompt = """
You are the Resubmission Agent, specialized in handling orders that failed because they were 'NOT_SENT_FOR_ACTIVATION'.

Your task is to attempt automatic resubmission. Follow these steps:
1. Receive the order details from the Master Agent. Confirm the `fallout_reason` is indeed 'NOT_SENT_FOR_ACTIVATION'.
2. If the reason is correct, use the `resubmit_order` tool with the correct `order_id`.
3. Analyze the tool's response:
    - If `success` is True, report that the order was successfully resubmitted and is now marked as Completed.
    - If `success` is False, analyze the `message` from the tool. Report the failure and the reason. Recommend escalating to human intervention by stating "Escalating to human_agent due to resubmission failure: [reason]".
4. If the initial `fallout_reason` was NOT 'NOT_SENT_FOR_ACTIVATION', state this is the wrong agent and recommend routing to 'human_agent' for re-evaluation.
"""

esim_agent_prompt = """
You are the eSIM Agent, specialized in resolving 'ESIM_ISSUE' fallouts.

Your task is to attempt automatic eSIM reprovisioning. Follow these steps:
1. Receive the order details. Confirm the `fallout_reason` is 'ESIM_ISSUE'.
2. If the reason is correct, use the `reprovision_esim` tool with the correct `order_id`.
3. Analyze the tool's response:
    - If `success` is True, report the successful reprovisioning, including the `new_activation_code`, and state the order is now Completed.
    - If `success` is False, analyze the `message`. Report the failure and reason. Recommend escalating by stating "Escalating to human_agent due to eSIM reprovisioning failure: [reason]".
4. If the initial `fallout_reason` was not 'ESIM_ISSUE', state this is the wrong agent and recommend routing to 'human_agent' for re-evaluation.
"""

switch_agent_prompt = """
You are the Switch Agent, specialized in resolving 'SWITCH_ISSUE' fallouts related to network configuration.

Your task is to attempt automatic switch reconfiguration. Follow these steps:
1. Receive the order details. Confirm the `fallout_reason` is 'SWITCH_ISSUE'.
2. If the reason is correct, use the `reconfigure_switch` tool with the correct `order_id`.
3. Analyze the tool's response:
    - If `success` is True, report the successful reconfiguration (mentioning switch and port if available in the response) and state the order is now Completed.
    - If `success` is False, analyze the `message`. Report the failure and reason. Recommend escalating by stating "Escalating to human_agent due to switch reconfiguration failure: [reason]".
4. If the initial `fallout_reason` was not 'SWITCH_ISSUE', state this is the wrong agent and recommend routing to 'human_agent' for re-evaluation.
"""

human_agent_prompt = """
You are the Human Intervention Agent. Your role is to formally log cases that require manual review because automated agents could not resolve them or the issue type was initially unclear ('OTHER_ISSUE').

Your task is to use the `mark_for_human_intervention` tool. Follow these steps:
1. Receive the order details and the reason for escalation (e.g., from Master Agent for 'OTHER_ISSUE', or from a specialist agent after a failed attempt).
2. Synthesize the situation into concise notes. Include the `order_id`, the original `fallout_reason` (if known), and why automation failed or wasn't applicable.
3. Use the `mark_for_human_intervention` tool, providing the `order_id` and the synthesized `notes`.
4. Report the outcome of the tool call. If successful, confirm that the order has been flagged for manual review with the provided notes. If it fails, report the error.
"""

# ==============================
# Part 6: Define Agent State
# ==============================

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages] # Automatically accumulates messages
    order_id: Optional[str]
    fallout_type: Optional[str] # Determined by master agent
    resolution_path: Optional[str] # Tracks which agent handled it (or tried to)
    resolution_status: Literal["PENDING", "RESOLVED", "FAILED_AUTOMATION", "HUMAN_INTERVENTION_REQUESTED"]
    error_message: Optional[str] # To store error details if automation fails

# ====================================
# Part 7: Define Agent Node Functions
# ====================================

# Helper function to create agent nodes
def create_agent_node(llm: BaseChatModel, system_prompt: str):
    """Factory function to create agent nodes."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])
    agent_runnable = prompt | llm # Chain prompt and LLM
    return agent_runnable

# Helper function to execute tools and format results
def execute_tools(state: AgentState) -> AgentState:
    """Executes tools based on the last message and returns updated state."""
    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        # No tool calls requested
        return state

    # Ensure state elements that might be updated exist
    updated_state = state.copy()
    updated_state["error_message"] = None # Clear previous errors

    tool_call_results = []
    for tool_call in last_message.tool_calls:
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args", {})
        tool_call_id = tool_call.get("id") # Important for ToolMessage

        logging.info(f"Invoking tool: {tool_name} with args: {tool_args}")
        try:
            # Ensure args are passed correctly to the executor
            # ToolExecutor expects a ToolInvocation object or similar structure
            # Let's try invoking directly with name and args
            tool_result = tool_executor.invoke({
                "tool": tool_name,
                "tool_input": tool_args
            })

            # Append result as ToolMessage
            tool_call_results.append(ToolMessage(
                content=json.dumps(tool_result), # Content must be string
                tool_call_id=tool_call_id,
                name=tool_name # Include tool name for context
            ))

            # --- Update state based on tool results ---
            # Master agent determines fallout type after get_order_details
            if tool_name == "get_order_details":
                 if isinstance(tool_result, dict):
                     updated_state["order_id"] = tool_result.get("order_id")
                     updated_state["fallout_type"] = tool_result.get("fallout_reason")
                     if tool_result.get("status") != "Failed":
                          updated_state["fallout_type"] = "NOT_FAILED" # Special case
                 else:
                     updated_state["error_message"] = "get_order_details returned unexpected format."
                     updated_state["resolution_status"] = "FAILED_AUTOMATION"


            # Specialist agents determine resolution status
            elif tool_name in ["resubmit_order", "reprovision_esim", "reconfigure_switch"]:
                agent_map = {
                    "resubmit_order": "resubmission_agent",
                    "reprovision_esim": "esim_agent",
                    "reconfigure_switch": "switch_agent"
                }
                updated_state["resolution_path"] = agent_map[tool_name]
                if isinstance(tool_result, dict) and tool_result.get("success"):
                    updated_state["resolution_status"] = "RESOLVED"
                else:
                    updated_state["resolution_status"] = "FAILED_AUTOMATION"
                    updated_state["error_message"] = tool_result.get("message", "Tool execution failed.") if isinstance(tool_result, dict) else "Tool execution failed."

            # Human agent marks for intervention
            elif tool_name == "mark_for_human_intervention":
                 updated_state["resolution_path"] = "human_agent"
                 if isinstance(tool_result, dict) and tool_result.get("success"):
                     updated_state["resolution_status"] = "HUMAN_INTERVENTION_REQUESTED"
                 else:
                     # Even if marking fails, we probably still need human intervention
                     updated_state["resolution_status"] = "HUMAN_INTERVENTION_REQUESTED" # Or FAILED_AUTOMATION?
                     updated_state["error_message"] = tool_result.get("message", "Failed to mark for human intervention.") if isinstance(tool_result, dict) else "Failed to mark for human intervention."


        except Exception as e:
            logging.error(f"Error executing tool {tool_name}: {e}")
            # Append error as ToolMessage
            tool_call_results.append(ToolMessage(
                content=json.dumps({"error": str(e)}),
                tool_call_id=tool_call_id,
                name=tool_name
            ))
            updated_state["resolution_status"] = "FAILED_AUTOMATION"
            updated_state["error_message"] = f"Exception during tool execution: {e}"


    # Add all tool results to messages
    updated_state["messages"] = add_messages(updated_state["messages"], tool_call_results)

    return updated_state


# Define the agent execution logic combining LLM call and tool execution
async def agent_node(state: AgentState, agent_runnable: Any, name: str) -> AgentState:
    """Runs the agent LLM, executes tools if needed, and returns updated state."""
    logging.info(f"--- Entering {name} ---")
    # Run the LLM
    result = await agent_runnable.ainvoke(state) # Use async invoke

    # Add LLM response to state
    # Ensure result is an AIMessage or BaseMessage
    if not isinstance(result, BaseMessage):
         # Handle unexpected LLM output format
         logging.error(f"{name} LLM did not return a BaseMessage. Got: {type(result)}")
         # Create an error message or handle appropriately
         # For now, just add the raw result if possible, or an error message
         error_content = f"LLM output error in {name}. Type: {type(result)}"
         updated_state = add_messages(state, AIMessage(content=error_content))
         updated_state["resolution_status"] = "FAILED_AUTOMATION"
         updated_state["error_message"] = error_content
         return updated_state # Return immediately on LLM error


    updated_state = add_messages(state, result) # Add AIMessage

    # Check if tools need to be executed
    if isinstance(result, AIMessage) and result.tool_calls:
        # Execute tools and get the next state
        tool_state = execute_tools(updated_state)
        logging.info(f"--- Exiting {name} after tool execution ---")
        return tool_state
    else:
        # No tool calls, just return the state with the LLM response
        # Check if the LLM recommended escalation without calling a tool
        if "escalating to human_agent" in result.content.lower():
             updated_state["resolution_status"] = "FAILED_AUTOMATION" # Treat recommendation as failure
             updated_state["resolution_path"] = name # Agent that recommended escalation
        logging.info(f"--- Exiting {name} (no tool call) ---")
        return updated_state


# =====================================
# Part 8: Define Graph Nodes and Edges
# =====================================

# Create agent runnables (assuming llm is defined)
if llm:
    master_agent_runnable = create_agent_node(llm, master_agent_prompt)
    resubmission_agent_runnable = create_agent_node(llm, resubmission_agent_prompt)
    esim_agent_runnable = create_agent_node(llm, esim_agent_prompt)
    switch_agent_runnable = create_agent_node(llm, switch_agent_prompt)
    human_agent_runnable = create_agent_node(llm, human_agent_prompt)
else:
    # Handle case where LLM is not defined - graph compilation will fail later
    master_agent_runnable = None
    # ... and so on for other agents

# Define node functions using the agent_node helper
async def master_agent_node(state: AgentState):
    return await agent_node(state, master_agent_runnable, "Master Agent")

async def resubmission_agent_node(state: AgentState):
    return await agent_node(state, resubmission_agent_runnable, "Resubmission Agent")

async def esim_agent_node(state: AgentState):
    return await agent_node(state, esim_agent_runnable, "eSIM Agent")

async def switch_agent_node(state: AgentState):
    return await agent_node(state, switch_agent_runnable, "Switch Agent")

async def human_agent_node(state: AgentState):
    # Human agent node might need slightly different logic if it doesn't call back to LLM after tool
    logging.info("--- Entering Human Agent ---")
    # Run the LLM to generate notes and decide to call the tool
    llm_result = await human_agent_runnable.ainvoke(state)
    updated_state = add_messages(state, llm_result)

    if isinstance(llm_result, AIMessage) and llm_result.tool_calls:
        # Execute the mark_for_human_intervention tool
        tool_state = execute_tools(updated_state)
        # Human agent node typically ends after marking, no further LLM call needed
        logging.info("--- Exiting Human Agent after tool execution ---")
        return tool_state
    else:
         # LLM didn't call the tool (maybe an error or unexpected response)
         logging.warning("Human Agent LLM did not request tool call.")
         updated_state["resolution_status"] = "FAILED_AUTOMATION" # Mark as failed if tool wasn't called
         updated_state["error_message"] = "Human agent failed to call the mark_for_human_intervention tool."
         logging.info("--- Exiting Human Agent (no tool call) ---")
         return updated_state


# Define conditional routing logic
def route_from_master(state: AgentState) -> Literal["resubmission_agent", "esim_agent", "switch_agent", "human_agent", "__end__"]:
    """Routes from Master Agent based on determined fallout type."""
    fallout_type = state.get("fallout_type")
    logging.info(f"Routing from Master: Fallout Type = {fallout_type}")

    if fallout_type == "NOT_SENT_FOR_ACTIVATION":
        return "resubmission_agent"
    elif fallout_type == "ESIM_ISSUE":
        return "esim_agent"
    elif fallout_type == "SWITCH_ISSUE":
        return "switch_agent"
    elif fallout_type == "NOT_FAILED": # Order was not actually failed
         logging.info("Order status is not Failed. Ending workflow.")
         return "__end__"
    else: # Includes "OTHER_ISSUE", None, or any unexpected value
        logging.info("Routing to Human Agent due to unclear or 'OTHER' issue type.")
        # Add a message indicating why it's going to human agent
        state["messages"] = add_messages(state["messages"], AIMessage(content=f"Routing to human agent: Fallout type is '{fallout_type}'."))
        return "human_agent"

def route_from_specialist(state: AgentState) -> Literal["human_agent", "__end__"]:
    """Routes from specialist agents based on resolution status."""
    resolution_status = state.get("resolution_status")
    resolution_path = state.get("resolution_path", "Unknown Agent")
    logging.info(f"Routing from {resolution_path}: Resolution Status = {resolution_status}")

    if resolution_status == "RESOLVED":
        logging.info("Resolution successful. Ending workflow.")
        return "__end__"
    elif resolution_status == "FAILED_AUTOMATION":
        logging.warning(f"Automation failed by {resolution_path}. Escalating to Human Agent.")
        # Add a message indicating why it's going to human agent
        error_msg = state.get('error_message', 'Unknown error')
        state["messages"] = add_messages(state["messages"], AIMessage(content=f"Escalating to human agent from {resolution_path} due to failure: {error_msg}"))
        return "human_agent"
    else:
        # Should not happen if logic is correct, but default to human agent
        logging.error(f"Unexpected resolution status '{resolution_status}' from {resolution_path}. Routing to Human Agent.")
        state["messages"] = add_messages(state["messages"], AIMessage(content=f"Unexpected status '{resolution_status}' from {resolution_path}. Escalating to human agent."))
        return "human_agent"


# ==============================
# Part 9: Build the Graph
# ==============================

# Ensure LLM is defined before building the graph
if not llm:
    raise ValueError("LLM instance ('llm') is not defined. Please configure your Gemini LLM.")

# Create a new graph
telecom_workflow = StateGraph(AgentState)

# Add nodes to the graph
telecom_workflow.add_node("master_agent", master_agent_node)
telecom_workflow.add_node("resubmission_agent", resubmission_agent_node)
telecom_workflow.add_node("esim_agent", esim_agent_node)
telecom_workflow.add_node("switch_agent", switch_agent_node)
telecom_workflow.add_node("human_agent", human_agent_node)

# Define the edges

# Start with the master agent
telecom_workflow.set_entry_point("master_agent")

# Route from master agent to specialists or human agent
telecom_workflow.add_conditional_edges(
    "master_agent",
    route_from_master,
    {
        "resubmission_agent": "resubmission_agent",
        "esim_agent": "esim_agent",
        "switch_agent": "switch_agent",
        "human_agent": "human_agent",
        "__end__": END # End if order is not failed
    }
)

# Route from specialist agents: end if resolved, else go to human agent
telecom_workflow.add_conditional_edges(
    "resubmission_agent",
    route_from_specialist,
    {
        "__end__": END,
        "human_agent": "human_agent"
    }
)
telecom_workflow.add_conditional_edges(
    "esim_agent",
    route_from_specialist,
    {
        "__end__": END,
        "human_agent": "human_agent"
    }
)
telecom_workflow.add_conditional_edges(
    "switch_agent",
    route_from_specialist,
    {
        "__end__": END,
        "human_agent": "human_agent"
    }
)

# Human agent node always leads to the end (after marking for intervention)
# The 'human_agent_node' function itself updates the status to HUMAN_INTERVENTION_REQUESTED
# We might want a final check after human_agent node, but for now, let's end.
telecom_workflow.add_edge("human_agent", END)


# Compile the graph
# Use async version if nodes are async
telecom_app = telecom_workflow.compile()

# ===============================
# Part 10: Visualize the Graph
# ===============================

def visualize_graph(graph_app=None):
    """Visualize the compiled LangGraph app."""
    if graph_app is None:
        logging.warning("Graph app not provided for visualization.")
        return

    try:
        # Get graph structure (may vary based on LangGraph version)
        # Option 1: Use get_graph method if available
        # graph = graph_app.get_graph()
        # graph.print_ascii() # Simple text representation

        # Option 2: Generate image (more visual)
        image_bytes = graph_app.get_graph().draw_mermaid_png()
        display(Image(image_bytes))
        logging.info("Displaying graph visualization.")

    except Exception as e:
        logging.error(f"Failed to visualize graph: {e}")
        print("Could not generate graph visualization. Ensure graphviz or mermaid support is correctly installed.")
        # Fallback: Manual visualization using NetworkX (less accurate for complex conditionals)
        # visualize_graph_manual()

def visualize_graph_manual():
     """Visualize the telecom workflow graph manually using NetworkX."""
     # Create a directed graph for visualization
     G = nx.DiGraph()

     nodes = ["Master Agent", "Resubmission Agent", "eSIM Agent", "Switch Agent", "Human Agent", "END"]
     node_ids = ["master_agent", "resubmission_agent", "esim_agent", "switch_agent", "human_agent", "END"]
     node_map = dict(zip(node_ids, nodes))

     # Add nodes
     for node_id, label in node_map.items():
         G.add_node(node_id, label=label)

     # Add edges based on routing logic
     # Master routes
     G.add_edge("master_agent", "resubmission_agent", label="NOT_SENT")
     G.add_edge("master_agent", "esim_agent", label="ESIM_ISSUE")
     G.add_edge("master_agent", "switch_agent", label="SWITCH_ISSUE")
     G.add_edge("master_agent", "human_agent", label="OTHER/UNKNOWN")
     G.add_edge("master_agent", "END", label="NOT_FAILED")


     # Specialist routes
     G.add_edge("resubmission_agent", "END", label="Resolved")
     G.add_edge("resubmission_agent", "human_agent", label="Failed")
     G.add_edge("esim_agent", "END", label="Resolved")
     G.add_edge("esim_agent", "human_agent", label="Failed")
     G.add_edge("switch_agent", "END", label="Resolved")
     G.add_edge("switch_agent", "human_agent", label="Failed")

     # Human route
     G.add_edge("human_agent", "END", label="Marked") # Human agent marks and ends

     # Set up positions (adjust for better layout)
     pos = {
         "master_agent": (0, 1),
         "resubmission_agent": (-3, -1),
         "esim_agent": (-1, -1),
         "switch_agent": (1, -1),
         "human_agent": (3, -1),
         "END": (0, -3)
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
     plt.figure(figsize=(16, 10))

     # Draw nodes with colors
     for node_id in G.nodes():
         nx.draw_networkx_nodes(G, pos, nodelist=[node_id], node_color=node_colors.get(node_id, 'white'), node_size=3000, alpha=0.9)

     # Draw edges
     nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.7, edge_color="gray", arrows=True, arrowsize=20, connectionstyle='arc3,rad=0.1')

     # Draw node labels
     labels = nx.get_node_attributes(G, "label")
     nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight="bold")

     # Draw edge labels
     edge_labels = nx.get_edge_attributes(G, "label")
     nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9, label_pos=0.3)

     plt.title("Telecom Activation Fallout Workflow (Manual Visualization)", fontsize=16)
     plt.axis("off")
     plt.tight_layout()
     plt.show()
     logging.info("Displaying manual graph visualization.")


# ===================================
# Part 11: Example Run Functions
# ===================================

async def run_telecom_workflow(order_id: Optional[str] = None):
    """Run the telecom workflow for a specific order or a random failed one."""
    global telecom_app # Ensure we use the compiled app

    if not llm:
         print("ERROR: LLM is not defined. Cannot run workflow.")
         return None

    if not telecom_app:
        print("ERROR: Graph application (telecom_app) is not compiled.")
        return None

    # Initialize the database and generate data if it doesn't exist
    if not os.path.exists(DB_NAME):
        print(f"Database {DB_NAME} not found. Initializing and generating mock data...")
        initialize_database()
        generate_mock_data(50) # Generate some data
    else:
        print(f"Using existing database: {DB_NAME}")


    # If no order_id is provided, get a random failed, unresolved order
    target_order_id = order_id
    if target_order_id is None:
        print("No specific order ID provided. Fetching a random failed, unresolved order...")
        failed_orders = TelecomAPI.get_failed_orders(limit=50) # Get a larger pool
        unresolved_failed = [o for o in failed_orders if o['fallout_reason']] # Filter for actual fallouts
        if unresolved_failed:
            target_order_id = random.choice(unresolved_failed)["order_id"]
            print(f"Selected random failed order: {target_order_id}")
        else:
            print("No suitable failed, unresolved orders found in the database.")
            # Optionally generate more data here if needed
            # print("Generating more mock data...")
            # generate_mock_data(20)
            # failed_orders = TelecomAPI.get_failed_orders(1)
            # if failed_orders:
            #     target_order_id = failed_orders[0]["order_id"]
            # else:
            #     print("Still no failed orders available.")
            #     return None
            return None # Exit if no order found

    # Get order details to show initial state
    print(f"\n==== Starting Workflow for Order ID: {target_order_id} ====")
    initial_order_details = TelecomAPI.get_order_details(target_order_id)

    if not initial_order_details:
        print(f"ERROR: Could not retrieve details for order {target_order_id}. Aborting.")
        return None

    print(f"Customer: {initial_order_details.get('name')} ({initial_order_details.get('customer_id')})")
    print(f"Service Type: {initial_order_details.get('service_type')}")
    print(f"Initial Status: {initial_order_details.get('status')}")
    print(f"Initial Fallout Reason: {initial_order_details.get('fallout_reason')}")
    print("-" * 60)

    # Define initial inputs for the workflow
    initial_state = AgentState(
        messages=[
            HumanMessage(
                content=f"Please analyze and resolve the fallout for order ID {target_order_id}."
            )
        ],
        order_id=target_order_id, # Start with order_id known
        fallout_type=None,
        resolution_path=None,
        resolution_status="PENDING",
        error_message=None
    )

    # Execute the workflow asynchronously
    final_state = None
    try:
        # Use astream for potentially long-running processes
        async for event in telecom_app.astream(initial_state):
            # You can inspect events here if needed (e.g., print node outputs)
            # print(f"Event: {event}")
            # The final state is the last event yielded
             for key, value in event.items():
                  print(f"--- {key} ---")
                  print(value)
                  print("\n")
                  final_state = value # Keep track of the latest state


    except Exception as e:
        logging.error(f"Workflow execution failed for order {target_order_id}: {e}")
        print(f"\nERROR: Workflow execution failed: {e}")
        # Attempt to get the state at the point of failure if possible
        # final_state = ... # This might be tricky depending on where the error occurred
        return None # Indicate failure

    # Check the final state of the order from the database
    print("\n" + "=" * 60)
    print("==== Workflow Finished ====")
    updated_order = TelecomAPI.get_order_details(target_order_id)

    if not updated_order:
         print(f"ERROR: Could not retrieve final details for order {target_order_id}.")
         return final_state # Return the graph state anyway

    print(f"Order ID: {target_order_id}")
    print(f"Final DB Status: {updated_order.get('status')}")
    print(f"Final DB Fallout Reason: {updated_order.get('fallout_reason')}")
    print(f"Resolved By (DB): {updated_order.get('resolved_by')}")

    # Display info from the final graph state
    if final_state:
        print(f"\nGraph Resolution Status: {final_state.get('resolution_status')}")
        print(f"Graph Resolution Path: {final_state.get('resolution_path')}")
        if final_state.get('error_message'):
            print(f"Graph Error Message: {final_state.get('error_message')}")

        # Print the conversation history
        print("\n==== Conversation History (Graph State) ====")
        for message in final_state.get("messages", []):
            role = "Unknown"
            content = ""
            tool_info = ""
            if isinstance(message, HumanMessage):
                role = "Human"
                content = message.content
            elif isinstance(message, AIMessage):
                role = "AI"
                content = message.content
                if message.tool_calls:
                    tool_info = f" -> Calls Tools: {[tc['name'] for tc in message.tool_calls]}"
            elif isinstance(message, ToolMessage):
                 role = f"Tool ({message.name})"
                 # Try to parse content, limit length
                 try:
                     parsed_content = json.loads(message.content)
                     content = json.dumps(parsed_content, indent=2)[:500] # Pretty print, limit length
                     if len(json.dumps(parsed_content)) > 500: content += "..."
                 except json.JSONDecodeError:
                     content = message.content[:500] + ("..." if len(message.content) > 500 else "")

            print(f"\n{role}:{tool_info}\n{content}")
    else:
        print("\nFinal graph state is not available.")

    return final_state


# ================================
# Part 12: Monitoring Functions
# ================================

def display_order_statistics():
    """Display statistics about orders in the database using Pandas and Matplotlib."""
    conn = None
    try:
        conn = TelecomAPI._get_connection()
        # Use pandas read_sql for convenience
        orders_df = pd.read_sql_query("SELECT * FROM orders", conn)

        if orders_df.empty:
            print("No orders found in the database.")
            return

        print("\n" + "=" * 60)
        print("==== Order Statistics ====")
        print(f"Total Orders: {len(orders_df)}")

        # Status Distribution
        status_counts = orders_df['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        print("\nStatus Distribution:")
        display(status_counts)

        # Fallout Reason Distribution (excluding None)
        fallout_counts = orders_df.dropna(subset=['fallout_reason'])['fallout_reason'].value_counts().reset_index()
        fallout_counts.columns = ['Fallout Reason', 'Count']
        print("\nFallout Reason Distribution:")
        if not fallout_counts.empty:
             display(fallout_counts)
        else:
             print("No orders with fallout reasons found.")


        # Resolver Distribution (excluding None)
        resolver_counts = orders_df.dropna(subset=['resolved_by'])['resolved_by'].value_counts().reset_index()
        resolver_counts.columns = ['Resolved By', 'Count']
        print("\nResolver Distribution:")
        if not resolver_counts.empty:
            display(resolver_counts)
        else:
            print("No resolved orders found.")


        # --- Create Plots ---
        num_plots = 1 + (not fallout_counts.empty) + (not resolver_counts.empty)
        if num_plots == 1 and status_counts.empty: # No data at all
             return

        fig, axes = plt.subplots(1, num_plots, figsize=(6 * num_plots, 5))
        if num_plots == 1: axes = [axes] # Make axes iterable if only one plot

        plot_index = 0

        # Status Plot
        if not status_counts.empty:
             axes[plot_index].bar(status_counts['Status'], status_counts['Count'], color='skyblue')
             axes[plot_index].set_title("Order Status Distribution")
             axes[plot_index].set_ylabel("Count")
             axes[plot_index].tick_params(axis='x', rotation=45)
             plot_index += 1


        # Fallout Plot
        if not fallout_counts.empty:
             axes[plot_index].bar(fallout_counts['Fallout Reason'], fallout_counts['Count'], color='salmon')
             axes[plot_index].set_title("Fallout Reason Distribution")
             axes[plot_index].set_ylabel("Count")
             axes[plot_index].tick_params(axis='x', rotation=45)
             plot_index += 1

        # Resolver Plot
        if not resolver_counts.empty:
             axes[plot_index].bar(resolver_counts['Resolved By'], resolver_counts['Count'], color='lightgreen')
             axes[plot_index].set_title("Resolver Distribution")
             axes[plot_index].set_ylabel("Count")
             axes[plot_index].tick_params(axis='x', rotation=45)
             plot_index += 1


        plt.tight_layout()
        plt.show()

    except sqlite3.Error as e:
        logging.error(f"Database error during statistics generation: {e}")
    except Exception as e:
         logging.error(f"Error generating statistics plot: {e}") # Catch plotting errors
    finally:
        if conn:
            conn.close()


# =====================================
# Part 13: Notebook Demo Main Section
# =====================================

async def run_demo():
    """Main async function to run the notebook demo."""
    print("*"*80)
    print("Welcome to the Telecom Activation Fallout Management System (LangGraph Demo)")
    print("*"*80)
    print("This system uses LangGraph to orchestrate multiple AI agents to resolve telecom order issues.")

    # --- Step 1: Initialize Database ---
    print("\n--- Step 1: Initializing Database ---")
    initialize_database()
    # Optionally generate fresh data each time, or use existing if available
    # print("Generating fresh mock data...")
    # generate_mock_data(75) # Generate a decent number
    if not os.path.exists(DB_NAME) or os.path.getsize(DB_NAME) < 1024: # Simple check if DB seems empty
         print("Database appears empty or new. Generating mock data...")
         generate_mock_data(75)
    else:
         print("Using existing data in database.")


    # --- Step 2: Display Initial Statistics ---
    print("\n--- Step 2: Displaying Initial Order Statistics ---")
    display_order_statistics()

    # --- Step 3: Visualize the Workflow Graph ---
    print("\n--- Step 3: Visualizing Agent Workflow ---")
    # Ensure the app is compiled before visualizing
    if telecom_app:
         visualize_graph(telecom_app)
         # visualize_graph_manual() # Optional manual visualization
    else:
         print("Graph app not compiled, cannot visualize.")


    # --- Step 4: Run Example Workflows ---
    print("\n--- Step 4: Running Example Workflows ---")
    print("Attempting to find one unresolved example for each fallout type...")

    # Find one unresolved order of each fallout type still in 'Failed' state
    conn = None
    example_orders = {}
    try:
        conn = TelecomAPI._get_connection()
        cursor = conn.cursor()
        fallout_types_to_find = ["NOT_SENT_FOR_ACTIVATION", "ESIM_ISSUE", "SWITCH_ISSUE", "OTHER_ISSUE"]
        for ft in fallout_types_to_find:
            cursor.execute("""
                SELECT order_id FROM orders
                WHERE fallout_reason = ? AND status = 'Failed' AND resolved_by IS NULL
                LIMIT 1
            """, (ft,))
            result = cursor.fetchone()
            if result:
                example_orders[ft] = result[0]
            else:
                print(f"Could not find an unresolved 'Failed' order with reason: {ft}")

    except sqlite3.Error as e:
        logging.error(f"Error finding example orders: {e}")
    finally:
        if conn:
            conn.close()

    # Run examples if orders were found
    if not example_orders:
        print("\nCould not find suitable example orders to run.")
    else:
        for reason, order_id in example_orders.items():
            print(f"\n\n{'='*20} Example: {reason} Order ({order_id}) {'='*20}")
            await run_telecom_workflow(order_id)
            # Add a small delay between runs if needed
            await asyncio.sleep(1)


    # --- Step 5: Display Final Statistics ---
    print("\n--- Step 5: Displaying Final Order Statistics (After Workflow Runs) ---")
    display_order_statistics()

    print("\n" + "*"*80)
    print("Telecom Activation Fallout Management demo completed.")
    print("*"*80)

# --- Entry Point for Running in Notebook/Script ---
import asyncio
import re # Import re for placeholder LLM

if __name__ == "__main__":
    # In a script, you can run the async function directly
    # In a Jupyter notebook, you might need to use await if in an async cell,
    # or run it like this if in a regular cell:
    # asyncio.run(run_demo())

    # Check if running in an environment with an event loop (like Jupyter)
    try:
        loop = asyncio.get_running_loop()
        print("Running in existing event loop...")
        # Schedule the coroutine in the existing loop
        # Note: This might not block execution in a notebook cell as expected.
        # Consider using `await run_demo()` in an async notebook cell.
        # loop.create_task(run_demo())
        # For simplicity in script execution, let's use asyncio.run
        asyncio.run(run_demo())
    except RuntimeError: # No running event loop
        print("No existing event loop, running using asyncio.run()...")
        asyncio.run(run_demo())

# To run in a Jupyter Notebook:
# 1. Make sure you have an LLM instance defined (replace the placeholder).
# 2. Run the cells defining the functions and classes.
# 3. In a final cell, execute: await run_demo() (ensure the cell is async)
#    or if not using async cells: asyncio.run(run_demo())
