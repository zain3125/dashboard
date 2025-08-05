from flask import Flask
from routes import register_routes

app = Flask(__name__)
app.secret_key = "glsominoo2406"


# تسجيل كل الـ routes من ملف routes.py
register_routes(app)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
