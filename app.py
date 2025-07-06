"""
LCSC Electronics Email Customer Service System
Gradio interface with UI formatting functions and streaming support
Clean separation between business logic and UI presentation
"""

import gradio as gr
import time
from datetime import datetime
from typing import List, Dict

# Import core email management system (business logic only)
from email_manager import (
    create_email_management_system,
    extract_customer_email_from_content,
    refresh_email_state,
    create_email_processor
)

# Import streaming utilities
from streaming_utils import StreamingEventCollector, format_streaming_event


# UI Constants
SUBJECT_TRUNCATE_LENGTH = 60

# Model options for the dropdown
MODEL_OPTIONS = [
#    ("Claude 3.5 Sonnet", "claude-3-5-sonnet"),
    ("Claude 3.7 Sonnet", "claude-3-7-sonnet")
]

# Default agent configuration with reasoning capabilities
DEFAULT_AGENT_CONFIG = {
    "agent": {
        "enable_native_thinking": True,
        "thinking_budget": 16000,
        "max_parallel_tools": 4,
        "record_direct_tool_call": True
    },
    "model": {
        "region": "us-west-2",
        "max_tokens": 24000
    }
}


# Global state management using functional approach with reasoning support
email_state, email_functions = create_email_management_system(
    emails_dir="./emails",
    model_name="claude-3-7-sonnet",
    config=DEFAULT_AGENT_CONFIG
)


# UI Formatting Functions (moved from email_manager.py)
def format_email_for_display(email: Dict) -> List[str]:
    """
    Format single email for display in UI
    
    Args:
        email: Email data dictionary to format
        
    Returns:
        List[str]: Formatted email row for display
    """
    subject_display = (
        email['subject'][:SUBJECT_TRUNCATE_LENGTH] + "..." 
        if len(email['subject']) > SUBJECT_TRUNCATE_LENGTH 
        else email['subject']
    )
    
    return [
        email['sender'],
        email['recipient'],
        email['send_time'],
        subject_display,
        email['status']
    ]


def format_emails_for_display(emails: List[Dict]) -> List[List[str]]:
    """
    Format list of emails for display in UI
    
    Args:
        emails: List of email data dictionaries
        
    Returns:
        List[List[str]]: Formatted email rows for display
    """
    return [format_email_for_display(email) for email in emails]


def format_email_details(email: Dict) -> str:
    """
    Format email details for detailed view
    
    Args:
        email: Email data dictionary to format
        
    Returns:
        str: Formatted email details string
    """
    return f"""
 

**Content:**
```
{email['content']}
```
"""


def format_ai_response(email: Dict, ai_response: str) -> str:
    """
    Format AI response for display
    
    Args:
        email: Original email data dictionary
        ai_response: AI generated response
        
    Returns:
        str: Formatted AI response string
    """
    return f"""
## 🤖 AI Agent Response

**Email:** {email['subject']}  
**From:** {email['sender']}  
**Processing Time:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  

**AI Generated Response:**
```
{ai_response}
```
"""


# Gradio Interface Functions
def refresh_emails():
    """
    Refresh the email list using functional approach
    
    Returns:
        List[List[str]]: Updated email display data
    """
    global email_state, email_functions
    
    # Refresh state immutably - creates new state object
    email_state = email_functions['refresh_state']()
    
    # Update functions with new state
    email_functions = create_email_processor(email_state)
    
    # Return new display data using UI formatting function
    return format_emails_for_display(email_functions['get_emails']())


def update_reasoning_config(enable_thinking: bool, thinking_budget: int, max_tokens: int):
    """
    Update reasoning configuration and reinitialize the system
    
    Args:
        enable_thinking: Whether to enable native thinking
        thinking_budget: Token budget for thinking process
        max_tokens: Maximum tokens for model response
    """
    global email_state, email_functions, DEFAULT_AGENT_CONFIG
    
    # Update configuration
    DEFAULT_AGENT_CONFIG["agent"]["enable_native_thinking"] = enable_thinking
    DEFAULT_AGENT_CONFIG["agent"]["thinking_budget"] = thinking_budget
    DEFAULT_AGENT_CONFIG["model"]["max_tokens"] = max_tokens
    
    # Get current model from state or use default
    current_model = "claude-3-7-sonnet"  # Default fallback
    
    # Reinitialize system with new config
    email_state, email_functions = create_email_management_system(
        emails_dir="./emails",
        model_name=current_model,
        config=DEFAULT_AGENT_CONFIG
    )
    
    return f"✅ Reasoning configuration updated: Thinking={'Enabled' if enable_thinking else 'Disabled'}, Budget={thinking_budget}, Max Tokens={max_tokens}"


