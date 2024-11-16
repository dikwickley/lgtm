from models import ReviewStatus
from utils import metadata_serializer
from views.review_view import make_reviewer_option
from slack_sdk.models.views import View
from slack_sdk.models.blocks import InputBlock
from slack_sdk.models.blocks import PlainTextInputElement, StaticSelectElement, Option

def edit_review_view(channel_id, review, reviewers):
    # Prepare options for the reviewer dropdown, pre-selecting the current reviewer
    reviewer_options = [make_reviewer_option(reviewer)for reviewer in reviewers]
    current_reviewer_option = next((option for option in reviewer_options if option.value == str(review.reviewer_id)), None)

    # TODO: Make this dynamic based on items in ReivewStatus.
    # Status options
    status_options = [
        Option(text={"type": "plain_text", "text": "In-Review"}, value=ReviewStatus.IN_REVIEW.value),
        Option(text={"type": "plain_text", "text": "Done"}, value=ReviewStatus.DONE.value)
    ]
    current_status_option = next((option for option in status_options if option.value == review.status.value), None)

    private_metadata = metadata_serializer({
        'review_id': review.id,
        'channel_id': channel_id
    })

    return View(
        type="modal",
        callback_id="submit_edit_review",
        private_metadata=private_metadata,
        title={"type": "plain_text", "text": "View Review"},
        submit={"type": "plain_text", "text": "Save"},
        blocks=[
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Edit Review",
                }
            },
            # TODO use: https://api.slack.com/reference/block-kit/block-elements#url
            InputBlock(
                block_id="url_input",
                label={"type": "plain_text", "text": "Review URL"},
                element=PlainTextInputElement(
                    action_id="url",
                    initial_value=review.url  # Prepopulate with the current URL
                )
            ),
            InputBlock(
                block_id="reviewer_select",
                label={"type": "plain_text", "text": "Select Reviewer (name | backlog)"},
                element=StaticSelectElement(
                    action_id="selected_reviewer",
                    options=reviewer_options,
                    initial_option=current_reviewer_option  # Preselect current reviewer
                )
            ),
            InputBlock(
                block_id="status_select",
                label={"type": "plain_text", "text": "Status"},
                element=StaticSelectElement(
                    action_id="selected_status",
                    options=status_options,
                    initial_option=current_status_option  # Preselect current status
                )
            ),
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Review Actions",
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": f"Ping {review.reviewer.name}",
                        },
                        "value": str(review.id),
                        "action_id": "ping_review_action"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Delete Review",
                        },
                        "confirm": {
                            "title": {
                                "type": "plain_text",
                                "text": "Are you sure?"
                            },
                            "text": {
                                "type": "plain_text",
                                "text": "Delete this review permanently?"
                            },
                            "confirm": {
                                "type": "plain_text",
                                "text": "Do it"
                            },
                            "deny": {
                                "type": "plain_text",
                                "text": "Stop, I've changed my mind!"
                            }
                        },
                        "style": "danger",
                        "value": str(review.id),
                        "action_id": "delete_review_action"
                    },
                ]
            }
        ]
    )
