from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class LearningStyle(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING = "reading"
    MULTIMODAL = "multimodal"


class AssessmentType(str, Enum):
    QUIZ = "quiz"
    EXERCISE = "exercise"
    EXAM = "exam"
    PRACTICE = "practice"
    DIAGNOSTIC = "diagnostic"


class ResponseType(str, Enum):
    EXPLAIN = "explain"
    BRIDGE_GAPS = "bridge_gaps"
    REFUSE = "refuse"


class GapPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GapType(str, Enum):
    MISSING_PREREQUISITE = "missing_prerequisite"
    FORGOTTEN = "forgotten"
    WEAK_UNDERSTANDING = "weak_understanding"
    MISCONCEPTION = "misconception"


class ConceptBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    domain: Optional[str] = Field(None, max_length=100)
    grade_level: Optional[int] = Field(None, ge=1, le=12)
    difficulty: Optional[float] = Field(None, ge=0.0, le=1.0)
    keywords: List[str] = Field(default_factory=list)
    curriculum_code: Optional[str] = Field(None, max_length=50)
    estimated_time_minutes: Optional[int] = Field(None, ge=1)


class ConceptCreate(ConceptBase):
    id: str = Field(..., min_length=1, max_length=100)


class ConceptResponse(ConceptBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConceptWithPrerequisites(ConceptResponse):
    prerequisites: List["ConceptResponse"] = Field(default_factory=list)
    prerequisite_count: int = 0


class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    grade_level: int = Field(..., ge=1, le=12)
    learning_style: LearningStyle = LearningStyle.VISUAL


class StudentCreate(StudentBase):
    student_id: str = Field(..., min_length=1, max_length=100)


class StudentResponse(StudentBase):
    student_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MasteryRecord(BaseModel):
    concept_id: str
    concept_name: str
    mastery_level: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    assessed_at: Optional[datetime] = None


class StruggleRecord(BaseModel):
    concept_id: str
    concept_name: str
    struggle_count: int
    error_patterns: List[str] = Field(default_factory=list)
    last_struggled: Optional[datetime] = None


class LearningQuery(BaseModel):
    student_id: str
    query: str = Field(..., min_length=1, max_length=1000)
    context: Optional[Dict[str, Any]] = None


class KnowledgeGap(BaseModel):
    concept_id: str
    concept_name: str
    priority: GapPriority
    gap_type: GapType
    distance_to_target: int
    current_mastery: float
    recommended_action: str


class LearningResponseModel(BaseModel):
    student_id: str
    query: str
    response: str
    response_type: ResponseType
    target_concept: Optional[Dict[str, Any]]
    prerequisites: List[Dict[str, Any]]
    knowledge_gaps: List[KnowledgeGap]
    readiness_score: float
    can_proceed: bool
    reasoning_path: List[str]


class Question(BaseModel):
    id: str
    text: str
    question_type: str = "multiple_choice"
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None
    difficulty: float = Field(0.5, ge=0.0, le=1.0)


class AssessmentBase(BaseModel):
    student_id: str
    concept_id: str
    assessment_type: AssessmentType = AssessmentType.QUIZ


class AssessmentCreateModel(AssessmentBase):
    questions: List[Question]


class Answer(BaseModel):
    question_id: str
    response: str


class AssessmentSubmission(BaseModel):
    assessment_id: str
    student_id: str
    answers: List[Answer]


class QuestionFeedback(BaseModel):
    question_id: str
    question: str
    student_answer: str
    correct_answer: str
    is_correct: bool
    explanation: Optional[str] = None


class AssessmentResultModel(BaseModel):
    assessment_id: str
    student_id: str
    concept_id: str
    score: float = Field(..., ge=0.0, le=1.0)
    mastery_level: float = Field(..., ge=0.0, le=1.0)
    questions_correct: int
    questions_total: int
    feedback: List[QuestionFeedback]
    recommendations: List[str]


class DomainProgress(BaseModel):
    domain: str
    concepts_mastered: int
    total_concepts: int
    average_mastery: float
    progress_percentage: float


class LearningProgress(BaseModel):
    student_id: str
    total_concepts_mastered: int
    total_assessments: int
    average_score: float
    domain_progress: List[DomainProgress]
    recent_activity: List[Dict[str, Any]]


class DifficultyStats(BaseModel):
    concept_id: str
    concept_name: str
    average_mastery: float
    student_count: int
    difficulty_score: float


class StrugglePattern(BaseModel):
    concept_id: str
    concept_name: str
    struggle_count: int
    common_errors: List[str]


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class KAGRefusal(BaseModel):
    student_id: str
    query: str
    reason: str
    message: str
    suggestions: List[str] = Field(default_factory=list)