def change_model(model_name: str):
    """
    Change the AI model and reinitialize the email management system with reasoning
    
    Args:
        model_name: The model name to switch to
    """
    global email_state, email_functions
    
    # Create new email management system with the selected model and reasoning config
    email_state, email_functions = create_email_management_system(
        emails_dir="./emails",
        model_name=model_name,
        config=DEFAULT_AGENT_CONFIG
    )


def change_model(model_name: str):
    """
    Change the AI model and reinitialize the email management system with reasoning
    
    Args:
        model_name: The model name to switch to
    """
    global email_state, email_functions
    
    # Create new email management system with the selected model and reasoning config
    email_state, email_functions = create_email_management_system(
        emails_dir="./emails",
        model_name=model_name,
        config=DEFAULT_AGENT_CONFIG
    )


def toggle_sidebar(sidebar_visible: bool):
    """
    Toggle sidebar visibility
    
    Args:
        sidebar_visible: Current sidebar visibility state
        
    Returns:
        Updated visibility state and the new state value
    """
    new_state = not sidebar_visible
    return gr.update(visible=new_state), new_state


def view_email_details(evt: gr.SelectData):
    """
    View detailed email information using functional approach
    
    Args:
        evt: Gradio select event data
        
    Returns:
        str: Formatted email details
    """
    if evt.index is None:
        return "Please select an email from the list."
    
    selected_row = evt.index[0]
    
    # Use functional approach to get email by index
    email = email_functions['get_email_by_index'](selected_row)
    
    if not email:
        return "❌ Email not found."
    
    # Use UI formatting function
    return format_email_details(email)


def handle_email_selection(evt: gr.SelectData):
    """
    Handle email selection and return details with index
    
    Args:
        evt: Gradio select event data
        
    Returns:
        Tuple: (email details string, selected index)
    """
    details = view_email_details(evt)
    index = evt.index[0] if evt.index else -1
    return details, index


