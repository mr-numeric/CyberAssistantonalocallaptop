import threading
import json
import re
import socket
import nmap
import hashlib
import psutil
import webbrowser
import datetime
import pyttsx3
import Speech_Recognition as sr
import base64
import pywhatkit as kt


engine = pyttsx3.init()


voices = engine.getProperty('voices')
female_voice_found = False
for v in voices:
    if "female" in v.name.lower() or "zira" in v.name.lower():
        engine.setProperty('voice', v.id)
        female_voice_found = True
        break
if not female_voice_found:
    print("Female voice not found. Using default voice.")

def speak(text):
    engine.say(text)
    engine.runAndWait()

def async_speak(text):
    threading.Thread(target=speak, args=(text,)).start()


response_cache = {}

def local_ai(cmd):
    cmd_lower = cmd.lower()
    if cmd_lower in response_cache:
        return response_cache[cmd_lower]

    if "hello" in cmd_lower or "hi" in cmd_lower:
        response = "Hello! Ready to hack."
    elif "time" in cmd_lower:
        response = f"The time is {datetime.datetime.now().strftime('%H:%M:%S')}"
    elif "help" in cmd_lower:
        response = "You can use commands: scan, crack this hash, lookup, memory, play, exit"
    else:
        response = "I don't know that yet, but I can try to help with commands."

    response_cache[cmd_lower] = response
    return response

def scan_ports(ip):
    try:
        nm = nmap.PortScanner()
        nm.scan(ip, '1-1024')
        results = []
        for host in nm.all_hosts():
            for proto in nm[host].all_protocols():
                ports = nm[host][proto].keys()
                for port in ports:
                    state = nm[host][proto][port]['state']
                    results.append(f"{host}:{port}/{proto} is {state}")
        return "\n".join(results) if results else "No open ports found."
    except Exception as e:
        return f"Scan error: {e}"

def crack_hash(hash_val):
    try:
        decoded_bytes = base64.b64decode(hash_val.encode())
        return decoded_bytes.decode()
    except Exception as e:
        return f"The hash you entered is false: {e}"

def encode(password):
    try:
        encoded_bytes = base64.b64encode(password.encode())
        return encoded_bytes.decode()
    except Exception as e:
        return f"Unable to encode: {e}"

def get_memory():
    mem = psutil.virtual_memory()
    return f"Total: {mem.total//(1024**2)} MB, Used: {mem.used//(1024**2)} MB"

def lookup_person(name):
    if not name:
        return "Please provide a name to lookup."
    url = f"https://www.google.com/search?q={name.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Searching Google for: {name}"

def play_song(song_name):
    if not song_name:
        return "Please provide a song name to play."
    try:
        kt.playonyt(song_name)
        async_speak("Right away sir")
        return f"Playing song: {song_name}"
    except Exception as e:
        return f"Could not play song: {e}"

def listen_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source, phrase_time_limit=5)
    try:
        cmd = r.recognize_google(audio)
        print(f"You said: {cmd}")
        return cmd
    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""
    except sr.RequestError as e:-+
    print(f"Could not request r-esults; {e}")
    return ""

def execute_command(cmd):
    cmd = cmd.strip().lower()

    # Only crack hash if command starts with "crack this hash"
    if cmd.startswith("crack this hash"):
        arg = cmd[len("crack this hash"):].strip()
        response = crack_hash(arg)
        print(response)
        async_speak("Right away sir")
        return

    commands = {
        "scan": scan_ports,
        "lookup": lookup_person,
        "memory": get_memory,
        "play": play_song,
    }

    for key in sorted(commands.keys(), key=len, reverse=True):
        if cmd.startswith(key):
            arg = cmd[len(key):].strip()
            response = commands[key](arg) if arg else commands[key]()
            async_speak("Right away sir")
            print(response)
            return

    if cmd == "exit":
        async_speak("Goodbye.")
        return "exit"

    response = local_ai(cmd)
    print(response)
    async_speak(response[:100])

def main():
    while True:
        choice = input("Use voice command? (y/n): ").strip().lower()
        if choice == 'y':
            cmd = listen_command()
        else:
            cmd = input(">>> ").strip()
        if not cmd:
            continue
        result = execute_command(cmd)
        if result == "exit":
            break

if __name__ == "__main__":
    main()
()