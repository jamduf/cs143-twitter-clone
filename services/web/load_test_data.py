# services/web/project/load_test_tweets.py

import random
import string
import time
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from project.config import DevelopmentConfig

# Create DB engine and session
engine = create_engine(DevelopmentConfig.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def load_test_tweets(user_count=1000, message_count=10000000, url_fraction=0.1):
    print(f"Inserting {user_count} users...")
    users = []
    for i in range(user_count):
        users.append({
            "email": f"user{i}@example.com",
            "username": f"user{i}",
            "active": True,
            "created_at": datetime.utcnow() - timedelta(days=random.randint(0, 1000))
        })

    session.execute(
        text("""
        INSERT INTO users (email, username, active, created_at)
        VALUES (:email, :username, :active, :created_at)
        """),
        users
    )
    session.commit()
    print("Users inserted.")

    print(f"Inserting {message_count} messages...")
    batch_size = 10000
    user_ids = [r[0] for r in session.execute(text("SELECT id FROM users")).fetchall()]

    for i in range(0, message_count, batch_size):
        batch = []
        for _ in range(min(batch_size, message_count - i)):
            batch.append({
                "user_id": random.choice(user_ids),
                "content": f"This is a test tweet {random_string(15)}",
                "created_at": datetime.utcnow() - timedelta(minutes=random.randint(0, 100000))
            })

        session.execute(
            text("""
            INSERT INTO messages (user_id, content, created_at)
            VALUES (:user_id, :content, :created_at)
            """),
            batch
        )
        session.commit()
        print(f"Inserted {i + len(batch)} / {message_count} messages")

    print("Messages inserted.")

    print("Inserting urls...")
    tweet_ids = [r[0] for r in session.execute(text("SELECT id FROM messages WHERE id %% :mod = 0 LIMIT 1000000"), {"mod": int(1 / url_fraction)}).fetchall()]
    url_batch = []
    for tweet_id in tweet_ids:
        url_batch.append({
            "tweet_id": tweet_id,
            "expanded_url": f"https://example.com/{random_string(8)}"
        })

    session.execute(
        text("""
        INSERT INTO urls (tweet_id, expanded_url)
        VALUES (:tweet_id, :expanded_url)
        """),
        url_batch
    )
    session.commit()
    print(f"Inserted {len(url_batch)} urls.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--users", type=int, default=1000)
    parser.add_argument("--messages", type=int, default=100)
    parser.add_argument("--url-fraction", type=float, default=0.1)
    args = parser.parse_args()

    start = time.time()
    load_test_tweets(args.users, args.messages, args.url_fraction)
    print(f"✅ Done in {time.time() - start:.2f} seconds.")

