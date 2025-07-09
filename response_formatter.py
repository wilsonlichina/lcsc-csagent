"""
Response Formatter Module
Utilities for formatting structured AI responses with intent classification, logistics status, and email replies
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import re


def format_intent_classification(intents: List[Dict[str, Any]]) -> str:
    """
    Format intent classification results
    
    Args:
        intents: List of intent dictionaries with name, confidence, and sub_category
        
    Returns:
        str: Formatted intent classification section
    """
    if not intents:
        return "## Intent Classification\n- No intents identified\n"
    
    formatted = "## Intent Classification\n"
    
    for i, intent in enumerate(intents):
        intent_name = intent.get('name', 'Unknown')
        confidence = intent.get('confidence', 'Medium')
        sub_category = intent.get('sub_category', '')
        
        if i == 0:
            formatted += f"- Primary Intent: {intent_name}\n"
        else:
            formatted += f"- Secondary Intent: {intent_name}\n"
        
        formatted += f"- Confidence: {confidence}\n"
        
        if sub_category:
            formatted += f"- Sub-category: {sub_category}\n"
    
    return formatted + "\n"


def format_logistics_status(order_data: Optional[Dict[str, Any]], logistics_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Format logistics and order status information
    
    Args:
        order_data: Order information dictionary
        logistics_data: Additional logistics information
        
    Returns:
        str: Formatted logistics status section
    """
    if not order_data:
        return "## Logistics/Order Status\n- No order information available\n\n"
    
    formatted = "## Logistics/Order Status\n"
    
    # Basic order information
    formatted += f"- Order ID: {order_data.get('order_id', 'N/A')}\n"
    formatted += f"- Current Status: {order_data.get('status', 'Unknown')}\n"
    formatted += f"- Shipping Status: {order_data.get('shipping_status', 'Unknown')}\n"
    
    # Tracking information
    tracking_number = order_data.get('tracking_number', '')
    if tracking_number:
        formatted += f"- Tracking Number: {tracking_number}\n"
    
    # Delivery information
    if logistics_data:
        estimated_delivery = logistics_data.get('estimated_delivery', '')
        if estimated_delivery:
            formatted += f"- Estimated Delivery: {estimated_delivery}\n"
    
    # Actions taken (interceptions, modifications)
    if order_data.get('shipping_status') == 'Intercepted':
        formatted += f"- Actions Taken: Order intercepted - {order_data.get('intercept_reason', 'Reason not specified')}\n"
        formatted += f"- Interception Time: {order_data.get('intercept_time', 'Not specified')}\n"
    
    # Order value
    total_amount = order_data.get('total_amount', 0)
    currency = order_data.get('currency', 'USD')
    if total_amount:
        formatted += f"- Order Value: {total_amount} {currency}\n"
    
    return formatted + "\n"


def format_email_response(response_content: str, customer_name: str = "Valued Customer", 
                         order_id: str = None, additional_info: Dict[str, Any] = None) -> str:
    """
    Format professional email response
    
    Args:
        response_content: Main response content
        customer_name: Customer name for personalization
        order_id: Order ID if applicable
        additional_info: Additional information to include
        
    Returns:
        str: Formatted professional email response
    """
    formatted = "## Professional Email Reply\n\n"
    
    # Email header
    formatted += f"Dear {customer_name},\n\n"
    
    # Thank you opening
    formatted += "Thank you for contacting LCSC Electronics. "
    
    if order_id:
        formatted += f"Regarding your inquiry about order {order_id}, "
    
    formatted += "we have processed your request and are pleased to provide the following information:\n\n"
    
    # Main content
    formatted += response_content + "\n\n"
    
    # Additional information if provided
    if additional_info:
        if additional_info.get('next_steps'):
            formatted += f"**Next Steps:**\n{additional_info['next_steps']}\n\n"
        
        if additional_info.get('timeline'):
            formatted += f"**Timeline:**\n{additional_info['timeline']}\n\n"
        
        if additional_info.get('contact_info'):
            formatted += f"**Contact Information:**\n{additional_info['contact_info']}\n\n"
    
    # Professional closing
    formatted += "If you have any further questions or need additional assistance, please don't hesitate to contact us. "
    formatted += "We appreciate your business and look forward to serving you.\n\n"
    formatted += "Best regards,\n"
    formatted += "LCSC Electronics Customer Service Team\n"
    formatted += "Email: service@lcsc.com\n"
    formatted += "Website: https://lcsc.com\n"
    
    return formatted


