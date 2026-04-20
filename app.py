import os
from flask import Flask, render_template, request, jsonify
import emojishift

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", emoji_count=emojishift.total())

@app.route("/api/encrypt", methods=["POST"])
def api_encrypt():
    data = request.get_json()
    text = data.get("text", "")
    password = data.get("password", "")
    if not text:
        return jsonify({"error": "input is empty"}), 400
    if not password:
        return jsonify({"error": "password is required"}), 400
    try:
        result = emojishift.encrypt(text, password)
        return jsonify({"result": result, "chars": len(text), "emoji": len(result)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/decrypt", methods=["POST"])
def api_decrypt():
    data = request.get_json()
    text = data.get("text", "")
    password = data.get("password", "")
    if not text:
        return jsonify({"error": "input is empty"}), 400
    if not password:
        return jsonify({"error": "password is required"}), 400
    try:
        result = emojishift.decrypt(text, password)
        return jsonify({"result": result, "chars": len(result)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)