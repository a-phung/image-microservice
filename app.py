from flask import Flask, request
import os
import json
import random
import requests
import nltk

app = Flask(__name__)

# Required for nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Heroku URL is: https://image-microservice-us.herokuapp.com/
@app.route("/")
def home():
    return """<p>Use '/background' path to get a random nature image url.</p>
              <p>Use '/gifguessr' path to get a random 'travel' or 'interior' image url along with 3 relevant words related to the image.</p>
              <p>Use '/image' path to get a random alpaca image url.</p>
              <p>Use '/reddit?interest=param' path to get a random "interest" image url of the passed parameter.</p>"""


@app.route("/image")
def image():
    # Send a GET request to the api endpoint to get a random "alpaca" image url
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
    word_count = 0
    while word_count < 3:
        # Use randrange to get either a random "travel" (0) image or a random "interior" (1) image
        if random.randrange(2) == 0:
            # Send a GET request to the api endpoint to get a random travel image url and related words
            res = requests.get(
                "https://api.unsplash.com/photos/random?query=travel&count=10&client_id=" + access_key)
        else:
            # Send a GET request to the api endpoint to get a random interior image url and related words
            res = requests.get(
                "https://api.unsplash.com/photos/random?query=interiors&count=10&client_id=" + access_key)
        # res.text returns content of the response in unicode, json.loads() converts json into python dictionary object
        image_jsons = json.loads(res.text)
        for each_json in image_jsons:
            image_dict = dict()
            # Store image url in the dictionary
            image_dict["image_urls"] = each_json["urls"]["small"]
            # Parse text with nltk to get the relevant words from the image
            words_set = set()
            img_desc = each_json["alt_description"]  # Store description of image in a variable
            text = nltk.word_tokenize(img_desc)
            res = nltk.pos_tag(text)
            # Each tuple contains ("word", tag), where tag is from the Penn Treebank tagset
            for each_tuple in res:
                # Add the word to a set if the word is a noun, plural noun, verb, or adjective for uniqueness
                if each_tuple[1] == "NN" or each_tuple[1] == "NNS" or each_tuple[1] == "VBG" or each_tuple[1] == "JJ":
                    words_set.add(each_tuple[0])
            # Convert the word set to a list for shuffling/randomization
            words_list = list(words_set)
            word_count = len(words_list)
            # Check if words list contains at least 3 words
            if word_count >= 3:
                random.shuffle(words_list)
                image_dict["words"] = [words_list[0], words_list[1], words_list[2]]
                image_dict["name"] = each_json["user"]["name"]
                image_dict["username"] = each_json["user"]["username"]
                # Return as json
                return json.dumps(image_dict)


@app.route("/background")
def background():
    """API route handler for teammate's main app."""
    # Send a GET request to the api endpoint to get a random "nature" image url
    access_key = os.environ.get("ACCESS_KEY")
    res = requests.get(
        "https://api.unsplash.com/photos/random?query=nature&orientation=landscape&client_id=" + access_key)
    image_json = res.json()
    image_url = image_json["urls"]["regular"]
    return image_url


@app.route("/reddit", methods=["GET"])
def reddit():
    """API route handler for teammate's main app used as: /reddit?interest=string."""
    # Get the parsed content of the query string
    query = request.args.get("interest")
    # Send a GET request to the api endpoint to get a random "interest" image url
    access_key = os.environ.get("ACCESS_KEY")
    url = "https://api.unsplash.com/photos/random?query=" + query + "&client_id=" + access_key
    res = requests.get(url)
    image_json = res.json()
    image_url = image_json["urls"]["small"]
    return image_url


if __name__ == "__main__":
    app.run(host="localhost", port=3000, debug=True)
