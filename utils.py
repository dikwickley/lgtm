import json
import threading

# Function to retrieve users in a channel
def get_channel_users(client, channel_id):
    response = client.conversations_members(channel=channel_id)
    user_ids = response["members"]
    users = []
    for user_id in user_ids:
        user_info = client.users_info(user=user_id)
        users.append(user_info["user"])
    return users

def ping_reviewer(client, review):
    msg = f"Please review {review.url}. Submitted by <@{review.user.slack_id}>."
    client.chat_postMessage(
        channel=review.reviewer.slack_id,
        text=msg
    )

def metadata_serializer(object):
    return json.dumps(object)

def metadata_deserializer(object):
    return json.loads(object)


class DelayedExecutor:
    def __init__(self):
        self.timers = []

    def set_timeout(self, callback, delay_in_seconds, *args, **kwargs):
        timer = threading.Timer(delay_in_seconds, callback, args=args, kwargs=kwargs)
        self.timers.append(timer)
        timer.start()
        return timer

    def cancel_all(self):
        """Cancel all scheduled timers."""
        for timer in self.timers:
            timer.cancel()
        self.timers.clear()