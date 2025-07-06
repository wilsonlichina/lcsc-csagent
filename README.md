# LCSC Electronics Email Customer Service System - Usage Guide

## 🆕 New Features - Real-time AI Agent Loop

### Streaming AI Response Generation
The system now includes **real-time streaming** of the AI agent's thinking process, powered by Strands Agent SDK's async iterators. You can now see:

- 🧠 **Real-time reasoning**: Watch the AI think through problems step by step
- 🔧 **Tool usage**: See which business tools the AI is calling and why
- ⚡ **Processing lifecycle**: Monitor initialization, cycles, and completion
- 💭 **Decision making**: Understand how the AI reaches its conclusions

### Enhanced UI Features
- **Tabbed Interface**: Separate tabs for final response and thinking process
- **Live Updates**: Real-time streaming of AI analysis
- **Event Categorization**: Different types of events are clearly marked
- **Session Summary**: Comprehensive overview of each AI processing session

## Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd lcsc-csagent
```

2. **Create virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

1. **Launch the application:**
   ```bash
   cd lcsc-csagent
   python app.py
   ```

2. **Access the interface:**
   - Open your browser and go to: `http://localhost:7860`
   - The interface will automatically load all emails from the `emails` directory

## 📧 Interface Features

### 1. Email List Display
- **Location:** Left side of the interface
- **Content:** Shows all customer emails with the following columns:
  - **Sender:** Customer name and email
  - **Recipient:** LCSC Customer Service
  - **Send Time:** When the email was received
  - **Status:** Current processing status (Pending/Processed)
  - **Subject:** Email subject line (truncated if too long)

### 2. Action Buttons
- **🔄 Refresh:** Reload emails from the `emails` directory
- **🤖 AI Copilot:** Generate intelligent response for selected email

### 3. Email Details Panel
- **Location:** Right side, top panel
- **Function:** Shows complete email content when an email is selected
- **Content:** Full sender info, subject, timestamp, and complete email body

### 4. AI Response Panel
- **Location:** Right side, bottom panel
- **Function:** Displays AI-generated customer service responses
- **Features:** Powered by Claude AI with access to business tools

## 🎯 How to Use

### View Email Details
1. Click on any email row in the email list
2. The email details will automatically appear in the right panel
3. You can see the complete email content, sender information, and timestamp

### Generate AI Response with Streaming
1. **Select an email** by clicking on it in the email list
2. **Click the "🤖 AI Copilot" button**
3. **Watch the real-time thinking process** in the "🧠 Agent Loop" tab
4. **View the final response** in the "💬 Final Response" tab
5. **Monitor AI reasoning** including:
   - Tool usage and business logic execution
   - Step-by-step decision making
   - Error handling and recovery
   - Processing lifecycle events

### Refresh Email List
1. **Add new emails** to the `emails` directory (as `.txt` files)
2. **Click the "🔄 Refresh" button** to reload the email list
3. **New emails will appear** in the list automatically

## 📁 Email File Format

The system expects email files in the `emails` directory with the following format:

```
Subject: Your email subject here

Name: Customer Name
Email: customer@example.com
Company: Customer Company
Country: Customer Country

Email content goes here...
Multiple lines are supported.
```

**Required fields:**
- `Subject:` - Email subject line
- Email content (can be any text)

**Optional fields:**
- `Name:` - Customer name
- `Email:` - Customer email address
- `Company:` - Customer company
- `Country:` - Customer country

## 🤖 AI Capabilities

The AI Copilot can:
- **Analyze customer inquiries** and understand intent with real-time reasoning display
- **Query business data** (customers, orders, products, inventory) with visible tool usage
- **Generate professional responses** following LCSC service standards
- **Stream thinking process** showing step-by-step analysis and decision making
- **Handle various scenarios:**
  - Price inquiries
  - Order status checks
  - Product information requests
  - Shipping and logistics questions
  - Order modifications and cancellations

### Streaming Features
- **Real-time Event Display**: See AI events as they happen
- **Tool Usage Monitoring**: Watch which business tools are being called
- **Reasoning Process**: Understand the AI's thought process
- **Error Handling**: Real-time error reporting and recovery
- **Session Analytics**: Comprehensive summary of each processing session

## 🔧 Technical Details

### System Requirements
- Python 3.8+
- Gradio library
- Strands Agent SDK
- AWS Bedrock access (for AI functionality)

### File Structure
```
lcsc-csagent/
├── app.py              # Main Gradio application with streaming UI
├── agent.py            # AI agent configuration with async support
├── business_tools.py   # Business logic and tools
├── email_manager.py    # Email management with streaming support
├── streaming_utils.py  # Streaming event processing utilities
├── test_streaming.py   # Test suite for streaming functionality
├── emails/             # Email files directory
│   ├── email1.txt
│   ├── email2.txt
│   └── ...
└── data/               # Business data (CSV files)
    ├── customers.csv
    ├── orders.csv
    └── ...
```

### Configuration
- **AI Model:** Claude 3.7 Sonnet (configurable in `agent.py`)
- **Server Port:** 7860 (configurable in `app.py`)
- **Email Directory:** `./emails` (configurable in `email_manager.py`)

## 🚨 Troubleshooting

### Common Issues

1. **"AI Agent is not available"**
   - Check AWS credentials configuration
   - Verify Bedrock access permissions
   - Ensure proper model access

2. **"No emails found"**
   - Check if `emails` directory exists
   - Verify email files have `.txt` extension
   - Ensure files are readable

3. **Interface not loading**
   - Check if port 7860 is available
   - Verify all dependencies are installed
   - Check console for error messages

### Getting Help
- Check the console output for detailed error messages
- Verify all required dependencies are installed
- Ensure AWS credentials are properly configured

## 📈 Future Enhancements

Planned features:
- Email status management (mark as processed)
- Response templates and customization
- Bulk email processing
- Email categorization and filtering
- Response history and analytics
