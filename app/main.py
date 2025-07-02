from app.gradio_ui import build_ui
from app.config import get_config

def launch_app():
    config = get_config()
    gradio_auth = config.get("gradio_auth", {})
    ui = build_ui()
    if gradio_auth.get("enable", False):
        username = gradio_auth.get("username", "admin")
        password = gradio_auth.get("password", "admin123")
        ui.launch(auth=(username, password))
    else:
        ui.launch()

if __name__ == "__main__":
    launch_app() 