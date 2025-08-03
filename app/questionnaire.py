from nicegui import ui, app
from typing import Dict, Optional
from decimal import Decimal

from app.services import UserService, AssessmentService, GotrakService, BodyPartAssessmentService
from app.models import SeverityLevel, FrequencyLevel, RiskLevel, AssessmentCreate


class GotrakQuestionnaireComponent:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.assessment_id: Optional[int] = None
        self.responses: Dict[str, Dict[str, str]] = {}
        self.current_question_index = 0
        self.questions = GotrakService.get_default_questions()

    def create(self):
        """Create the GOTRAK questionnaire UI"""
        # Create assessment
        self._create_assessment()

        with ui.column().classes("w-full max-w-4xl mx-auto"):
            # Progress indicator
            self.progress = ui.linear_progress(value=0, show_value=True).classes("w-full mb-6")

            # Question container
            self.question_container = ui.card().classes("w-full p-8 shadow-lg")

            # Navigation buttons
            with ui.row().classes("gap-4 justify-between w-full mt-6"):
                self.prev_btn = (
                    ui.button("← Previous", on_click=self._previous_question).classes("px-6 py-2").props("outline")
                )

                self.next_btn = ui.button("Next →", on_click=self._next_question).classes(
                    "px-6 py-2 bg-primary text-white"
                )

                self.finish_btn = ui.button("Complete Assessment", on_click=self._complete_assessment).classes(
                    "px-6 py-2 bg-green-500 text-white"
                )

            # Show first question
            self._show_current_question()
            self._update_navigation()

    def _create_assessment(self):
        """Create a new assessment"""
        assessment_data = AssessmentCreate(
            user_id=self.user_id,
            session_name=f"GOTRAK Assessment - {app.storage.client.get('session_timestamp', 'Unknown')}",
        )
        assessment = AssessmentService.create_assessment(assessment_data)
        if assessment and assessment.id is not None:
            self.assessment_id = assessment.id

    def _show_current_question(self):
        """Display the current question"""
        if self.current_question_index >= len(self.questions):
            return

        question = self.questions[self.current_question_index]

        self.question_container.clear()

        with self.question_container:
            # Question header
            ui.label(f"Question {self.current_question_index + 1} of {len(self.questions)}").classes(
                "text-sm text-gray-500 mb-2"
            )
            ui.label(question["question_text"]).classes("text-xl font-semibold mb-6")

            # Body part indicator
            if question.get("body_part"):
                ui.label(f"Body Part: {question['body_part'].value}").classes("text-lg text-blue-600 mb-4")

            # Response options based on question category
            question_key = f"q_{self.current_question_index}"

            if question["question_category"] == "frequency":
                self._create_frequency_options(question_key)
            elif question["question_category"] == "severity":
                self._create_severity_options(question_key)

    def _create_frequency_options(self, question_key: str):
        """Create frequency response options"""
        ui.label("How often do you experience this?").classes("font-medium mb-3")

        frequency_options = [
            (FrequencyLevel.NEVER, "🟢 Never"),
            (FrequencyLevel.SOMETIMES, "🟡 Sometimes"),
            (FrequencyLevel.OFTEN, "🟠 Often"),
            (FrequencyLevel.ALWAYS, "🔴 Always"),
        ]

        current_value = self.responses.get(question_key, {}).get("frequency", "")

        for freq_level, display_text in frequency_options:
            ui.radio(
                options=[display_text],
                value=display_text if current_value == freq_level.value else None,
                on_change=lambda e, freq=freq_level: self._save_response(question_key, "frequency", freq.value),
            ).classes("mb-2")

    def _create_severity_options(self, question_key: str):
        """Create severity response options"""
        ui.label("How severe is the discomfort?").classes("font-medium mb-3")

        severity_options = [
            (SeverityLevel.NO_PROBLEM, "🟢 No problem"),
            (SeverityLevel.UNCOMFORTABLE, "🟡 Uncomfortable"),
            (SeverityLevel.PAIN, "🟠 Pain"),
            (SeverityLevel.SEVERE_PAIN, "🔴 Severe pain"),
        ]

        current_value = self.responses.get(question_key, {}).get("severity", "")

        for sev_level, display_text in severity_options:
            ui.radio(
                options=[display_text],
                value=display_text if current_value == sev_level.value else None,
                on_change=lambda e, sev=sev_level: self._save_response(question_key, "severity", sev.value),
            ).classes("mb-2")

    def _save_response(self, question_key: str, response_type: str, value: str):
        """Save response to internal storage"""
        if question_key not in self.responses:
            self.responses[question_key] = {}

        self.responses[question_key][response_type] = value
        self._update_navigation()

    def _previous_question(self):
        """Go to previous question"""
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self._show_current_question()
            self._update_progress()
            self._update_navigation()

    def _next_question(self):
        """Go to next question"""
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self._show_current_question()
            self._update_progress()
            self._update_navigation()

    def _update_progress(self):
        """Update progress indicator"""
        progress_value = (self.current_question_index + 1) / len(self.questions)
        self.progress.set_value(progress_value)

    def _update_navigation(self):
        """Update navigation button states"""
        # Previous button
        self.prev_btn.set_visibility(self.current_question_index > 0)

        # Next button
        current_question_answered = self._is_current_question_answered()
        is_last_question = self.current_question_index >= len(self.questions) - 1

        self.next_btn.set_visibility(current_question_answered and not is_last_question)

        # Finish button
        all_questions_answered = self._are_all_questions_answered()
        self.finish_btn.set_visibility(all_questions_answered)

    def _is_current_question_answered(self) -> bool:
        """Check if current question is answered"""
        question_key = f"q_{self.current_question_index}"
        question = self.questions[self.current_question_index]

        response = self.responses.get(question_key, {})

        if question["question_category"] == "frequency":
            return "frequency" in response
        elif question["question_category"] == "severity":
            return "severity" in response

        return False

    def _are_all_questions_answered(self) -> bool:
        """Check if all questions are answered"""
        for i in range(len(self.questions)):
            question_key = f"q_{i}"
            question = self.questions[i]
            response = self.responses.get(question_key, {})

            if question["question_category"] == "frequency" and "frequency" not in response:
                return False
            elif question["question_category"] == "severity" and "severity" not in response:
                return False

        return True

    def _complete_assessment(self):
        """Complete the assessment and save results"""
        if not self.assessment_id:
            ui.notify("Error: No assessment found", type="negative")
            return

        try:
            # Process responses and create body part assessments
            self._process_responses()

            # Calculate overall scores
            overall_rula, overall_risk = self._calculate_overall_scores()

            # Complete the assessment
            AssessmentService.complete_assessment(self.assessment_id, overall_rula, overall_risk)

            # Store assessment ID for body map
            app.storage.client["completed_assessment_id"] = self.assessment_id

            ui.notify("Assessment completed successfully!", type="positive")
            ui.navigate.to("/body_map")

        except Exception as e:
            import logging

            logging.error(f"Error completing questionnaire assessment: {str(e)}", exc_info=True)
            ui.notify(f"Error completing assessment: {str(e)}", type="negative")

    def _process_responses(self):
        """Process questionnaire responses and create body part assessments"""
        if not self.assessment_id:
            return

        # Group responses by body part
        body_part_responses = {}

        for i, question in enumerate(self.questions):
            question_key = f"q_{i}"
            response = self.responses.get(question_key, {})
            body_part = question.get("body_part")

            if body_part and response:
                if body_part not in body_part_responses:
                    body_part_responses[body_part] = {}

                if question["question_category"] == "frequency":
                    body_part_responses[body_part]["frequency"] = response.get("frequency")
                elif question["question_category"] == "severity":
                    body_part_responses[body_part]["severity"] = response.get("severity")

        # Create body part assessments
        webcam_component = app.storage.client.get("webcam_component")
        latest_analysis = webcam_component.get_latest_analysis() if webcam_component else None
        angles = latest_analysis.get("angles", {}) if latest_analysis else {}

        for body_part, responses in body_part_responses.items():
            if "severity" in responses and "frequency" in responses:
                severity = SeverityLevel(responses["severity"])
                frequency = FrequencyLevel(responses["frequency"])

                BodyPartAssessmentService.create_body_part_assessment(
                    assessment_id=self.assessment_id,
                    body_part=body_part,
                    angles=angles,
                    severity=severity,
                    frequency=frequency,
                )

    def _calculate_overall_scores(self) -> tuple[Decimal, RiskLevel]:
        """Calculate overall RULA score and risk level"""
        if not self.assessment_id:
            return Decimal("2"), RiskLevel.GREEN

        # Get all body part assessments
        body_parts = BodyPartAssessmentService.get_assessment_body_parts(self.assessment_id)

        if not body_parts:
            return Decimal("2"), RiskLevel.GREEN

        # Calculate average RULA score
        rula_scores = [bp.rula_score for bp in body_parts if bp.rula_score is not None]
        if rula_scores:
            avg_rula = sum(rula_scores) / len(rula_scores)
        else:
            avg_rula = Decimal("2")

        # Determine overall risk level
        high_risk_count = sum(1 for bp in body_parts if bp.gotrak_risk_level == RiskLevel.RED)
        moderate_risk_count = sum(1 for bp in body_parts if bp.gotrak_risk_level == RiskLevel.YELLOW)

        if high_risk_count > 0:
            overall_risk = RiskLevel.RED
        elif moderate_risk_count > 1:
            overall_risk = RiskLevel.YELLOW
        else:
            overall_risk = RiskLevel.GREEN

        return Decimal(str(avg_rula)), overall_risk


