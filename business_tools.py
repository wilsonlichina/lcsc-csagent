"""
Business Tools Module
Defines LCSC business tools used by the Agent
"""

from strands import tool
from typing import Dict, List, Optional
import csv
import os
from datetime import datetime, timedelta

# Data directory path
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def load_customers_from_csv() -> Dict:
    """Load customers data from CSV file"""
    customers = {}
    csv_path = os.path.join(DATA_DIR, 'customers.csv')
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                customers[row['email']] = row
        print(f"✅ Loaded {len(customers)} customers from CSV")
    except FileNotFoundError:
        print(f"❌ Customers CSV file not found: {csv_path}")
    except Exception as e:
        print(f"❌ Error loading customers CSV: {e}")
    
    return customers

def load_orders_from_csv() -> Dict:
    """Load orders data from CSV file"""
    orders = {}
    csv_path = os.path.join(DATA_DIR, 'orders.csv')
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert numeric fields
                row['total_amount'] = float(row['total_amount'])
                orders[row['order_id']] = row
        print(f"✅ Loaded {len(orders)} orders from CSV")
    except FileNotFoundError:
        print(f"❌ Orders CSV file not found: {csv_path}")
    except Exception as e:
        print(f"❌ Error loading orders CSV: {e}")
    
    return orders

def load_order_products_from_csv() -> Dict:
    """Load order products data from CSV file"""
    order_products = {}
    csv_path = os.path.join(DATA_DIR, 'order_products.csv')
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert numeric fields
                row['quantity'] = int(row['quantity'])
                row['unit_price'] = float(row['unit_price'])
                
                order_id = row['order_id']
                if order_id not in order_products:
                    order_products[order_id] = []
                order_products[order_id].append({
                    'product_id': row['product_id'],
                    'name': row['product_name'],
                    'quantity': row['quantity'],
                    'unit_price': row['unit_price']
                })
        print(f"✅ Loaded order products for {len(order_products)} orders from CSV")
    except FileNotFoundError:
        print(f"❌ Order products CSV file not found: {csv_path}")
    except Exception as e:
        print(f"❌ Error loading order products CSV: {e}")
    
    return order_products

def load_products_from_csv() -> Dict:
    """Load products data from CSV file"""
    products = {}
    csv_path = os.path.join(DATA_DIR, 'products.csv')
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert numeric fields
                row['unit_price'] = float(row['unit_price'])
                row['stock_quantity'] = int(row['stock_quantity'])
                row['min_order_qty'] = int(row['min_order_qty'])
                products[row['product_id']] = row
        print(f"✅ Loaded {len(products)} products from CSV")
    except FileNotFoundError:
        print(f"❌ Products CSV file not found: {csv_path}")
    except Exception as e:
        print(f"❌ Error loading products CSV: {e}")
    
    return products

# Load data from CSV files
CUSTOMERS = load_customers_from_csv()
ORDERS = load_orders_from_csv()
ORDER_PRODUCTS = load_order_products_from_csv()
PRODUCTS = load_products_from_csv()

# In-memory storage for runtime modifications (like order interceptions)
RUNTIME_ORDER_UPDATES = {}

@tool
def query_order_by_id(order_id: str) -> Dict:
    """
    Query order information by order ID
    
    Args:
        order_id (str): Order ID, e.g. LC123456
        
    Returns:
        Dict: Detailed order information including status, products, amount, etc.
    """
    print(f"🔍 Querying order: {order_id}")
    
    if order_id in ORDERS:
        order = ORDERS[order_id].copy()
        
        # Add products to order
        if order_id in ORDER_PRODUCTS:
            order['products'] = ORDER_PRODUCTS[order_id]
        else:
            order['products'] = []
        
        # Apply runtime updates if any
        if order_id in RUNTIME_ORDER_UPDATES:
            order.update(RUNTIME_ORDER_UPDATES[order_id])
        
        print(f"✅ Order found: {order_id}, Status: {order['status']}")
        return {
            "success": True,
            "data": order,
            "message": f"Successfully retrieved order {order_id}"
        }
    else:
        print(f"❌ Order not found: {order_id}")
        return {
            "success": False,
            "data": None,
            "message": f"Order {order_id} does not exist"
        }

