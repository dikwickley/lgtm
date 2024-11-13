from dotenv import load_dotenv
load_dotenv()

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.models.views import View
from slack_sdk.models.blocks import InputBlock, StaticSelectElement, Option

from views.review_view import review_modal
from views.config_view import config_modal
from utils import get_channel_users

from db import db, init_db
from datastore import DataStore

import os

init_db()
app = App(token=os.getenv("SLACK_BOT_TOKEN"))
datastore = DataStore(db=db)

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
        view=review_modal(reviewers)
    )

@app.view("submit_review")
def handle_review_submission(ack, body, logger):
    ack()
    submitted_data = body["view"]["state"]["values"]
    print(f"Review Submission Data: {submitted_data}")
    channel_id = body["user"]["id"]
    app.client.chat_postMessage(channel=channel_id, text="Thank you for your submission!")

@app.command("/config")
def open_config_modal(ack, body, client):
    ack()

    channel_id = body['channel_id']

    # Retrieve the list of users from DataStore
    users = datastore.get_all_users()

    # Open the modal
    client.views_open(
        trigger_id=body["trigger_id"],
        view=config_modal(channel_id, users)
    )

@app.action("sync_users_action")
def handle_sync_users_action(ack, body, client):
    ack()
    channel_id = body["view"]["private_metadata"]
    current_channel_users = get_channel_users(client, channel_id)

    # Add each user to the database if they do not already exist
    for user in current_channel_users:
        if not datastore.get_user_by_slack_id(user["id"]):
            datastore.create_user(name=user["real_name"], slack_id=user["id"])

    # Notify the user who pressed the button in a private message
    client.chat_postMessage(
        channel=channel_id,
        text="User list has been synchronized with the channel."
    )


@app.view("config_modal")
def handle_config_modal_submission(ack, body, client):
    ack()

    # Extract selected reviewers from the user multi-select input
    selected_reviewers = body["view"]["state"]["values"]["reviewer_select"]["selected_reviewers"]["selected_users"]
    selected_reviewer_ids = set(selected_reviewers)

    # Update reviewer status only for users already in the database
    all_users = datastore.get_all_users()
    for user in all_users:
        # Set is_reviewer to True for selected reviewers, False for unselected
        is_reviewer = user.slack_id in selected_reviewer_ids
        datastore.update_user(user.id, is_reviewer=is_reviewer)

    # Post a message to the channel to confirm the update
    channel_id = body["view"]["private_metadata"]
    client.chat_postMessage(
        channel=channel_id,
        text="Reviewer statuses have been successfully updated in the channel."
    )

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_LEVEL_TOKEN"))
    handler.start()
