"""
LCSC Email Customer Service AI Agent - Functional Style
Intelligent agent for handling customer service inquiries
"""

from strands import Agent
from strands.models import BedrockModel
from strands_tools import current_time
from business_tools import BUSINESS_TOOLS


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



def create_agent(model_name: str = "claude-3-7-sonnet") -> Agent:
    """
    Create LCSC agent instance
    
    Args:
        model_name: Model name (claude-3-5-sonnet, claude-3-7-sonnet)
        
    Returns:
        Agent: Configured agent instance
    """
    # Get model ID
    model_id = MODEL_MAPPING.get(model_name, MODEL_MAPPING["claude-3-7-sonnet"])
    if model_name not in MODEL_MAPPING:
        print(f"⚠️  Unknown model name: {model_name}, using default claude-3-7-sonnet")
    
    print(f"🔧 Model mapping: {model_name} -> {model_id}")
    
    # Create Bedrock model
    bedrock_model = BedrockModel(
        model_id=model_id,
        region_name='us-west-2',
    )
    
    # Create Agent
    agent = Agent(
        model=bedrock_model,
        tools=BUSINESS_TOOLS + [current_time],
        system_prompt=SYSTEM_PROMPT
    )
    
    print(f"🤖 LCSC Email Customer Service Agent initialized successfully")
    print(f"   Model: {model_name}")
    print(f"   Model ID: {model_id}")
    print(f"   Number of tools: {len(BUSINESS_TOOLS) + 1}")
    
    return agent


