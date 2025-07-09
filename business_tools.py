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

def load_batch_codes_from_csv() -> Dict:
    """Load batch codes data from CSV file"""
    batch_codes = {}
    csv_path = os.path.join(DATA_DIR, 'batch_codes.csv')
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                batch_codes[row['product_id']] = row
        print(f"✅ Loaded {len(batch_codes)} batch codes from CSV")
    except FileNotFoundError:
        print(f"❌ Batch codes CSV file not found: {csv_path}")
    except Exception as e:
        print(f"❌ Error loading batch codes CSV: {e}")
    
    return batch_codes

def load_document_templates_from_csv() -> Dict:
    """Load document templates data from CSV file"""
    templates = {}
    csv_path = os.path.join(DATA_DIR, 'document_templates.csv')
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert numeric fields
                row['processing_time_hours'] = int(row['processing_time_hours'])
                row['processing_fee_usd'] = float(row['processing_fee_usd'])
                templates[row['document_type']] = row
        print(f"✅ Loaded {len(templates)} document templates from CSV")
    except FileNotFoundError:
        print(f"❌ Document templates CSV file not found: {csv_path}")
    except Exception as e:
        print(f"❌ Error loading document templates CSV: {e}")
    
    return templates

def load_general_inquiries_from_csv() -> Dict:
    """Load general inquiries data from CSV file"""
    inquiries = {}
    csv_path = os.path.join(DATA_DIR, 'general_inquiries.csv')
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert numeric fields
                row['response_time_hours'] = int(row['response_time_hours'])
                row['escalation_required'] = row['escalation_required'].lower() == 'yes'
                inquiries[row['inquiry_type']] = row
        print(f"✅ Loaded {len(inquiries)} general inquiry templates from CSV")
    except FileNotFoundError:
        print(f"❌ General inquiries CSV file not found: {csv_path}")
    except Exception as e:
        print(f"❌ Error loading general inquiries CSV: {e}")
    
    return inquiries

# Load data from CSV files
CUSTOMERS = load_customers_from_csv()
ORDERS = load_orders_from_csv()
ORDER_PRODUCTS = load_order_products_from_csv()
PRODUCTS = load_products_from_csv()
BATCH_CODES = load_batch_codes_from_csv()
DOCUMENT_TEMPLATES = load_document_templates_from_csv()
GENERAL_INQUIRIES = load_general_inquiries_from_csv()

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

@tool
def query_batch_dc_code(product_id: str) -> Dict:
    """
    Query product batch/DC code information
    
    Args:
        product_id (str): Product ID to query batch information for
        
    Returns:
        Dict: Batch/DC code information including production date, quality grade, etc.
    """
    print(f"🔍 Querying batch/DC code for product: {product_id}")
    
    if product_id in BATCH_CODES:
        batch_info = BATCH_CODES[product_id].copy()
        
        print(f"✅ Batch info found for {product_id}")
        return {
            "success": True,
            "data": batch_info,
            "message": f"Batch/DC code information retrieved for product {product_id}"
        }
    elif product_id in PRODUCTS:
        # Fallback: generate batch info if not in batch_codes.csv but product exists
        product = PRODUCTS[product_id]
        batch_info = {
            "product_id": product_id,
            "product_name": product["name"],
            "batch_code": f"DC{datetime.now().strftime('%Y%m')}{product_id[-4:]}",
            "production_date": "2024-06-15",
            "expiry_date": "2026-06-15",
            "quality_grade": "A",
            "supplier_info": "Certified Supplier - ISO9001",
            "lot_number": f"LOT{product_id[-6:]}",
            "manufacturing_location": "Shenzhen, China"
        }
        
        print(f"✅ Generated batch info for {product_id}")
        return {
            "success": True,
            "data": batch_info,
            "message": f"Batch/DC code information generated for product {product_id}"
        }
    else:
        print(f"❌ Product not found: {product_id}")
        return {
            "success": False,
            "data": None,
            "message": f"Product {product_id} does not exist, cannot retrieve batch information"
        }

