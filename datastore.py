from models import User, Review

class DataStore:
    def __init__(self, db):
        self.db = db

    def create_user(self, name: str, slack_id: str, is_reviewer: bool = False):
        new_user = User(name=name, slack_id=slack_id, is_reviewer=is_reviewer)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def get_user(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_all_users(self):
        return self.db.query(User).all()

    def get_all_reviewers(self):
        return self.db.query(User).filter(User.is_reviewer).all()

    def update_user(self, user_id: int, name: str = None, slack_id: str = None, is_reviewer: bool = None):
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            if name is not None:
                user.name = name
            if slack_id is not None:
                user.slack_id = slack_id
            if is_reviewer is not None:
                user.is_reviewer = is_reviewer
            self.db.commit()
            self.db.refresh(user)
        return user

    def delete_user(self, user_id: int):
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            self.db.delete(user)
            self.db.commit()
        return user
    
    def get_user_by_slack_id(self, slack_id: str):
        return self.db.query(User).filter(User.slack_id == slack_id).first()