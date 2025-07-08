# LCSC Electronics Email Customer Service System - Usage Guide

## 🆕 New Features - Excel Integration + Native Reasoning + Real-time AI Agent Loop

### Excel-Based Email Management
The system now uses **Excel-based email data** for improved data management:

- 📊 **Excel Integration**: Load emails from `lcsc-emails.xlsx` file
- 🔄 **Real-time Updates**: Refresh data directly from Excel file
- 📈 **Scalable Data**: Handle large volumes of email data efficiently
- 🏷️ **Email Grouping**: Automatic grouping by Email ID for conversation tracking
- 📋 **Rich Metadata**: Support for CS ID, conversation time, and structured data

### Native Thinking Capabilities
The system includes **native reasoning** powered by Claude's built-in thinking process, providing:

- 🧠 **Native reasoning**: AI's internal thought process using Claude's native thinking
- 💭 **Configurable thinking budget**: Adjustable token allocation for reasoning (8K-32K tokens)
- 🎛️ **Real-time configuration**: Change reasoning settings without restarting
- 📊 **Token management**: Intelligent max token allocation (1.5x thinking budget)
- 🔧 **Enhanced decision making**: More thorough analysis and better responses

### Streaming AI Response Generation
The system includes **real-time streaming** of the AI agent's thinking process, powered by Strands Agent SDK's async iterators:

- 🧠 **Real-time reasoning**: Watch the AI think through problems step by step
- 🔧 **Tool usage**: See which business tools the AI is calling and why
- ⚡ **Processing lifecycle**: Monitor initialization, cycles, and completion
- 💭 **Decision making**: Understand how the AI reaches its conclusions

### Enhanced UI Features
- **Reasoning Configuration Panel**: Real-time adjustment of thinking parameters
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

### 1. AI Configuration Panel
- **Location:** Left sidebar, top section
- **Model Selection:** Choose between available Claude models
- **Reasoning Configuration:** 
  - **Enable Native Thinking:** Toggle AI's internal reasoning process
  - **Thinking Budget:** Adjust token allocation for reasoning (8K-32K tokens)
  - **Max Response Tokens:** Set maximum tokens for complete response (16K-48K tokens)
  - **Apply Configuration:** Real-time updates without restart

### 2. Email List Display
- **Location:** Left side of the interface
- **Content:** Shows all customer emails loaded from Excel with the following columns:
  - **Email-ID:** Unique identifier for email conversations
  - **Time:** When the email was received
  - **Email Content:** First part of the email content
  - **Status:** Current processing status (Pending/Processed)
- **Order:** Emails are displayed in chronological order (oldest first)

### 2. Action Buttons
- **🔄 Refresh:** Reload emails from the Excel file (`lcsc-emails.xlsx`)
- **🤖 AI Agent Loop:** Generate intelligent response for selected email

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
2. **Click the "🤖 AI Agent Loop" button**
3. **Watch the real-time thinking process** in the "🧠 Agent Loop" tab
4. **View the final response** in the "💬 Final Response" tab
5. **Monitor AI reasoning** including:
   - Tool usage and business logic execution
   - Step-by-step decision making
   - Error handling and recovery
   - Processing lifecycle events

### Refresh Email List
1. **Update the Excel file** (`lcsc-emails.xlsx`) with new email data
2. **Click the "🔄 Refresh Excel Data" button** to reload the email list
3. **New emails will appear** in the list automatically

## 📁 Email File Format

The system now uses an Excel file (`lcsc-emails.xlsx`) located in the `emails` directory with the following structure:

**Required columns:**
- `email-id` - Unique identifier for email conversations
- `converse-time` - Timestamp of the email
- `cs-id` - Customer service representative ID
- `sender` - Email address of the sender
- `receiver` - Email address of the receiver
- `email-content` - Full email content (HTML or text)

**Excel file location:** `./emails/lcsc-emails.xlsx`

**Features:**
- **Email Grouping:** Emails with the same `email-id` are grouped as conversations
- **First Email Display:** The system shows the first email from each conversation in the main list
- **Full Conversation Access:** Complete conversation history available for each email ID
- **Rich Content Support:** Supports both HTML and plain text email content
- **Metadata Tracking:** Includes CS ID and conversation timestamps for better tracking

## 🤖 AI Capabilities

The AI Agent Loop can:
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
├── app.py                      # Main Gradio application with streaming UI
├── agent.py                    # AI agent configuration with async support
├── business_tools.py           # Business logic and tools
├── email_manager.py            # Excel-based email management with streaming support
├── email_parser.py             # Excel email parsing and data management
├── streaming_utils.py          # Streaming event processing utilities
├── data_manager.py             # Data management utilities
├── run_app.sh                  # Application startup script
├── emails/                     # Email files directory
│   ├── lcsc-emails.xlsx        # Main Excel file with email data
│   └── ...                     # Legacy email files (optional)
└── data/                       # Business data (CSV files)
    ├── customers.csv
    ├── orders.csv
    └── ...
```

### Configuration
- **AI Model:** Claude 3.7 Sonnet (configurable in `agent.py`)
- **Server Port:** 7860 (configurable in `app.py`)
- **Excel File:** `./emails/lcsc-emails.xlsx` (configurable in `email_manager.py`)

## 🚨 Troubleshooting

### Common Issues

1. **"AI Agent is not available"**
   - Check AWS credentials configuration
   - Verify Bedrock access permissions
   - Ensure proper model access

2. **"No emails found"**
   - Check if `emails` directory exists
   - Verify `lcsc-emails.xlsx` file exists and is readable
   - Ensure Excel file has the required columns
   - Check Excel file format and data integrity

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
