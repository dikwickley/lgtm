from datetime import datetime

def backlog_view(target_user_name,submitted_reviews, assigned_reviews):
    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": f"Backlog for {target_user_name}", "emoji": True}},
        {"type": "divider"}
    ]
    
    # Section: Submitted Reviews
    if submitted_reviews:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "*Submitted Reviews:*"}})
        for review in submitted_reviews:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• <{review.url}|URL> | Reviewer: <@{review.reviewer_id}> | Status: `{review.status.value}` \n _{review.created_at.strftime('%Y-%m-%d %H:%M:%S')}_"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Edit"},
                        "action_id": "edit_review_action",
                        "value": str(review.id)  # Pass review ID as the button value
                    }
                }
            )
    else:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "_No submitted reviews found._"}})

    # Section: Reviews To Do
    blocks.append({"type": "divider"})
    if assigned_reviews:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "*Reviews To Do:*"}})
        for review in assigned_reviews:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• <{review.url}|URL> | Submitted by: <@{review.user_id}> | Status: `{review.status.value}` \n _{review.created_at.strftime('%Y-%m-%d %H:%M:%S')}_"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Edit"},
                        "action_id": "edit_review_action",
                        "value": str(review.id)  # Pass review ID as the button value
                    }
                }
            )
    else:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "_No pending reviews to do._"}})

    return blocks
