from datetime import datetime, timedelta
from slack_sdk.models.blocks import SectionBlock

def backlog_view(target_name, submitted_reviews, assigned_reviews):
    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": f"Backlog for {target_name}", "emoji": True}},
        {"type": "divider"}
    ]
    
    # Section: Submitted Reviews
    if submitted_reviews:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "*Submitted Reviews:*"}})
        for review in submitted_reviews:
            elapsed_time = datetime.now() - review.created_at
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• <{review.url}|URL> | Reviewer: <@{review.reviewer_id}> | Status: `{review.status.value}`"
                    },
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"_{review.created_at.strftime('%Y-%m-%d %H:%M:%S')} | {elapsed_time.days} days ago_"
                        }
                    ]
                }
            )
    else:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "_No submitted reviews found._"}})

    # Section: Reviews To Do
    blocks.append({"type": "divider"})
    if assigned_reviews:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "*Reviews To Do:*"}})
        for review in assigned_reviews:
            elapsed_time = datetime.now() - review.created_at
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• <{review.url}|URL> | Submitted by: <@{review.user_id}> | Status: `{review.status.value}`"
                    },
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"_{review.created_at.strftime('%Y-%m-%d %H:%M:%S')}_\n_{elapsed_time.days} days ago_"
                        }
                    ]
                }
            )
    else:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "_No pending reviews to do._"}})

    return blocks
