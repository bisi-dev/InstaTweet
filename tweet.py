from flask import Flask
from flask import request
import flask
import tweepy
from dotenv import load_dotenv
import os

app = Flask(__name__)

# config

load_dotenv()
client = os.getenv("CONSUMER_TOKEN")
secret = os.getenv("CONSUMER_SECRET")

CONSUMER_TOKEN = client
CONSUMER_SECRET = secret
CALLBACK_URL = "https://instatweetbot.herokuapp.com/verify"
session = dict()
db = dict()  # you can save these values to a database


@app.route("/")
def send_token():
    auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET, CALLBACK_URL)

    try:
        # get the request tokens
        redirect_url = auth.get_authorization_url()
        print(auth.request_token)
        session["request_token"] = auth.request_token["oauth_token"]
        # session["request_token"] = (
        #     auth.request_token["oauth_token"],
        #     # auth.request_token["oauth_token_secret"],
        # )
        # print(session)
    except tweepy.TweepyException:
        print("Error! Failed to get request token")

    # this is twitter's url for authentication
    return flask.redirect(redirect_url)


@app.route("/verify")
def get_verification():

    # get the verifier key from the request url
    verifier = request.args["oauth_verifier"]

    auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
    token = session["request_token"]
    del session["request_token"]

    auth.request_token = {"oauth_token": token, "oauth_token_secret": verifier}

    # auth.set_request_token(token[0], token[1])

    try:
        auth.get_access_token(verifier)
    except tweepy.TweepyException:
        print("Error! Failed to get access token.")

    # now you have access!
    api = tweepy.API(auth)

    # store in a db
    db["api"] = api
    db["access_token_key"] = auth.access_token
    db["access_token_secret"] = auth.access_token_secret
    return flask.redirect(flask.url_for("start"))


@app.route("/start")
def start():
    # auth done, app logic can begin
    api = db["api"]

    # example, print your latest status posts
    return flask.render_template("tweet.html", tweets=api.user_timeline())


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port="5000")
    # app.run(debug=True)
