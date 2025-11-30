from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"

class QuestionDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class QuizQuestionCreate(BaseModel):
    video_id: str
    question: str
    options: List[str]
    correct_answer: str
    explanation: Optional[str] = None
    difficulty: QuestionDifficulty = QuestionDifficulty.MEDIUM
    question_type: QuestionType = QuestionType.MULTIPLE_CHOICE

class QuizQuestionResponse(BaseModel):
    id: str
    video_id: str
    question: str
    options: List[str]
    difficulty: str
    question_type: str
    created_at: datetime

class UserAnswer(BaseModel):
    question_id: str
    answer: str

class AnswerResult(BaseModel):
    question_id: str
    is_correct: bool
    correct_answer: str
    explanation: Optional[str] = None

class QuizSession(BaseModel):
    session_id: str
    video_id: str
    questions: List[QuizQuestionResponse]
    started_at: datetime

class QuizResult(BaseModel):
    session_id: str
    score: float
    total_questions: int
    correct_answers: int
    results: List[AnswerResult]
    completed_at: datetime
