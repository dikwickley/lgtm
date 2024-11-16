from slack_sdk.models.views import View
from slack_sdk.models.blocks import SectionBlock, ActionsBlock, ButtonElement, InputBlock
from slack_sdk.models.blocks import UserMultiSelectElement

def config_modal(channel_id, users):
    # Pre-select current reviewers in the UserMultiSelectElement
    preselected_reviewer_ids = [user.slack_id for user in users if user.is_reviewer]

    # Create a text list of all users in the database for this channel
    user_list_text = "\n".join([f"• <@{user.slack_id}>" for user in users])

    return View(
        type="modal",
        callback_id="config_modal",
        private_metadata=channel_id,
        title={"type": "plain_text", "text": "LGTM Settings"},
        submit={"type": "plain_text", "text": "Submit"},
        submit_disabled=False,
        blocks=[
            ActionsBlock(
                block_id="sync_block",
                elements=[
                    ButtonElement(
                        text={"type": "plain_text", "text": "Sync Users"},
                        action_id="sync_users_action",
                        style="primary",
                    )
                ]
            ),
            InputBlock(
                block_id="reviewer_select",
                element=UserMultiSelectElement(
                    action_id="selected_reviewers",
                    placeholder={"type": "plain_text", "text": "Select reviewers..."},
                    initial_users=preselected_reviewer_ids
                ),
                optional=True,
                label={"type": "plain_text", "text": "Mark users as reviewers"}
            ),
            SectionBlock(
                block_id="all_users",
                text={"type": "mrkdwn", "text": f"*All Users:*\n{user_list_text}"}
            )
        ]
    )
