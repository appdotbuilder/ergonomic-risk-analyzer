from sqlmodel import Session, select
from typing import Optional, List, Dict, Any
from decimal import Decimal
import math
from typing import Union
from datetime import datetime

from app.database import ENGINE as engine
from app.models import (
    User,
    Assessment,
    WebcamCapture,
    BodyPartAssessment,
    BodyPartType,
    SeverityLevel,
    FrequencyLevel,
    RiskLevel,
    UserCreate,
    AssessmentCreate,
    BodyPartRiskInfo,
)


class UserService:
    @staticmethod
    def create_user(user_data: UserCreate) -> User:
        with Session(engine) as session:
            user = User(**user_data.model_dump())
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    @staticmethod
    def get_user(user_id: int) -> Optional[User]:
        with Session(engine) as session:
            return session.get(User, user_id)

    @staticmethod
    def get_users() -> List[User]:
        with Session(engine) as session:
            return list(session.exec(select(User).where(User.is_active)).all())

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        with Session(engine) as session:
            statement = select(User).where(User.email == email)
            return session.exec(statement).first()


class AssessmentService:
    @staticmethod
    def create_assessment(assessment_data: AssessmentCreate) -> Assessment:
        with Session(engine) as session:
            assessment = Assessment(**assessment_data.model_dump())
            session.add(assessment)
            session.commit()
            session.refresh(assessment)
            return assessment

    @staticmethod
    def get_assessment(assessment_id: int) -> Optional[Assessment]:
        with Session(engine) as session:
            return session.get(Assessment, assessment_id)

    @staticmethod
    def get_user_assessments(user_id: int) -> List[Assessment]:
        with Session(engine) as session:
            statement = select(Assessment).where(Assessment.user_id == user_id)
            return list(session.exec(statement).all())

    @staticmethod
    def complete_assessment(
        assessment_id: int, overall_rula_score: Decimal, overall_risk_level: RiskLevel
    ) -> Optional[Assessment]:
        with Session(engine) as session:
            assessment = session.get(Assessment, assessment_id)
            if assessment is None:
                return None

            assessment.overall_rula_score = overall_rula_score
            assessment.overall_risk_level = overall_risk_level
            assessment.is_completed = True
            assessment.updated_at = datetime.utcnow()

            session.add(assessment)
            session.commit()
            session.refresh(assessment)
            return assessment


class PostureAnalysisService:
    def __init__(self):
        # Mock implementation - in production would use MediaPipe
        pass

    def analyze_posture(self, image_data: Union[str, bytes]) -> Dict[str, Any]:
        """Analyze posture from webcam image and extract body part angles"""
        # Mock analysis - in production would use computer vision
        # This simulates realistic RULA assessment angles
        import random

        # Simulate pose detection
        pose_detected = random.choice([True, True, True, False])  # 75% success rate

        if not pose_detected:
            return {"error": "No pose detected", "landmarks": None, "pose_detected": False}

        # Mock pose points (normalized coordinates)
        pose_points = {
            0: {"x": 320, "y": 100, "z": 0, "visibility": 0.9},  # nose
            11: {"x": 280, "y": 200, "z": 0, "visibility": 0.9},  # left shoulder
            12: {"x": 360, "y": 200, "z": 0, "visibility": 0.9},  # right shoulder
            13: {"x": 250, "y": 300, "z": 0, "visibility": 0.8},  # left elbow
            14: {"x": 390, "y": 300, "z": 0, "visibility": 0.8},  # right elbow
            15: {"x": 220, "y": 400, "z": 0, "visibility": 0.7},  # left wrist
            16: {"x": 420, "y": 400, "z": 0, "visibility": 0.7},  # right wrist
            23: {"x": 290, "y": 450, "z": 0, "visibility": 0.9},  # left hip
            24: {"x": 350, "y": 450, "z": 0, "visibility": 0.9},  # right hip
        }

        # Calculate angles for RULA assessment
        angles = self._calculate_mock_rula_angles()

        return {"landmarks": pose_points, "angles": angles, "pose_detected": True}

    def _calculate_mock_rula_angles(self) -> Dict[str, float]:
        """Generate realistic mock RULA angles for demonstration"""
        import random

        # Generate realistic angles based on common workplace postures
        angles = {
            "neck_flexion": random.uniform(5, 35),  # 5-35 degrees forward head posture
            "left_upper_arm": random.uniform(15, 60),  # Upper arm elevation
            "right_upper_arm": random.uniform(15, 60),
            "left_forearm": random.uniform(80, 120),  # Elbow angle
            "right_forearm": random.uniform(80, 120),
            "trunk_flexion": random.uniform(0, 25),  # Forward trunk lean
            "left_wrist_deviation": random.uniform(-15, 15),  # Wrist deviation
            "right_wrist_deviation": random.uniform(-15, 15),
        }

        return angles

    def _calculate_angle(self, point1: Dict[str, float], point2: Dict[str, float], point3: Dict[str, float]) -> float:
        """Calculate angle between three points"""
        # Convert to vectors
        a = [point1["x"] - point2["x"], point1["y"] - point2["y"]]
        b = [point3["x"] - point2["x"], point3["y"] - point2["y"]]

        # Calculate dot product and magnitudes
        dot_product = a[0] * b[0] + a[1] * b[1]
        mag_a = math.sqrt(a[0] ** 2 + a[1] ** 2)
        mag_b = math.sqrt(b[0] ** 2 + b[1] ** 2)

        # Calculate angle
        if mag_a == 0 or mag_b == 0:
            return 0.0

        cosine_angle = dot_product / (mag_a * mag_b)
        cosine_angle = max(-1.0, min(1.0, cosine_angle))  # Clamp to [-1, 1]
        angle = math.acos(cosine_angle)

        return math.degrees(angle)

    def _calculate_trunk_angle(
        self,
        left_shoulder: Dict[str, float],
        right_shoulder: Dict[str, float],
        left_hip: Dict[str, float],
        right_hip: Dict[str, float],
    ) -> float:
        """Calculate trunk flexion angle"""
        # Calculate midpoints
        shoulder_mid = {
            "x": (left_shoulder["x"] + right_shoulder["x"]) / 2,
            "y": (left_shoulder["y"] + right_shoulder["y"]) / 2,
        }
        hip_mid = {"x": (left_hip["x"] + right_hip["x"]) / 2, "y": (left_hip["y"] + right_hip["y"]) / 2}

        # Calculate angle from vertical
        dy = hip_mid["y"] - shoulder_mid["y"]
        dx = hip_mid["x"] - shoulder_mid["x"]

        if dy == 0:
            return 0.0

        angle = math.degrees(math.atan2(abs(dx), abs(dy)))
        return angle


