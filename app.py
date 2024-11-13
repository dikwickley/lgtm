from dotenv import load_dotenv
load_dotenv()

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.models.views import View
from slack_sdk.models.blocks import InputBlock, StaticSelectElement, Option

from views.review_view import get_review_modal

import os

app = App(token=os.getenv("SLACK_BOT_TOKEN"))

@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(f"Hey there <@{message['user']}>!")

@app.command("/review")
def open_review_modal(ack, body, client):
    ack()
    
    # Static list of reviewers for the dropdown
    reviewers = [
        Option(text={"type": "plain_text", "text": "Reviewer 1"}, value="reviewer_1"),
        Option(text={"type": "plain_text", "text": "Reviewer 2"}, value="reviewer_2"),
        Option(text={"type": "plain_text", "text": "Reviewer 3"}, value="reviewer_3")
    ]

    client.views_open(
        trigger_id=body["trigger_id"],
        view=get_review_modal(reviewers)
    )

@app.view("submit_review")
def handle_review_submission(ack, body, logger):
    ack()
    submitted_data = body["view"]["state"]["values"]
    print(f"Review Submission Data: {submitted_data}")
    channel_id = body["user"]["id"]
    app.client.chat_postMessage(channel=channel_id, text="Thank you for your submission!")

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_LEVEL_TOKEN"))
    handler.start()
