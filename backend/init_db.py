# init_db.py
import os
from app import app, db, User, seed_db

print("--- Running Database Init Script ---")

with app.app_context():
    # Create all tables (it won't delete existing ones)
    db.create_all()
    print("Database tables created (if they didn't exist).")

    # Check if the User table is empty
    try:
        existing_users = User.query.first()
        if not existing_users:
            print("Database is empty, seeding...")
            seed_db()
            print("Database seeding complete.")
        else:
            print("Database already has data. Skipping seed.")
    except Exception as e:
        print(f"Database query failed, tables might be creating: {e}")
        # This can happen on the very first run, let's try seeding
        try:
            print("Attempting to seed...")
            seed_db()
            print("Database seeding complete.")
        except Exception as se:
            print(f"Seeding failed: {se}")

print("--- Database Init Script Finished ---")