class RulaCalculationService:
    @staticmethod
    def calculate_rula_score(angles: Dict[str, float], body_part: BodyPartType) -> Dict[str, Any]:
        """Calculate RULA score based on body part angles"""
        scores = {}

        match body_part:
            case BodyPartType.NECK:
                if "neck_flexion" in angles:
                    neck_angle = angles["neck_flexion"]
                    if neck_angle < 10:
                        scores["position_score"] = 1
                    elif neck_angle < 20:
                        scores["position_score"] = 2
                    else:
                        scores["position_score"] = 3

                    # Simplified RULA calculation for neck
                    scores["final_score"] = scores["position_score"]

            case BodyPartType.ARM_LEFT | BodyPartType.ARM_RIGHT:
                arm_key = "left_upper_arm" if body_part == BodyPartType.ARM_LEFT else "right_upper_arm"
                if arm_key in angles:
                    arm_angle = angles[arm_key]
                    if arm_angle < 20:
                        scores["position_score"] = 1
                    elif arm_angle < 45:
                        scores["position_score"] = 2
                    elif arm_angle < 90:
                        scores["position_score"] = 3
                    else:
                        scores["position_score"] = 4

                    scores["final_score"] = scores["position_score"]

            case BodyPartType.UPPER_BACK:
                if "trunk_flexion" in angles:
                    trunk_angle = angles["trunk_flexion"]
                    if trunk_angle < 5:
                        scores["position_score"] = 1
                    elif trunk_angle < 20:
                        scores["position_score"] = 2
                    elif trunk_angle < 60:
                        scores["position_score"] = 3
                    else:
                        scores["position_score"] = 4

                    scores["final_score"] = scores["position_score"]

            case _:
                # Default scoring for other body parts
                scores["position_score"] = 2
                scores["final_score"] = 2

        return scores

    @staticmethod
    def get_risk_level_from_rula_score(rula_score: int) -> RiskLevel:
        """Convert RULA score to risk level"""
        if rula_score <= 2:
            return RiskLevel.GREEN
        elif rula_score <= 4:
            return RiskLevel.YELLOW
        else:
            return RiskLevel.RED


