"""
Streaming Utilities for LCSC Email Customer Service System
Helper functions for processing and formatting streaming events from Strands Agent
"""

import time
from typing import Dict, Any, List
from datetime import datetime


def format_streaming_event(event: Dict[str, Any]) -> str:
    """
    Format a streaming event for display in the UI
    
    Args:
        event: Raw streaming event from Strands Agent
        
    Returns:
        str: Formatted event string for UI display
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Handle different event types
    if "error" in event:
        return f"🔴 **[{timestamp}] ERROR:** {event['error']}\n\n"
    
    # Text generation events
    if "data" in event:
        return event["data"]
    
    # Tool usage events - improved formatting
    if "current_tool_use" in event:
        tool_info = event["current_tool_use"]
        tool_name = tool_info.get("name", "Unknown Tool")
        tool_input = tool_info.get("input", {})
        tool_use_id = tool_info.get("toolUseId", "")
        
        # Parse input if it's a string
        if isinstance(tool_input, str):
            try:
                import json
                tool_input = json.loads(tool_input)
            except:
                pass
        
        formatted_input = ""
        if tool_input:
            if isinstance(tool_input, dict):
                formatted_params = []
                for key, value in tool_input.items():
                    formatted_params.append(f"{key}='{value}'")
                formatted_input = f"\n**Parameters:** {', '.join(formatted_params)}"
            else:
                formatted_input = f"\n**Input:** `{tool_input}`"
        
        return f"\n🔧 **[{timestamp}] TOOL CALL:** {tool_name}{formatted_input}\n**Tool ID:** {tool_use_id[:8]}...\n\n"
    
    # Reasoning events
    if event.get("reasoning") and "reasoningText" in event:
        reasoning_text = event["reasoningText"]
        return f"🧠 **[{timestamp}] THINKING:** {reasoning_text}\n\n"
    
    # Lifecycle events
    if event.get("init_event_loop"):
        return f"⚡ **[{timestamp}] INITIALIZING:** Starting AI processing...\n\n"
    
    if event.get("start_event_loop"):
        return f"🚀 **[{timestamp}] STARTED:** AI agent is now processing your request...\n\n"
    
    if event.get("start"):
        return f"🔄 **[{timestamp}] NEW CYCLE:** Beginning analysis cycle...\n\n"
    
    if "message" in event:
        return f"💬 **[{timestamp}] MESSAGE:** New message created\n\n"
    
    if event.get("force_stop"):
        reason = event.get("force_stop_reason", "Unknown reason")
        return f"⏹️ **[{timestamp}] STOPPED:** Processing stopped - {reason}\n\n"
    
    # Default case for unhandled events
    if event:
        return f"ℹ️ **[{timestamp}] EVENT:** {str(event)}\n\n"
    
    return ""


def create_thinking_process_display(events: List[Dict[str, Any]]) -> str:
    """
    Create a comprehensive thinking process display from multiple events
    
    Args:
        events: List of streaming events
        
    Returns:
        str: Formatted thinking process display
    """
    if not events:
        return "🤔 **Thinking Process**\n\nNo events captured yet..."
    
    display_parts = [
        "# 🧠 AI Agent Thinking Process\n",
        f"**Session Started:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "---\n\n"
    ]
    
    for event in events:
        formatted_event = format_streaming_event(event)
        if formatted_event.strip():  # Only add non-empty events
            display_parts.append(formatted_event)
    
    display_parts.append("\n---\n**End of Thinking Process**")
    
    return "".join(display_parts)


def extract_final_response(events: List[Dict[str, Any]]) -> str:
    """
    Extract the final response text from streaming events
    
    Args:
        events: List of streaming events
        
    Returns:
        str: Final response text
    """
    response_parts = []
    
    for event in events:
        if "data" in event and not event.get("reasoning"):
            # This is actual response text, not reasoning
            response_parts.append(event["data"])
    
    final_response = "".join(response_parts).strip()
    
    if not final_response:
        return "No response generated. Please check the thinking process for details."
    
    return final_response


def categorize_events(events: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
    """
    Categorize streaming events by type for analysis
    
    Args:
        events: List of streaming events
        
    Returns:
        Dict: Categorized events
    """
    categories = {
        "reasoning": [],
        "tool_usage": [],
        "text_generation": [],
        "lifecycle": [],
        "errors": []
    }
    
    for event in events:
        if "error" in event:
            categories["errors"].append(event)
        elif event.get("reasoning"):
            categories["reasoning"].append(event)
        elif "current_tool_use" in event:
            categories["tool_usage"].append(event)
        elif "data" in event:
            categories["text_generation"].append(event)
        else:
            categories["lifecycle"].append(event)
    
    return categories


def create_event_summary(events: List[Dict[str, Any]]) -> str:
    """
    Create a summary of the streaming session
    
    Args:
        events: List of streaming events
        
    Returns:
        str: Event summary
    """
    if not events:
        return "No events to summarize."
    
    categories = categorize_events(events)
    
    # Count unique tool calls (avoid counting incremental updates)
    unique_tool_calls = set()
    tool_names_used = set()
    
    for event in categories["tool_usage"]:
        tool_info = event.get("current_tool_use", {})
        tool_name = tool_info.get("name")
        tool_use_id = tool_info.get("toolUseId")
        
        if tool_name and tool_use_id:
            unique_tool_calls.add(tool_use_id)
            tool_names_used.add(tool_name)
    
    summary_parts = [
        "## 📊 Session Summary\n",
        f"**Total Events:** {len(events)}\n",
        f"**Reasoning Steps:** {len(categories['reasoning'])}\n",
        f"**Tools Used:** {len(unique_tool_calls)}\n",
        f"**Text Chunks:** {len(categories['text_generation'])}\n",
        f"**Lifecycle Events:** {len(categories['lifecycle'])}\n",
        f"**Errors:** {len(categories['errors'])}\n\n"
    ]
    
    # List tools used
    if tool_names_used:
        summary_parts.append(f"**Tools Called:** {', '.join(sorted(tool_names_used))}\n\n")
    
    # Show errors if any
    if categories["errors"]:
        summary_parts.append("**Errors Encountered:**\n")
        for i, error_event in enumerate(categories["errors"], 1):
            summary_parts.append(f"{i}. {error_event.get('error', 'Unknown error')}\n")
        summary_parts.append("\n")
    
    return "".join(summary_parts)


class StreamingEventCollector:
    """
    Utility class to collect and manage streaming events
    """
    
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.start_time = time.time()
        self.is_complete = False
    
    def add_event(self, event: Dict[str, Any]):
        """Add an event to the collection"""
        self.events.append({
            **event,
            "_timestamp": time.time(),
            "_relative_time": time.time() - self.start_time
        })
    
    def mark_complete(self):
        """Mark the streaming session as complete"""
        self.is_complete = True
    
    def get_thinking_process(self) -> str:
        """Get formatted thinking process display"""
        return create_thinking_process_display(self.events)
    
    def get_final_response(self) -> str:
        """Get the final response text"""
        return extract_final_response(self.events)
    
    def get_summary(self) -> str:
        """Get session summary"""
        return create_event_summary(self.events)
    
    def clear(self):
        """Clear all events and reset"""
        self.events.clear()
        self.start_time = time.time()
        self.is_complete = False
