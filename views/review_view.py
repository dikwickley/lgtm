from slack_sdk.models.views import View
from slack_sdk.models.blocks import InputBlock
from slack_sdk.models.blocks import PlainTextInputElement, StaticSelectElement, Option, SectionBlock

def make_reviewer_option(reviewer):
    return Option(text={"type": "plain_text", "text": f"{reviewer.name} | {len(reviewer.reviews_given)}"}, value=str(reviewer.id))

def review_modal(channel_id, reviewers):
    # Prepare dropdown options for reviewers
    reviewer_options = [make_reviewer_option(reviewer)for reviewer in reviewers]

    if reviewer_options:
        reviewer_with_least_backlog = min(reviewers, key=lambda reviewer: len(reviewer.reviews_given))
        reviewer_with_least_backlog_option = make_reviewer_option(reviewer_with_least_backlog)

        reviewer_block = InputBlock(
                block_id="reviewer_select",
                label={"type": "plain_text", "text": "Select Reviewer (name | backlog)"},
                element=StaticSelectElement(
                    action_id="selected_reviewer",
                    options=reviewer_options,
                    initial_option=reviewer_with_least_backlog_option
                )
            )
    else:
        reviewer_block = SectionBlock(
                block_id="all_users",
                text={"type": "mrkdwn", "text": "No available reviewers. Please use `\config`."}
            )

    return View(
        type="modal",
        callback_id="submit_review",
        private_metadata=channel_id,
        title={"type": "plain_text", "text": "Submit a Review"},
        submit={"type": "plain_text", "text": "Submit"},
        blocks=[
            # TODO: use https://api.slack.com/reference/block-kit/block-elements#url
            InputBlock(
                block_id="url_input",
                label={"type": "plain_text", "text": "Review URL"},
                element=PlainTextInputElement(
                    action_id="url",
                    placeholder={"type": "plain_text", "text": "Enter the review URL"}
                )
            ),
            reviewer_block
        ]
    )
