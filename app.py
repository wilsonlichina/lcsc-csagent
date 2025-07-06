"""
LCSC Electronics Email Customer Service System
Gradio interface using functional programming style email management
"""

import gradio as gr
import re
from datetime import datetime
from typing import Optional

# Import functional email management system
from email_manager import (
    create_email_management_system,
    format_email_details,
    format_ai_response,
    extract_customer_email_from_content,
    refresh_email_state,
    format_emails_for_display
)


# Global state management using functional approach
# Instead of a class instance, we use a state object and bound functions
email_state, email_functions = create_email_management_system(
    emails_dir="./emails",
    model_name="claude-3-7-sonnet"
)

# Model options for the dropdown
MODEL_OPTIONS = [
    ("Claude 3.5 Sonnet", "claude-3-5-sonnet"),
    ("Claude 3.7 Sonnet", "claude-3-7-sonnet")
]


def refresh_emails():
    """
    Refresh the email list using functional approach
    
    Key Change: Instead of calling a method on an object instance,
    we refresh the state and get new display data functionally
    """
    global email_state, email_functions
    
    # Refresh state immutably - creates new state object
    email_state = email_functions['refresh_state']()
    
    # Update functions with new state
    from email_manager import create_email_processor
    email_functions = create_email_processor(email_state)
    
    # Return new display data
    return email_functions['get_emails_for_display']()


