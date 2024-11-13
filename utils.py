# Function to retrieve users in a channel
def get_channel_users(client, channel_id):
    response = client.conversations_members(channel=channel_id)
    user_ids = response["members"]
    users = []
    for user_id in user_ids:
        user_info = client.users_info(user=user_id)
        users.append(user_info["user"])
    return users