import pytest
from app.database import reset_db


@pytest.fixture()
def new_db():
    reset_db()
    yield
    reset_db()


class TestBasicUIFunctionality:
    def test_application_components_exist(self, new_db):
        """Test that application components exist"""
        # Test that the modules can be imported without errors
        from app import homepage, webcam_capture, questionnaire, body_map

        # Verify key functions exist
        assert hasattr(homepage, "create")
        assert hasattr(webcam_capture, "create")
        assert hasattr(questionnaire, "create")
        assert hasattr(body_map, "create")

    def test_services_are_functional(self, new_db):
        """Test that services are functional"""
        from app.services import UserService
        from app.models import UserCreate

        # Test basic service functionality
        user_data = UserCreate(name="Test User", email="test@example.com")
        user = UserService.create_user(user_data)

        assert user.id is not None
        assert user.name == "Test User"

        # Test that we can retrieve the user
        retrieved_user = UserService.get_user(user.id)
        assert retrieved_user is not None
        assert retrieved_user.name == "Test User"


class TestApplicationIntegrity:
    def test_model_enums_work(self):
        """Test that model enums work correctly"""
        from app.models import SeverityLevel, FrequencyLevel, RiskLevel

        # Test enum values
        assert SeverityLevel.NO_PROBLEM.value == "No problem"
        assert FrequencyLevel.NEVER.value == "Never"
        assert RiskLevel.GREEN.value == "Green"

    def test_calculation_services_work(self):
        """Test that calculation services work"""
        from app.services import GotrakService, RulaCalculationService
        from app.models import SeverityLevel, FrequencyLevel, BodyPartType

        # Test GOTRAK calculation
        score = GotrakService.calculate_gotrak_score(SeverityLevel.UNCOMFORTABLE, FrequencyLevel.SOMETIMES)
        assert score == 4

        # Test RULA calculation
        angles = {"neck_flexion": 15.0}
        result = RulaCalculationService.calculate_rula_score(angles, BodyPartType.NECK)

        assert "final_score" in result
        assert isinstance(result["final_score"], int)
