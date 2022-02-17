from flask import Flask
import os
import requests

app = Flask(__name__)


@app.route("/")
def home():
    return "<p>Use '/random' path to get a random image.</p>"


@app.route("/random")
def random():
    # Send a GET request to the api endpoint to get a random image url
    access_key = os.environ.get("ACCESS_KEY")
    res = requests.get(
        "https://api.unsplash.com/photos/random?query=alpaca&client_id=" + access_key)
    image_json = res.json()
    image_url = image_json["urls"]["small"]
    return image_url


if __name__ == "__main__":
    app.run(host="localhost", port=3000, debug=True)
