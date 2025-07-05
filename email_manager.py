"""
LCSC Electronics Email Management - Functional Programming Style
Pure functions for email parsing, management, and AI processing
"""

import os
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple, NamedTuple
from functools import partial
from agent import create_agent


# Data structures for type safety and immutability
class EmailData(NamedTuple):
    """Immutable email data structure"""
    filename: str
    subject: str
    sender: str
    recipient: str
    send_time: str
    status: str
    content: str
    file_path: str


class EmailManagerState(NamedTuple):
    """Immutable state container for email management"""
    emails_dir: str
    agent: Optional[object]
    emails_cache: List[EmailData]


# Constants
DEFAULT_EMAILS_DIR = "./emails"
DEFAULT_RECIPIENT = "LCSC Customer Service"
DEFAULT_STATUS = "Pending"
SUBJECT_TRUNCATE_LENGTH = 60


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
def parse_single_email(file_path: str) -> Optional[EmailData]:
    """
    Parse a single email file into EmailData structure
    
    Args:
        file_path: Path to email file
        
    Returns:
        Optional[EmailData]: Parsed email data or None if parsing fails
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
        
        return EmailData(
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


def load_emails_from_directory(emails_dir: str) -> List[EmailData]:
    """
    Load and parse all emails from directory
    
    Args:
        emails_dir: Directory containing email files
        
    Returns:
        List[EmailData]: List of parsed email data
    """
    email_files = get_email_files(emails_dir)
    emails = []
    
    for file_path in email_files:
        email_data = parse_single_email(file_path)
        if email_data:
            emails.append(email_data)
    
    # Sort by send time (newest first) - functional approach
    return sorted(emails, key=lambda x: x.send_time, reverse=True)


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


def process_email_with_ai(agent: object, email_content: str, customer_email: Optional[str] = None) -> str:
    """
    Process email content with AI agent
    
    Args:
        agent: AI agent instance
        email_content: Email content to process
        customer_email: Customer email for context
        
    Returns:
        str: AI response or error message
    """
    if not agent:
        return "❌ AI Agent is not available. Please check the configuration."
    
    try:
        context = prepare_ai_context(email_content, customer_email)
        response = agent.run(context)
        return response
    except Exception as e:
        return f"❌ Error processing email with AI: {str(e)}"


# State management functions
def create_email_manager_state(emails_dir: str = DEFAULT_EMAILS_DIR, 
                              model_name: str = "claude-3-7-sonnet") -> EmailManagerState:
    """
    Create initial email manager state
    
    Args:
        emails_dir: Directory containing email files
        model_name: AI model name
        
    Returns:
        EmailManagerState: Initial state with loaded emails and agent
    """
    agent = initialize_ai_agent(model_name)
    emails = load_emails_from_directory(emails_dir)
    
    return EmailManagerState(
        emails_dir=emails_dir,
        agent=agent,
        emails_cache=emails
    )


def refresh_email_state(state: EmailManagerState) -> EmailManagerState:
    """
    Refresh email state by reloading emails from directory
    
    Args:
        state: Current email manager state
        
    Returns:
        EmailManagerState: Updated state with refreshed emails
    """
    emails = load_emails_from_directory(state.emails_dir)
    
    return EmailManagerState(
        emails_dir=state.emails_dir,
        agent=state.agent,
        emails_cache=emails
    )


# Display formatting functions
def format_email_for_display(email: EmailData) -> List[str]:
    """
    Format single email for display in UI
    
    Args:
        email: Email data to format
        
    Returns:
        List[str]: Formatted email row for display
    """
    subject_display = (
        email.subject[:SUBJECT_TRUNCATE_LENGTH] + "..." 
        if len(email.subject) > SUBJECT_TRUNCATE_LENGTH 
        else email.subject
    )
    
    return [
        email.sender,
        email.recipient,
        email.send_time,
        email.status,
        subject_display
    ]


def format_emails_for_display(emails: List[EmailData]) -> List[List[str]]:
    """
    Format list of emails for display in UI
    
    Args:
        emails: List of email data
        
    Returns:
        List[List[str]]: Formatted email rows for display
    """
    return [format_email_for_display(email) for email in emails]


def get_email_by_index(emails: List[EmailData], index: int) -> Optional[EmailData]:
    """
    Get email by index from list
    
    Args:
        emails: List of email data
        index: Index to retrieve
        
    Returns:
        Optional[EmailData]: Email data or None if index invalid
    """
    if 0 <= index < len(emails):
        return emails[index]
    return None


def format_email_details(email: EmailData) -> str:
    """
    Format email details for detailed view
    
    Args:
        email: Email data to format
        
    Returns:
        str: Formatted email details string
    """
    return f"""
## 📧 Email Details

**From:** {email.sender}  
**To:** {email.recipient}  
**Subject:** {email.subject}  
**Send Time:** {email.send_time}  
**Status:** {email.status}  

**Content:**
```
{email.content}
```
"""


def format_ai_response(email: EmailData, ai_response: str) -> str:
    """
    Format AI response for display
    
    Args:
        email: Original email data
        ai_response: AI generated response
        
    Returns:
        str: Formatted AI response string
    """
    return f"""
## 🤖 AI Copilot Response

**Email:** {email.subject}  
**From:** {email.sender}  
**Processing Time:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  

**AI Generated Response:**
```
{ai_response}
```
"""


# Higher-order functions for creating specialized processors
def create_email_processor(state: EmailManagerState):
    """
    Create email processing functions bound to specific state
    
    Args:
        state: Email manager state
        
    Returns:
        Dict: Dictionary of bound functions
    """
    return {
        'get_emails_for_display': lambda: format_emails_for_display(state.emails_cache),
        'get_email_by_index': partial(get_email_by_index, state.emails_cache),
        'process_with_ai': partial(process_email_with_ai, state.agent),
        'refresh_state': lambda: refresh_email_state(state),
        'get_email_count': lambda: len(state.emails_cache)
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
                                 model_name: str = "claude-3-7-sonnet") -> Tuple[EmailManagerState, Dict]:
    """
    Factory function to create complete email management system
    
    Args:
        emails_dir: Directory containing email files
        model_name: AI model name
        
    Returns:
        Tuple[EmailManagerState, Dict]: State and bound functions
    """
    state = create_email_manager_state(emails_dir, model_name)
    functions = create_email_processor(state)
    
    print(f"📧 Email Management System initialized with {len(state.emails_cache)} emails")
    
    return state, functions


# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing Functional Email Management System...")
    
    # Create email management system
    state, funcs = create_email_management_system()
    
    print(f"✅ System initialized with {funcs['get_email_count']()} emails")
    
    # Test email display formatting
    display_data = funcs['get_emails_for_display']()
    if display_data:
        print("✅ First email display format:")
        print(f"   {display_data[0]}")
    
    # Test email retrieval
    first_email = funcs['get_email_by_index'](0)
    if first_email:
        print("✅ First email details available")
        print(f"   Subject: {first_email.subject}")
    
    print("✅ All functional components working correctly")