@tool
def process_document_request(request_type: str, order_id: str = None) -> Dict:
    """
    Process document requests (invoice, COC, package list)
    
    Args:
        request_type (str): Type of document requested (invoice, COC, package_list, commercial_invoice)
        order_id (str, optional): Order ID if document is order-specific
        
    Returns:
        Dict: Document processing result and next steps
    """
    print(f"📄 Processing document request: {request_type}, Order: {order_id or 'General'}")
    
    # Check if we have template information for this document type
    template_info = None
    for doc_type, template in DOCUMENT_TEMPLATES.items():
        if doc_type.lower() == request_type.lower():
            template_info = template
            break
    
    if not template_info:
        # Fallback for unknown document types
        valid_types = list(DOCUMENT_TEMPLATES.keys())
        return {
            "success": False,
            "data": None,
            "message": f"Invalid document type: {request_type}. Valid types: {', '.join(valid_types)}"
        }
    
    # Check if order exists (if order_id provided)
    if order_id and order_id not in ORDERS:
        return {
            "success": False,
            "data": None,
            "message": f"Order {order_id} does not exist"
        }
    
    # Process document request using template information
    document_info = {
        "request_type": request_type,
        "order_id": order_id,
        "processing_status": "In Progress",
        "estimated_completion": (datetime.now() + timedelta(hours=template_info['processing_time_hours'])).strftime("%Y-%m-%d %H:%M"),
        "document_format": template_info['format'],
        "delivery_method": "Email",
        "processing_fee": f"${template_info['processing_fee_usd']} USD" if template_info['processing_fee_usd'] > 0 else "Free",
        "required_fields": template_info['required_fields'].split(';'),
        "processing_time_hours": template_info['processing_time_hours']
    }
    
    # Add order-specific information if available
    if order_id and order_id in ORDERS:
        order = ORDERS[order_id]
        document_info.update({
            "customer_email": order["customer_email"],
            "order_amount": order["total_amount"],
            "currency": order["currency"]
        })
    
    print(f"✅ Document request processed: {request_type}")
    return {
        "success": True,
        "data": document_info,
        "message": f"Document request for {request_type} has been processed and will be ready within {template_info['processing_time_hours']} hours"
    }

@tool
def handle_shipped_invoice(order_id: str, invoice_type: str) -> Dict:
    """
    Handle post-shipment invoice processing for customs clearance
    
    Args:
        order_id (str): Order ID for shipped goods
        invoice_type (str): Type of invoice needed (commercial_invoice, customs_declaration)
        
    Returns:
        Dict: Shipped invoice processing result
    """
    print(f"🚢 Processing shipped invoice: {order_id}, Type: {invoice_type}")
    
    if order_id not in ORDERS:
        return {
            "success": False,
            "data": None,
            "message": f"Order {order_id} does not exist"
        }
    
    order = ORDERS[order_id].copy()
    
    # Apply runtime updates if any
    if order_id in RUNTIME_ORDER_UPDATES:
        order.update(RUNTIME_ORDER_UPDATES[order_id])
    
    # Check if order has been shipped
    shipping_status = order.get("shipping_status", "")
    if shipping_status not in ["Shipped", "In Transit", "Delivered"]:
        return {
            "success": False,
            "data": None,
            "message": f"Order {order_id} has not been shipped yet. Current status: {shipping_status}"
        }
    
    # Process shipped invoice
    invoice_info = {
        "order_id": order_id,
        "invoice_type": invoice_type,
        "shipping_status": shipping_status,
        "tracking_number": order.get("tracking_number", ""),
        "invoice_status": "Processing",
        "estimated_delivery": "24-48 hours",
        "customs_value": order.get("total_amount", 0),
        "currency": order.get("currency", "USD"),
        "shipping_address": order.get("shipping_address", ""),
        "urgency_available": True,
        "rush_processing_fee": "$50 USD (6-12 hours)"
    }
    
    print(f"✅ Shipped invoice processing initiated for {order_id}")
    return {
        "success": True,
        "data": invoice_info,
        "message": f"Shipped invoice processing for order {order_id} has been initiated. Invoice will be available within 24-48 hours."
    }

