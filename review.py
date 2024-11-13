from collections import deque

class DataStore:
    def __init__(self):
        self.reviews = deque()  # Queue to hold the reviews
        self.reviewed_items = []  # List to keep track of reviewed items
        self.users = {}  # Dictionary to store user information

    def add_review(self, review_item):
        self.reviews.append(review_item)

    def get_reviews(self):
        return list(self.reviews)

    def update_review_status(self, user, link, status):
        for review in self.reviews:
            if review['user'] == user and review['link'] == link:
                review['status'] = status
                break

    def add_user(self, username, is_reviewer):
        self.users[username] = {'is_reviewer': is_reviewer}

    def get_reviewers(self):
        return [user for user, details in self.users.items() if details['is_reviewer']]

    def get_users(self):
        return self.users

    def remove_as_reviewer(self, username):
        if username in self.users:
            self.users[username]['is_reviewer'] = False

class UserManager:
    def __init__(self, data_store):
        self.data_store = data_store

    def add_user(self, username, is_reviewer=False):
        self.data_store.add_user(username, is_reviewer)

    def get_reviewers(self):
        return self.data_store.get_reviewers()

    def remove_as_reviewer(self, username):
        self.data_store.remove_as_reviewer(username)

class ReviewManager:
    def __init__(self, data_store, user_manager):
        # Initialize data store and user manager
        self.data_store = data_store
        self.user_manager = user_manager
        self.round_robin_counter = 0  # To manage round-robin assignment

    def submit(self, user, link):
        # Get the list of reviewers from user manager
        reviewers = self.user_manager.get_reviewers()
        if not reviewers:
            raise ValueError("No reviewers available to assign the review.")

        # Assign a reviewer in a round-robin fashion
        reviewer = reviewers[self.round_robin_counter]
        
        # Update round-robin counter
        self.round_robin_counter = (self.round_robin_counter + 1) % len(reviewers)
        
        # Create a review item with initial status 'in-review'
        review_item = {
            'user': user,
            'link': link,
            'reviewer': reviewer,
            'status': 'in-review'
        }
        
        # Add this review item to the data store
        self.data_store.add_review(review_item)
        return review_item

    def complete_review(self, user, link):
        # Update the status of the review to 'completed'
        self.data_store.update_review_status(user, link, 'completed')
        return f"Review for {link} by {user} has been marked as completed."

# Example usage
data_store = DataStore()
user_manager = UserManager(data_store)
review_manager = ReviewManager(data_store, user_manager)

# Adding users
user_manager.add_user('User1')
user_manager.add_user('Reviewer1', is_reviewer=True)
user_manager.add_user('Reviewer2', is_reviewer=True)

# Removing a user as reviewer
user_manager.remove_as_reviewer('Reviewer2')

# Submitting a review
review_item = review_manager.submit('User1', 'http://example.com')
print(review_item)  # Example output to see the structure

all_reviews = data_store.get_reviews()
print(all_reviews)  # Example output to see all reviews

# Completing a review
review_completion_message = review_manager.complete_review('User1', 'http://example.com')
print(review_completion_message)  # Example output to see the completion message

all_reviews_after_completion = data_store.get_reviews()
print(all_reviews_after_completion)  # Example output to see all reviews after completion