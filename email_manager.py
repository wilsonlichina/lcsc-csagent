"""
LCSC Electronics Email Management - Core Business Logic
Pure functions for email parsing, management, and AI processing with streaming support
Function-style approach without classes, separated from UI concerns
"""

import os
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Generator
from functools import partial
from agent import create_agent, run_streaming_process


# Constants
DEFAULT_EMAILS_DIR = "./emails"
DEFAULT_RECIPIENT = "LCSC Customer Service"
DEFAULT_STATUS = "Pending"


# Email data creation functions
def create_email_data(filename: str, subject: str, sender: str, recipient: str, 
                     send_time: str, status: str, content: str, file_path: str) -> Dict:
    """Create email data dictionary"""
    return {
        'filename': filename,
        'subject': subject,
        'sender': sender,
        'recipient': recipient,
        'send_time': send_time,
        'status': status,
        'content': content,
        'file_path': file_path
    }


def create_email_manager_state(emails_dir: str, agent: Optional[object], emails_cache: List[Dict]) -> Dict:
    """Create email manager state dictionary"""
    return {
        'emails_dir': emails_dir,
        'agent': agent,
        'emails_cache': emails_cache
    }


# Core parsing functions
def extract_field_from_content(content: str, field_name: str, default: str = "") -> str:
    """
    Extract a specific field from email content using regex
    
    Args:
        content: Email content string
        field_name: Field name to extract (e.g., 'Subject', 'Email', 'Name')
        default: Default value if field not found
        
    Returns:
        str: Extracted field value or default
    """
    pattern = rf'{field_name}[：:]\s*(.+)'
    match = re.search(pattern, content, re.IGNORECASE)
    return match.group(1).strip() if match else default


def extract_email_address(content: str) -> str:
    """
    Extract email address from content
    
    Args:
        content: Email content string
        
    Returns:
        str: Email address or "Unknown"
    """
    email_match = re.search(r'([^\s\n]+@[^\s\n]+)', content)
    return email_match.group(1).strip() if email_match else "Unknown"


def format_sender_info(name: str, email: str) -> str:
    """
    Format sender information combining name and email
    
    Args:
        name: Sender name
        email: Sender email
        
    Returns:
        str: Formatted sender string
    """
    if name and name.strip() and name != "Unknown":
        return f"{name.strip()} <{email}>"
    return email


def get_file_timestamp(file_path: str) -> str:
    """
    Get file modification timestamp as formatted string
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: Formatted timestamp
    """
    try:
        file_stat = os.stat(file_path)
        return datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Email parsing functions
def parse_single_email(file_path: str) -> Optional[Dict]:
    """
    Parse a single email file into email data dictionary
    
    Args:
        file_path: Path to email file
        
    Returns:
        Optional[Dict]: Parsed email data or None if parsing fails
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Extract fields using pure functions
        subject = extract_field_from_content(content, 'Subject', 'No Subject')
        sender_email = extract_field_from_content(content, 'Email', 'Unknown')
        sender_name = extract_field_from_content(content, 'Name', '')
        
        # If no explicit email field, try to extract from content
        if sender_email == 'Unknown':
            sender_email = extract_email_address(content)
        
        # Format sender information
        sender = format_sender_info(sender_name, sender_email)
        
        # Get timestamp
        send_time = get_file_timestamp(file_path)
        
        return create_email_data(
            filename=os.path.basename(file_path),
            subject=subject,
            sender=sender,
            recipient=DEFAULT_RECIPIENT,
            send_time=send_time,
            status=DEFAULT_STATUS,
            content=content,
            file_path=file_path
        )
    except Exception as e:
        print(f"Error parsing email {file_path}: {e}")
        return None


def get_email_files(emails_dir: str) -> List[str]:
    """
    Get list of email files from directory
    
    Args:
        emails_dir: Directory containing email files
        
    Returns:
        List[str]: List of email file paths
    """
    if not os.path.exists(emails_dir):
        return []
    
    email_files = []
    for filename in os.listdir(emails_dir):
        if filename.endswith('.txt'):
            email_files.append(os.path.join(emails_dir, filename))
    
    return email_files


def load_emails_from_directory(emails_dir: str) -> List[Dict]:
    """
    Load and parse all emails from directory
    
    Args:
        emails_dir: Directory containing email files
        
    Returns:
        List[Dict]: List of parsed email data dictionaries
    """
    email_files = get_email_files(emails_dir)
    emails = []
    
    for file_path in email_files:
        email_data = parse_single_email(file_path)
        if email_data:
            emails.append(email_data)
    
    # Sort by send time (newest first) - functional approach
    return sorted(emails, key=lambda x: x['send_time'], reverse=True)


# AI agent functions
def initialize_ai_agent(model_name: str = "claude-3-7-sonnet") -> Optional[object]:
    """
    Initialize AI agent for email processing
    
    Args:
        model_name: Name of the AI model to use
        
    Returns:
        Optional[object]: Initialized agent or None if failed
    """
    try:
        agent = create_agent(model_name=model_name)
        print("✅ AI Agent initialized successfully")
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
def create_initial_email_manager_state(emails_dir: str = DEFAULT_EMAILS_DIR, 
                                     model_name: str = "claude-3-7-sonnet") -> Dict:
    """
    Create initial email manager state
    
    Args:
        emails_dir: Directory containing email files
        model_name: AI model name
        
    Returns:
        Dict: Initial state with loaded emails and agent
    """
    agent = initialize_ai_agent(model_name)
    emails = load_emails_from_directory(emails_dir)
    
    return create_email_manager_state(
        emails_dir=emails_dir,
        agent=agent,
        emails_cache=emails
    )


def refresh_email_state(state: Dict) -> Dict:
    """
    Refresh email state by reloading emails from directory
    
    Args:
        state: Current email manager state dictionary
        
    Returns:
        Dict: Updated state with refreshed emails
    """
    emails = load_emails_from_directory(state['emails_dir'])
    
    return create_email_manager_state(
        emails_dir=state['emails_dir'],
        agent=state['agent'],
        emails_cache=emails
    )


# Email access functions
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
    email_match = re.search(r'([^\s\n]+@[^\s\n]+)', content)
    return email_match.group(1) if email_match else None


# Main factory function
def create_email_management_system(emails_dir: str = DEFAULT_EMAILS_DIR, 
                                 model_name: str = "claude-3-7-sonnet") -> Tuple[Dict, Dict]:
    """
    Factory function to create complete email management system
    
    Args:
        emails_dir: Directory containing email files
        model_name: AI model name
        
    Returns:
        Tuple[Dict, Dict]: State dictionary and bound functions dictionary
    """
    state = create_initial_email_manager_state(emails_dir, model_name)
    functions = create_email_processor(state)
    
    print(f"📧 Email Management System initialized with {len(state['emails_cache'])} emails")
    
    return state, functions
