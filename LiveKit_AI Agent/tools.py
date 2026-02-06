import logging
import os
import json
import requests
import smtplib
import socket
import psutil
from datetime import datetime
from typing import Optional

from livekit.agents import function_tool, RunContext
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from langchain_community.tools import DuckDuckGoSearchRun

# ️ WEATHER

@function_tool()
async def get_weather(context: RunContext, city: str) -> str:
    try:
        r = requests.get(f"https://wttr.in/{city}?format=3", timeout=5)
        return f"Sir, {r.text.strip()}" if r.status_code == 200 else "Sir, weather data is unavailable."
    except Exception as e:
        logging.error(e)
        return "Sir, I am unable to retrieve the weather."

#  WEB SEARCH

@function_tool()
async def search_web(context: RunContext, query: str) -> str:
    try:
        result = DuckDuckGoSearchRun().run(query)
        return f"Sir, here is what I found: {result}"
    except Exception as e:
        logging.error(e)
        return "Sir, the search operation failed."

#  EMAIL (CONFIRMATION REQUIRED)

@function_tool()
async def send_email(
    context: RunContext,
    to_email: str,
    subject: str,
    message: str,
    confirm: bool = False
) -> str:

    if not confirm:
        return "Sir, the email is ready; please confirm before I send it."

    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")

    if not gmail_user or not gmail_password:
        return "Sir, email credentials are not configured."

    try:
        msg = MIMEMultipart()
        msg["From"] = gmail_user
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.quit()

        return f"Sir, the email has been sent to {to_email}."
    except Exception as e:
        logging.error(e)
        return "Sir, I failed to send the email."

#  OPEN APPLICATION (WHITELISTED)

@function_tool()
async def open_application(
    context: RunContext,
    app_name: str,
    confirm: bool = False
) -> str:

    SAFE_APPS = {
        "chrome": "start chrome",
        "notepad": "notepad",
        "calculator": "calc",
    }

    app = app_name.lower()
    if app not in SAFE_APPS:
        return "Sir, that application is not in my approved list."

    if not confirm:
        return f"Sir, shall I open {app_name}?"

    os.system(SAFE_APPS[app])
    return f"Sir, {app_name} has been opened."

#  REMINDER

@function_tool()
async def set_reminder(
    context: RunContext,
    task: str,
    time: str,
    confirm: bool = False
) -> str:

    if not confirm:
        return f"Sir, should I set a reminder for '{task}' at {time}?"

    reminder = {
        "task": task,
        "time": time,
        "created_at": datetime.now().isoformat()
    }

    with open("reminders.json", "a") as f:
        f.write(json.dumps(reminder) + "\n")

    return "Sir, the reminder has been set."

#  FILE SEARCH (READ-ONLY)

@function_tool()
async def find_file(context: RunContext, filename: str) -> str:
    base_dir = os.path.expanduser("~/Documents")

    for root, _, files in os.walk(base_dir):
        if filename in files:
            return f"Sir, I found {filename} in {root}."

    return "Sir, I could not locate the file."

#  TIME

@function_tool()
async def get_time(context: RunContext) -> str:
    return f"Sir, the current time is {datetime.now().strftime('%I:%M %p')}."

#  SYSTEM STATUS (READ-ONLY)

@function_tool()
async def system_status(context: RunContext) -> str:
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    return f"Sir, CPU usage is {cpu}% and memory usage is {ram}%."

#  NOTES

@function_tool()
async def take_note(context: RunContext, note: str) -> str:
    with open("notes.txt", "a") as f:
        f.write(note + "\n")
    return "Sir, I have saved the note."

# INTERNET CHECK

@function_tool()
async def check_internet(context: RunContext) -> str:
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return "Sir, the internet connection is active."
    except OSError:
        return "Sir, the internet appears to be offline."

# DAILY SUMMARY

@function_tool()
async def daily_summary(context: RunContext) -> str:
    return (
        "Sir, today you worked on your AI assistant, "
        "enhanced security, and made commendable progress."
    )
