from app.gradio_ui import build_ui

def launch_app():
    ui = build_ui()
    ui.launch()

if __name__ == "__main__":
    launch_app() 