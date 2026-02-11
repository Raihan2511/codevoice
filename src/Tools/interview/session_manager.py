# src/Tools/interview/session_manager.py
import os
import sys
from typing import Type, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.tool_framework.base_tool import BaseTool

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from src.apps.interviews.models import InterviewSession, InterviewTurn, Question
from src.apps.users.models import User


class SessionManagerInput(BaseModel):
    """Input schema for session management."""
    action: str = Field(
        ..., 
        description="Action to perform: 'create', 'save_turn', or 'complete'"
    )
    user_id: str = Field(default="", description="User ID (for create action)")
    session_id: str = Field(default="", description="Session ID (for save_turn/complete)")
    question_id: str = Field(default="", description="Question ID (for save_turn)")
    user_transcript: str = Field(default="", description="User's answer (for save_turn)")
    ai_message: str = Field(default="", description="AI's response (for save_turn)")
    score: int = Field(default=0, description="Answer score 0-10 (for save_turn)")
    feedback: str = Field(default="", description="Evaluation feedback (for save_turn)")


class SessionManagerTool(BaseTool):
    """
    Manages interview sessions and turns in the Django database.
    Handles creation, updates, and persistence of interview data.
    """
    name: str = "Session_Manager"
    args_schema: Type[BaseModel] = SessionManagerInput
    description: str = (
        "Manages interview sessions in the database. "
        "Can create sessions, save conversation turns, and complete interviews."
    )

    def _execute(
        self,
        action: str,
        user_id: str = "",
        session_id: str = "",
        question_id: str = "",
        user_transcript: str = "",
        ai_message: str = "",
        score: int = 0,
        feedback: str = ""
    ) -> Dict[str, Any]:
        """
        Execute session management actions.
        
        Args:
            action: 'create', 'save_turn', or 'complete'
            user_id: User ID for creating session
            session_id: Session ID for updates
            question_id: Question ID for saving turns
            user_transcript: User's answer
            ai_message: AI's response
            score: Answer score
            feedback: Evaluation feedback
            
        Returns:
            Dictionary with session_id, status, and action result
        """
        try:
            if action == "create":
                return self._create_session(user_id)
            elif action == "save_turn":
                return self._save_turn(
                    session_id, question_id, user_transcript, 
                    ai_message, score, feedback
                )
            elif action == "complete":
                return self._complete_session(session_id)
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            return {"error": f"Session management failed: {str(e)}"}

    def _create_session(self, user_id: str) -> Dict[str, Any]:
        """Create a new interview session."""
        try:
            # Get or create a default user if user_id not provided
            if not user_id:
                user, _ = User.objects.get_or_create(
                    username="test_user",
                    defaults={"email": "test@example.com"}
                )
            else:
                user = User.objects.get(id=user_id)
            
            # Create session
            session = InterviewSession.objects.create(
                user=user,
                status='STARTED',
                total_score=0.0
            )
            
            return {
                "session_id": str(session.id),
                "status": "created",
                "user_id": str(user.id)
            }
        except Exception as e:
            return {"error": f"Failed to create session: {str(e)}"}

    def _save_turn(
        self, 
        session_id: str, 
        question_id: str,
        user_transcript: str,
        ai_message: str,
        score: int,
        feedback: str
    ) -> Dict[str, Any]:
        """Save a conversation turn to the database."""
        try:
            session = InterviewSession.objects.get(id=session_id)
            question = Question.objects.get(id=question_id) if question_id else None
            
            # Create turn
            turn = InterviewTurn.objects.create(
                session=session,
                question=question,
                ai_message=ai_message,
                user_transcript=user_transcript,
                score=score,
                feedback=feedback
            )
            
            # Update session total score (average of all turns)
            turns = session.turns.all()
            if turns:
                avg_score = sum(t.score for t in turns) / len(turns)
                session.total_score = avg_score
                session.save()
            
            return {
                "session_id": str(session.id),
                "turn_id": str(turn.id),
                "status": "saved",
                "total_score": session.total_score
            }
        except Exception as e:
            return {"error": f"Failed to save turn: {str(e)}"}

    def _complete_session(self, session_id: str) -> Dict[str, Any]:
        """Mark a session as completed."""
        try:
            session = InterviewSession.objects.get(id=session_id)
            session.status = 'COMPLETED'
            session.end_time = datetime.now()
            session.save()
            
            return {
                "session_id": str(session.id),
                "status": "completed",
                "total_score": session.total_score,
                "total_turns": session.turns.count()
            }
        except Exception as e:
            return {"error": f"Failed to complete session: {str(e)}"}
