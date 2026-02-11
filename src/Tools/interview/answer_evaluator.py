# src/Tools/interview/answer_evaluator.py
import os
import sys
from typing import Type, Dict, Any
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.tool_framework.base_tool import BaseTool


class AnswerEvaluatorInput(BaseModel):
    """Input schema for answer evaluation."""
    user_transcript: str = Field(..., description="The user's spoken answer (transcript)")
    expected_answer_points: str = Field(
        ..., 
        description="Expected key points that should be in the answer"
    )
    question_text: str = Field(..., description="The original question asked")


class AnswerEvaluatorTool(BaseTool):
    """
    Evaluates a user's answer using LLM-based scoring.
    Compares the transcript against expected answer points.
    """
    name: str = "Answer_Evaluator"
    args_schema: Type[BaseModel] = AnswerEvaluatorInput
    description: str = (
        "Evaluates a candidate's answer by comparing it against expected key points. "
        "Returns a score (0-10), reasoning, and constructive feedback."
    )

    def _execute(
        self,
        user_transcript: str,
        expected_answer_points: str,
        question_text: str
    ) -> Dict[str, Any]:
        """
        Execute the answer evaluation logic.
        
        Args:
            user_transcript: What the user said
            expected_answer_points: What we expect in a good answer
            question_text: The original question
            
        Returns:
            Dictionary with score, reasoning, and feedback
        """
        try:
            # Get Krutrim API key
            krutrim_api_key = self.get_tool_config('KRUTRIM_API_KEY')
            if not krutrim_api_key:
                return {
                    "error": "KRUTRIM_API_KEY not configured in environment"
                }
            
            # Initialize LLM (Krutrim via OpenAI-compatible endpoint)
            llm = ChatOpenAI(
                model="gpt-oss-120b",
                base_url="https://cloud.olakrutrim.com/v1",
                api_key=krutrim_api_key,
                temperature=0.3  # Lower temperature for consistent evaluation
            )
            
            # Create evaluation prompt
            evaluation_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert technical interviewer evaluating a candidate's answer.

Your task:
1. Compare the candidate's answer against the expected key points
2. Assign a score from 0-10 (10 = perfect answer covering all points)
3. Provide clear reasoning for the score
4. Give constructive feedback

Be fair but rigorous. Partial credit for partially correct answers."""),
                ("user", """Question: {question}

Expected Key Points:
{expected_points}

Candidate's Answer:
{user_answer}

Provide your evaluation in this format:
SCORE: [0-10]
REASONING: [Why you gave this score]
FEEDBACK: [Constructive feedback for the candidate]""")
            ])
            
            # Run evaluation
            chain = evaluation_prompt | llm
            result = chain.invoke({
                "question": question_text,
                "expected_points": expected_answer_points,
                "user_answer": user_transcript
            })
            
            # Parse the response
            response_text = result.content
            
            # Extract score, reasoning, feedback
            score = 5  # Default
            reasoning = ""
            feedback = ""
            
            for line in response_text.split('\n'):
                if line.startswith('SCORE:'):
                    try:
                        score = int(line.split(':')[1].strip())
                    except:
                        pass
                elif line.startswith('REASONING:'):
                    reasoning = line.split(':', 1)[1].strip()
                elif line.startswith('FEEDBACK:'):
                    feedback = line.split(':', 1)[1].strip()
            
            return {
                "score": score,
                "reasoning": reasoning,
                "feedback": feedback,
                "raw_evaluation": response_text
            }
            
        except Exception as e:
            return {
                "error": f"Failed to evaluate answer: {str(e)}",
                "score": 0,
                "reasoning": "Evaluation failed",
                "feedback": "Unable to evaluate answer due to technical error"
            }