def handle_ai_copilot_streaming(selected_idx: int):
    """
    Process email with AI using streaming approach
    
    Args:
        selected_idx: Index of selected email
        
    Yields:
        Tuple: (thinking_process_display, final_response_display)
    """
    if selected_idx < 0:
        yield "Please select an email from the list first.", "Please select an email from the list first."
        return
    
    # Get email using functional approach
    email = email_functions['get_email_by_index'](selected_idx)
    if not email:
        yield "❌ Email not found.", "❌ Email not found."
        return
    
    # Extract customer email using core business function
    customer_email = extract_customer_email_from_content(email['content'])
    
    # Initialize event collector
    collector = StreamingEventCollector()
    
    try:
        # Initialize displays
        thinking_display = "🚀 **Starting AI Analysis...**\n\nInitializing agent and preparing to process your email...\n\n"
        response_display = "🤖 **AI Processing Started**\n\nPlease wait while the AI agent analyzes the email and generates a response...\n\n"
        
        yield thinking_display, response_display
        
        # Batch processing variables
        last_update_time = time.time()
        update_interval = 10.0  # Update UI every 10 seconds to allow complete thinking accumulation
        pending_updates = False
        
        # Process with AI using streaming
        for event in email_functions['process_with_ai_streaming'](email['content'], customer_email):
            # Add event to collector
            collector.add_event(event)
            
            # Format and update thinking process display with buffering
            formatted_event = format_streaming_event(event, collector)
            if formatted_event:  # Only add non-empty formatted events
                thinking_display += formatted_event
                pending_updates = True
            
            # Special handling for MESSAGE event - flush thinking buffer and show final response
            if event.get("message"):
                # Force flush any remaining thinking buffer
                remaining_thinking = collector.force_flush_thinking_buffer()
                if remaining_thinking:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    thinking_display += f"🧠 **[{timestamp}] THINKING:** {remaining_thinking}\n\n"
                
                # Add the MESSAGE event to thinking display
                thinking_display += formatted_event
                
                # Now get the final response (after MESSAGE event is added)
                final_response = collector.get_final_response()
                if final_response and final_response != "No response generated. Please check the thinking process for details.":
                    response_display = format_ai_response(email, final_response)
                
                # Force update when MESSAGE event occurs
                yield thinking_display, response_display
                pending_updates = False
                continue
            
            # Only yield updates at intervals or for important events
            current_time = time.time()
            should_update = (
                current_time - last_update_time >= update_interval or
                "current_tool_use" in event or  # Always show tool usage immediately
                event.get("init_event_loop") or
                event.get("start_event_loop") or
                event.get("force_stop")
            )
            
            if should_update and pending_updates:
                yield thinking_display, response_display
                last_update_time = current_time
                pending_updates = False
                time.sleep(0.1)  # Brief pause for UI responsiveness
        
        # Mark as complete and final update
        collector.mark_complete()
        
        # Flush any remaining thinking buffer
        remaining_thinking = collector.force_flush_thinking_buffer()
        if remaining_thinking:
            timestamp = datetime.now().strftime("%H:%M:%S")
            thinking_display += f"🧠 **[{timestamp}] THINKING:** {remaining_thinking}\n\n"
            print("thinking_display: " + thinking_display)
        
        # Final response formatting
        final_response = collector.get_final_response()
        if final_response == "No response generated. Please check the thinking process for details.":
            response_display = f"""
## 🤖 AI Agent Loop Response

**Email:** {email['subject']}  
**From:** {email['sender']}  
**Processing Time:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  

**Status:** ⚠️ Processing completed but no final response was generated.
Please check the thinking process panel for detailed information about what happened during processing.

{collector.get_summary()}
"""
        else:
            response_display = format_ai_response(email, final_response)
        
        # Add session summary to thinking process
        thinking_display += f"\n\n{collector.get_summary()}"
        thinking_display += "\n\n✅ **Processing Complete!**"
        
        yield thinking_display, response_display
        
    except Exception as e:
        error_msg = f"❌ Error processing with AI: {str(e)}"
        yield thinking_display + f"\n\n{error_msg}", error_msg


def get_initial_email_display():
    """
    Get initial email display data
    
    Returns:
        List[List[str]]: Formatted email data for initial display
    """
    return format_emails_for_display(email_functions['get_emails']())


