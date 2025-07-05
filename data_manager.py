#!/usr/bin/env python3
"""
Data Manager Utility
Helper script to manage CSV data files for LCSC business tools
"""

import csv
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def add_customer(customer_id, name, email, phone, company, country, vip_level="Bronze"):
    """Add a new customer to the CSV file"""
    csv_path = os.path.join(DATA_DIR, 'customers.csv')
    
    # Check if customer already exists
    existing_customers = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            existing_customers = list(reader)
            
        # Check for duplicate email
        for customer in existing_customers:
            if customer['email'] == email:
                print(f"❌ Customer with email {email} already exists")
                return False
    except FileNotFoundError:
        pass
    
    # Add new customer
    new_customer = {
        'customer_id': customer_id,
        'name': name,
        'email': email,
        'phone': phone,
        'company': company,
        'country': country,
        'registration_date': datetime.now().strftime('%Y-%m-%d'),
        'vip_level': vip_level
    }
    
    existing_customers.append(new_customer)
    
    # Write back to CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['customer_id', 'name', 'email', 'phone', 'company', 'country', 'registration_date', 'vip_level']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_customers)
    
    print(f"✅ Added customer: {name} ({email})")
    return True

def add_product(product_id, name, category, unit_price, currency, stock_quantity, min_order_qty=1, lead_time="1-3 days"):
    """Add a new product to the CSV file"""
    csv_path = os.path.join(DATA_DIR, 'products.csv')
    
    # Check if product already exists
    existing_products = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            existing_products = list(reader)
            
        # Check for duplicate product_id
        for product in existing_products:
            if product['product_id'] == product_id:
                print(f"❌ Product with ID {product_id} already exists")
                return False
    except FileNotFoundError:
        pass
    
    # Add new product
    new_product = {
        'product_id': product_id,
        'name': name,
        'category': category,
        'unit_price': unit_price,
        'currency': currency,
        'stock_status': 'In Stock' if stock_quantity > 0 else 'Out of Stock',
        'stock_quantity': stock_quantity,
        'min_order_qty': min_order_qty,
        'lead_time': lead_time
    }
    
    existing_products.append(new_product)
    
    # Write back to CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['product_id', 'name', 'category', 'unit_price', 'currency', 'stock_status', 'stock_quantity', 'min_order_qty', 'lead_time']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_products)
    
    print(f"✅ Added product: {name} ({product_id})")
    return True

def list_data(data_type):
    """List all data of a specific type"""
    if data_type == 'customers':
        csv_path = os.path.join(DATA_DIR, 'customers.csv')
        print("\n📋 Customers:")
        print("-" * 80)
    elif data_type == 'orders':
        csv_path = os.path.join(DATA_DIR, 'orders.csv')
        print("\n📋 Orders:")
        print("-" * 80)
    elif data_type == 'products':
        csv_path = os.path.join(DATA_DIR, 'products.csv')
        print("\n📋 Products:")
        print("-" * 80)
    else:
        print(f"❌ Unknown data type: {data_type}")
        return
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for i, row in enumerate(reader, 1):
                if data_type == 'customers':
                    print(f"{i}. {row['name']} ({row['email']}) - {row['vip_level']}")
                elif data_type == 'orders':
                    print(f"{i}. {row['order_id']} - {row['status']} - ${row['total_amount']} {row['currency']}")
                elif data_type == 'products':
                    print(f"{i}. {row['product_id']} - {row['name']} - {row['stock_status']}")
    except FileNotFoundError:
        print(f"❌ CSV file not found: {csv_path}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python data_manager.py list [customers|orders|products]")
        print("  python data_manager.py add_customer <id> <name> <email> <phone> <company> <country> [vip_level]")
        print("  python data_manager.py add_product <id> <name> <category> <price> <currency> <stock> [min_qty] [lead_time]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        if len(sys.argv) != 3:
            print("Usage: python data_manager.py list [customers|orders|products]")
            sys.exit(1)
        list_data(sys.argv[2])
    
    elif command == "add_customer":
        if len(sys.argv) < 8:
            print("Usage: python data_manager.py add_customer <id> <name> <email> <phone> <company> <country> [vip_level]")
            sys.exit(1)
        
        vip_level = sys.argv[8] if len(sys.argv) > 8 else "Bronze"
        add_customer(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], vip_level)
    
    elif command == "add_product":
        if len(sys.argv) < 8:
            print("Usage: python data_manager.py add_product <id> <name> <category> <price> <currency> <stock> [min_qty] [lead_time]")
            sys.exit(1)
        
        min_qty = int(sys.argv[9]) if len(sys.argv) > 9 else 1
        lead_time = sys.argv[10] if len(sys.argv) > 10 else "1-3 days"
        add_product(sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5]), sys.argv[6], int(sys.argv[7]), min_qty, lead_time)
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
