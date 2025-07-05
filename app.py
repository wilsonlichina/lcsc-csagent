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
    Create the enhanced Gradio interface using functional email management
    
    Key Enhancements:
    1. Modern card-based layout with better visual hierarchy
    2. Improved responsive design with proper column layouts
    3. Enhanced styling with custom CSS and better spacing
    4. Status indicators and loading states
    5. Better accessibility and user experience
    """
    
    # Custom CSS for enhanced styling
    custom_css = """
    .main-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 20px;
    }
    
    .header-section {
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 10px;
        text-align: left;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .header-content {
        text-align: left !important;
    }
    
    .header-content h1 {
        text-align: left !important;
        margin: 0 0 10px 0;
        padding-left: 0 !important;
    }
    
    .header-content p {
        text-align: left !important;
        margin: 0;
        padding-left: 0 !important;
    }
    
    .header-content * {
        text-align: left !important;
    }
    
    .section-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        border: 1px solid #e1e5e9;
    }
    
    .email-list-container {
        min-height: 400px;
    }
    
    .details-panel {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 20px;
        min-height: 300px;
        border-left: 4px solid #667eea;
    }
    
    .ai-response-panel {
        background: #f0f8ff;
        border-radius: 8px;
        padding: 20px;
        min-height: 300px;
        border-left: 4px solid #28a745;
    }
    
    .action-buttons {
        display: flex;
        gap: 10px;
        justify-content: center;
        margin: 20px 0;
    }
    
    .status-indicator {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    
    .status-pending {
        background-color: #fff3cd;
        color: #856404;
    }
    
    .status-processed {
        background-color: #d4edda;
        color: #155724;
    }
    
    .section-title {
        color: #2c3e50;
        font-weight: 600;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 20px 0;
        flex-wrap: wrap;
    }
    
    .stat-item {
        text-align: center;
        padding: 15px;
        background: rgba(255,255,255,0.2);
        border-radius: 8px;
        min-width: 120px;
        margin: 5px;
    }
    
    .stat-number {
        font-size: 24px;
        font-weight: bold;
        display: block;
    }
    
    .stat-label {
        font-size: 14px;
        opacity: 0.9;
    }
    """
    
    with gr.Blocks(
        title="LCSC Electronics - Email Customer Service System",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="gray",
            neutral_hue="slate",
            font=gr.themes.GoogleFont("Inter")
        ),
        css=custom_css
    ) as interface:
        
        # Enhanced Header Section
        with gr.Column(elem_classes="main-container"):
            with gr.Column(elem_classes="header-section"):
                gr.Markdown(
                    """
                    # 📧 LCSC Electronics Customer Service System
                    基于Gradio + Strands Agent SDK构建的智能邮件处理系统
                    """,
                    elem_classes="header-content"
                )
                

            
            # Main Content Layout - Email List at Top
            with gr.Column(elem_classes="section-card"):
                gr.Markdown(
                    """
                    <div class="section-title">
                        📋 Customer Email Inbox
                    </div>
                    """,
                    elem_classes="section-header"
                )
                
                # Email list with enhanced styling
                email_list = gr.Dataframe(
                    headers=["👤 Sender", "📧 Recipient", "🕒 Time", "📊 Status", "📝 Subject"],
                    value=email_functions['get_emails_for_display'](),
                    interactive=True,
                    wrap=True,
                    elem_id="email_list",
                    elem_classes="email-list-container",
                    column_widths=["20%", "15%", "15%", "10%", "40%"]
                )
                
                # Enhanced Action Buttons
                with gr.Row(elem_classes="action-buttons"):
                    refresh_btn = gr.Button(
                        "🔄 Refresh Emails", 
                        variant="secondary", 
                        size="lg",
                        elem_classes="refresh-button"
                    )
                    ai_btn = gr.Button(
                        "🤖 Generate AI Response", 
                        variant="primary", 
                        size="lg",
                        elem_classes="ai-button"
                    )
            
            # Details and Response Panels Below - Side by Side
            with gr.Row():
                # Email Details Section
                with gr.Column(scale=1, elem_classes="section-card"):
                    gr.Markdown(
                        """
                        <div class="section-title">
                            📄 Email Details
                        </div>
                        """,
                        elem_classes="section-header"
                    )
                    
                    email_details = gr.Markdown(
                        """
                        <div class="details-panel">
                            <div style="text-align: center; padding: 40px; color: #6c757d;">
                                <h3>📬 No Email Selected</h3>
                                <p>Click on an email from the list to view its complete details here.</p>
                                <p><em>Details will include sender information, timestamp, and full content.</em></p>
                            </div>
                        </div>
                        """,
                        elem_classes="email-details-display"
                    )
                
                # AI Response Section
                with gr.Column(scale=1, elem_classes="section-card"):
                    gr.Markdown(
                        """
                        <div class="section-title">
                            🤖 AI-Generated Response
                        </div>
                        """,
                        elem_classes="section-header"
                    )
                    
                    ai_response = gr.Markdown(
                        """
                        <div class="ai-response-panel">
                            <div style="text-align: center; padding: 40px; color: #6c757d;">
                                <h3>🧠 AI Assistant Ready</h3>
                                <p>Select an email and click <strong>'Generate AI Response'</strong> to create an intelligent customer service reply.</p>
                                <p><em>Powered by Claude AI with business context awareness.</em></p>
                            </div>
                        </div>
                        """,
                        elem_classes="ai-response-display"
                    )
            
            # Footer Information
            with gr.Row():
                with gr.Column(elem_classes="section-card"):
                    gr.Markdown(
                        """
                        ### 💡 Quick Tips
                        - **Select Email**: Click any row in the email list to view details
                        - **AI Processing**: Use the AI Copilot for intelligent response generation
                        - **Refresh**: Click refresh to load new emails from the directory
                        - **Status Tracking**: Monitor email processing status in real-time
                        """,
                        elem_classes="footer-info"
                    )
        
        # State management using Gradio State (functional approach)
        selected_email_idx = gr.State(-1)
        
        # Event handlers using functional approach with loading states
        refresh_btn.click(
            fn=refresh_emails,
            outputs=email_list,
            show_progress=True
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
