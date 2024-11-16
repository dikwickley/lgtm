from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from views.review_view import review_modal
from views.config_view import config_modal
from views.backlog_view import backlog_view
from views.edit_review_view import edit_review_view
from views.message_view import message_view

from utils import get_channel_users, metadata_deserializer, ping_reviewer, DelayedExecutor
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
def handle_config_modal_submission(ack, body, respond, client):
    ack()

    channel_id = body["view"]["private_metadata"]

    # Extract selected reviewers from the user multi-select input
    selected_reviewers = body["view"]["state"]["values"]["reviewer_select"]["selected_reviewers"]["selected_users"]
    selected_reviewer_ids = set(selected_reviewers)

    # Update reviewer status only for users already in the database
    all_users = datastore.get_all_users_for_channel(channel_id=channel_id)
    # List of all reviewers with some pending reviews.
    busy_reviewers = []
    for user in all_users:
        # Set is_reviewer to True for selected reviewers, False for unselected
        is_already_reviewer = user.is_reviewer
        is_user_in_selected_reviewer = user.slack_id in selected_reviewer_ids
        # We have to handle few cases.
        # 1. user is a reviewer & is selected. // no change
        # 2. user is not a reviewer & is selected. // promote user to reviewer.
        if (is_user_in_selected_reviewer):
            datastore.update_user(user.id, is_reviewer=True, channel_id=channel_id)
        
        # 3. user is a reviewer & is NOT selected. // demote a reviewer.
        #    condition: do not let reviewer be demoted unless backlog is clear.
        if (is_already_reviewer and not is_user_in_selected_reviewer):
            # check if user has any pending reviews.
            pending_reviews = [review for review in user.reviews_given if review.status == ReviewStatus.IN_REVIEW]
            busy_reviewers.append(user)

            # Only remove the reviewer is he has no pending reviews.
            if (len(pending_reviews) == 0):
                datastore.update_user(user.id, is_reviewer=False, channel_id=channel_id)

    if busy_reviewers:
        client.chat_postMessage(
            channel=channel_id,
            text="""These reviewers cannot be removed as they have pending reviews. \n""" +
                f"""Reviewers: {','.join([f"<@{user.slack_id}>" for user in busy_reviewers])} \n""" +
                """Please complete the reviews or assign them to someone else."""
        )

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
    channel_id = body["view"]["private_metadata"]
    submitted_data = body["view"]["state"]["values"]
    review_url = submitted_data["url_input"]["url"]["value"]
    reviewer_id = submitted_data["reviewer_select"]["selected_reviewer"]["selected_option"]["value"]
    user_slack_id = body["user"]["id"]  # The person who initiated the review

    user = datastore.get_user_by_slack_id(user_slack_id, channel_id)
    reviewer = datastore.get_user_by_id(reviewer_id, channel_id)

    # Add the review to the database
    new_review = datastore.create_review(user_id=user.id, url=review_url, reviewer_id=reviewer.id, status=ReviewStatus.IN_REVIEW)

    ping_reviewer(client, new_review)

    # Post a message in the channel to notify about the review request
    channel_id = body["view"]["private_metadata"]
    client.chat_postMessage(
        channel=channel_id,
        text=f"<@{user_slack_id}> requested a review from <@{reviewer.slack_id}> for {review_url}"
    )

@app.command("/backlog")
def handle_backlog_command(ack, respond, body, client):
    ack()
    channel_id = body['channel_id']
    # Determine the target user (self or mentioned user)
    user_id = body["user_id"]

    user = datastore.get_user_by_slack_id(slack_id=user_id, channel_id=channel_id)

    if (user is None):
        respond(f"<@{user_id}> not in LGTM. Please sync with `/config`")
        return

    # Fetch submitted and assigned reviews from the datastore
    submitted_reviews = datastore.get_reviews_submitted_by(user.id)
    assigned_reviews = datastore.get_reviews_assigned_to(user.id)

    # Generate the message blocks using backlog_view
    blocks = backlog_view(user.name, submitted_reviews, assigned_reviews)

    # Send the backlog message
    chat = client.chat_postEphemeral(
        channel=channel_id,
        user=user_id,
        blocks=blocks,
        text=f"Backlog for <@{user_id}>",
    )


    # TODO: Look into deleting message after some time.
    # executor = DelayedExecutor()

    # def delete_chat_message():
    #     message_id = chat.data["message_ts"]
    #     client.chat_delete(
    #         channel=channel_id,
    #         ts=message_id
    #     )

    # executor.set_timeout(delete_chat_message, 10)

@app.action("ping_review_action")
def handle_ping_reviewer_action(ack, body, client):
    ack()

    review_id = int(body["actions"][0]["value"])
    review = datastore.get_review(review_id)

    ping_reviewer(client, review)

    # Don't need to send message as we are showing message modal.
    # channel_id = review.user.channel_id
    # user_slack_id = review.user.slack_id
    # reviewer_slack_id = review.reviewer.slack_id

    # client.chat_postEphemeral(
    #     channel=channel_id,
    #     user=user_slack_id,
    #     text=f"<@{reviewer_slack_id}> was pinged for {review.url}."
    # )

    client.views_update(
        view_id=body["view"]["id"],
        trigger_id=body["trigger_id"],
        view=message_view("Pinged!")
    )

@app.action("delete_review_action")
def handle_delete_reviewer_action(ack, body, client):
    ack()

    review_id = int(body["actions"][0]["value"])
    review = datastore.get_review(review_id=review_id)
    result = datastore.delete_review(review_id=review_id)

    message = "Some Error Occured!"
    if result:
        message = f"Review {review.url} deleted successfully!"

    client.views_update(
        view_id=body["view"]["id"],
        trigger_id=body["trigger_id"],
        view=message_view(message)
    )

@app.action("edit_review_action")
def handle_edit_review_action(ack, body, client):
    ack()

    # Retrieve the review ID from the button's value
    review_id = body["actions"][0]["value"]
    channel_id = body["channel"]["id"]
    reviewers = datastore.get_all_reviewers_for_channel(channel_id=channel_id)

    # Fetch review details from the database
    review = datastore.get_review(int(review_id))

    # Open the edit modal with review details
    client.views_open(
        trigger_id=body["trigger_id"],
        view=edit_review_view(channel_id, review, reviewers)
    )

@app.view("submit_edit_review")
def handle_edit_review_submission(ack, body, client):
    ack()

    # Extract data from the submission
    user_id = body["user"]["id"]
    submitted_data = body["view"]["state"]["values"]
    private_metadata = metadata_deserializer(body["view"]["private_metadata"])
    review_id = private_metadata['review_id']
    channel_id = private_metadata['channel_id']
    updated_url = submitted_data["url_input"]["url"]["value"]
    updated_reviewer_id = submitted_data["reviewer_select"]["selected_reviewer"]["selected_option"]["value"]
    updated_status = submitted_data["status_select"]["selected_status"]["selected_option"]["value"]

    # TODO: Check if reviewer is sill a reviewer.
    # If not, push the update review modal again.

    old_review = datastore.get_review(int(review_id))
    updated_review = datastore.update_review(
        review_id=int(review_id),
        url=updated_url,
        reviewer_id=updated_reviewer_id,
        status=updated_status
    )

    # Only ping reviwer if there is a new one.
    if old_review.reviewer_id != updated_review.reviewer_id:
        ping_reviewer(client, updated_review)

    client.chat_postEphemeral(
        channel=channel_id,
        user=user_id,
        text="The review has been successfully updated."
    )

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_LEVEL_TOKEN"))
    handler.start()
