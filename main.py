# import modules
from flask import Flask, render_template, request, redirect, url_for
from urllib.parse import urlparse, urlsplit
import re
from instaloader import *
from dotenv import load_dotenv
import os
import base64
import requests

# initialise flask app
app = Flask(__name__)

# initialise environment variables - instagram credentials
load_dotenv()
client = os.getenv("USERNAME")
secret = os.getenv("PASSWORD")

# Index WebPage - Main Page for Onboarding
@app.route("/")
def index():
    image = base64.b64encode(
        requests.get(
            "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png"
        ).content
    )
    image = image.decode("utf-8")
    image = "data:image/jpeg;base64," + image
    return render_template(
        "index.html",
        profile_html=f"Post Profile",
        caption_html=f"Post Caption",
        image=f"{image}",
        date_html=f"DATE",
        ecaption_html=f"Edit Caption...",
    )


# POST action by User
@app.route("/", methods=["POST"])
def generate():

    # Protect against unauthorized requests
    try:
        url = request.form.get("url")
        urlgiven = urlsplit(url)
        url = urlgiven.geturl()
        url = re.sub("https://|www.|instagram.com/p/", "", url)
        url = url.split("/", 1)
        shortcode = url[0]

        L = instaloader.Instaloader()

        try:
            L.load_session_from_file(
                "_professir_", "./static/session-_professir_"
            )

        except:
            L.login(client, secret)
            L.save_session_to_file("./static/session-_professir_")

        post = Post.from_shortcode(L.context, shortcode)
        image = base64.b64encode(requests.get(post.url).content)
        image = image.decode("utf-8")
        image = "data:image/jpeg;base64," + image

        return render_template(
            "index.html",
            profile_html=f"{post.profile}",
            caption_html=f"{post.caption}",
            image=f"{image}",
            date_html=f"{post.date}",
            ecaption_html=f"{post.caption}",
        )

    except:
        return render_template("raw.html")


# Test to Ping Application
@app.route("/test", methods=["GET"])
def test():
    return "Pinging Model Application!"


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port="5000")
    # app.run(debug=True)
