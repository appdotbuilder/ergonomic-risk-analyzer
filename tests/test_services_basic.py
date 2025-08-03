import pytest
from decimal import Decimal
from app.database import reset_db
from app.services import UserService, AssessmentService, PostureAnalysisService, RulaCalculationService, GotrakService
from app.models import UserCreate, AssessmentCreate, BodyPartType, SeverityLevel, FrequencyLevel, RiskLevel


@pytest.fixture()
def new_db():
    reset_db()
    yield
    reset_db()


class TestUserServiceBasic:
    def test_create_and_get_user(self, new_db):
        """Test creating and retrieving a user"""
        user_data = UserCreate(name="John Doe", email="john@example.com", department="Engineering")

        created_user = UserService.create_user(user_data)
        assert created_user.id is not None
        user_id = created_user.id
        assert created_user.name == "John Doe"
        assert created_user.email == "john@example.com"

        # Retrieve the user
        retrieved_user = UserService.get_user(user_id)
        assert retrieved_user is not None
        assert retrieved_user.id == user_id
        assert retrieved_user.name == "John Doe"

    def test_get_nonexistent_user(self, new_db):
        """Test retrieving a non-existent user returns None"""
        user = UserService.get_user(999)
        assert user is None

    def test_get_user_by_email(self, new_db):
        """Test retrieving user by email"""
        user_data = UserCreate(name="Jane Doe", email="jane@example.com")
        created_user = UserService.create_user(user_data)
        assert created_user.id is not None

        retrieved_user = UserService.get_user_by_email("jane@example.com")
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == "jane@example.com"

    def test_get_users_list(self, new_db):
        """Test getting list of users"""
        user1_data = UserCreate(name="User 1", email="user1@example.com")
        user2_data = UserCreate(name="User 2", email="user2@example.com")

        UserService.create_user(user1_data)
        UserService.create_user(user2_data)

        users = UserService.get_users()
        assert len(users) == 2
        assert all(user.is_active for user in users)


class TestAssessmentServiceBasic:
    def test_create_assessment(self, new_db):
        """Test creating an assessment"""
        # Create user first
        user_data = UserCreate(name="Test User", email="test@example.com")
        user = UserService.create_user(user_data)
        assert user.id is not None

        # Create assessment
        assessment_data = AssessmentCreate(user_id=user.id, session_name="Test Assessment")

        assessment = AssessmentService.create_assessment(assessment_data)
        assert assessment.id is not None
        assert assessment.user_id == user.id
        assert assessment.session_name == "Test Assessment"
        assert not assessment.is_completed

    def test_get_assessment(self, new_db):
        """Test retrieving an assessment"""
        user_data = UserCreate(name="Test User", email="test@example.com")
        user = UserService.create_user(user_data)
        assert user.id is not None

        assessment_data = AssessmentCreate(user_id=user.id)
        created_assessment = AssessmentService.create_assessment(assessment_data)

        assert created_assessment.id is not None
        retrieved_assessment = AssessmentService.get_assessment(created_assessment.id)
        assert retrieved_assessment is not None
        assert retrieved_assessment.id == created_assessment.id

    def test_complete_assessment(self, new_db):
        """Test completing an assessment"""
        user_data = UserCreate(name="Test User", email="test@example.com")
        user = UserService.create_user(user_data)
        assert user.id is not None

        assessment_data = AssessmentCreate(user_id=user.id)
        assessment = AssessmentService.create_assessment(assessment_data)
        assert assessment.id is not None

        completed = AssessmentService.complete_assessment(assessment.id, Decimal("3.5"), RiskLevel.YELLOW)

        assert completed is not None
        assert completed.overall_rula_score == Decimal("3.5")
        assert completed.overall_risk_level == RiskLevel.YELLOW
        assert completed.is_completed


class TestPostureAnalysisServiceBasic:
    def test_posture_analysis_returns_valid_structure(self):
        """Test that posture analysis returns expected structure"""
        service = PostureAnalysisService()
        result = service.analyze_posture("mock_data")

        assert isinstance(result, dict)
        assert "pose_detected" in result

        if result.get("pose_detected"):
            assert "angles" in result
            assert "landmarks" in result
            assert isinstance(result["angles"], dict)

    def test_mock_angles_are_realistic(self):
        """Test that mock angles are within realistic ranges"""
        service = PostureAnalysisService()
        angles = service._calculate_mock_rula_angles()

        assert isinstance(angles, dict)
        assert len(angles) > 0

        # Check that angles are within realistic ranges
        for angle_name, angle_value in angles.items():
            if isinstance(angle_value, (int, float)):
                assert -180 <= angle_value <= 180  # Basic angle range check


