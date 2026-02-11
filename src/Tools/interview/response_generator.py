# src/Tools/interview/response_generator.py
import os
import sys
from typing import Type, Dict, Any, List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.tool_framework.base_tool import BaseTool


class ResponseGeneratorInput(BaseModel):
    """Input schema for response generation."""
    evaluation_result: Dict = Field(..., description="The evaluation result from AnswerEvaluatorTool")
    conversation_history: List[Dict] = Field(
        default=[],
        description="Previous conversation messages"
    )
    question_text: str = Field(..., description="The current question")


class ResponseGeneratorTool(BaseTool):
    """
    Generates conversational AI responses based on evaluation results.
    Decides whether to ask follow-up questions or move to the next question.
    """
    name: str = "Response_Generator"
    args_schema: Type[BaseModel] = ResponseGeneratorInput
    description: str = (
        "Generates natural conversational responses based on answer evaluation. "
        "Provides feedback and decides next action (follow-up or next question)."
    )

    def _execute(
        self,
        evaluation_result: Dict,
        conversation_history: List[Dict] = None,
        question_text: str = ""
    ) -> Dict[str, Any]:
        """
        Execute the response generation logic.
        
        Args:
            evaluation_result: Score, reasoning, feedback from evaluator
            conversation_history: Previous messages
            question_text: Current question
            
        Returns:
            Dictionary with response_text and action (follow_up or next_question)
        """
        if conversation_history is None:
            conversation_history = []
            
        try:
            # Get Krutrim API key
            krutrim_api_key = self.get_tool_config('KRUTRIM_API_KEY')
            if not krutrim_api_key:
                return {
                    "error": "KRUTRIM_API_KEY not configured in environment"
                }
            
            # Initialize LLM
            llm = ChatOpenAI(
                model="gpt-oss-120b",
                base_url="https://cloud.olakrutrim.com/v1",
                api_key=krutrim_api_key,
                temperature=0.7  # Higher temperature for natural conversation
            )
            
            score = evaluation_result.get('score', 0)
            feedback = evaluation_result.get('feedback', '')
            
            # Determine action based on score
            if score >= 7:
                action = "next_question"
                instruction = "The candidate did well. Acknowledge their answer positively and indicate you'll move to the next question."
            elif score >= 4:
                action = "next_question"
                instruction = "The candidate's answer was okay but could be improved. Provide the feedback and move on."
            else:
                action = "follow_up"
                instruction = "The candidate struggled with this question. Provide a hint or ask a simpler follow-up to help them."
            
            # Create response prompt
            response_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a friendly AI technical interviewer conducting a voice interview.

Guidelines:
- Speak naturally as if in a real conversation
- Keep responses concise (2-3 sentences max)
- Don't use markdown formatting (no asterisks, underscores, etc.)
- Be encouraging and constructive
- Sound human, not robotic

{instruction}"""),
                ("user", """Question: {question}

Evaluation Feedback: {feedback}

Generate a natural spoken response:""")
            ])
            
            # Generate response
            chain = response_prompt | llm
            result = chain.invoke({
                "question": question_text,
                "feedback": feedback,
                "instruction": instruction
            })
            
            response_text = result.content.strip()
            
            return {
                "response_text": response_text,
                "action": action,
                "score": score
            }
            
        except Exception as e:
            return {
                "error": f"Failed to generate response: {str(e)}",
                "response_text": "I apologize, I'm having trouble processing that. Let's continue.",
                "action": "next_question"
            }
