"""
Streaming Utilities for LCSC Email Customer Service System
Helper functions for processing and formatting streaming events from Strands Agent
"""

import time
from typing import Dict, Any, List
from datetime import datetime


def format_streaming_event(event: Dict[str, Any], collector=None) -> str:
    """
    Format a streaming event for display in the UI
    
    Args:
        event: Raw streaming event from Strands Agent
        collector: Optional StreamingEventCollector for buffering
        
    Returns:
        str: Formatted event string for UI display
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Handle different event types
    if "error" in event:
        return f"🔴 **[{timestamp}] ERROR:** {event['error']}\n\n"
    
    # Text generation events - don't display until thinking is complete
    if "data" in event:
        if collector:
            # Only return data if we've seen a MESSAGE event (thinking complete)
            has_message = any(e.get("message") for e in collector.events)
            if has_message:
                return event["data"]
            else:
                return ""  # Buffer the response data until thinking is done
        else:
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
    
    # Reasoning events - use buffering if collector is provided
    if event.get("reasoning") and "reasoningText" in event:
        reasoning_text = event["reasoningText"]
        
        if collector:
            # Use buffering for smoother display
            buffered_text = collector.add_thinking_text(reasoning_text)
            if buffered_text:
                return f"🧠 **[{timestamp}] THINKING:** {buffered_text}\n\n"
            else:
                return ""  # Text is being buffered
        else:
            # Fallback to immediate display - but only if it's substantial
            if len(reasoning_text.strip()) >= 10:  # Higher threshold for better quality
                return f"🧠 **[{timestamp}] THINKING:** {reasoning_text.strip()}\n\n"
            else:
                return ""
    
    # Lifecycle events
    if event.get("init_event_loop"):
        return f"⚡ **[{timestamp}] INITIALIZING:** Starting AI processing...\n\n"
    
    if event.get("start_event_loop"):
        return f"🚀 **[{timestamp}] STARTED:** AI agent is now processing your request...\n\n"
    
    if event.get("start"):
        return f"🔄 **[{timestamp}] NEW CYCLE:** Beginning analysis cycle...\n\n"
    
    if "message" in event:
        return f"\n\n💬 **[{timestamp}] MESSAGE:** New message created\n\n"
    
    if event.get("force_stop"):
        reason = event.get("force_stop_reason", "Unknown reason")
        return f"⏹️ **[{timestamp}] STOPPED:** Processing stopped - {reason}\n\n"
    
    # Default case for unhandled events
    # if event:
    #     return f"ℹ️ **[{timestamp}] EVENT:** {str(event)}\n\n"
    
    return ""





def extract_final_response(events: List[Dict[str, Any]]) -> str:
    """
    Extract the final response text from streaming events
    Only return response if we've seen a MESSAGE event (indicating thinking is complete)
    
    Args:
        events: List of streaming events
        
    Returns:
        str: Final response text or empty string if thinking not complete
    """
    # Check if we have a MESSAGE event indicating completion
    has_message_event = any(event.get("message") for event in events)
    
    if not has_message_event:
        return ""  # Don't return response until thinking is complete
    
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
        self.thinking_buffer = ""  # Buffer for thinking text chunks
        self.last_thinking_flush = time.time()
    
    def add_event(self, event: Dict[str, Any]):
        """Add an event to the collection"""
        self.events.append({
            **event,
            "_timestamp": time.time(),
            "_relative_time": time.time() - self.start_time
        })
    
    def should_flush_thinking_buffer(self) -> bool:
        """Determine if thinking buffer should be flushed - very conservative approach"""
        current_time = time.time()
        buffer_length = len(self.thinking_buffer.strip())
        
        # Extremely conservative flushing - only flush when absolutely necessary:
        
        # 1. Buffer is extremely long (force flush to avoid memory issues only)
        if buffer_length >= 2000:
            return True
            
        # 2. Very long timeout - only flush after very long time with substantial content
        if current_time - self.last_thinking_flush > 15.0 and buffer_length > 500:
            return True
        
        # Don't flush on punctuation or paragraph breaks - let it accumulate
        return False
    
    def add_thinking_text(self, text: str) -> str:
        """Add thinking text to buffer and return when ready to display"""
        # Skip empty or whitespace-only text
        if not text or not text.strip():
            return ""
            
        self.thinking_buffer += text
        
        # Check if we should flush based on current conditions
        if self.should_flush_thinking_buffer():
            result = self.thinking_buffer.strip()
            self.thinking_buffer = ""
            self.last_thinking_flush = time.time()
            return result
        
        return ""
    
    def force_flush_thinking_buffer(self) -> str:
        """Force flush any remaining thinking buffer"""
        if self.thinking_buffer.strip():
            result = self.thinking_buffer.strip()
            self.thinking_buffer = ""
            return result
        return ""
    
    def mark_complete(self):
        """Mark the streaming session as complete"""
        self.is_complete = True
    
    def get_thinking_process(self) -> str:
        """Get formatted thinking process display"""
        if not self.events:
            return "🤔 **Agent Loop**\n\nNo events captured yet..."
        
        display_parts = [
            "# 🧠 AI Agent Agent Loop\n",
            f"**Session Started:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "---\n\n"
        ]
        
        for event in self.events:
            formatted_event = format_streaming_event(event)
            if formatted_event.strip():  # Only add non-empty events
                display_parts.append(formatted_event)
        
        display_parts.append("\n---\n**End of Agent Loop**")
        
        return "".join(display_parts)
    
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
