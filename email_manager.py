"""
LCSC Electronics Email Management System - Excel Integration
Core business logic for email parsing, management, and AI processing with streaming support
Integrates with EmailParser for Excel-based email data
"""

import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Generator
from functools import partial
from agent import create_agent, run_streaming_process
from email_parser import EmailParser, EmailParserError


# Constants
DEFAULT_EXCEL_FILE = "./emails/lcsc-emails.xlsx"
DEFAULT_RECIPIENT = "LCSC Customer Service"
DEFAULT_STATUS = "Pending"


# Email data creation functions
def create_email_data(email_id: str, subject: str, sender: str, recipient: str, 
                     send_time: str, status: str, content: str, cs_id: str = "") -> Dict:
    """Create email data dictionary compatible with the original format"""
    return {
        'email_id': email_id,
        'filename': f"email_{email_id}.xlsx",  # Virtual filename for compatibility
        'subject': subject,
        'sender': sender,
        'recipient': recipient,
        'send_time': send_time,
        'status': status,
        'content': content,
        'cs_id': cs_id,
        'file_path': DEFAULT_EXCEL_FILE  # All emails come from the same Excel file
    }


def create_email_manager_state(excel_file: str, agent: Optional[object], emails_cache: List[Dict]) -> Dict:
    """Create email manager state dictionary"""
    return {
        'excel_file': excel_file,
        'agent': agent,
        'emails_cache': emails_cache
    }


# Excel-based email parsing functions
def parse_excel_email_to_dict(excel_email: Dict) -> Dict:
    """
    Convert Excel email data to the expected format
    
    Args:
        excel_email: Email data from EmailParser
        
    Returns:
        Dict: Email data in expected format
    """
    # Extract subject from email content if not provided separately
    content = excel_email.get('email-content', '')
    
    # Try to extract subject from content (if it starts with "Subject:")
    subject = "No Subject"
    if content.startswith("Subject:"):
        lines = content.split('\n')
        if lines:
            subject = lines[0].replace("Subject:", "").strip()
            # Remove subject line from content
            content = '\n'.join(lines[1:]).strip()
    
    # Format sender information
    sender = excel_email.get('sender', 'Unknown')
    
    # Format timestamp
    converse_time = excel_email.get('converse-time', '')
    if isinstance(converse_time, str):
        send_time = converse_time
    else:
        # Handle pandas Timestamp objects
        send_time = str(converse_time) if converse_time else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return create_email_data(
        email_id=str(excel_email.get('email-id', '')),
        subject=subject,
        sender=sender,
        recipient=excel_email.get('receiver', DEFAULT_RECIPIENT),
        send_time=send_time,
        status=DEFAULT_STATUS,
        content=content,
        cs_id=str(excel_email.get('cs-id', ''))
    )


def load_emails_from_excel(excel_file: str) -> List[Dict]:
    """
    Load and parse all first emails from Excel file
    
    Args:
        excel_file: Path to Excel file
        
    Returns:
        List[Dict]: List of parsed email data dictionaries (first email per ID)
    """
    try:
        parser = EmailParser(excel_file)
        email_ids = parser.get_email_ids()
        emails = []
        
        for email_id in email_ids:
            first_email = parser.get_first_email_by_id(email_id)
            if first_email:
                email_data = parse_excel_email_to_dict(first_email)
                emails.append(email_data)
        
        # Sort by send time (oldest first)
        return sorted(emails, key=lambda x: x['send_time'], reverse=False)
        
    except EmailParserError as e:
        print(f"Error loading emails from Excel: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error loading emails: {e}")
        return []


# AI agent functions (unchanged from original)
def initialize_ai_agent(model_name: str = "claude-3-7-sonnet", config: dict = None) -> Optional[object]:
    """
    Initialize AI agent for email processing with reasoning capabilities
    
    Args:
        model_name: Name of the AI model to use
        config: Optional configuration dictionary with agent and model settings
        
    Returns:
        Optional[object]: Initialized agent or None if failed
    """
    try:
        agent = create_agent(model_name=model_name, config=config)
        print("✅ AI Agent initialized successfully with reasoning capabilities")
        return agent
    except Exception as e:
        print(f"❌ Failed to initialize AI Agent: {e}")
        return None


def prepare_ai_context(email_content: str, customer_email: Optional[str] = None) -> str:
    """
    Prepare context string for AI processing
    
    Args:
        email_content: Email content to process
        customer_email: Customer email for context
        
    Returns:
        str: Formatted context string
    """
    return f"Customer Email: {customer_email or 'Not provided'}\n\nEmail Content:\n{email_content}"


def process_email_with_ai_streaming(agent: object, email_content: str, customer_email: Optional[str] = None) -> Generator:
    """
    Process email content with AI agent using streaming
    
    Args:
        agent: AI agent instance
        email_content: Email content to process
        customer_email: Customer email for context
        
    Yields:
        Dict: Streaming events from the agent
    """
    if not agent:
        yield {"error": "❌ AI Agent is not available. Please check the configuration."}
        return
    
    try:
        # Use the streaming function from agent.py
        for event in run_streaming_process(agent, email_content, customer_email):
            yield event
    except Exception as e:
        yield {"error": f"❌ Error processing email with AI: {str(e)}"}


