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

## Your Responsibilities
1. Analyze customer email content and accurately identify customer intent
2. Call appropriate business tools to retrieve information based on intent
3. For requests involving order modifications, cancellations, or mergers, proactively execute order interception
4. Provide accurate, professional, and friendly customer service responses

## Important Business Rules
1. **Order Interception Trigger Conditions**:
   - Customer requests to modify shipping address
   - Customer requests to add or remove products
   - Customer requests to cancel order
   - Customer requests to merge orders
   
2. **Processing Workflow**:
   - First identify customer and related orders from email content
   - Query relevant information (customer, orders, products, etc.)
   - If order changes are involved, immediately execute interception operation
   - Provide detailed processing results and follow-up guidance

3. **Response Requirements**:
   - Use professional and friendly tone
   - Provide specific order numbers and product information
   - Clearly state operations that have been executed
   - Give follow-up processing recommendations

## Example Scenarios
- Price inquiries: Query product information and inventory status
- Order inquiries: Query order status and logistics information
- Address changes: Intercept shipping and explain follow-up process
- Product changes: Intercept shipping and confirm change details
- Order cancellations: Intercept shipping and handle refund process

Please always maintain professional, accurate, and efficient service standards."""


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


