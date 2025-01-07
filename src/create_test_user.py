#!/usr/bin/env python3

from database import add_user, add_message

def create_test_data():
    # Create a test user
    user_id = add_user(
        github_id=12345,
        username="TestUser",
        avatar_url="https://github.com/identicons/test.png"
    )
    
    # Add a test message
    add_message(user_id, "Hello, this is a test message!")
    
    print("Test data created successfully!")

if __name__ == "__main__":
    create_test_data()
