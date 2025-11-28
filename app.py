# app.py
import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "RoutePulse service online for CIE set 103\n"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    # bind to 0.0.0.0 so it's reachable from outside the container
    app.run(host="0.0.0.0", port=port)
