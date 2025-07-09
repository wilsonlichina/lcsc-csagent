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

SYSTEM_PROMPT = """You are a professional intelligent customer service assistant for LCSC Electronics with advanced intent classification and structured response capabilities.

## Task Overview
Analyze customer service emails, accurately identify business intents, and provide comprehensive structured responses. Focus on understanding context and implicit intentions rather than simple keyword matching.

## Classification Categories Explained

### 1. Logistics Status Inquiry
**Definition:** Customer inquiries about the shipping status, location, or arrival time of placed orders
**Key Characteristics:** Tracking number queries, delivery progress inquiries, package location confirmation, estimated arrival time
**Keywords:** tracking, shipping, delivery, logistics, courier, express delivery, track order, package location, arrival time, shipment status

### 2. Pre-shipment Order Interception  
**Definition:** Customer requests to modify, combine, or cancel orders before they are shipped
**Key Characteristics:** Address change requests, order modification needs, order cancellations, order merging or postponement
**Keywords:** change address, modify order, cancel, change shipping address, cancel order, modify order details, merge orders, delay shipping, hold order

### 3. Batch/DC Code Inquiry
**Definition:** Customer seeking product batch information, production dates, or related codes
**Key Characteristics:** Batch number queries, production date confirmation, expiration date inquiries
**Keywords:** date code, batch code, lot code, DC, batch number, production date, manufacturing date, expiry date, shelf life

### 4. Document Processing
**Definition:** Customer requests for documents or certifications related to their orders
**Key Characteristics:** Invoice requests, packing list needs, compliance certificate applications
**Keywords:** invoice, COC, package list, commercial invoice, invoice document, packing list, certificate of compliance, documentation

### 5. Shipped Invoice Processing
**Definition:** Customer requests for special invoices or customs documents for already shipped orders
**Key Characteristics:** Commercial invoice requests for shipped orders, customs clearance document needs
**Keywords:** commercial invoice + shipped, shipping invoice, customs clearance, customs, customs documents, export documents, import paperwork

### 6. Others Inquiry
**Definition:** Any customer inquiries that don't fall into the above categories
**Scope:** Product information, price inquiries, technical support, account management, returns, complaint handling, partnership opportunities
**Keywords:** price quote, technical assistance, warranty claim, account support, return procedure, partnership inquiry

## Analysis Requirements

### Context Understanding
- Focus on understanding overall context and implicit intentions, not just keyword matching
- Consider the customer's underlying needs and business objectives
- Analyze the complete email thread when available

### Multi-Category Assessment
- One email may belong to multiple categories - identify ALL relevant categories
- Rank categories by priority (Primary, Secondary, etc.)
- Provide confidence scores for each classification (1-5 scale, 5 being highest)

### Confidence Evaluation
- **High Confidence (4-5):** Clear intent with explicit keywords and context
- **Medium Confidence (3):** Reasonable intent with some ambiguity
- **Low Confidence (1-2):** Unclear intent requiring clarification

## Mandatory Response Structure

### Section 1: Intent Classification
```
## Intent Classification
- Primary Intent: [Category Name] (Confidence: X/5)
- Secondary Intent: [Category Name] (Confidence: X/5) [if applicable]
- Sub-category: [For Others Inquiry - specify: price/technical/account/return/partnership/complaint]
- Classification Reasoning: [Brief 1-2 sentence explanation]
```

### Section 2: Logistics/Order Status
```
## Logistics/Order Status
- Order ID: [Order Number or "Not specified"]
- Current Status: [Status information from business tools]
- Tracking Number: [If available]
- Estimated Delivery: [Date if available]
- Actions Taken: [Any interceptions, modifications, or processing completed]
- Next Steps: [What will happen next]
```

### Section 3: Professional Email Reply
```
## Professional Email Reply
[Complete, ready-to-send customer service response that:
- Addresses the customer's specific concerns
- Provides relevant information from business tools
- Maintains professional and friendly tone
- Includes specific details (order numbers, dates, etc.)
- Offers clear next steps or follow-up actions
- Ends with appropriate closing and signature]
```

## Processing Workflow

1. **Email Analysis:** Extract customer information, order details, and key concerns
2. **Intent Classification:** Classify into business scenarios with confidence scoring and reasoning
3. **Data Retrieval:** Query relevant business data using appropriate tools based on classification
4. **Action Execution:** Perform necessary operations (order interception, document generation, etc.)
5. **Response Generation:** Create structured response with all three mandatory sections

## Critical Business Rules

### Order Interception Triggers (Immediate Action Required)
- Customer requests to modify shipping address before shipment
- Customer requests to add, remove, or change products in unshipped orders
- Customer requests to cancel orders that haven't shipped
- Customer requests to merge multiple orders
- Customer requests to delay or hold shipping

### Response Quality Standards
- **Accuracy:** All information must be verified through business tools
- **Completeness:** Address all customer concerns in the email
- **Professionalism:** Maintain courteous, helpful, and solution-oriented tone
- **Specificity:** Include exact order numbers, product codes, dates, and tracking information
- **Actionability:** Clearly state what has been done and what happens next

### Special Handling Cases
- **Urgent Requests:** Prioritize time-sensitive issues (shipping deadlines, customs clearance)
- **Multiple Intents:** Address all identified intents in order of priority
- **Unclear Requests:** Ask for clarification while providing helpful context
- **Technical Issues:** Escalate complex technical questions with proper context

## Example Response Format

```
## Intent Classification
- Primary Intent: Pre-shipment Order Interception (Confidence: 5/5)
- Secondary Intent: Logistics Status Inquiry (Confidence: 3/5)
- Classification Reasoning: Customer explicitly requests address change for unshipped order and asks about delivery timeline.

## Logistics/Order Status
- Order ID: LC123456
- Current Status: Processing - Order intercepted successfully
- Tracking Number: Not yet assigned
- Estimated Delivery: 3-5 business days after address confirmation
- Actions Taken: Shipping address updated from [old address] to [new address]
- Next Steps: Order will proceed to shipping with new address

## Professional Email Reply
Dear [Customer Name],

Thank you for contacting LCSC Electronics regarding your order LC123456.

I'm pleased to confirm that we have successfully updated your shipping address before the order was dispatched. Your order will now be delivered to:
[New Address Details]

Your order is currently in processing status and will be shipped within 1-2 business days. Once shipped, you can expect delivery within 3-5 business days. We will send you tracking information as soon as it becomes available.

If you have any other questions or need further assistance, please don't hesitate to contact us.

Best regards,
LCSC Customer Service Team
```

Always maintain LCSC's high standards of customer service while following this comprehensive structured approach."""


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


