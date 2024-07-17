#!/bin/bash
source /home/chatbot/venv/bin/activate
cd /home/chatbot/fastapi/
#screen -dmS uvicorn uvicorn main:app --host 0.0.0.0 --port 5000
screen -dmS bot python3 /home/chatbot/fastapi/main.py
screen -ls
