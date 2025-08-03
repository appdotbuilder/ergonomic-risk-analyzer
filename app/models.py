from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum


# Enums for standardized values
class SeverityLevel(str, Enum):
    NO_PROBLEM = "No problem"
    UNCOMFORTABLE = "Uncomfortable"
    PAIN = "Pain"
    SEVERE_PAIN = "Severe pain"


class FrequencyLevel(str, Enum):
    NEVER = "Never"
    SOMETIMES = "Sometimes"
    OFTEN = "Often"
    ALWAYS = "Always"


class RiskLevel(str, Enum):
    GREEN = "Green"  # Low risk (1-4)
    YELLOW = "Yellow"  # Moderate risk (6)
    RED = "Red"  # High risk (8-16)


class BodyPartType(str, Enum):
    NECK = "Neck"
    SHOULDER_LEFT = "Left Shoulder"
    SHOULDER_RIGHT = "Right Shoulder"
    ARM_LEFT = "Left Arm"
    ARM_RIGHT = "Right Arm"
    ELBOW_LEFT = "Left Elbow"
    ELBOW_RIGHT = "Right Elbow"
    WRIST_LEFT = "Left Wrist"
    WRIST_RIGHT = "Right Wrist"
    HAND_LEFT = "Left Hand"
    HAND_RIGHT = "Right Hand"
    UPPER_BACK = "Upper Back"
    LOWER_BACK = "Lower Back"
    HIP_LEFT = "Left Hip"
    HIP_RIGHT = "Right Hip"
    THIGH_LEFT = "Left Thigh"
    THIGH_RIGHT = "Right Thigh"
    KNEE_LEFT = "Left Knee"
    KNEE_RIGHT = "Right Knee"
    ANKLE_LEFT = "Left Ankle"
    ANKLE_RIGHT = "Right Ankle"


# Persistent models (stored in database)
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    email: str = Field(unique=True, max_length=255)
    employee_id: Optional[str] = Field(default=None, max_length=50)
    department: Optional[str] = Field(default=None, max_length=100)
    job_title: Optional[str] = Field(default=None, max_length=100)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    assessments: List["Assessment"] = Relationship(back_populates="user")
    webcam_captures: List["WebcamCapture"] = Relationship(back_populates="user")


class Assessment(SQLModel, table=True):
    __tablename__ = "assessments"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    session_name: str = Field(max_length=200, default="Assessment Session")
    overall_rula_score: Optional[Decimal] = Field(default=None, decimal_places=2)
    overall_risk_level: Optional[RiskLevel] = Field(default=None)
    notes: str = Field(default="", max_length=2000)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="assessments")
    webcam_captures: List["WebcamCapture"] = Relationship(back_populates="assessment")
    body_part_assessments: List["BodyPartAssessment"] = Relationship(back_populates="assessment")
    gotrak_responses: List["GotrakResponse"] = Relationship(back_populates="assessment")


class WebcamCapture(SQLModel, table=True):
    __tablename__ = "webcam_captures"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    assessment_id: Optional[int] = Field(default=None, foreign_key="assessments.id")
    image_path: str = Field(max_length=500)  # Path to stored image file
    image_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # Camera settings, resolution, etc.
    posture_analysis: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # Body part coordinates, angles
    processing_status: str = Field(default="pending", max_length=50)  # pending, processing, completed, failed
    error_message: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="webcam_captures")
    assessment: Optional[Assessment] = Relationship(back_populates="webcam_captures")


class BodyPartAssessment(SQLModel, table=True):
    __tablename__ = "body_part_assessments"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    assessment_id: int = Field(foreign_key="assessments.id")
    body_part: BodyPartType
    rula_score: Optional[Decimal] = Field(default=None, decimal_places=2)
    angle_measurements: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # Joint angles, positions
    severity_level: Optional[SeverityLevel] = Field(default=None)
    frequency_level: Optional[FrequencyLevel] = Field(default=None)
    gotrak_risk_level: Optional[RiskLevel] = Field(default=None)
    gotrak_score: Optional[int] = Field(default=None)  # 1-16 score for GOTRAK
    additional_notes: str = Field(default="", max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    assessment: Assessment = Relationship(back_populates="body_part_assessments")


class GotrakQuestion(SQLModel, table=True):
    __tablename__ = "gotrak_questions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    question_text: str = Field(max_length=500)
    question_category: str = Field(max_length=100)  # e.g., "pain", "frequency", "intensity"
    body_part: Optional[BodyPartType] = Field(default=None)  # None for general questions
    question_order: int = Field(default=0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    responses: List["GotrakResponse"] = Relationship(back_populates="question")


class GotrakResponse(SQLModel, table=True):
    __tablename__ = "gotrak_responses"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    assessment_id: int = Field(foreign_key="assessments.id")
    question_id: int = Field(foreign_key="gotrak_questions.id")
    response_value: str = Field(max_length=200)  # The actual response
    response_score: Optional[int] = Field(default=None)  # Numerical score for the response
    body_part: Optional[BodyPartType] = Field(default=None)  # Body part this response relates to
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    assessment: Assessment = Relationship(back_populates="gotrak_responses")
    question: GotrakQuestion = Relationship(back_populates="responses")


class RulaCalculation(SQLModel, table=True):
    __tablename__ = "rula_calculations"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    assessment_id: int = Field(foreign_key="assessments.id")
    body_part: BodyPartType
    angle_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # Raw angle measurements
    position_scores: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # Individual position scores
    muscle_use_score: Optional[int] = Field(default=None)
    force_load_score: Optional[int] = Field(default=None)
    group_a_score: Optional[int] = Field(default=None)  # Upper arm, lower arm, wrist
    group_b_score: Optional[int] = Field(default=None)  # Neck, trunk, legs
    final_rula_score: Optional[int] = Field(default=None)  # 1-7 final score
    action_level: Optional[int] = Field(default=None)  # 1-4 action level
    calculation_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # Additional calculation data
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BodyMap(SQLModel, table=True):
    __tablename__ = "body_maps"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)  # e.g., "Standard Human Body Map"
    image_path: str = Field(max_length=500)  # Path to body map image
    clickable_areas: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # Coordinates for clickable body parts
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas (for validation, forms, API requests/responses)
class UserCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    email: str = Field(max_length=255)
    employee_id: Optional[str] = Field(default=None, max_length=50)
    department: Optional[str] = Field(default=None, max_length=100)
    job_title: Optional[str] = Field(default=None, max_length=100)


class UserUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)
    employee_id: Optional[str] = Field(default=None, max_length=50)
    department: Optional[str] = Field(default=None, max_length=100)
    job_title: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = Field(default=None)


