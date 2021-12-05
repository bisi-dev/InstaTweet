# import modules
from flask import Flask, render_template, request, redirect, url_for, session
import flask
from urllib.parse import urlparse, urlsplit
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
        image = base64.b64encode(
            requests.get(
                "https://miro.medium.com/max/800/1*hFwwQAW45673VGKrMPE2qQ.png"
            ).content
        )
        image = image.decode("utf-8")
        image = "data:image/jpeg;base64," + image
        return render_template(
            "index.html",
            profile_html=f"Invalid Link!!!",
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
    return flask.redirect(redirect_url)


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

    return redirect("/complete")


@app.route("/complete")
def complete():
    # rebuild auth
    token, token_secret = session["token"]
    auth = tweepy.OAuthHandler(twitter_client, twitter_secret)
    auth.set_access_token(token, token_secret)

    # now you have access!
    api = tweepy.API(auth)

    # example, print your latest status posts
    return flask.render_template("tweet.html", tweets=api.user_timeline())


# Test to Ping Application
@app.route("/test", methods=["GET"])
def test():
    return "Pinging Model Application!"


if __name__ == "__main__":
    # app.run(debug=True, host="127.0.0.1", port="5000")
    app.run(debug=True)
