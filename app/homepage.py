from nicegui import ui, app
from typing import Optional
from datetime import datetime

from app.services import UserService, AssessmentService
from app.models import UserCreate, User, RiskLevel


class HomePage:
    def __init__(self):
        self.current_user: Optional[User] = None

    def create(self):
        """Create the homepage UI"""
        # Apply modern theme
        self._apply_theme()

        # Hero section
        self._create_hero_section()

        # Feature overview
        self._create_feature_overview()

        # User management
        self._create_user_section()

        # Quick start
        self._create_quick_start()

        # Footer
        self._create_footer()

    def _apply_theme(self):
        """Apply modern color theme"""
        ui.colors(
            primary="#2563eb",  # Professional blue
            secondary="#64748b",  # Subtle gray
            accent="#10b981",  # Success green
            positive="#10b981",
            negative="#ef4444",  # Error red
            warning="#f59e0b",  # Warning amber
            info="#3b82f6",  # Info blue
        )

    def _create_hero_section(self):
        """Create hero section with title and description"""
        with ui.column().classes("w-full bg-gradient-to-br from-blue-50 to-indigo-100 py-16 mb-12"):
            ui.label("Ergonomic Risk Assessment System").classes("text-5xl font-bold text-center mb-6 text-primary")
            ui.label("AI-Powered Posture Analysis & GOTRAK Risk Assessment").classes(
                "text-xl text-center text-gray-600 mb-8 max-w-3xl mx-auto"
            )

            # Key benefits
            with ui.row().classes("gap-8 justify-center"):
                self._create_benefit_card(
                    "🎥", "Live Webcam Analysis", "Real-time posture detection using computer vision"
                )
                self._create_benefit_card("📊", "RULA Scoring", "Automated Rapid Upper Limb Assessment calculations")
                self._create_benefit_card(
                    "🗺️", "Interactive Body Map", "Click on body parts to view detailed risk information"
                )

    def _create_benefit_card(self, icon: str, title: str, description: str):
        """Create a benefit card"""
        with ui.card().classes("w-64 p-6 bg-white shadow-lg hover:shadow-xl transition-shadow"):
            ui.label(icon).classes("text-4xl text-center mb-3")
            ui.label(title).classes("text-lg font-semibold text-center mb-2")
            ui.label(description).classes("text-sm text-gray-600 text-center")

    def _create_feature_overview(self):
        """Create feature overview section"""
        with ui.card().classes("w-full max-w-6xl mx-auto mb-12 p-8 shadow-lg"):
            ui.label("How It Works").classes("text-3xl font-bold text-center mb-8")

            with ui.row().classes("gap-8 w-full justify-center"):
                # Step 1
                with ui.column().classes("items-center text-center flex-1"):
                    ui.html(
                        '<div class="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center text-white text-2xl font-bold mb-4">1</div>'
                    )
                    ui.label("Webcam Capture").classes("text-xl font-semibold mb-2")
                    ui.label("Position yourself in front of the camera and capture your working posture").classes(
                        "text-gray-600"
                    )

                ui.html('<div class="w-0.5 h-24 bg-gray-300 self-center"></div>')

                # Step 2
                with ui.column().classes("items-center text-center flex-1"):
                    ui.html(
                        '<div class="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center text-white text-2xl font-bold mb-4">2</div>'
                    )
                    ui.label("GOTRAK Survey").classes("text-xl font-semibold mb-2")
                    ui.label("Complete the questionnaire about discomfort frequency and severity").classes(
                        "text-gray-600"
                    )

                ui.html('<div class="w-0.5 h-24 bg-gray-300 self-center"></div>')

                # Step 3
                with ui.column().classes("items-center text-center flex-1"):
                    ui.html(
                        '<div class="w-16 h-16 bg-purple-500 rounded-full flex items-center justify-center text-white text-2xl font-bold mb-4">3</div>'
                    )
                    ui.label("Interactive Results").classes("text-xl font-semibold mb-2")
                    ui.label("View detailed risk information on the interactive body map").classes("text-gray-600")

    def _create_user_section(self):
        """Create user management section"""
        with ui.card().classes("w-full max-w-4xl mx-auto mb-8 p-6 shadow-lg"):
            ui.label("User Information").classes("text-2xl font-bold mb-6")

            # Check for existing demo user
            demo_user = UserService.get_user_by_email("demo@example.com")

            if demo_user:
                self.current_user = demo_user
                with ui.row().classes("items-center gap-4 mb-4"):
                    ui.label(f"Welcome, {demo_user.name}!").classes("text-xl font-semibold text-green-600")
                    ui.label(f"({demo_user.email})").classes("text-gray-600")

                # Show recent assessments
                if demo_user.id is not None:
                    self._show_recent_assessments(demo_user.id)

            else:
                # User creation form
                self._create_user_form()

    def _create_user_form(self):
        """Create user registration form"""
        ui.label("Create User Profile").classes("text-lg font-semibold mb-4")

        with ui.column().classes("gap-4 max-w-md"):
            self.name_input = ui.input("Full Name", placeholder="Enter your full name").classes("w-full")
            self.email_input = ui.input("Email", placeholder="Enter your email address").classes("w-full")
            self.department_input = ui.input("Department", placeholder="Your department (optional)").classes("w-full")
            self.job_title_input = ui.input("Job Title", placeholder="Your job title (optional)").classes("w-full")

            ui.button("Create Profile", on_click=self._create_user, color="primary").classes("px-6 py-2 mt-2")

    def _create_user(self):
        """Create a new user"""
        try:
            name = self.name_input.value.strip()
            email = self.email_input.value.strip()

            if not name or not email:
                ui.notify("Name and email are required", type="warning")
                return

            # Check if user already exists
            existing_user = UserService.get_user_by_email(email)
            if existing_user:
                ui.notify("A user with this email already exists", type="warning")
                return

            user_data = UserCreate(
                name=name,
                email=email,
                department=self.department_input.value.strip() or None,
                job_title=self.job_title_input.value.strip() or None,
            )

            user = UserService.create_user(user_data)
            self.current_user = user

            ui.notify(f"Profile created successfully for {user.name}!", type="positive")

            # Refresh the page to show the new user
            ui.navigate.to("/")

        except Exception as e:
            import logging

            logging.error(f"Error creating user profile: {str(e)}", exc_info=True)
            ui.notify(f"Error creating profile: {str(e)}", type="negative")

    def _show_recent_assessments(self, user_id: int):
        """Show recent assessments for the user"""
        assessments = AssessmentService.get_user_assessments(user_id)

        if assessments:
            ui.label("Recent Assessments").classes("text-lg font-semibold mb-3")

            with ui.column().classes("gap-2 max-w-2xl"):
                for assessment in assessments[-5:]:  # Show last 5 assessments
                    with ui.card().classes("w-full p-4 bg-gray-50 hover:bg-gray-100 cursor-pointer"):
                        with ui.row().classes("items-center justify-between w-full"):
                            with ui.column():
                                ui.label(assessment.session_name).classes("font-medium")
                                ui.label(f"Created: {assessment.created_at.strftime('%Y-%m-%d %H:%M')}").classes(
                                    "text-sm text-gray-600"
                                )

                            with ui.column().classes("items-end"):
                                status_color = "text-green-600" if assessment.is_completed else "text-orange-600"
                                status_text = "Completed" if assessment.is_completed else "In Progress"
                                ui.label(status_text).classes(f"text-sm font-medium {status_color}")

                                if assessment.overall_risk_level:
                                    risk_color = "text-green-600"
                                    if assessment.overall_risk_level.value == "Yellow":
                                        risk_color = "text-yellow-600"
                                    elif assessment.overall_risk_level.value == "Red":
                                        risk_color = "text-red-600"
                                    ui.label(f"Risk: {assessment.overall_risk_level.value}").classes(
                                        f"text-sm {risk_color}"
                                    )
        else:
            ui.label("No previous assessments found").classes("text-gray-600")

    def _create_quick_start(self):
        """Create quick start section"""
        with ui.card().classes("w-full max-w-4xl mx-auto mb-8 p-8 bg-gradient-to-r from-green-50 to-blue-50 shadow-lg"):
            ui.label("Ready to Start?").classes("text-3xl font-bold text-center mb-6")
            ui.label("Begin your ergonomic risk assessment in just a few clicks").classes(
                "text-lg text-center text-gray-600 mb-8"
            )

            with ui.row().classes("gap-4 justify-center"):
                ui.button(
                    "🎥 Start Assessment", on_click=lambda: ui.navigate.to("/webcam_capture"), color="primary"
                ).classes("px-8 py-4 text-lg font-semibold")

                ui.button("📚 View Demo Results", on_click=self._create_demo_assessment, color="secondary").classes(
                    "px-8 py-4 text-lg font-semibold"
                ).props("outline")

    def _create_demo_assessment(self):
        """Create a demo assessment for demonstration"""
        try:
            # Ensure demo user exists
            demo_user = UserService.get_user_by_email("demo@example.com")
            if not demo_user:
                user_data = UserCreate(
                    name="Demo User", email="demo@example.com", department="Demo Department", job_title="Demo Position"
                )
                demo_user = UserService.create_user(user_data)

            # Create demo assessment with mock data
            from app.models import AssessmentCreate, BodyPartType, SeverityLevel, FrequencyLevel
            from app.services import BodyPartAssessmentService
            from decimal import Decimal

            if demo_user.id is None:
                ui.notify("Error: Could not create demo user", type="negative")
                return

            assessment_data = AssessmentCreate(
                user_id=demo_user.id, session_name=f"Demo Assessment - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            assessment = AssessmentService.create_assessment(assessment_data)

            if assessment and assessment.id is not None:
                # Create demo body part assessments
                demo_data = [
                    (BodyPartType.NECK, SeverityLevel.UNCOMFORTABLE, FrequencyLevel.OFTEN),
                    (BodyPartType.UPPER_BACK, SeverityLevel.PAIN, FrequencyLevel.SOMETIMES),
                    (BodyPartType.SHOULDER_LEFT, SeverityLevel.NO_PROBLEM, FrequencyLevel.NEVER),
                    (BodyPartType.SHOULDER_RIGHT, SeverityLevel.UNCOMFORTABLE, FrequencyLevel.SOMETIMES),
                ]

                for body_part, severity, frequency in demo_data:
                    BodyPartAssessmentService.create_body_part_assessment(
                        assessment_id=assessment.id,
                        body_part=body_part,
                        angles={"mock_angle": 25.0},
                        severity=severity,
                        frequency=frequency,
                    )

                # Complete the assessment
                AssessmentService.complete_assessment(assessment.id, Decimal("3.2"), RiskLevel.YELLOW)

                # Store assessment ID and navigate
                app.storage.client["completed_assessment_id"] = assessment.id
                ui.notify("Demo assessment created!", type="positive")
                ui.navigate.to("/body_map")

        except Exception as e:
            import logging

            logging.error(f"Error creating demo assessment: {str(e)}", exc_info=True)
            ui.notify(f"Error creating demo: {str(e)}", type="negative")

    def _create_footer(self):
        """Create footer section"""
        with ui.card().classes("w-full mt-12 p-6 bg-gray-800 text-white"):
            with ui.row().classes("w-full justify-between items-center"):
                ui.label("Ergonomic Risk Assessment System").classes("text-lg font-semibold")
                ui.label("Built with NiceGUI & Python").classes("text-gray-400")

            ui.separator().classes("my-4 bg-gray-600")

            with ui.row().classes("gap-8"):
                ui.label("Features:").classes("font-medium text-gray-300")
                ui.label("• Real-time posture analysis").classes("text-gray-400")
                ui.label("• RULA scoring system").classes("text-gray-400")
                ui.label("• GOTRAK risk assessment").classes("text-gray-400")
                ui.label("• Interactive body mapping").classes("text-gray-400")


def create():
    """Create the homepage module"""

    @ui.page("/")
    def homepage():
        homepage_component = HomePage()
        homepage_component.create()
