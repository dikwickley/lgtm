from slack_sdk.models.views import View
from slack_sdk.models.blocks import SectionBlock

def edit_review_view(review):
    return View(
        type="modal",
        callback_id="submit_edit_review",
        title={"type": "plain_text", "text": "Edit Review"},
        close={"type": "plain_text", "text": "Close"},
        blocks=[
            SectionBlock(
                block_id="url_display",
                text={
                    "type": "mrkdwn",
                    "text": f"*Review URL:*\n<{review.url}|{review.url}>"
                }
            ),
            SectionBlock(
                block_id="status_display",
                text={
                    "type": "mrkdwn",
                    "text": f"*Status:*\n{review.status.value}"  # Display current status
                }
            ),
            SectionBlock(
                block_id="created_at_display",
                text={
                    "type": "mrkdwn",
                    "text": f"*Created At:*\n{review.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
                }
            )
        ]
    )
