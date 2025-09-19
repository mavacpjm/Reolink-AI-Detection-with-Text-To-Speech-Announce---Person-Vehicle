#!/usr/bin/env python3
"""
Reolink AI Detection Alert System - Version 2.1
Monitors TWO cameras for person/vehicle detection with separate credentials.
Plays human-sounding text-to-speech alerts.
"""

import requests
import time
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from gtts import gTTS
import platform
import subprocess

# --- Configuration ---
CAMERA_1_IP = "camera_ip_1"  # Camera 1 IP
CAMERA_1_USER = "username1"      # Camera 1 username
CAMERA_1_PASS = "password1"  # Camera 1 password

CAMERA_2_IP = "camera_ip_2"  # Camera 2 IP
CAMERA_2_USER = "username2"      # Camera 2 username
CAMERA_2_PASS = "password2"  # Camera 2 password

POLL_INTERVAL = 2            # Polling interval in seconds

# --- Setup ---
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Suppress SSL warnings

def speak(text):
    """Convert text to speech and play silently."""
    try:
        tts = gTTS(text=text, lang='en')
        tts.save("alert.mp3")
        if platform.system() == "Windows":
            subprocess.run(f"start alert.mp3", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(f"afplay alert.mp3 > /dev/null 2>&1", shell=True)
        else:  # Linux
            subprocess.run(f"mpg123 -q alert.mp3 > /dev/null 2>&1", shell=True)
    except Exception as e:
        print(f"[ERROR] TTS failed: {e}")

def check_ai_detection(camera_ip, username, password, camera_name):
    """Poll a single camera for AI detection events."""
    url = f"https://{camera_ip}/cgi-bin/api.cgi?cmd=GetAiState&channel=0&user={username}&password={password}"
    try:
        response = requests.get(url, verify=False, timeout=5)
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            value = data[0].get("value", {})
            person = value.get("people", {}).get("alarm_state", 0)
            vehicle = value.get("vehicle", {}).get("alarm_state", 0)
            return person, vehicle
    except Exception as e:
        print(f"[ERROR] Camera {camera_name} request failed: {e}")
    return 0, 0

def main():
    """Main loop: Poll both cameras and announce detections."""
    print("[INFO] Starting Reolink AI Detection Alert System (v2.1)")
    print("[INFO] Monitoring Camera 1 and Camera 2 for person/vehicle detection.")
    print("[INFO] Press Ctrl+C to exit.\n")
    try:
        while True:
            # --- Check Camera 1 ---
            person1, vehicle1 = check_ai_detection(CAMERA_1_IP, CAMERA_1_USER, CAMERA_1_PASS, "1")
            if person1 == 1:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] Camera 1: Person detected at Camera1!")
                speak("Warning: Person detected at Camera1")
            if vehicle1 == 1:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] Camera 1: Vehicle detected at Camera1!")
                speak("Warning: Vehicle detected at Camera1!")

            # --- Check Camera 2 ---
            person2, vehicle2 = check_ai_detection(CAMERA_2_IP, CAMERA_2_USER, CAMERA_2_PASS, "2")
            if person2 == 1:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] Camera 2: Person detected at Camera2!")
                speak("Warning: Person detected at Camera2!")
            if vehicle2 == 1:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] Camera 2: Vehicle detected at Camera2!")
                speak("Warning: Vehicle detected at Camera2!")

            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\n[INFO] Exiting...")

if __name__ == "__main__":
    main()