def change_model(model_name: str):
    """
    Change the AI model and reinitialize the email management system
    
    Args:
        model_name: The model name to switch to
    """
    global email_state, email_functions
    
    # Create new email management system with the selected model
    email_state, email_functions = create_email_management_system(
        emails_dir="./emails",
        model_name=model_name
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
    
    Key Change: Uses pure functions instead of object methods
    """
    if evt.index is None:
        return "Please select an email from the list."
    
    selected_row = evt.index[0]
    
    # Use functional approach to get email by index
    email = email_functions['get_email_by_index'](selected_row)
    
    if not email:
        return "❌ Email not found."
    
    # Use pure function to format email details
    return format_email_details(email)


def handle_email_selection(evt: gr.SelectData):
    """
    Handle email selection and return details with index
    
    Key Change: Combines multiple operations using functional composition
    """
    details = view_email_details(evt)
    index = evt.index[0] if evt.index else -1
    return details, index


def handle_ai_copilot(selected_idx: int):
    """
    Process email with AI using functional approach
    
    Key Change: Uses pure functions and immutable data structures
    instead of object state manipulation
    """
    if selected_idx < 0:
        return "Please select an email from the list first."
    
    # Get email using functional approach
    email = email_functions['get_email_by_index'](selected_idx)
    if not email:
        return "❌ Email not found."
    
    # Extract customer email using pure function
    customer_email = extract_customer_email_from_content(email.content)
    
    try:
        # Process with AI using functional approach
        ai_response = email_functions['process_with_ai'](email.content, customer_email)
        
        # Format response using pure function
        return format_ai_response(email, ai_response)
    except Exception as e:
        return f"❌ Error processing with AI: {str(e)}"


def create_interface():
    """
    Create the Gradio interface with sidebar using functional email management
    
    Key Features:
    1. Left sidebar with model selection and email details
    2. Email list display with proper column layout
    3. AI response generation functionality
    4. Responsive design with proper component organization
    """
    
    with gr.Blocks(
        title="LCSC Electronics - Email Customer Service System",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="gray",
            neutral_hue="slate"
        )
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
                with gr.Column(scale=1, visible=True) as sidebar_left:
                    # Model Selection Section
                    with gr.Column():
                        gr.Markdown("**🤖 Configuration**")
                        
                        model_dropdown = gr.Dropdown(
                            choices=MODEL_OPTIONS,
                            label="Select Model",
                            value="claude-3-7-sonnet",
                            interactive=True
                        )
                    
                    # Email Details Section
                    with gr.Column():
                        gr.Markdown("**📄 Email Details**")
                        
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
                    # Email List Section
                    with gr.Column():
                        # Title and Toggle Button
                        with gr.Row():                      
                            gr.Markdown("**📋 Customer Email Inbox**")
                            toggle_btn = gr.Button(
                                "◀ Hide Sidebar", 
                                variant="secondary", 
                                size="sm"
                            )
                        
                        # Email list
                        email_list = gr.Dataframe(
                            headers=["👤 Sender", "📧 Recipient", "🕒 Time", "📊 Status", "📝 Subject"],
                            value=email_functions['get_emails_for_display'](),
                            interactive=True,
                            wrap=True,
                            column_widths=["20%", "15%", "15%", "10%", "40%"]
                        )
                        
                        # Action Buttons
                        with gr.Row():
                            refresh_btn = gr.Button("🔄 Refresh Emails", variant="secondary")
                            ai_btn = gr.Button("🤖 Generate AI Response", variant="primary")
                    
                    # AI Response Section
                    with gr.Column():
                        gr.Markdown("**🤖 AI-Generated Response**")
                        
                        ai_response = gr.Markdown(
                            """
                            <div>
                                <div style="text-align: center; padding: 40px; color: #6c757d;">
                                    <h3>🧠 AI Assistant Ready</h3>
                                    <p>Select an email and click <strong>'Generate AI Response'</strong> to create an intelligent customer service reply.</p>
                                    <p><em>Powered by Claude AI with business context awareness.</em></p>
                                </div>
                            </div>
                            """
                        )
            
            # Footer Information
            gr.Markdown(
                "**💡 Tips**: Select Model → Click Email → Generate AI Response → Refresh for new emails"
            )
        
        # State management using Gradio State (functional approach)
        selected_email_idx = gr.State(-1)
        sidebar_state = gr.State(True)
        
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
        
        # Sidebar toggle handler - simplified
        toggle_btn.click(
            fn=toggle_sidebar,
            inputs=sidebar_state,
            outputs=[sidebar_left, sidebar_state]
        ).then(
            fn=lambda visible: "▶ Show Sidebar" if not visible else "◀ Hide Sidebar",
            inputs=sidebar_state,
            outputs=toggle_btn
        )
        
        # Email selection handler using functional composition
        email_list.select(
            fn=handle_email_selection,
            outputs=[email_details, selected_email_idx],
            show_progress=True
        )
        
        # AI processing handler using functional approach
        ai_btn.click(
            fn=handle_ai_copilot,
            inputs=selected_email_idx,
            outputs=ai_response,
            show_progress=True
        )
    
    return interface


def get_system_info():
    """
    Get system information using functional approach
    
    Returns information about the current email management system
    """
    return {
        'email_count': email_functions['get_email_count'](),
        'emails_directory': email_state.emails_dir,
        'ai_agent_available': email_state.agent is not None,
        'architecture': 'Functional Programming',
        'immutable_data': True,
        'pure_functions': True
    }


if __name__ == "__main__":
    # Enhanced system information display
    system_info = get_system_info()
    
    print("\n" + "="*60)
    print("🚀 LCSC EMAIL CUSTOMER SERVICE SYSTEM")
    print("="*60)
    print(f"📧 Email Count:        {system_info['email_count']} emails loaded")
    print(f"📁 Emails Directory:   {system_info['emails_directory']}")
    print(f"🤖 AI Agent Status:    {'✅ Available' if system_info['ai_agent_available'] else '❌ Not Available'}")
    print(f"🏗️  Architecture:       {system_info['architecture']}")
    print(f"🔒 Data Management:    {'✅ Immutable' if system_info['immutable_data'] else '❌ Mutable'}")
    print(f"⚡ Function Style:     {'✅ Pure Functions' if system_info['pure_functions'] else '❌ Impure Functions'}")
    print("="*60)
    print("🌐 Starting web interface...")
    print("📱 Access URL: http://localhost:7860")
    print("🔧 Debug Mode: Enabled")
    print("="*60)
    
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