@tool
def query_customer_by_email(email: str) -> Dict:
    """
    Query customer information by email address
    
    Args:
        email (str): Customer email address
        
    Returns:
        Dict: Detailed customer information
    """
    print(f"🔍 Querying customer: {email}")
    
    if email in CUSTOMERS:
        customer = CUSTOMERS[email].copy()
        print(f"✅ Customer found: {customer['name']} ({customer['customer_id']})")
        return {
            "success": True,
            "data": customer,
            "message": f"Successfully retrieved customer {email}"
        }
    else:
        print(f"❌ Customer not found: {email}")
        return {
            "success": False,
            "data": None,
            "message": f"Customer {email} does not exist"
        }

@tool
def query_orders_by_customer(customer_email: str) -> Dict:
    """
    Query all orders for a customer by email address
    
    Args:
        customer_email (str): Customer email address
        
    Returns:
        Dict: List of customer orders
    """
    print(f"🔍 Querying customer orders: {customer_email}")
    
    customer_orders = []
    for order_id, order in ORDERS.items():
        if order.get("customer_email") == customer_email:
            order_copy = order.copy()
            # Add products to order
            if order_id in ORDER_PRODUCTS:
                order_copy['products'] = ORDER_PRODUCTS[order_id]
            else:
                order_copy['products'] = []
            
            # Apply runtime updates if any
            if order_id in RUNTIME_ORDER_UPDATES:
                order_copy.update(RUNTIME_ORDER_UPDATES[order_id])
            
            customer_orders.append(order_copy)
    
    if customer_orders:
        print(f"✅ Found {len(customer_orders)} orders")
        return {
            "success": True,
            "data": customer_orders,
            "message": f"Customer {customer_email} has {len(customer_orders)} orders"
        }
    else:
        print(f"❌ No orders found")
        return {
            "success": False,
            "data": [],
            "message": f"Customer {customer_email} has no orders"
        }

@tool
def query_product_by_id(product_id: str) -> Dict:
    """
    Query product information by product ID
    
    Args:
        product_id (str): Product ID, e.g. 08-50-0113
        
    Returns:
        Dict: Detailed product information
    """
    print(f"🔍 Querying product: {product_id}")
    
    if product_id in PRODUCTS:
        product = PRODUCTS[product_id].copy()
        print(f"✅ Product found: {product['name']}")
        return {
            "success": True,
            "data": product,
            "message": f"Successfully retrieved product {product_id}"
        }
    else:
        print(f"❌ Product not found: {product_id}")
        return {
            "success": False,
            "data": None,
            "message": f"Product {product_id} does not exist"
        }

