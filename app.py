from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "RoutePulse service online for CIE set 103 - Flask v4"

if __name__ == '__main__':
    # Bind to 0.0.0.0 so container can accept external connections
    app.run(host='0.0.0.0', port=12104)