def create_structured_response(intents: List[Dict[str, Any]], 
                             order_data: Optional[Dict[str, Any]] = None,
                             logistics_data: Optional[Dict[str, Any]] = None,
                             email_content: str = "",
                             customer_name: str = "Valued Customer",
                             additional_info: Dict[str, Any] = None) -> str:
    """
    Create complete structured response with all sections
    
    Args:
        intents: List of classified intents
        order_data: Order information
        logistics_data: Logistics information
        email_content: Main email response content
        customer_name: Customer name
        additional_info: Additional information for email
        
    Returns:
        str: Complete structured response
    """
    response = ""
    
    # Intent Classification section
    response += format_intent_classification(intents)
    
    # Logistics/Order Status section (if applicable)
    if order_data or any(intent.get('name', '').lower() in ['logistics status inquiry', 'pre-shipment order interception'] 
                        for intent in intents):
        response += format_logistics_status(order_data, logistics_data)
    
    # Professional Email Reply section
    order_id = order_data.get('order_id') if order_data else None
    response += format_email_response(email_content, customer_name, order_id, additional_info)
    
    return response


def extract_intent_from_response(ai_response: str) -> List[Dict[str, Any]]:
    """
    Extract intent classification from AI response text
    
    Args:
        ai_response: Raw AI response text
        
    Returns:
        List[Dict]: Extracted intent information
    """
    intents = []
    
    # Look for intent classification patterns
    intent_patterns = [
        r'Primary Intent:\s*([^\n]+)',
        r'Secondary Intent:\s*([^\n]+)',
        r'Intent:\s*([^\n]+)'
    ]
    
    confidence_pattern = r'Confidence:\s*([^\n]+)'
    subcategory_pattern = r'Sub-category:\s*([^\n]+)'
    
    lines = ai_response.split('\n')
    current_intent = {}
    
    for line in lines:
        # Check for intent patterns
        for pattern in intent_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                if current_intent:  # Save previous intent
                    intents.append(current_intent)
                current_intent = {'name': match.group(1).strip()}
                break
        
        # Check for confidence
        conf_match = re.search(confidence_pattern, line, re.IGNORECASE)
        if conf_match and current_intent:
            current_intent['confidence'] = conf_match.group(1).strip()
        
        # Check for sub-category
        sub_match = re.search(subcategory_pattern, line, re.IGNORECASE)
        if sub_match and current_intent:
            current_intent['sub_category'] = sub_match.group(1).strip()
    
    # Add the last intent
    if current_intent:
        intents.append(current_intent)
    
    return intents


def validate_response_structure(response: str) -> Dict[str, bool]:
    """
    Validate that response contains all required sections
    
    Args:
        response: Response text to validate
        
    Returns:
        Dict: Validation results for each section
    """
    required_sections = {
        "Intent Classification": r"##\s*Intent Classification",
        "Logistics/Order Status": r"##\s*Logistics/Order Status",
        "Professional Email Reply": r"##\s*Professional Email Reply"
    }
    
    validation_results = {}
    
    for section_name, pattern in required_sections.items():
        validation_results[section_name] = bool(re.search(pattern, response, re.IGNORECASE))
    
    return validation_results


def enhance_response_with_metadata(response: str, processing_time: float = None, 
                                 tools_used: List[str] = None) -> str:
    """
    Add metadata section to response for internal tracking
    
    Args:
        response: Original response
        processing_time: Time taken to process
        tools_used: List of business tools used
        
    Returns:
        str: Enhanced response with metadata
    """
    if not (processing_time or tools_used):
        return response
    
    metadata = "\n## Internal Notes\n"
    
    if tools_used:
        metadata += f"- Tools Used: {', '.join(tools_used)}\n"
    
    if processing_time:
        metadata += f"- Processing Time: {processing_time:.2f} seconds\n"
    
    metadata += f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    return response + metadata


# Intent classification helper functions
def classify_intent_by_keywords(email_content: str) -> List[Dict[str, Any]]:
    """
    Basic intent classification using keyword matching
    
    Args:
        email_content: Email content to classify
        
    Returns:
        List[Dict]: Classified intents with confidence scores
    """
    intent_keywords = {
        "Logistics Status Inquiry": ["tracking", "shipping", "delivery", "logistics", "courier", "logistics status", "express delivery", "track order"],
        "Pre-shipment Order Interception": ["change address", "modify order", "cancel", "change shipping address", "cancel order", "modify order details", "merge orders"],
        "Batch/DC Code Inquiry": ["date code", "batch code", "lot code", "DC", "batch number", "production date"],
        "Document Processing": ["invoice", "COC", "package list", "commercial invoice", "invoice document", "packing list"],
        "Shipped Invoice Processing": ["commercial invoice", "shipped", "shipping invoice", "customs clearance", "customs", "customs documents"],
        "Others Inquiry": ["price", "technical", "account", "return", "partnership", "complaint"]
    }
    
    email_lower = email_content.lower()
    classified_intents = []
    
    for intent_name, keywords in intent_keywords.items():
        matches = sum(1 for keyword in keywords if keyword.lower() in email_lower)
        
        if matches > 0:
            confidence = "High" if matches >= 3 else "Medium" if matches >= 2 else "Low"
            classified_intents.append({
                "name": intent_name,
                "confidence": confidence,
                "keyword_matches": matches
            })
    
    # Sort by number of matches (highest first)
    classified_intents.sort(key=lambda x: x["keyword_matches"], reverse=True)
    
    return classified_intents[:2]  # Return top 2 intents
