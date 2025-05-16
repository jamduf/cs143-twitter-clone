# services/web/generate_test_data.py

import argparse
import sqlalchemy
from tqdm import tqdm
import random
import string
import time
import datetime
from essential_generators import DocumentGenerator

parser = argparse.ArgumentParser()
parser.add_argument('--db', required=True)
parser.add_argument('--users', type=int, default=100)
parser.add_argument('--messages', type=int, default=1000)
parser.add_argument('--urls', type=float, default=0.1)
args = parser.parse_args()

engine = sqlalchemy.create_engine(args.db, connect_args={'application_name': 'generate_test_data'})
conn = engine.connect()
gen = DocumentGenerator()

def generate_users(n):
    print(f"ℹ️ Inserting {n} users...")

    sql = sqlalchemy.sql.text("""
        INSERT INTO users (email, username, password, active)
        VALUES (:email, :username, :password, :active)
        ON CONFLICT DO NOTHING;
    """)

    with engine.begin() as tx_conn:
        for i in tqdm(range(n), desc="Users"):
            email = f"user{i}@example.com"
            username = f"user{i}"
            password = gen.word()
            active = True

            try:
                tx_conn.execute(sql, {
                    "email": email,
                    "username": username,
                    "password": password,
                    "active": active
                })
            except sqlalchemy.exc.IntegrityError as e:
                print(f"❌ User insert fail {i}: {e}")

def generate_messages(n):
    user_ids = [r[0] for r in conn.execute(sqlalchemy.text("SELECT id FROM users")).fetchall()]
    if not user_ids:
        print("❌ No users found — cannot insert messages.")
        return

    print(f"ℹ️ Inserting {n} messages...")

    sql = sqlalchemy.sql.text("""
        INSERT INTO messages (user_id, content, created_at)
        VALUES (:uid, :content, :created_at)
    """)

    with engine.begin() as tx_conn:  # 👈 Use engine to create a fresh connection
        for i in tqdm(range(n), desc="Messages"):
            uid = random.choice(user_ids)
            content = gen.sentence()
            created_at = datetime.datetime.utcnow()

            try:
                tx_conn.execute(sql, {
                    "uid": uid,
                    "content": content,
                    "created_at": created_at
                })
            except sqlalchemy.exc.IntegrityError as e:
                print(f"❌ Failed to insert message {i}: {e}")


def generate_urls(fraction):
    # 👇 Create the table if it doesn't exist
    create_sql = sqlalchemy.sql.text("""
        CREATE TABLE IF NOT EXISTS urls (
            id SERIAL PRIMARY KEY,
            tweet_id INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
            expanded_url TEXT NOT NULL
        );
    """)
    conn.execute(create_sql)

    message_ids = [r[0] for r in conn.execute(sqlalchemy.text("SELECT id FROM messages")).fetchall()]
    n = int(len(message_ids) * fraction)
    for mid in tqdm(random.sample(message_ids, n), desc="URLs"):
        url = gen.url()
        sql = sqlalchemy.sql.text("""
            INSERT INTO urls (tweet_id, expanded_url)
            VALUES (:mid, :url);
        """)
        try:
            conn.execute(sql, {
                "mid": mid,
                "url": url
            })
        except sqlalchemy.exc.IntegrityError as e:
            print("URL insert fail:", mid, e)
            conn.rollback()

start = time.time()

generate_users(args.users)
generate_messages(args.messages)
generate_urls(args.urls)

print(f"✅ Done in {time.time() - start:.2f}s")
conn.close()
