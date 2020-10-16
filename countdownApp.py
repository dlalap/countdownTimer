from flask import Flask
from flask_cors import CORS
from countdown import CountdownTimer

app = Flask(__name__)
timer = CountdownTimer()

@app.route('/')
def hello_world():
    timer.startCountdown(5)
    return "Hello, world!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="1337", debug=True)
