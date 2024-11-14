from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from views.review_view import review_modal
from views.config_view import config_modal
from views.backlog_view import backlog_view
from views.edit_review_view import edit_review_view

from utils import get_channel_users
from models import ReviewStatus
from db import db, init_db
from datastore import DataStore

import os

load_dotenv()
init_db()
app = App(token=os.getenv("SLACK_BOT_TOKEN"))
datastore = DataStore(db=db)

@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(f"Hey there <@{message['user']}>!")

@app.command("/config")
def open_config_modal(ack, body, client):
    ack()

    channel_id = body['channel_id']

    # Retrieve the list of users from DataStore
    users = datastore.get_all_users_for_channel(channel_id)

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
        if not datastore.get_user_by_slack_id(user["id"], channel_id):
            datastore.create_user(
                name=user["real_name"],
                slack_id=user["id"],
                channel_id=channel_id
                )

    # Notify the user who pressed the button in a private message
    client.chat_postMessage(
        channel=channel_id,
        text="User list has been synchronized with the channel."
    )


@app.view("config_modal")
def handle_config_modal_submission(ack, body, client):
    ack()

    channel_id = body["view"]["private_metadata"]

    # Extract selected reviewers from the user multi-select input
    selected_reviewers = body["view"]["state"]["values"]["reviewer_select"]["selected_reviewers"]["selected_users"]
    selected_reviewer_ids = set(selected_reviewers)

    # Update reviewer status only for users already in the database
    all_users = datastore.get_all_users_for_channel(channel_id=channel_id)
    for user in all_users:
        # Set is_reviewer to True for selected reviewers, False for unselected
        is_reviewer = user.slack_id in selected_reviewer_ids
        datastore.update_user(user.id, is_reviewer=is_reviewer, channel_id=channel_id)

    # Post a message to the channel to confirm the update
    
    client.chat_postMessage(
        channel=channel_id,
        text="Reviewer statuses have been successfully updated in the channel."
    )

@app.command("/review")
def open_review_modal(ack, body, client):
    ack()
    channel_id = body['channel_id']
    # Fetch reviewers from the database
    reviewers = datastore.get_all_reviewers_for_channel(channel_id=channel_id)

    # Open the modal
    client.views_open(
        trigger_id=body["trigger_id"],
        view=review_modal(channel_id, reviewers)
    )

@app.view("submit_review")
def handle_review_submission(ack, body, client):
    ack()

    # Extract data from the submitted modal
    submitted_data = body["view"]["state"]["values"]
    review_url = submitted_data["url_input"]["url"]["value"]
    reviewer_id = submitted_data["reviewer_select"]["selected_reviewer"]["selected_option"]["value"]
    user_id = body["user"]["id"]  # The person who initiated the review

    # Add the review to the database
    datastore.create_review(user_id=user_id, url=review_url, reviewer_id=reviewer_id, status=ReviewStatus.IN_REVIEW)

    # Post a message in the channel to notify about the review request
    channel_id = body["view"]["private_metadata"]
    client.chat_postMessage(
        channel=channel_id,
        text=f"<@{user_id}> requested a review from <@{reviewer_id}>: {review_url}"
    )

@app.command("/backlog")
def handle_backlog_command(ack, respond, body, client):
    ack()
    channel_id = body['channel_id']
    # Determine the target user (self or mentioned user)
    user_id = body["user_id"]
    text = body.get("text", "").strip()
    # target_user_id = text[2:-1] if text.startswith("<@") and text.endswith(">") else user_id
    target_user_id = user_id

    user = datastore.get_user_by_slack_id(slack_id=target_user_id, channel_id=channel_id)

    # Fetch submitted and assigned reviews from the datastore
    submitted_reviews = datastore.get_reviews_submitted_by(target_user_id)
    assigned_reviews = datastore.get_reviews_assigned_to(target_user_id)

    # Generate the message blocks using backlog_view
    blocks = backlog_view(user.name, submitted_reviews, assigned_reviews)

    # Send the backlog message
    respond(
        blocks=blocks,
        text=f"Backlog for <@{target_user_id}>",
        response_type="ephemeral" 
    )
@app.action("edit_review_action")
def handle_edit_review_action(ack, body, client):
    ack()

    # Retrieve the review ID from the button's value
    review_id = body["actions"][0]["value"]

    # Fetch review details from the database
    review = datastore.get_review(int(review_id))

    # Open the edit modal with review details
    client.views_open(
        trigger_id=body["trigger_id"],
        view=edit_review_view(review)
    )

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_LEVEL_TOKEN"))
    handler.start()