def create_interface():
    """
    Create the Gradio interface with sidebar and streaming support
    
    Key Features:
    1. Left sidebar with model selection and email details
    2. Email list display with proper column layout
    3. AI response generation with real-time thinking process
    4. Streaming display of AI agent's reasoning and tool usage
    5. Responsive design with proper component organization
    """
    
    with gr.Blocks(
        title="LCSC Electronics - Email Customer Service System",
        theme=gr.themes.Soft()
    ) as interface:
        
        # Header Section
        with gr.Column():
            with gr.Column():
                gr.Markdown(
                    """
                    # 📧 LCSC Electronics Customer Service System
                    基于Gradio + Strands Agent SDK构建的智能邮件处理系统 
                    """
                )
            
            # Main layout with sidebar
            with gr.Row():
                # Left Sidebar
                with gr.Column(scale=1, visible=False) as sidebar_left:
                    # Model Selection Group
                    with gr.Group():
                        gr.Markdown("### 🤖 AI Configuration")
                        model_dropdown = gr.Dropdown(
                            choices=MODEL_OPTIONS,
                            label="Select Model",
                            value="claude-3-7-sonnet",
                            interactive=True
                        )
                    
                    # Reasoning Configuration Group
                    with gr.Group():
                        gr.Markdown("### 🧠 Reasoning Configuration")
                        enable_thinking = gr.Checkbox(
                            label="Enable Native Thinking",
                            value=DEFAULT_AGENT_CONFIG["agent"]["enable_native_thinking"],
                            info="Enable AI's internal reasoning process"
                        )
                        thinking_budget = gr.Slider(
                            minimum=8000,
                            maximum=32000,
                            step=1000,
                            value=DEFAULT_AGENT_CONFIG["agent"]["thinking_budget"],
                            label="Thinking Budget (tokens)",
                            info="Token budget for reasoning process"
                        )
                        max_tokens = gr.Slider(
                            minimum=16000,
                            maximum=48000,
                            step=1000,
                            value=DEFAULT_AGENT_CONFIG["model"]["max_tokens"],
                            label="Max Response Tokens",
                            info="Maximum tokens for complete response"
                        )
                        apply_reasoning_btn = gr.Button(
                            "🔧 Apply Reasoning Config",
                            variant="secondary",
                            size="sm"
                        )
                        reasoning_status = gr.Markdown(
                            f"**Status:** ✅ Native thinking enabled with {DEFAULT_AGENT_CONFIG['agent']['thinking_budget']} token budget"
                        )
                    
                    # Email Details Group
                    with gr.Group():
                        gr.Markdown("### 📄 Email Details")
                        email_details = gr.Markdown(
                            """
                            <div>
                                <div style="text-align: center; padding: 30px; color: #6c757d;">
                                    <h4>📬 No Email Selected</h4>
                                    <p>Click on an email from the list to view its complete details here.</p>
                                </div>
                            </div>
                            """
                        )
                
                # Main Content Area
                with gr.Column(scale=2):
                    # Email List Group
                    with gr.Group():
                        gr.Markdown("### 📋 Customer Email List")
                        # Title and Toggle Button
                        with gr.Row():                      
                            toggle_btn = gr.Button(
                                "▶ Show Configuration", 
                                variant="secondary", 
                                size="sm"
                            )
                        
                        # Email list
                        email_list = gr.Dataframe(
                            headers=["👤 Sender", "📧 Recipient", "🕒 Time", "📝 Subject","📊 Status"],
                            value=get_initial_email_display(),
                            interactive=True,
                            wrap=True,
                            column_widths=["20%", "15%", "15%", "40%", "10%"]
                        )
                        
                        # Action Buttons
                        with gr.Row():
                            refresh_btn = gr.Button("🔄 Refresh Emails", variant="secondary")
                            ai_btn = gr.Button("🤖 AI Agent", variant="primary")
                    
                    # AI Response Group with Tabs
                    with gr.Group():
                        gr.Markdown("### 🤖 AI Agent Response & Processing")
                        with gr.Tabs():
                            # AI Response Tab
                            with gr.TabItem("💬 Final Response"):
                                ai_response = gr.Markdown(
                                    """
                                    <div>
                                        <div style="text-align: center; padding: 40px; color: #6c757d;">
                                            <h3>🧠 AI Assistant Ready</h3>
                                            <p>Select an email and click <strong>'Agent Loop'</strong> to create an intelligent customer service reply.</p>
                                            <p><em>Powered by Claude AI with business context awareness and real-time thinking process.</em></p>
                                        </div>
                                    </div>
                                    """
                                )
                            
                            # Agent Loop Tab
                            with gr.TabItem("🧠 Agent Loop"):
                                thinking_process = gr.Markdown(
                                    """
                                    <div>
                                        <div style="text-align: center; padding: 40px; color: #6c757d;">
                                            <h3>🤔 AI Agent Loop</h3>
                                            <p>This panel will show the AI agent's real-time thinking process, including:</p>
                                            <ul style="text-align: left; display: inline-block;">
                                                <li>🧠 Reasoning steps and analysis</li>
                                                <li>🔧 Business tools being used</li>
                                                <li>💭 Decision-making process</li>
                                                <li>⚡ Processing lifecycle events</li>
                                            </ul>
                                            <p><em>Start processing an email to see the magic happen!</em></p>
                                        </div>
                                    </div>
                                    """
                                )
            
            # Footer Information
            gr.Markdown(
                "**💡 Tips**: Configure Reasoning → Select Model → Click Email → AI Agent Loop → Watch real-time thinking process → Refresh for new emails"
            )
        
        # State management using Gradio State (functional approach)
        selected_email_idx = gr.State(-1)
        sidebar_state = gr.State(False)
        
        # Event handlers using functional approach with loading states
        refresh_btn.click(
            fn=refresh_emails,
            outputs=email_list,
            show_progress=True
        )
        
        # Model change handler
        model_dropdown.change(
            fn=change_model,
            inputs=model_dropdown,
            show_progress=True
        )
        
        # Reasoning configuration handler
        apply_reasoning_btn.click(
            fn=update_reasoning_config,
            inputs=[enable_thinking, thinking_budget, max_tokens],
            outputs=reasoning_status,
            show_progress=True
        )
        
        # Sidebar toggle handler - simplified
        toggle_btn.click(
            fn=toggle_sidebar,
            inputs=sidebar_state,
            outputs=[sidebar_left, sidebar_state]
        ).then(
            fn=lambda visible: "▶ Show Configuration" if not visible else "◀ Hide Configuration",
            inputs=sidebar_state,
            outputs=toggle_btn
        )
        
        # Email selection handler using functional composition
        email_list.select(
            fn=handle_email_selection,
            outputs=[email_details, selected_email_idx],
            show_progress=True
        )
        
        # AI processing handler with streaming support
        ai_btn.click(
            fn=handle_ai_copilot_streaming,
            inputs=selected_email_idx,
            outputs=[thinking_process, ai_response],
            show_progress=True
        )
    
    return interface