def create():
    """Create the questionnaire module"""

    @ui.page("/questionnaire")
    async def questionnaire_page():
        await ui.context.client.connected()

        # Get or create default user
        user = UserService.get_user_by_email("demo@example.com")
        if not user:
            ui.notify("Please complete the webcam capture first", type="warning")
            ui.navigate.to("/webcam_capture")
            return

        # Page header
        ui.label("GOTRAK Complaint Survey").classes("text-3xl font-bold text-center mb-8 text-primary")

        # Instructions
        with ui.card().classes("w-full max-w-4xl mx-auto mb-6 p-6 bg-green-50"):
            ui.label("Instructions:").classes("text-lg font-semibold mb-2")
            with ui.column().classes("gap-2"):
                ui.label("Please answer all questions honestly based on your typical work experience").classes(
                    "text-gray-700"
                )
                ui.label("The survey focuses on discomfort frequency and severity for different body parts").classes(
                    "text-gray-700"
                )
                ui.label("Your responses will help determine ergonomic risk levels").classes("text-gray-700")

        # Questionnaire component
        if user and user.id is not None:
            questionnaire = GotrakQuestionnaireComponent(user_id=user.id)
            questionnaire.create()

        # Store timestamp for session naming
        from datetime import datetime

        app.storage.client["session_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M")
