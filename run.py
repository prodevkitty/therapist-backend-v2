import subprocess

subprocess.run(["uvicorn", "main:app", "--reload"])