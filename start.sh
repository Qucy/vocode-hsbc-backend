#!/bin/bash

# Active the python venv enviornment
source /root/vocode_python_env/bin/activate
# Start the FastAPI application
nohup uvicorn main:app --host 0.0.0.0 --port 8000 &