@tool
def handle_general_inquiry(inquiry_type: str, content: str, customer_email: str) -> Dict:
    """
    Handle general inquiries including price, technical, account, return, partnership, complaints
    
    Args:
        inquiry_type (str): Type of inquiry (price, technical, account, return, partnership, complaint)
        content (str): Content of the inquiry
        customer_email (str): Customer email address
        
    Returns:
        Dict: General inquiry processing result and guidance
    """
    print(f"❓ Processing general inquiry: {inquiry_type} from {customer_email}")
    
    # Get inquiry template information
    inquiry_template = None
    if inquiry_type.lower() in GENERAL_INQUIRIES:
        inquiry_template = GENERAL_INQUIRIES[inquiry_type.lower()]
    else:
        # Try to find matching inquiry type by keywords
        content_lower = content.lower()
        for template_type, template_data in GENERAL_INQUIRIES.items():
            keywords = template_data['keywords'].split(',')
            if any(keyword.strip().lower() in content_lower for keyword in keywords):
                inquiry_template = template_data
                inquiry_type = template_type
                break
    
    if not inquiry_template:
        inquiry_type = "general"  # Default fallback
        inquiry_template = {
            "standard_response": "Your inquiry has been received and will be processed by our customer service team.",
            "escalation_required": False,
            "response_time_hours": 48,
            "priority_level": "Normal"
        }
    
    # Get customer information if available
    customer_info = None
    if customer_email in CUSTOMERS:
        customer_info = CUSTOMERS[customer_email]
    
    # Adjust response time based on VIP level
    base_response_time = inquiry_template['response_time_hours']
    if customer_info:
        vip_level = customer_info.get("vip_level", "Bronze")
        if vip_level == "Gold":
            response_time = max(4, base_response_time // 2)  # Minimum 4 hours for Gold
        elif vip_level == "Silver":
            response_time = max(8, int(base_response_time * 0.75))  # 25% faster for Silver
        else:
            response_time = base_response_time
    else:
        response_time = base_response_time
    
    # Process based on inquiry type
    response_info = {
        "inquiry_type": inquiry_type,
        "customer_email": customer_email,
        "customer_vip_level": customer_info.get("vip_level", "Bronze") if customer_info else "Bronze",
        "processing_priority": inquiry_template['priority_level'],
        "estimated_response_time": f"{response_time} hours",
        "escalation_required": inquiry_template['escalation_required'],
        "standard_response": inquiry_template['standard_response']
    }
    
    # Add specific guidance based on inquiry type
    if inquiry_type.lower() == "price":
        response_info.update({
            "next_steps": "Product pricing and quote will be provided",
            "additional_info_needed": "Product IDs, quantities, and delivery location",
            "bulk_discount_available": True
        })
    elif inquiry_type.lower() == "technical":
        response_info.update({
            "next_steps": "Technical specifications and compatibility information will be provided",
            "escalation": "May be escalated to technical team if complex",
            "documentation_available": True
        })
    elif inquiry_type.lower() == "account":
        response_info.update({
            "next_steps": "Account-related assistance will be provided",
            "verification_required": True,
            "security_check": "Identity verification may be required"
        })
    elif inquiry_type.lower() == "return":
        response_info.update({
            "next_steps": "Return process and RMA number will be provided",
            "return_policy": "30-day return policy applies",
            "condition_check": "Product condition assessment required"
        })
    elif inquiry_type.lower() == "partnership":
        response_info.update({
            "next_steps": "Partnership inquiry will be forwarded to business development team",
            "contact_info": "Dedicated partnership manager will be assigned",
            "evaluation_process": "Business evaluation and qualification process"
        })
    elif inquiry_type.lower() == "complaint":
        response_info.update({
            "next_steps": "Complaint will be investigated and resolved",
            "escalation": "May be escalated to management if serious",
            "follow_up": "Regular follow-up until resolution"
        })
    
    print(f"✅ General inquiry processed: {inquiry_type}")
    return {
        "success": True,
        "data": response_info,
        "message": f"Your {inquiry_type} inquiry has been received and will be processed according to our service standards"
    }

# Business tools list for Agent usage
BUSINESS_TOOLS = [
    query_order_by_id,
    query_customer_by_email,
    query_orders_by_customer,
    query_product_by_id,
    query_inventory_status,
    intercept_order_shipping,
    query_logistics_status,
    query_batch_dc_code,
    process_document_request,
    handle_shipped_invoice,
    handle_general_inquiry
]
