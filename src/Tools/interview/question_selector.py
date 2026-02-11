# src/Tools/interview/question_selector.py
import os
import sys
import random
from typing import Type, Dict, Any
from pydantic import BaseModel, Field

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.tool_framework.base_tool import BaseTool

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from src.apps.interviews.models import Question


class QuestionSelectorInput(BaseModel):
    """Input schema for question selection."""
    session_id: str = Field(..., description="The interview session ID")
    difficulty: str = Field(
        default="MEDIUM",
        description="Difficulty level: EASY, MEDIUM, or HARD"
    )
    topic: str = Field(
        default="",
        description="Optional topic filter (e.g., 'Network Engineering', 'Algorithms')"
    )


class QuestionSelectorTool(BaseTool):
    """
    Selects the next interview question from the database.
    Uses smart selection based on difficulty, topic, and interview history.
    """
    name: str = "Question_Selector"
    args_schema: Type[BaseModel] = QuestionSelectorInput
    description: str = (
        "Selects the next technical interview question from the database. "
        "Can filter by difficulty (EASY/MEDIUM/HARD) and topic."
    )

    def _execute(
        self, 
        session_id: str, 
        difficulty: str = "MEDIUM",
        topic: str = ""
    ) -> Dict[str, Any]:
        """
        Execute the question selection logic.
        
        Args:
            session_id: The interview session ID
            difficulty: Question difficulty level
            topic: Optional topic filter
            
        Returns:
            Dictionary with question_id, text, expected_points, difficulty, topic
        """
        try:
            # Build query
            query = Question.objects.filter(difficulty=difficulty.upper())
            
            if topic:
                query = query.filter(topic__icontains=topic)
            
            # Get all matching questions
            questions = list(query)
            
            if not questions:
                # Fallback: get any question if no matches
                questions = list(Question.objects.all())
                
            if not questions:
                return {
                    "error": "No questions found in database. Please add questions first."
                }
            
            # Randomly select one question
            selected_question = random.choice(questions)
            
            return {
                "question_id": str(selected_question.id),
                "text": selected_question.text,
                "expected_points": selected_question.expected_answer_points,
                "difficulty": selected_question.difficulty,
                "topic": selected_question.topic,
            }
            
        except Exception as e:
            return {
                "error": f"Failed to select question: {str(e)}"
            }
