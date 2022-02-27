from flask import Flask
import os
import json
import random
import requests
import nltk

app = Flask(__name__)

# Required for nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')


@app.route("/")
def home():
    return """<p>Use '/background' path to get a random nature image url.</p>
              <p>Use '/image' path to get a random alpaca image url.</p>
              <p>Use '/gifguessr' path to get a random 'travel' or 'interior' image url along with 3 relevant words related to the image.</p>"""


@app.route("/image")
def image():
    # Send a GET request to the api endpoint to get a random image url
    access_key = os.environ.get("ACCESS_KEY")
    res = requests.get(
        "https://api.unsplash.com/photos/random?query=alpaca&client_id=" + access_key)
    image_json = res.json()
    image_url = image_json["urls"]["small"]
    return image_url


@app.route("/gifguessr")
def gifguessr():
    # Get the access key from environment variable
    access_key = os.environ.get("ACCESS_KEY")
    # Use randrange to get either a random "travel" (0) image or a random "interior" (1) image
    if random.randrange(2) == 0:
        # Send a GET request to the api endpoint to get a random travel image url and related words
        res = requests.get(
            "https://api.unsplash.com/photos/random?query=travel&client_id=" + access_key)
    else:
        # Send a GET request to the api endpoint to get a random interior image url and related words
        res = requests.get(
            "https://api.unsplash.com/photos/random?query=interiors&client_id=" + access_key)
    # Process the json
    image_json = res.json()
    # Store image url in a variable
    image_url = image_json["urls"]["small"]
    # Parse text with nltk to get the relevant words from the image
    words_set = set()
    img_desc = image_json["alt_description"]  # Store description of image in a variable
    text = nltk.word_tokenize(img_desc)
    res = nltk.pos_tag(text)
    # Each tuple contains ("word", tag), where tag is from the Penn Treebank tagset
    for each_tuple in res:
        # Add the word to a set if the word is a noun, plural noun, verb, or adjective for uniqueness
        if each_tuple[1] == "NN" or each_tuple[1] == "NNS" or each_tuple[1] == "VBG" or each_tuple[1] == "JJ":
            words_set.add(each_tuple[0])
    # Convert the word set to a list for shuffling/randomization
    words_list = list(words_set)
    random.shuffle(words_list)
    word_dict = {"image": image_url, "words": [words_list[0], words_list[1], words_list[2]]}
    # Return as json
    return json.dumps(word_dict)


@app.route("/background")
def background():
    """API route handler for teammate's main app."""
    # Send a GET request to the api endpoint to get a random image url
    access_key = os.environ.get("ACCESS_KEY")
    res = requests.get(
        "https://api.unsplash.com/photos/random?query=nature&orientation=landscape&client_id=" + access_key)
    image_json = res.json()
    image_url = image_json["urls"]["regular"]
    return image_url


if __name__ == "__main__":
    app.run(host="localhost", port=3000, debug=True)
