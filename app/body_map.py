from nicegui import ui, app
from typing import Optional, Dict

from app.services import BodyPartAssessmentService, AssessmentService
from app.models import BodyPartType, RiskLevel, BodyPartRiskInfo


class InteractiveBodyMap:
    def __init__(self, assessment_id: int):
        self.assessment_id = assessment_id
        self.selected_body_part: Optional[BodyPartType] = None
        self.body_part_data: Dict[BodyPartType, BodyPartRiskInfo] = {}
        self._load_body_part_data()

    def _load_body_part_data(self):
        """Load body part assessment data"""
        body_parts = BodyPartAssessmentService.get_assessment_body_parts(self.assessment_id)

        for bp in body_parts:
            risk_info = BodyPartRiskInfo(
                body_part_name=bp.body_part.value,
                rula_score=bp.rula_score,
                severity_level=bp.severity_level,
                frequency_level=bp.frequency_level,
                gotrak_risk_level=bp.gotrak_risk_level,
                gotrak_score=bp.gotrak_score,
                additional_notes=bp.additional_notes,
            )
            self.body_part_data[bp.body_part] = risk_info

    def create(self):
        """Create the interactive body map UI"""
        with ui.row().classes("w-full gap-6"):
            # Left side - Body map
            with ui.column().classes("flex-1"):
                ui.label("Interactive Body Map").classes("text-2xl font-bold mb-4")
                ui.label("Click on body parts to view detailed risk information").classes("text-gray-600 mb-4")

                # Body map container
                with ui.card().classes("w-full p-4 bg-gray-50"):
                    self._create_body_map_svg()

            # Right side - Risk information panel
            with ui.column().classes("w-96"):
                ui.label("Risk Information").classes("text-2xl font-bold mb-4")

                self.info_card = ui.card().classes("w-full p-6 min-h-96")
                self._show_default_info()

    def _create_body_map_svg(self):
        """Create SVG-based interactive body map"""
        # Create a simplified body map using HTML/CSS
        body_map_html = """
        <div style="position: relative; width: 400px; height: 600px; margin: 0 auto; background: #f0f0f0; border-radius: 10px;">
            <!-- Head/Neck -->
            <div class="body-part" data-part="NECK" style="position: absolute; top: 20px; left: 175px; width: 50px; height: 60px; background: #e0e0e0; border-radius: 25px; border: 2px solid #ccc; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 10px;">
                Neck
            </div>
            
            <!-- Shoulders -->
            <div class="body-part" data-part="SHOULDER_LEFT" style="position: absolute; top: 80px; left: 120px; width: 60px; height: 40px; background: #e0e0e0; border-radius: 20px; border: 2px solid #ccc; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 10px;">
                L.Shoulder
            </div>
            <div class="body-part" data-part="SHOULDER_RIGHT" style="position: absolute; top: 80px; right: 120px; width: 60px; height: 40px; background: #e0e0e0; border-radius: 20px; border: 2px solid #ccc; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 10px;">
                R.Shoulder
            </div>
            
            <!-- Arms -->
            <div class="body-part" data-part="ARM_LEFT" style="position: absolute; top: 120px; left: 80px; width: 40px; height: 80px; background: #e0e0e0; border-radius: 20px; border: 2px solid #ccc; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 10px; writing-mode: vertical-rl;">
                L.Arm
            </div>
            <div class="body-part" data-part="ARM_RIGHT" style="position: absolute; top: 120px; right: 80px; width: 40px; height: 80px; background: #e0e0e0; border-radius: 20px; border: 2px solid #ccc; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 10px; writing-mode: vertical-rl;">
                R.Arm
            </div>
            
            <!-- Upper Back -->
            <div class="body-part" data-part="UPPER_BACK" style="position: absolute; top: 120px; left: 150px; width: 100px; height: 60px; background: #e0e0e0; border-radius: 15px; border: 2px solid #ccc; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 10px;">
                Upper Back
            </div>
            
            <!-- Lower Back -->
            <div class="body-part" data-part="LOWER_BACK" style="position: absolute; top: 180px; left: 150px; width: 100px; height: 80px; background: #e0e0e0; border-radius: 15px; border: 2px solid #ccc; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 10px;">
                Lower Back
            </div>
            
            <!-- Wrists -->
            <div class="body-part" data-part="WRIST_LEFT" style="position: absolute; top: 200px; left: 60px; width: 30px; height: 30px; background: #e0e0e0; border-radius: 15px; border: 2px solid #ccc; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 8px;">
                L.Wrist
            </div>
            <div class="body-part" data-part="WRIST_RIGHT" style="position: absolute; top: 200px; right: 60px; width: 30px; height: 30px; background: #e0e0e0; border-radius: 15px; border: 2px solid #ccc; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 8px;">
                R.Wrist
            </div>
        </div>
        
        <style>
        .body-part {
            transition: all 0.3s ease;
        }
        .body-part:hover {
            transform: scale(1.1);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .body-part.risk-green {
            background-color: #dcfce7 !important;
            border-color: #16a34a !important;
        }
        .body-part.risk-yellow {
            background-color: #fef3c7 !important;
            border-color: #f59e0b !important;
        }
        .body-part.risk-red {
            background-color: #fee2e2 !important;
            border-color: #dc2626 !important;
        }
        .body-part.selected {
            border-width: 4px !important;
            border-color: #3b82f6 !important;
        }
        </style>
        """

        self.body_map_element = ui.html(body_map_html)

        # Apply risk colors
        self._update_body_map_colors()

        # Add click handlers
        ui.run_javascript("""
        document.querySelectorAll('.body-part').forEach(part => {
            part.addEventListener('click', function() {
                const bodyPart = this.dataset.part;
                // Remove previous selection
                document.querySelectorAll('.body-part').forEach(p => p.classList.remove('selected'));
                // Add selection to clicked part
                this.classList.add('selected');
                // Notify Python
                window.bodyMapClick(bodyPart);
            });
        });
        
        window.bodyMapClick = function(bodyPart) {
            // This will be overridden by Python
        };
        """)

        # Set up the callback
        ui.run_javascript(f"""
        window.bodyMapClick = function(bodyPart) {{
            fetch('/body_map_click', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{bodyPart: bodyPart, assessmentId: {self.assessment_id}}})
            }});
        }};
        """)

    def _update_body_map_colors(self):
        """Update body map colors based on risk levels"""
        js_code = """
        document.querySelectorAll('.body-part').forEach(part => {
            part.classList.remove('risk-green', 'risk-yellow', 'risk-red');
        });
        """

        for body_part, risk_info in self.body_part_data.items():
            risk_class = "risk-green"
            if risk_info.gotrak_risk_level == RiskLevel.YELLOW:
                risk_class = "risk-yellow"
            elif risk_info.gotrak_risk_level == RiskLevel.RED:
                risk_class = "risk-red"

            js_code += f'''
            const part_{body_part.name} = document.querySelector('[data-part="{body_part.name}"]');
            if (part_{body_part.name}) {{
                part_{body_part.name}.classList.add('{risk_class}');
            }}
            '''

        ui.run_javascript(js_code)

    def _show_default_info(self):
        """Show default information panel"""
        with self.info_card:
            ui.label("Select a body part").classes("text-xl font-semibold mb-4")
            ui.label("Click on any highlighted body part on the map to view detailed risk information.").classes(
                "text-gray-600 mb-4"
            )

            # Legend
            ui.label("Risk Level Legend:").classes("font-semibold mb-2")
            with ui.column().classes("gap-2"):
                with ui.row().classes("items-center gap-2"):
                    ui.html(
                        '<div style="width: 20px; height: 20px; background: #dcfce7; border: 2px solid #16a34a; border-radius: 4px;"></div>'
                    )
                    ui.label("Low Risk (1-4)").classes("text-green-600")

                with ui.row().classes("items-center gap-2"):
                    ui.html(
                        '<div style="width: 20px; height: 20px; background: #fef3c7; border: 2px solid #f59e0b; border-radius: 4px;"></div>'
                    )
                    ui.label("Moderate Risk (6)").classes("text-yellow-600")

                with ui.row().classes("items-center gap-2"):
                    ui.html(
                        '<div style="width: 20px; height: 20px; background: #fee2e2; border: 2px solid #dc2626; border-radius: 4px;"></div>'
                    )
                    ui.label("High Risk (8-16)").classes("text-red-600")

    def show_body_part_info(self, body_part: BodyPartType):
        """Show detailed information for selected body part"""
        self.selected_body_part = body_part

        self.info_card.clear()

        risk_info = self.body_part_data.get(body_part)

        with self.info_card:
            if risk_info:
                # Header
                ui.label(risk_info.body_part_name).classes("text-2xl font-bold mb-4")

                # Risk level indicator
                risk_color = "text-green-600"
                risk_bg = "bg-green-100"
                if risk_info.gotrak_risk_level == RiskLevel.YELLOW:
                    risk_color = "text-yellow-600"
                    risk_bg = "bg-yellow-100"
                elif risk_info.gotrak_risk_level == RiskLevel.RED:
                    risk_color = "text-red-600"
                    risk_bg = "bg-red-100"

                with ui.card().classes(f"w-full p-4 {risk_bg} mb-4"):
                    if risk_info.gotrak_risk_level is not None:
                        ui.label(f"Risk Level: {risk_info.gotrak_risk_level.value}").classes(
                            f"text-lg font-semibold {risk_color}"
                        )
                    else:
                        ui.label("Risk Level: Not Assessed").classes("text-lg font-semibold text-gray-500")

                # Detailed information
                with ui.column().classes("gap-4"):
                    # RULA Score
                    if risk_info.rula_score is not None:
                        with ui.row().classes("items-center justify-between"):
                            ui.label("RULA Score:").classes("font-medium")
                            ui.label(f"{float(risk_info.rula_score):.1f}").classes("text-lg font-bold text-blue-600")

                    # Severity Level
                    if risk_info.severity_level:
                        with ui.row().classes("items-center justify-between"):
                            ui.label("Severity Level:").classes("font-medium")
                            severity_color = self._get_severity_color(risk_info.severity_level.value)
                            ui.label(risk_info.severity_level.value).classes(f"font-semibold {severity_color}")

                    # Frequency Level
                    if risk_info.frequency_level:
                        with ui.row().classes("items-center justify-between"):
                            ui.label("Frequency Level:").classes("font-medium")
                            frequency_color = self._get_frequency_color(risk_info.frequency_level.value)
                            ui.label(risk_info.frequency_level.value).classes(f"font-semibold {frequency_color}")

                    # GOTRAK Score
                    if risk_info.gotrak_score is not None:
                        with ui.row().classes("items-center justify-between"):
                            ui.label("GOTRAK Score:").classes("font-medium")
                            ui.label(f"{risk_info.gotrak_score}/16").classes("text-lg font-bold text-purple-600")

                    # Additional notes
                    if risk_info.additional_notes:
                        ui.separator()
                        ui.label("Additional Notes:").classes("font-medium")
                        ui.label(risk_info.additional_notes).classes("text-gray-600")

                    # Recommendations
                    ui.separator()
                    self._show_recommendations(risk_info)

            else:
                ui.label(f"{body_part.value}").classes("text-2xl font-bold mb-4")
                ui.label("No assessment data available for this body part.").classes("text-gray-600")
                ui.label("This body part was not included in the current assessment.").classes("text-sm text-gray-500")

    def _get_severity_color(self, severity: str) -> str:
        """Get color class for severity level"""
        match severity:
            case "No problem":
                return "text-green-600"
            case "Uncomfortable":
                return "text-yellow-600"
            case "Pain":
                return "text-orange-600"
            case "Severe pain":
                return "text-red-600"
            case _:
                return "text-gray-600"

    def _get_frequency_color(self, frequency: str) -> str:
        """Get color class for frequency level"""
        match frequency:
            case "Never":
                return "text-green-600"
            case "Sometimes":
                return "text-yellow-600"
            case "Often":
                return "text-orange-600"
            case "Always":
                return "text-red-600"
            case _:
                return "text-gray-600"

    def _show_recommendations(self, risk_info: BodyPartRiskInfo):
        """Show recommendations based on risk level"""
        ui.label("Recommendations:").classes("font-medium mb-2")

        recommendations = []

        if risk_info.gotrak_risk_level == RiskLevel.GREEN:
            recommendations = [
                "✅ Continue current practices",
                "🔄 Regular monitoring recommended",
                "💪 Maintain good posture habits",
            ]
        elif risk_info.gotrak_risk_level == RiskLevel.YELLOW:
            recommendations = [
                "⚠️ Monitor symptoms closely",
                "🔧 Consider ergonomic adjustments",
                "📋 Schedule follow-up assessment",
                "🧘 Practice stretching exercises",
            ]
        else:  # RED
            recommendations = [
                "🚨 Immediate intervention recommended",
                "👨‍⚕️ Consult healthcare professional",
                "🔧 Urgent ergonomic modifications needed",
                "📊 Implement risk control measures",
                "📅 Schedule regular reassessments",
            ]

        for rec in recommendations:
            ui.label(rec).classes("text-sm text-gray-700 mb-1")