def get_system_info():
    """
    Get system information using functional approach with reasoning capabilities
    
    Returns:
        Dict: Information about the current email management system
    """
    return {
        'email_count': email_functions['get_email_count'](),
        'emails_directory': email_state['emails_dir'],
        'ai_agent_available': email_state['agent'] is not None,
        'architecture': 'Functional Programming',
        'immutable_data': True,
        'pure_functions': True,
        'streaming_enabled': True,
        'async_support': True,
        'native_thinking_enabled': DEFAULT_AGENT_CONFIG["agent"]["enable_native_thinking"],
        'thinking_budget': DEFAULT_AGENT_CONFIG["agent"]["thinking_budget"],
        'max_tokens': DEFAULT_AGENT_CONFIG["model"]["max_tokens"]
    }


if __name__ == "__main__":
    # Enhanced system information display with reasoning capabilities
    system_info = get_system_info()
    
    print("\n" + "="*70)
    print("🚀 LCSC EMAIL CUSTOMER SERVICE SYSTEM (REASONING + STREAMING ENABLED)")
    print("="*70)
    print(f"📧 Email Count:        {system_info['email_count']} emails loaded")
    print(f"📁 Emails Directory:   {system_info['emails_directory']}")
    print(f"🤖 AI Agent Status:    {'✅ Available' if system_info['ai_agent_available'] else '❌ Not Available'}")
    print(f"🏗️  Architecture:       {system_info['architecture']}")
    print(f"🔒 Data Management:    {'✅ Immutable' if system_info['immutable_data'] else '❌ Mutable'}")
    print(f"⚡ Function Style:     {'✅ Pure Functions' if system_info['pure_functions'] else '❌ Impure Functions'}")
    print(f"🌊 Streaming Support:  {'✅ Enabled' if system_info['streaming_enabled'] else '❌ Disabled'}")
    print(f"🔄 Async Support:      {'✅ Enabled' if system_info['async_support'] else '❌ Disabled'}")
    print(f"🧠 Native Thinking:    {'✅ Enabled' if system_info['native_thinking_enabled'] else '❌ Disabled'}")
    print(f"💭 Thinking Budget:    {system_info['thinking_budget']} tokens")
    print(f"📝 Max Response:       {system_info['max_tokens']} tokens")
    print("="*70)
    print("🌐 Starting web interface...")
    print("📱 Access URL: http://localhost:7860")
    print("🔧 Debug Mode: Enabled")
    print("🧠 Real-time AI Agent Loop: Available")
    print("💡 Native Reasoning: Configurable via UI")
    print("="*70)
    
    # Create and launch the enhanced interface
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True,
        show_error=True,
        quiet=False
    )
