# import modules
from flask import Flask, render_template, request, redirect, session
from urllib.parse import urlsplit
import re
from instaloader import *
from dotenv import load_dotenv
import os
import base64
import requests
import tweepy

# initialise flask app
app = Flask(__name__)

# initialise environment variables
load_dotenv()
client = os.getenv("USERNAME")
secret = os.getenv("PASSWORD")
twitter_client = os.getenv("CONSUMER_TOKEN")
twitter_secret = os.getenv("CONSUMER_SECRET")
CALLBACK_URL = "https://instatweetbot.herokuapp.com/verify"

app.config.update(SECRET_KEY=twitter_secret)

# Index WebPage - Main Page for Onboarding
@app.route("/")
def index():
    with open("./static/img/waiting.jpg", "rb") as image_file:
        image = base64.b64encode(image_file.read())
    image = image.decode("utf-8")
    image = "data:image/jpeg;base64," + image
    return render_template(
        "index.html",
        profile_html=f"InstaTweet",
        caption_html=f"Post Caption",
        image=f"{image}",
        date_html=f"DATE",
        ecaption_html=f"Edit Caption...",
    )


def complete():
    # # rebuild auth
    # token, token_secret = session["token"]
    # auth = tweepy.OAuthHandler(twitter_client, twitter_secret)
    # auth.set_access_token(token, token_secret)

    # # now you have access!
    # api = tweepy.API(auth)

    with open("./static/img/success.jpg", "rb") as image_file:
        image = base64.b64encode(image_file.read())
    image = image.decode("utf-8")
    image = "data:image/jpeg;base64," + image
    return render_template(
        "index.html",
        profile_html=f"InstaTweet",
        caption_html=f"Success",
        image=f"{image}",
        date_html=f"DATE",
        ecaption_html=f"Success!!!",
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
            L.load_session_from_file(client, "./static/session")

        except:
            L.login(client, secret)
            L.save_session_to_file("./static/session")

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
        with open("./static/img/error.png", "rb") as image_file:
            image = base64.b64encode(image_file.read())
        image = image.decode("utf-8")
        image = "data:image/jpeg;base64," + image
        return render_template(
            "index.html",
            profile_html=f"Instatweet",
            caption_html=f"Invalid Link!!!",
            image=f"{image}",
            date_html=f"Invalid Link!!!",
            ecaption_html=f"Invalid Link!!!",
        )


@app.route("/start")
def send_token():
    auth = tweepy.OAuthHandler(twitter_client, twitter_secret, CALLBACK_URL)

    try:
        # get the request tokens
        redirect_url = auth.get_authorization_url()
        session["request_token"] = auth.request_token["oauth_token"]

    except tweepy.TweepyException:
        print("Error! Failed to get request token")

    # this is twitter's url for authentication
    return redirect(redirect_url)


@app.route("/verify")
def get_verification():

    # get the verifier key from the request url
    verifier = request.args["oauth_verifier"]
    token = session["request_token"]
    del session["request_token"]

    auth = tweepy.OAuthHandler(twitter_client, twitter_secret)
    auth.request_token = {"oauth_token": token, "oauth_token_secret": verifier}

    try:
        auth.get_access_token(verifier)
    except tweepy.TweepyException:
        print("Error! Failed to get access token.")

    session["token"] = (auth.access_token, auth.access_token_secret)

    return redirect("/complete", complete)


# Test to Ping Application
@app.route("/test", methods=["GET"])
def test():
    return "Pinging Model Application!"


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port="5010")
    # app.run(debug=True)
