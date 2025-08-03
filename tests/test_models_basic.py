import pytest
from decimal import Decimal
from datetime import datetime
from app.database import reset_db, ENGINE
from sqlmodel import Session
from app.models import (
    User,
    Assessment,
    BodyPartType,
    SeverityLevel,
    FrequencyLevel,
    RiskLevel,
    UserCreate,
    AssessmentCreate,
)


@pytest.fixture()
def new_db():
    reset_db()
    yield
    reset_db()


class TestBasicModels:
    def test_user_creation_basic(self, new_db):
        """Test basic user creation"""
        user = User(name="John Doe", email="john@example.com")

        with Session(ENGINE) as session:
            session.add(user)
            session.commit()
            session.refresh(user)

        assert user.id is not None
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.is_active is True

    def test_assessment_creation_basic(self, new_db):
        """Test basic assessment creation"""
        # Create user first
        user = User(name="Test User", email="test@example.com")

        with Session(ENGINE) as session:
            session.add(user)
            session.commit()
            session.refresh(user)

            # Ensure user.id is not None before proceeding
            assert user.id is not None
            user_id = user.id

            # Create assessment in same session
            assessment = Assessment(user_id=user_id, session_name="Test Assessment")
            session.add(assessment)
            session.commit()
            session.refresh(assessment)

            assert assessment.id is not None
            assert assessment.user_id == user_id
            assert assessment.session_name == "Test Assessment"
            assert assessment.is_completed is False

    def test_enums_work_correctly(self):
        """Test that all enums have correct values"""
        # Test SeverityLevel
        assert SeverityLevel.NO_PROBLEM.value == "No problem"
        assert SeverityLevel.UNCOMFORTABLE.value == "Uncomfortable"
        assert SeverityLevel.PAIN.value == "Pain"
        assert SeverityLevel.SEVERE_PAIN.value == "Severe pain"

        # Test FrequencyLevel
        assert FrequencyLevel.NEVER.value == "Never"
        assert FrequencyLevel.SOMETIMES.value == "Sometimes"
        assert FrequencyLevel.OFTEN.value == "Often"
        assert FrequencyLevel.ALWAYS.value == "Always"

        # Test RiskLevel
        assert RiskLevel.GREEN.value == "Green"
        assert RiskLevel.YELLOW.value == "Yellow"
        assert RiskLevel.RED.value == "Red"

    def test_body_part_types(self):
        """Test that body part types are correctly defined"""
        assert BodyPartType.NECK.value == "Neck"
        assert BodyPartType.SHOULDER_LEFT.value == "Left Shoulder"
        assert BodyPartType.ARM_RIGHT.value == "Right Arm"
        assert BodyPartType.UPPER_BACK.value == "Upper Back"
        assert BodyPartType.LOWER_BACK.value == "Lower Back"

    def test_schema_models(self):
        """Test schema models work correctly"""
        user_data = UserCreate(name="John Doe", email="john@example.com", department="Engineering")

        assert user_data.name == "John Doe"
        assert user_data.email == "john@example.com"
        assert user_data.department == "Engineering"

        assessment_data = AssessmentCreate(user_id=1, session_name="Test Assessment")

        assert assessment_data.user_id == 1
        assert assessment_data.session_name == "Test Assessment"

    def test_decimal_handling(self, new_db):
        """Test that decimal fields work correctly"""
        user = User(name="Test User", email="test@example.com")

        with Session(ENGINE) as session:
            session.add(user)
            session.commit()
            session.refresh(user)

            assert user.id is not None

            assessment = Assessment(user_id=user.id, overall_rula_score=Decimal("3.5"))

            session.add(assessment)
            session.commit()
            session.refresh(assessment)

        assert assessment.overall_rula_score == Decimal("3.5")

    def test_default_values(self, new_db):
        """Test that default values are set correctly"""
        user = User(name="Test User", email="test@example.com")

        with Session(ENGINE) as session:
            session.add(user)
            session.commit()
            session.refresh(user)

            assert user.id is not None

            assessment = Assessment(user_id=user.id)
            session.add(assessment)
            session.commit()
            session.refresh(assessment)

        assert assessment.session_name == "Assessment Session"
        assert assessment.notes == ""
        assert assessment.is_completed is False
        assert assessment.overall_rula_score is None
        assert assessment.overall_risk_level is None

    def test_datetime_fields(self, new_db):
        """Test that datetime fields are set correctly"""
        user = User(name="Test User", email="test@example.com")

        with Session(ENGINE) as session:
            session.add(user)
            session.commit()
            session.refresh(user)

        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
        assert user.created_at <= user.updated_at
