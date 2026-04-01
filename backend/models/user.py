from datetime import datetime
from db.mongo import get_db

class User:
    @staticmethod
    def find_one_and_update(user_id):
        """Find or create user and increment visit count"""
        db = get_db()
        collection = db['users']
        
        now = datetime.now()
        
        user = collection.find_one_and_update(
            {'user_id': user_id},
            {
                '$set': {'last_seen': now},
                '$inc': {'visit_count': 1},
                '$setOnInsert': {'first_seen': now, 'visit_count': 1}
            },
            upsert=True,
            return_document=True
        )
        
        return user
