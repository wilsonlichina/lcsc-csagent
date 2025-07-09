"""
LCSC Email Customer Service AI Agent - Functional Style
Intelligent agent for handling customer service inquiries with streaming support and native thinking
"""

import asyncio
from strands import Agent
from strands.models import BedrockModel
from strands_tools import current_time
from business_tools import BUSINESS_TOOLS
from botocore.config import Config


# Constants definition
MODEL_MAPPING = {
    "claude-3-5-sonnet": "us.anthropic.claude-3-5-sonnet-20240620-v1:0",
    "claude-3-7-sonnet": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
}

SYSTEM_PROMPT = """You are a professional intelligent customer service assistant for LCSC Electronics.

## Intent Classification
Analyze each email and classify it into one or more of these 6 business scenarios:
1. **Logistics Status Inquiry** - Keywords: tracking, shipping, delivery, logistics, courier, logistics status, express delivery, track order
2. **Pre-shipment Order Interception** - Keywords: change address, modify order, cancel, change shipping address, cancel order, modify order details, merge orders, delay shipping
3. **Batch/DC Code Inquiry** - Keywords: date code, batch code, lot code, DC, batch number, production date, manufacturing date
4. **Document Processing** - Keywords: invoice, COC, package list, commercial invoice, invoice document, packing list, certificate of compliance
5. **Shipped Invoice Processing** - Keywords: commercial invoice + shipped, shipping invoice, customs clearance, customs, customs documents
6. **Others Inquiry** - Any inquiry not fitting above categories, including price, technical, account, return, partnership, complaints

## Classification Rules
- Always provide confidence level (High/Medium/Low) for each classification
- If multiple intents are detected, list them in order of priority
- For "Others Inquiry", specify the sub-category (price/technical/account/return/partnership/complaint)

## Response Structure
Your response must include these sections:
1. **Intent Classification**: List identified business scenarios with confidence levels
2. **Logistics/Order Status**: Current status information (if applicable)
3. **Professional Email Reply**: Complete, ready-to-send customer response

## Processing Workflow
1. Extract customer information and order details from email content
2. Classify email intent into business scenarios with confidence scoring
3. Query relevant business data using appropriate tools
4. Execute necessary operations (e.g., order interception for pre-shipment modifications)
5. Generate structured response with all required sections

## Important Business Rules
1. **Order Interception Trigger Conditions**:
   - Customer requests to modify shipping address
   - Customer requests to add or remove products
   - Customer requests to cancel order
   - Customer requests to merge orders
   - Customer requests to delay shipping
   
2. **Response Requirements**:
   - Use professional and friendly tone
   - Provide specific order numbers and product information
   - Clearly state operations that have been executed
   - Give follow-up processing recommendations
   - Include confidence levels for intent classification

## Example Response Format
```
## Intent Classification
- Primary Intent: [Business Scenario Name]
- Secondary Intent: [If applicable]
- Confidence: [High/Medium/Low]
- Sub-category: [For Others Inquiry - specify type]

## Logistics/Order Status  
- Order ID: [Order Number]
- Current Status: [Status]
- Tracking Number: [If available]
- Estimated Delivery: [Date]
- Actions Taken: [Any interceptions or modifications]

## Professional Email Reply
[Complete, professional customer service email response]
```

Please always maintain professional, accurate, and efficient service standards while following this structured approach."""


# Agent Configuration
DEFAULT_AGENT_CONFIG = {
    "enable_native_thinking": True,
    "thinking_budget": 16000,
    "max_parallel_tools": 4,
    "record_direct_tool_call": True
}

DEFAULT_MODEL_CONFIG = {
    "region": "us-west-2",
    "max_tokens": 24000  # 1.5x thinking budget by default
}


def create_agent(model_name: str = "claude-3-7-sonnet", config: dict = None) -> Agent:
    """
    Create LCSC agent instance with native thinking capabilities
    
    Args:
        model_name: Model name (claude-3-5-sonnet, claude-3-7-sonnet)
        config: Optional configuration dictionary with agent and model settings
        
    Returns:
        Agent: Configured agent instance with reasoning capabilities
    """
    # Merge with default configurations
    agent_config = {**DEFAULT_AGENT_CONFIG, **(config.get("agent", {}) if config else {})}
    model_config = {**DEFAULT_MODEL_CONFIG, **(config.get("model", {}) if config else {})}
    
    # Get model ID
    model_id = MODEL_MAPPING.get(model_name, MODEL_MAPPING["claude-3-7-sonnet"])
    if model_name not in MODEL_MAPPING:
        print(f"⚠️  Unknown model name: {model_name}, using default claude-3-7-sonnet")
    
    print(f"🔧 Model mapping: {model_name} -> {model_id}")
    
    # Prepare additional request fields for native thinking
    additional_request_fields = {}
    if agent_config.get("enable_native_thinking", False):
        thinking_budget = agent_config.get("thinking_budget", 16000)
        max_tokens = model_config.get("max_tokens", int(thinking_budget * 1.5))
        additional_request_fields = {
            "max_tokens": max_tokens,
            "thinking": {
                "type": "enabled",
                "budget_tokens": thinking_budget
            }
        }
        print(f"🧠 Native thinking enabled: budget={thinking_budget}, max_tokens={max_tokens}")
    
    # Create Bedrock model with enhanced configuration
    bedrock_model = BedrockModel(
        model_id=model_id,
        region=model_config.get("region", "us-west-2"),
        boto_client_config=Config(
            retries={
                "max_attempts": 3,
                "mode": "standard",
            },
            read_timeout=600,
            connect_timeout=30,
        ),
        additional_request_fields=additional_request_fields
    )
    
    # Create Agent with enhanced configuration
    agent = Agent(
        model=bedrock_model,
        tools=BUSINESS_TOOLS + [current_time],
        system_prompt=SYSTEM_PROMPT,
        max_parallel_tools=agent_config.get("max_parallel_tools", 4),
        record_direct_tool_call=agent_config.get("record_direct_tool_call", True),
        callback_handler=None  # Disable callback handler for streaming
    )
    
    print(f"🤖 LCSC Email Customer Service Agent initialized successfully")
    print(f"   Model: {model_name}")
    print(f"   Model ID: {model_id}")
    print(f"   Number of tools: {len(BUSINESS_TOOLS) + 1}")
    print(f"   Native thinking: {'✅ Enabled' if agent_config.get('enable_native_thinking') else '❌ Disabled'}")
    print(f"   Max parallel tools: {agent_config.get('max_parallel_tools', 4)}")
    print(f"   Streaming: Enabled")
    
    return agent


async def process_email_with_streaming(agent: Agent, email_content: str, customer_email: str = None):
    """
    Process email with AI agent using async streaming
    
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
        # Prepare context
        context = f"Customer Email: {customer_email or 'Not provided'}\n\nEmail Content:\n{email_content}"
        
        # Stream agent response
        async for event in agent.stream_async(context):
            yield event
            
    except Exception as e:
        yield {"error": f"❌ Error processing email with AI: {str(e)}"}


def run_streaming_process(agent: Agent, email_content: str, customer_email: str = None):
    """
    Synchronous wrapper for async streaming process
    
    Args:
        agent: AI agent instance
        email_content: Email content to process
        customer_email: Customer email for context
        
    Returns:
        Generator: Streaming events
    """
    async def async_generator():
        async for event in process_email_with_streaming(agent, email_content, customer_email):
            yield event
    
    # Create new event loop for this process
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        async_gen = async_generator()
        while True:
            try:
                event = loop.run_until_complete(async_gen.__anext__())
                yield event
            except StopAsyncIteration:
                break
    finally:
        loop.close()