class TestRulaCalculationServiceBasic:
    def test_calculate_rula_score_basic(self):
        """Test basic RULA score calculation"""
        angles = {"neck_flexion": 15.0}
        result = RulaCalculationService.calculate_rula_score(angles, BodyPartType.NECK)

        assert "position_score" in result
        assert "final_score" in result
        assert isinstance(result["final_score"], int)
        assert 1 <= result["final_score"] <= 7

    def test_risk_level_conversion(self):
        """Test converting RULA scores to risk levels"""
        assert RulaCalculationService.get_risk_level_from_rula_score(1) == RiskLevel.GREEN
        assert RulaCalculationService.get_risk_level_from_rula_score(2) == RiskLevel.GREEN
        assert RulaCalculationService.get_risk_level_from_rula_score(3) == RiskLevel.YELLOW
        assert RulaCalculationService.get_risk_level_from_rula_score(4) == RiskLevel.YELLOW
        assert RulaCalculationService.get_risk_level_from_rula_score(5) == RiskLevel.RED
        assert RulaCalculationService.get_risk_level_from_rula_score(7) == RiskLevel.RED


class TestGotrakServiceBasic:
    def test_default_questions_exist(self):
        """Test that default questions are available"""
        questions = GotrakService.get_default_questions()

        assert isinstance(questions, list)
        assert len(questions) > 0

        for question in questions:
            assert "question_text" in question
            assert "question_category" in question
            assert question["question_category"] in ["frequency", "severity"]

    def test_gotrak_score_calculation(self):
        """Test GOTRAK score calculation"""
        # Test minimum score
        min_score = GotrakService.calculate_gotrak_score(SeverityLevel.NO_PROBLEM, FrequencyLevel.NEVER)
        assert min_score == 1

        # Test maximum score
        max_score = GotrakService.calculate_gotrak_score(SeverityLevel.SEVERE_PAIN, FrequencyLevel.ALWAYS)
        assert max_score == 16

        # Test intermediate score
        mid_score = GotrakService.calculate_gotrak_score(SeverityLevel.UNCOMFORTABLE, FrequencyLevel.SOMETIMES)
        assert mid_score == 4

    def test_gotrak_risk_level_mapping(self):
        """Test GOTRAK risk level mapping"""
        assert GotrakService.get_gotrak_risk_level(1) == RiskLevel.GREEN
        assert GotrakService.get_gotrak_risk_level(4) == RiskLevel.GREEN
        assert GotrakService.get_gotrak_risk_level(6) == RiskLevel.YELLOW
        assert GotrakService.get_gotrak_risk_level(8) == RiskLevel.RED
        assert GotrakService.get_gotrak_risk_level(16) == RiskLevel.RED


class TestIntegrationBasic:
    def test_complete_workflow_basic(self, new_db):
        """Test a basic complete workflow"""
        # 1. Create user
        user_data = UserCreate(name="Integration User", email="integration@example.com")
        user = UserService.create_user(user_data)
        assert user.id is not None

        # 2. Create assessment
        assessment_data = AssessmentCreate(user_id=user.id)
        assessment = AssessmentService.create_assessment(assessment_data)
        assert assessment.id is not None
        assessment_id = assessment.id

        # 3. Analyze posture (mock)
        posture_service = PostureAnalysisService()
        analysis = posture_service.analyze_posture("mock_data")

        # Should get some kind of result
        assert isinstance(analysis, dict)
        assert "pose_detected" in analysis

        # 4. Complete assessment
        completed_assessment = AssessmentService.complete_assessment(assessment_id, Decimal("2.5"), RiskLevel.GREEN)

        assert completed_assessment is not None
        assert completed_assessment.is_completed
        assert completed_assessment.overall_rula_score == Decimal("2.5")
        assert completed_assessment.overall_risk_level == RiskLevel.GREEN
