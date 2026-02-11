# src/Tools/interview/interview_toolkit.py
import os
import sys
from typing import List
from abc import ABC

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.tool_framework.base_tool import BaseTool
from src.tool_framework.base_toolkit import BaseToolkit
from src.tool_framework.tool_config import ToolConfiguration
from src.types.key_type import ToolConfigKeyType

# Import interview tools
from src.Tools.interview.question_selector import QuestionSelectorTool
from src.Tools.interview.answer_evaluator import AnswerEvaluatorTool
from src.Tools.interview.response_generator import ResponseGeneratorTool
from src.Tools.interview.session_manager import SessionManagerTool


class InterviewToolkit(BaseToolkit, ABC):
    """
    Interview Toolkit contains all tools related to conducting AI technical interviews.
    
    Tools included:
    - QuestionSelectorTool: Selects questions from database
    - AnswerEvaluatorTool: Scores answers using LLM
    - ResponseGeneratorTool: Generates conversational responses
    - SessionManagerTool: Manages database persistence
    """
    name: str = "Interview Toolkit"
    description: str = (
        "Interview Toolkit contains all tools for conducting AI-powered technical interviews, "
        "including question selection, answer evaluation, response generation, and session management."
    )

    def get_tools(self) -> List[BaseTool]:
        """
        Returns all interview tools.
        
        Returns:
            List of BaseTool instances for interview operations
        """
        return [
            QuestionSelectorTool(),
            AnswerEvaluatorTool(),
            ResponseGeneratorTool(),
            SessionManagerTool(),
        ]

    def get_env_keys(self) -> List[ToolConfiguration]:
        """
        Declares required environment variables for the interview toolkit.
        
        Returns:
            List of ToolConfiguration objects specifying required env vars
        """
        return [
            # LLM Configuration
            ToolConfiguration(
                key="KRUTRIM_API_KEY",
                key_type=ToolConfigKeyType.STRING,
                is_required=True,
                is_secret=True
            ),
            
            # Observability Configuration
            ToolConfiguration(
                key="LANGFUSE_PUBLIC_KEY",
                key_type=ToolConfigKeyType.STRING,
                is_required=False,  # Optional for now
                is_secret=False
            ),
            ToolConfiguration(
                key="LANGFUSE_SECRET_KEY",
                key_type=ToolConfigKeyType.STRING,
                is_required=False,  # Optional for now
                is_secret=True
            ),
            ToolConfiguration(
                key="LANGFUSE_HOST",
                key_type=ToolConfigKeyType.STRING,
                is_required=False,
                is_secret=False
            ),
            
            # Interview Configuration
            ToolConfiguration(
                key="MAX_QUESTIONS_PER_INTERVIEW",
                key_type=ToolConfigKeyType.INTEGER,
                is_required=False,
                is_secret=False
            ),
            ToolConfiguration(
                key="MAX_TOOL_TOKEN_LIMIT",
                key_type=ToolConfigKeyType.INTEGER,
                is_required=False,
                is_secret=False
            ),
        ]