def create():
    """Create the body map module"""

    @ui.page("/body_map")
    async def body_map_page():
        await ui.context.client.connected()

        # Get assessment ID
        assessment_id = app.storage.client.get("completed_assessment_id")
        if not assessment_id:
            ui.notify("No completed assessment found", type="warning")
            ui.navigate.to("/")
            return

        # Get assessment details
        assessment = AssessmentService.get_assessment(assessment_id)
        if not assessment:
            ui.notify("Assessment not found", type="negative")
            ui.navigate.to("/")
            return

        # Page header
        ui.label("Ergonomic Risk Assessment Results").classes("text-3xl font-bold text-center mb-2 text-primary")
        ui.label(f"Assessment: {assessment.session_name}").classes("text-lg text-center text-gray-600 mb-8")

        # Assessment summary
        with ui.card().classes("w-full max-w-4xl mx-auto mb-6 p-6 bg-blue-50"):
            ui.label("Assessment Summary").classes("text-lg font-semibold mb-4")

            with ui.row().classes("gap-8 w-full justify-center"):
                # Overall RULA Score
                if assessment.overall_rula_score is not None:
                    with ui.column().classes("items-center"):
                        ui.label("Overall RULA Score").classes("text-sm text-gray-600")
                        ui.label(f"{float(assessment.overall_rula_score):.1f}").classes(
                            "text-2xl font-bold text-blue-600"
                        )

                # Overall Risk Level
                with ui.column().classes("items-center"):
                    ui.label("Overall Risk Level").classes("text-sm text-gray-600")
                    if assessment.overall_risk_level is not None:
                        risk_color = "text-green-600"
                        if assessment.overall_risk_level == RiskLevel.YELLOW:
                            risk_color = "text-yellow-600"
                        elif assessment.overall_risk_level == RiskLevel.RED:
                            risk_color = "text-red-600"
                        ui.label(assessment.overall_risk_level.value).classes(f"text-2xl font-bold {risk_color}")
                    else:
                        ui.label("Not Assessed").classes("text-2xl font-bold text-gray-500")

                # Completion Status
                with ui.column().classes("items-center"):
                    ui.label("Status").classes("text-sm text-gray-600")
                    ui.label("✅ Completed" if assessment.is_completed else "⏳ In Progress").classes(
                        "text-lg font-semibold text-green-600"
                    )

        # Interactive body map
        body_map = InteractiveBodyMap(assessment_id)
        body_map.create()

        # Set up API endpoint for body part clicks
        @ui.page("/body_map_click", methods=["POST"])
        async def handle_body_map_click(request):
            try:
                data = await request.json()
                body_part_name = data.get("bodyPart")

                if body_part_name:
                    body_part = BodyPartType(body_part_name)
                    body_map.show_body_part_info(body_part)

                return {"status": "success"}
            except Exception as e:
                import logging

                logging.error(f"Error handling body map click: {str(e)}", exc_info=True)
                return {"status": "error", "message": str(e)}

        # Navigation
        with ui.row().classes("gap-4 justify-center mt-8"):
            ui.button("← Start New Assessment", on_click=lambda: ui.navigate.to("/")).classes("px-6 py-2").props(
                "outline"
            )
            ui.button("📊 Export Results", on_click=lambda: ui.notify("Export feature coming soon!")).classes(
                "px-6 py-2 bg-green-500 text-white"
            )
