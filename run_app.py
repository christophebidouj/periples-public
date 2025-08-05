import subprocess
import sys
import os

if getattr(sys, 'frozen', False):
    # En mode exécutable PyInstaller
    base_path = os.path.dirname(sys.executable)
else:
    # En mode script normal
    base_path = os.path.dirname(os.path.abspath(__file__))

# Chemin vers app.py dans le dossier "periples"
app_path = os.path.join(base_path, "app.py")

subprocess.run(["streamlit", "run", app_path])