class AssessmentCreate(SQLModel, table=False):
    user_id: int
    session_name: str = Field(max_length=200, default="Assessment Session")
    notes: str = Field(default="", max_length=2000)


class AssessmentUpdate(SQLModel, table=False):
    session_name: Optional[str] = Field(default=None, max_length=200)
    overall_rula_score: Optional[Decimal] = Field(default=None)
    overall_risk_level: Optional[RiskLevel] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=2000)
    is_completed: Optional[bool] = Field(default=None)


class WebcamCaptureCreate(SQLModel, table=False):
    user_id: int
    assessment_id: Optional[int] = Field(default=None)
    image_path: str = Field(max_length=500)
    image_metadata: Dict[str, Any] = Field(default={})


class BodyPartAssessmentCreate(SQLModel, table=False):
    assessment_id: int
    body_part: BodyPartType
    rula_score: Optional[Decimal] = Field(default=None)
    angle_measurements: Dict[str, Any] = Field(default={})
    severity_level: Optional[SeverityLevel] = Field(default=None)
    frequency_level: Optional[FrequencyLevel] = Field(default=None)
    gotrak_risk_level: Optional[RiskLevel] = Field(default=None)
    gotrak_score: Optional[int] = Field(default=None)
    additional_notes: str = Field(default="", max_length=1000)


class BodyPartAssessmentUpdate(SQLModel, table=False):
    rula_score: Optional[Decimal] = Field(default=None)
    angle_measurements: Optional[Dict[str, Any]] = Field(default=None)
    severity_level: Optional[SeverityLevel] = Field(default=None)
    frequency_level: Optional[FrequencyLevel] = Field(default=None)
    gotrak_risk_level: Optional[RiskLevel] = Field(default=None)
    gotrak_score: Optional[int] = Field(default=None)
    additional_notes: Optional[str] = Field(default=None, max_length=1000)


class GotrakQuestionCreate(SQLModel, table=False):
    question_text: str = Field(max_length=500)
    question_category: str = Field(max_length=100)
    body_part: Optional[BodyPartType] = Field(default=None)
    question_order: int = Field(default=0)


class GotrakResponseCreate(SQLModel, table=False):
    assessment_id: int
    question_id: int
    response_value: str = Field(max_length=200)
    response_score: Optional[int] = Field(default=None)
    body_part: Optional[BodyPartType] = Field(default=None)


class RulaCalculationCreate(SQLModel, table=False):
    assessment_id: int
    body_part: BodyPartType
    angle_data: Dict[str, Any] = Field(default={})
    position_scores: Dict[str, Any] = Field(default={})
    muscle_use_score: Optional[int] = Field(default=None)
    force_load_score: Optional[int] = Field(default=None)
    group_a_score: Optional[int] = Field(default=None)
    group_b_score: Optional[int] = Field(default=None)
    final_rula_score: Optional[int] = Field(default=None)
    action_level: Optional[int] = Field(default=None)
    calculation_metadata: Dict[str, Any] = Field(default={})


class BodyMapCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    image_path: str = Field(max_length=500)
    clickable_areas: Dict[str, Any] = Field(default={})


# Response schemas for API/UI
class BodyPartRiskInfo(SQLModel, table=False):
    body_part_name: str
    rula_score: Optional[Decimal]
    severity_level: Optional[SeverityLevel]
    frequency_level: Optional[FrequencyLevel]
    gotrak_risk_level: Optional[RiskLevel]
    gotrak_score: Optional[int]
    additional_notes: str


class AssessmentSummary(SQLModel, table=False):
    id: int
    session_name: str
    overall_rula_score: Optional[Decimal]
    overall_risk_level: Optional[RiskLevel]
    is_completed: bool
    created_at: str  # ISO format datetime string
    body_parts_assessed: int
    high_risk_body_parts: int
