from slack_sdk.models.views import View
from slack_sdk.models.blocks import SectionBlock

def message_view(message: str):
    return View(
        type="modal",
        title={"type": "plain_text", "text": "Message"},
        close={"type": "plain_text", "text": "Close"},
        blocks=[
            {
              "type": "header",
              "text": {
                "type": "plain_text",
                "text": message,
              }
        }
        ]
    )