@tool
def query_inventory_status(product_id: str) -> Dict:
    """
    Query product inventory status
    
    Args:
        product_id (str): Product ID
        
    Returns:
        Dict: Inventory status information (in stock/on order)
    """
    print(f"🔍 Querying inventory: {product_id}")
    
    if product_id in PRODUCTS:
        product = PRODUCTS[product_id]
        inventory_info = {
            "product_id": product_id,
            "product_name": product["name"],
            "stock_status": product["stock_status"],
            "stock_quantity": int(product["stock_quantity"]),
            "min_order_qty": int(product["min_order_qty"]),
            "lead_time": product["lead_time"],
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print(f"✅ Stock status: {product['stock_status']}, Quantity: {product['stock_quantity']}")
        return {
            "success": True,
            "data": inventory_info,
            "message": f"Product {product_id} stock status: {product['stock_status']}"
        }
    else:
        print(f"❌ Product not found: {product_id}")
        return {
            "success": False,
            "data": None,
            "message": f"Product {product_id} does not exist"
        }

@tool
def intercept_order_shipping(order_id: str, reason: str) -> Dict:
    """
    Intercept order shipping - Critical business operation
    
    Args:
        order_id (str): Order ID
        reason (str): Reason for interception
        
    Returns:
        Dict: Interception operation result
    """
    print(f"🛑 Intercepting order shipment: {order_id}, Reason: {reason}")
    
    if order_id in ORDERS:
        # Get current shipping status (check runtime updates first)
        current_status = RUNTIME_ORDER_UPDATES.get(order_id, {}).get('shipping_status', ORDERS[order_id]['shipping_status'])
        
        if current_status in ["Shipped", "In Transit", "Delivered"]:
            print(f"❌ Order already shipped, cannot intercept")
            return {
                "success": False,
                "data": None,
                "message": f"Order {order_id} has already been shipped and cannot be intercepted"
            }
        elif current_status == "Intercepted":
            print(f"⚠️  Order already intercepted")
            return {
                "success": True,
                "data": {"status": "Intercepted", "reason": reason},
                "message": f"Order {order_id} is already intercepted"
            }
        else:
            # Execute interception - store in runtime updates
            if order_id not in RUNTIME_ORDER_UPDATES:
                RUNTIME_ORDER_UPDATES[order_id] = {}
            
            RUNTIME_ORDER_UPDATES[order_id].update({
                "shipping_status": "Intercepted",
                "intercept_reason": reason,
                "intercept_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            print(f"✅ Order interception successful")
            return {
                "success": True,
                "data": {
                    "order_id": order_id,
                    "status": "Intercepted",
                    "reason": reason,
                    "intercept_time": RUNTIME_ORDER_UPDATES[order_id]["intercept_time"]
                },
                "message": f"Order {order_id} has been successfully intercepted"
            }
    else:
        print(f"❌ Order not found: {order_id}")
        return {
            "success": False,
            "data": None,
            "message": f"Order {order_id} does not exist"
        }

@tool
def query_logistics_status(order_id: str) -> Dict:
    """
    Query order logistics status
    
    Args:
        order_id (str): Order ID
        
    Returns:
        Dict: Logistics status information
    """
    print(f"🚚 Querying logistics status: {order_id}")
    
    if order_id in ORDERS:
        order = ORDERS[order_id].copy()
        
        # Apply runtime updates if any
        if order_id in RUNTIME_ORDER_UPDATES:
            order.update(RUNTIME_ORDER_UPDATES[order_id])
        
        logistics_info = {
            "order_id": order_id,
            "shipping_status": order["shipping_status"],
            "tracking_number": order.get("tracking_number", ""),
            "shipping_address": order["shipping_address"],
            "estimated_delivery": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        }
        
        # Add intercept information if applicable
        if order.get("shipping_status") == "Intercepted":
            logistics_info["intercept_reason"] = order.get("intercept_reason", "")
            logistics_info["intercept_time"] = order.get("intercept_time", "")
        
        # Simulate tracking history based on status
        if order["shipping_status"] == "In Transit":
            logistics_info["tracking_history"] = [
                {"time": "2024-07-01 10:00", "status": "Shipped", "location": "Shenzhen Warehouse"},
                {"time": "2024-07-01 18:00", "status": "In Transit", "location": "Shenzhen Distribution Center"},
                {"time": "2024-07-02 08:00", "status": "In Transit", "location": "Guangzhou Distribution Center"}
            ]
        elif order["shipping_status"] == "Preparing":
            logistics_info["tracking_history"] = [
                {"time": "2024-07-02 09:15", "status": "Order Confirmed", "location": "LCSC System"},
                {"time": "2024-07-02 14:30", "status": "Preparing", "location": "Madrid Warehouse"}
            ]
        elif order["shipping_status"] == "Intercepted":
            logistics_info["tracking_history"] = [
                {"time": order.get("intercept_time", ""), "status": "Intercepted", "location": "Warehouse", "reason": order.get("intercept_reason", "")}
            ]
        
        print(f"✅ Logistics status: {order['shipping_status']}")
        return {
            "success": True,
            "data": logistics_info,
            "message": f"Order {order_id} logistics status: {order['shipping_status']}"
        }
    else:
        print(f"❌ Order not found: {order_id}")
        return {
            "success": False,
            "data": None,
            "message": f"Order {order_id} does not exist"
        }

# Business tools list for Agent usage
BUSINESS_TOOLS = [
    query_order_by_id,
    query_customer_by_email,
    query_orders_by_customer,
    query_product_by_id,
    query_inventory_status,
    intercept_order_shipping,
    query_logistics_status
]