class GotrakService:
    @staticmethod
    def get_default_questions() -> List[Dict[str, Any]]:
        """Get default GOTRAK questionnaire questions"""
        return [
            {
                "question_text": "How often do you experience discomfort in your neck?",
                "question_category": "frequency",
                "body_part": BodyPartType.NECK,
                "question_order": 1,
            },
            {
                "question_text": "How severe is the discomfort in your neck?",
                "question_category": "severity",
                "body_part": BodyPartType.NECK,
                "question_order": 2,
            },
            {
                "question_text": "How often do you experience discomfort in your shoulders?",
                "question_category": "frequency",
                "body_part": BodyPartType.SHOULDER_LEFT,
                "question_order": 3,
            },
            {
                "question_text": "How severe is the discomfort in your shoulders?",
                "question_category": "severity",
                "body_part": BodyPartType.SHOULDER_LEFT,
                "question_order": 4,
            },
            {
                "question_text": "How often do you experience discomfort in your upper back?",
                "question_category": "frequency",
                "body_part": BodyPartType.UPPER_BACK,
                "question_order": 5,
            },
            {
                "question_text": "How severe is the discomfort in your upper back?",
                "question_category": "severity",
                "body_part": BodyPartType.UPPER_BACK,
                "question_order": 6,
            },
            {
                "question_text": "How often do you experience discomfort in your lower back?",
                "question_category": "frequency",
                "body_part": BodyPartType.LOWER_BACK,
                "question_order": 7,
            },
            {
                "question_text": "How severe is the discomfort in your lower back?",
                "question_category": "severity",
                "body_part": BodyPartType.LOWER_BACK,
                "question_order": 8,
            },
        ]

    @staticmethod
    def calculate_gotrak_score(severity: SeverityLevel, frequency: FrequencyLevel) -> int:
        """Calculate GOTRAK score based on severity and frequency"""
        severity_scores = {
            SeverityLevel.NO_PROBLEM: 1,
            SeverityLevel.UNCOMFORTABLE: 2,
            SeverityLevel.PAIN: 3,
            SeverityLevel.SEVERE_PAIN: 4,
        }

        frequency_scores = {
            FrequencyLevel.NEVER: 1,
            FrequencyLevel.SOMETIMES: 2,
            FrequencyLevel.OFTEN: 3,
            FrequencyLevel.ALWAYS: 4,
        }

        severity_score = severity_scores.get(severity, 1)
        frequency_score = frequency_scores.get(frequency, 1)

        return severity_score * frequency_score

    @staticmethod
    def get_gotrak_risk_level(gotrak_score: int) -> RiskLevel:
        """Convert GOTRAK score to risk level"""
        if gotrak_score <= 4:
            return RiskLevel.GREEN
        elif gotrak_score == 6:
            return RiskLevel.YELLOW
        else:
            return RiskLevel.RED


class BodyPartAssessmentService:
    @staticmethod
    def create_body_part_assessment(
        assessment_id: int,
        body_part: BodyPartType,
        angles: Dict[str, float],
        severity: SeverityLevel,
        frequency: FrequencyLevel,
    ) -> BodyPartAssessment:
        with Session(engine) as session:
            # Calculate RULA score
            rula_data = RulaCalculationService.calculate_rula_score(angles, body_part)
            rula_score = Decimal(str(rula_data.get("final_score", 2)))

            # Calculate GOTRAK score and risk level
            gotrak_score = GotrakService.calculate_gotrak_score(severity, frequency)
            gotrak_risk_level = GotrakService.get_gotrak_risk_level(gotrak_score)

            body_part_assessment = BodyPartAssessment(
                assessment_id=assessment_id,
                body_part=body_part,
                rula_score=rula_score,
                angle_measurements=angles,
                severity_level=severity,
                frequency_level=frequency,
                gotrak_score=gotrak_score,
                gotrak_risk_level=gotrak_risk_level,
            )

            session.add(body_part_assessment)
            session.commit()
            session.refresh(body_part_assessment)
            return body_part_assessment

    @staticmethod
    def get_assessment_body_parts(assessment_id: int) -> List[BodyPartAssessment]:
        with Session(engine) as session:
            statement = select(BodyPartAssessment).where(BodyPartAssessment.assessment_id == assessment_id)
            return list(session.exec(statement).all())

    @staticmethod
    def get_body_part_risk_info(assessment_id: int, body_part: BodyPartType) -> Optional[BodyPartRiskInfo]:
        with Session(engine) as session:
            statement = select(BodyPartAssessment).where(
                BodyPartAssessment.assessment_id == assessment_id, BodyPartAssessment.body_part == body_part
            )
            body_part_assessment = session.exec(statement).first()

            if body_part_assessment is None:
                return None

            return BodyPartRiskInfo(
                body_part_name=body_part_assessment.body_part.value,
                rula_score=body_part_assessment.rula_score,
                severity_level=body_part_assessment.severity_level,
                frequency_level=body_part_assessment.frequency_level,
                gotrak_risk_level=body_part_assessment.gotrak_risk_level,
                gotrak_score=body_part_assessment.gotrak_score,
                additional_notes=body_part_assessment.additional_notes,
            )


class WebcamService:
    @staticmethod
    def save_webcam_capture(
        user_id: int, assessment_id: Optional[int], image_path: str, posture_analysis: Dict[str, Any]
    ) -> WebcamCapture:
        with Session(engine) as session:
            webcam_capture = WebcamCapture(
                user_id=user_id,
                assessment_id=assessment_id,
                image_path=image_path,
                posture_analysis=posture_analysis,
                processing_status="completed",
            )

            session.add(webcam_capture)
            session.commit()
            session.refresh(webcam_capture)
            return webcam_capture
