from nicegui import ui, app
from typing import Optional, Dict, Any
from datetime import datetime

from app.services import PostureAnalysisService, WebcamService


class WebcamCaptureComponent:
    def __init__(self, user_id: int, assessment_id: Optional[int] = None):
        self.user_id = user_id
        self.assessment_id = assessment_id
        self.posture_service = PostureAnalysisService()
        self.latest_analysis: Optional[Dict[str, Any]] = None

    def create(self):
        """Create the webcam capture UI component"""
        with ui.card().classes("w-full max-w-2xl mx-auto p-6 shadow-lg"):
            ui.label("Posture Analysis Camera").classes("text-xl font-bold mb-4")

            # Camera preview
            with ui.row().classes("w-full justify-center mb-4"):
                self.camera_preview = ui.interactive_image().classes("w-96 h-72 border-2 border-gray-300 rounded-lg")
                self.camera_preview.content = "/static/images/camera_placeholder.png"

            # Camera controls
            with ui.row().classes("gap-4 justify-center mb-4"):
                self.start_camera_btn = ui.button("Start Camera", on_click=self._start_camera, color="primary").classes(
                    "px-6 py-2"
                )

                self.capture_btn = ui.button(
                    "Capture Posture", on_click=self._capture_posture, color="positive"
                ).classes("px-6 py-2")

                self.stop_camera_btn = ui.button("Stop Camera", on_click=self._stop_camera, color="negative").classes(
                    "px-6 py-2"
                )

            # Status display
            self.status_label = ui.label('Click "Start Camera" to begin posture analysis').classes(
                "text-center text-gray-600 mb-4"
            )

            # Analysis results
            with ui.expansion("Analysis Results", icon="analytics").classes("w-full") as self.results_expansion:
                self.results_container = ui.column().classes("p-4")
                self._show_placeholder_results()

    def _start_camera(self):
        """Start the camera feed"""
        # In a real implementation, this would initialize the camera
        self.status_label.set_text("Camera started - Position yourself in front of the camera")
        self.camera_preview.content = "/static/images/camera_active.png"
        ui.notify("Camera started successfully", type="positive")

    def _stop_camera(self):
        """Stop the camera feed"""
        self.status_label.set_text("Camera stopped")
        self.camera_preview.content = "/static/images/camera_placeholder.png"
        ui.notify("Camera stopped", type="info")

    def _capture_posture(self):
        """Capture and analyze current posture"""
        try:
            # Mock image data - in production would capture from camera
            mock_image_data = "mock_webcam_capture_data"

            # Analyze posture
            self.latest_analysis = self.posture_service.analyze_posture(mock_image_data)

            if not self.latest_analysis.get("pose_detected"):
                ui.notify("No pose detected. Please ensure you are visible in the camera.", type="warning")
                return

            # Save the capture
            image_path = f"captures/user_{self.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            WebcamService.save_webcam_capture(
                user_id=self.user_id,
                assessment_id=self.assessment_id,
                image_path=image_path,
                posture_analysis=self.latest_analysis,
            )

            # Update UI
            self.status_label.set_text("Posture captured and analyzed successfully!")
            self._update_analysis_results()
            self.results_expansion.open()

            ui.notify("Posture analysis completed!", type="positive")

        except Exception as e:
            import logging

            logging.error(f"Error during webcam capture: {str(e)}", exc_info=True)
            ui.notify(f"Error during capture: {str(e)}", type="negative")
            self.status_label.set_text("Error occurred during posture analysis")

    def _update_analysis_results(self):
        """Update the analysis results display"""
        if not self.latest_analysis:
            return

        self.results_container.clear()

        with self.results_container:
            if self.latest_analysis.get("pose_detected"):
                ui.label("✅ Pose Detection: Successful").classes("text-green-600 font-semibold mb-2")

                # Display angle measurements
                angles = self.latest_analysis.get("angles", {})
                if angles:
                    ui.label("📐 Measured Angles:").classes("font-semibold mb-2")

                    with ui.grid(columns=2).classes("gap-4 w-full"):
                        for angle_name, angle_value in angles.items():
                            if isinstance(angle_value, (int, float)):
                                ui.label(f"{angle_name.replace('_', ' ').title()}:").classes("font-medium")
                                ui.label(f"{angle_value:.1f}°").classes("text-blue-600")

                # Risk indicators
                ui.separator().classes("my-4")
                ui.label("⚠️ Initial Risk Assessment:").classes("font-semibold mb-2")

                # Simple risk assessment based on angles
                risk_items = []
                if angles.get("neck_flexion", 0) > 20:
                    risk_items.append("Neck forward posture detected")
                if angles.get("trunk_flexion", 0) > 15:
                    risk_items.append("Forward trunk lean detected")
                if any(angles.get(f"{side}_upper_arm", 0) > 45 for side in ["left", "right"]):
                    risk_items.append("Elevated arm posture detected")

                if risk_items:
                    for item in risk_items:
                        ui.label(f"• {item}").classes("text-orange-600 ml-4")
                else:
                    ui.label("• Good overall posture detected").classes("text-green-600 ml-4")

            else:
                ui.label("❌ Pose Detection: Failed").classes("text-red-600 font-semibold")
                ui.label("Please ensure you are clearly visible in the camera frame.").classes("text-gray-600")

    def _show_placeholder_results(self):
        """Show placeholder analysis results"""
        with self.results_container:
            ui.label("Capture your posture to see detailed analysis results here.").classes("text-gray-500 text-center")

    def get_latest_analysis(self) -> Optional[Dict[str, Any]]:
        """Get the latest posture analysis results"""
        return self.latest_analysis


def create():
    """Create the webcam capture module"""

    @ui.page("/webcam_capture")
    async def webcam_capture_page():
        await ui.context.client.connected()

        # Get or create default user
        from app.services import UserService
        from app.models import UserCreate

        user = UserService.get_user_by_email("demo@example.com")
        if user is None:
            user_data = UserCreate(
                name="Demo User", email="demo@example.com", department="Demo Department", job_title="Demo Position"
            )
            user = UserService.create_user(user_data)

        # Page header
        ui.label("Ergonomic Risk Assessment - Posture Capture").classes(
            "text-3xl font-bold text-center mb-8 text-primary"
        )

        # Instructions
        with ui.card().classes("w-full max-w-4xl mx-auto mb-6 p-6 bg-blue-50"):
            ui.label("Instructions:").classes("text-lg font-semibold mb-2")
            with ui.column().classes("gap-2"):
                ui.label('1. Click "Start Camera" to activate your webcam').classes("text-gray-700")
                ui.label("2. Position yourself so your full upper body is visible").classes("text-gray-700")
                ui.label("3. Maintain your normal working posture").classes("text-gray-700")
                ui.label('4. Click "Capture Posture" to analyze your current position').classes("text-gray-700")
                ui.label("5. Review the analysis results and proceed to the questionnaire").classes("text-gray-700")

        # Webcam capture component
        if user and user.id is not None:
            webcam_component = WebcamCaptureComponent(user_id=user.id)
            webcam_component.create()

            # Store component in app storage for other pages to access
            app.storage.client["webcam_component"] = webcam_component

        # Navigation
        with ui.row().classes("gap-4 justify-center mt-8"):
            ui.button("← Back to Home", on_click=lambda: ui.navigate.to("/")).classes("px-6 py-2").props("outline")
            ui.button("Continue to Questionnaire →", on_click=lambda: ui.navigate.to("/questionnaire")).classes(
                "px-6 py-2 bg-primary text-white"
            )
