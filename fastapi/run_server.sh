#!/bin/bash
source /home/chatbot/venv/bin/activate
cd /home/chatbot/fastapi/
#screen -dmS uvicorn uvicorn main:app --host 0.0.0.0 --port 5000 --reload
screen -dmS uvicorn python3 /home/fastapi/main.py
screen -dmS bot python3 /home/chatbot/fastapi/tg_bot.py
screen -ls
