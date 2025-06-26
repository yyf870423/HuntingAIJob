from .gradio_ui import build_ui

def launch_app():
    ui = build_ui()
    ui.launch() 