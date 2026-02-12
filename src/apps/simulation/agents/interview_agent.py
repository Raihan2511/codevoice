# src/apps/simulation/agents/interview_agent.py
"""
Interview Agent - Main orchestration layer for AI interviews.
Loads tools, converts them to LangChain format, and prepares for LangGraph.
"""
import os
import sys
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.tools import StructuredTool

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.Tools.interview.interview_toolkit import InterviewToolkit
from src.apps.simulation.agents.tool_converter import to_langchain_tools
from src.apps.simulation.agents.prompts import initialize_langfuse


class InterviewAgent:
    """
    Main interview agent that manages tools and LLM.
    
    This class follows the user's pattern from their LangGraph examples,
    loading toolkits, converting tools, and grouping them by purpose.
    """
    
    def __init__(self):
        """Initialize the interview agent with tools and LLM."""
        print("🤖 Initializing Interview Agent...")
        
        # Initialize Langfuse for prompt management
        initialize_langfuse()
        
        # Load the interview toolkit
        print("📦 Loading Interview Toolkit...")
        self.toolkit = InterviewToolkit()
        
        # Convert tools to LangChain format
        print("🔧 Converting tools to LangChain format...")
        all_tools = to_langchain_tools(self.toolkit.get_tools())
        
        # Group tools by purpose (following user's pattern)
        self.question_tools = [t for t in all_tools if t.name == "Question_Selector"]
        self.evaluation_tools = [t for t in all_tools if t.name == "Answer_Evaluator"]
        self.response_tools = [t for t in all_tools if t.name == "Response_Generator"]
        self.session_tools = [t for t in all_tools if t.name == "Session_Manager"]
        
        # All tools combined
        self.all_tools = all_tools
        
        print(f"✅ Loaded {len(all_tools)} tools:")
        print(f"   - Question tools: {[t.name for t in self.question_tools]}")
        print(f"   - Evaluation tools: {[t.name for t in self.evaluation_tools]}")
        print(f"   - Response tools: {[t.name for t in self.response_tools]}")
        print(f"   - Session tools: {[t.name for t in self.session_tools]}")
        
        # Initialize LLM (Krutrim via OpenAI-compatible endpoint)
        print("🧠 Initializing Krutrim LLM...")
        self.llm = self._create_llm()
        
        print("✅ Interview Agent ready!")
    
    def _create_llm(self) -> ChatOpenAI:
        """
        Create the LLM instance using Krutrim's OpenAI-compatible endpoint.
        
        Returns:
            ChatOpenAI instance configured for Krutrim
        """
        krutrim_api_key = os.getenv("KRUTRIM_API_KEY")
        
        if not krutrim_api_key:
            raise ValueError(
                "KRUTRIM_API_KEY not found in environment. "
                "Please set it in your .env file."
            )
        
        return ChatOpenAI(
            model="gpt-oss-120b",
            base_url="https://cloud.olakrutrim.com/v1",
            api_key=krutrim_api_key,
            temperature=0.7  # Balanced for natural conversation
        )
    
    def get_tools_by_category(self, category: str) -> List[StructuredTool]:
        """
        Get tools filtered by category.
        
        Args:
            category: One of 'question', 'evaluation', 'response', 'session', 'all'
            
        Returns:
            List of tools for that category
        """
        category_map = {
            'question': self.question_tools,
            'evaluation': self.evaluation_tools,
            'response': self.response_tools,
            'session': self.session_tools,
            'all': self.all_tools,
        }
        
        return category_map.get(category, [])


# Singleton instance
_agent_instance = None


def get_interview_agent() -> InterviewAgent:
    """
    Get the singleton interview agent instance.
    
    Returns:
        InterviewAgent instance
    """
    global _agent_instance
    
    if _agent_instance is None:
        _agent_instance = InterviewAgent()
    
    return _agent_instance
