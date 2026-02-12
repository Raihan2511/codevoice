# src/apps/simulation/agents/tool_converter.py
"""
Tool conversion utilities to bridge BaseTool and LangChain StructuredTool.
Follows the user's pattern from their LangGraph examples.
"""
from typing import List
from langchain_core.tools import StructuredTool
import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.tool_framework.base_tool import BaseTool


def to_langchain_tools(tool_list: List[BaseTool]) -> List[StructuredTool]:
    """
    Convert BaseTool instances to LangChain StructuredTool objects.
    
    This allows our custom tools to be used with LangGraph's ToolNode
    and other LangChain components.
    
    Args:
        tool_list: List of BaseTool instances
        
    Returns:
        List of LangChain StructuredTool instances
        
    Example:
        >>> from Tools.interview.interview_toolkit import InterviewToolkit
        >>> toolkit = InterviewToolkit()
        >>> lc_tools = to_langchain_tools(toolkit.get_tools())
        >>> # Now lc_tools can be used with LangGraph
    """
    lc_tools = []
    
    for tool in tool_list:
        lc_tool = StructuredTool.from_function(
            name=tool.name,
            description=tool.description,
            func=tool._execute,
            args_schema=tool.args_schema,
        )
        lc_tools.append(lc_tool)
    
    return lc_tools
