from slack_sdk.models.views import View
from slack_sdk.models.blocks import InputBlock
from slack_sdk.models.blocks import PlainTextInputElement, StaticSelectElement, Option

def edit_review_view(review, reviewers):
    # Prepare options for the reviewer dropdown, pre-selecting the current reviewer
    reviewer_options = [
        Option(text={"type": "plain_text", "text": reviewer.name}, value=reviewer.slack_id)
        for reviewer in reviewers
    ]
    current_reviewer_option = next((option for option in reviewer_options if option.value == review.reviewer_id), None)

    # Status options
    status_options = [
        Option(text={"type": "plain_text", "text": "In-Review"}, value="IN_REVIEW"),
        Option(text={"type": "plain_text", "text": "Done"}, value="DONE")
    ]
    current_status_option = next((option for option in status_options if option.value == review.status.value), None)

    return View(
        type="modal",
        callback_id="submit_edit_review",
        private_metadata=str(review.id),
        title={"type": "plain_text", "text": "Edit Review"},
        submit={"type": "plain_text", "text": "Save"},
        blocks=[
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
                label={"type": "plain_text", "text": "Select Reviewer"},
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
            )
        ]
    )
