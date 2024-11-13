from slack_sdk.models.views import View
from slack_sdk.models.blocks import InputBlock, StaticSelectElement

def review_modal(reviewer_list):
  return View(
        type="modal",
        callback_id="submit_review",
        title={
            "type": "plain_text",
            "text": "Submit a Review"
        },
        blocks=[
            InputBlock(
                block_id="url_input",
                label={
                    "type": "plain_text",
                    "text": "Review URL"
                },
                element={
                    "type": "plain_text_input",
                    "action_id": "url"
                }
            ),
            InputBlock(
                block_id="reviewer_select",
                label={
                    "type": "plain_text",
                    "text": "Select Reviewer"
                },
                element=StaticSelectElement(
                    action_id="selected_reviewer",
                    options=reviewer_list
                )
            )
        ],
        submit={
            "type": "plain_text",
            "text": "Submit"
        }
  )