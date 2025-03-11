from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host="0.0.0.0", port=5000)

def start_server():
    server = threading.Thread(target=run)
    server.start()