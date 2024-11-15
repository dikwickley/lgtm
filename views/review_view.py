from slack_sdk.models.views import View
from slack_sdk.models.blocks import InputBlock
from slack_sdk.models.blocks import PlainTextInputElement, StaticSelectElement, Option

def review_modal(channel_id, reviewers):
    # Prepare dropdown options for reviewers
    reviewer_options = [
        Option(text={"type": "plain_text", "text": reviewer.name}, value=reviewer.slack_id)
        for reviewer in reviewers
    ]

    return View(
        type="modal",
        callback_id="submit_review",
        private_metadata=channel_id,
        title={"type": "plain_text", "text": "Submit a Review"},
        submit={"type": "plain_text", "text": "Submit"},
        blocks=[
            InputBlock(
                block_id="url_input",
                label={"type": "plain_text", "text": "Review URL"},
                element=PlainTextInputElement(
                    action_id="url",
                    placeholder={"type": "plain_text", "text": "Enter the review URL"}
                )
            ),
            InputBlock(
                block_id="reviewer_select",
                label={"type": "plain_text", "text": "Select Reviewer"},
                element=StaticSelectElement(
                    action_id="selected_reviewer",
                    options=reviewer_options
                )
            )
        ]
    )
