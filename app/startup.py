from app.database import create_tables
import app.homepage
import app.webcam_capture
import app.questionnaire
import app.body_map
import app.static_content


def startup() -> None:
    # this function is called before the first request
    create_tables()

    # Setup static content and styles
    app.static_content.create()

    # Register all modules
    app.homepage.create()
    app.webcam_capture.create()
    app.questionnaire.create()
    app.body_map.create()