# State management functions
def create_initial_email_manager_state(excel_file: str = DEFAULT_EXCEL_FILE, 
                                     model_name: str = "claude-3-7-sonnet",
                                     config: dict = None) -> Dict:
    """
    Create initial email manager state with reasoning capabilities
    
    Args:
        excel_file: Path to Excel file containing emails
        model_name: AI model name
        config: Optional configuration dictionary with agent and model settings
        
    Returns:
        Dict: Initial state with loaded emails and agent with reasoning
    """
    agent = initialize_ai_agent(model_name, config)
    emails = load_emails_from_excel(excel_file)
    
    return create_email_manager_state(
        excel_file=excel_file,
        agent=agent,
        emails_cache=emails
    )


def refresh_email_state(state: Dict) -> Dict:
    """
    Refresh email state by reloading emails from Excel file
    
    Args:
        state: Current email manager state dictionary
        
    Returns:
        Dict: Updated state with refreshed emails
    """
    emails = load_emails_from_excel(state['excel_file'])
    
    return create_email_manager_state(
        excel_file=state['excel_file'],
        agent=state['agent'],
        emails_cache=emails
    )


# Email access functions (unchanged from original)
def get_email_by_index(emails: List[Dict], index: int) -> Optional[Dict]:
    """
    Get email by index from list
    
    Args:
        emails: List of email data dictionaries
        index: Index to retrieve
        
    Returns:
        Optional[Dict]: Email data or None if index invalid
    """
    if 0 <= index < len(emails):
        return emails[index]
    return None


def get_email_count(emails: List[Dict]) -> int:
    """
    Get count of emails
    
    Args:
        emails: List of email data dictionaries
        
    Returns:
        int: Number of emails
    """
    return len(emails)


# Higher-order functions for creating specialized processors
def create_email_processor(state: Dict):
    """
    Create email processing functions bound to specific state
    
    Args:
        state: Email manager state dictionary
        
    Returns:
        Dict: Dictionary of bound functions
    """
    return {
        'get_email_by_index': partial(get_email_by_index, state['emails_cache']),
        'process_with_ai_streaming': partial(process_email_with_ai_streaming, state['agent']),
        'refresh_state': lambda: refresh_email_state(state),
        'get_email_count': lambda: get_email_count(state['emails_cache']),
        'get_emails': lambda: state['emails_cache']
    }


# Utility functions for email content analysis
def extract_customer_email_from_content(content: str) -> Optional[str]:
    """
    Extract customer email from email content
    
    Args:
        content: Email content
        
    Returns:
        Optional[str]: Customer email or None
    """
    import re
    email_match = re.search(r'([^\s\n]+@[^\s\n]+)', content)
    return email_match.group(1) if email_match else None


# Main factory function
def create_email_management_system(excel_file: str = DEFAULT_EXCEL_FILE, 
                                 model_name: str = "claude-3-7-sonnet",
                                 config: dict = None) -> Tuple[Dict, Dict]:
    """
    Factory function to create complete email management system with reasoning capabilities
    
    Args:
        excel_file: Path to Excel file containing emails
        model_name: AI model name
        config: Optional configuration dictionary with agent and model settings
        
    Returns:
        Tuple[Dict, Dict]: State dictionary and bound functions dictionary
    """
    state = create_initial_email_manager_state(excel_file, model_name, config)
    functions = create_email_processor(state)
    
    reasoning_status = "✅ Enabled" if config and config.get("agent", {}).get("enable_native_thinking", True) else "❌ Disabled"
    print(f"📧 Email Management System initialized with {len(state['emails_cache'])} emails from Excel")
    print(f"🧠 Native reasoning: {reasoning_status}")
    
    return state, functions


# Additional Excel-specific functions
def get_email_conversation_by_id(excel_file: str, email_id: str) -> List[Dict]:
    """
    Get full conversation for a specific email ID
    
    Args:
        excel_file: Path to Excel file
        email_id: Email ID to get conversation for
        
    Returns:
        List[Dict]: List of all emails in the conversation
    """
    try:
        parser = EmailParser(excel_file)
        excel_emails = parser.get_all_emails_by_id(email_id)
        
        conversation = []
        for excel_email in excel_emails:
            email_data = parse_excel_email_to_dict(excel_email)
            conversation.append(email_data)
        
        # Sort by timestamp
        return sorted(conversation, key=lambda x: x['send_time'])
        
    except EmailParserError as e:
        print(f"Error getting conversation for email ID {email_id}: {e}")
        return []


def get_excel_email_stats(excel_file: str) -> Dict:
    """
    Get statistics about emails in the Excel file
    
    Args:
        excel_file: Path to Excel file
        
    Returns:
        Dict: Statistics about the emails
    """
    try:
        parser = EmailParser(excel_file)
        return parser.get_summary_stats()
    except EmailParserError as e:
        print(f"Error getting email stats: {e}")
        return {}
