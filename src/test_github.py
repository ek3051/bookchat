#!/usr/bin/env python3

from github_handler import GitHubHandler

def test_github_message():
    try:
        handler = GitHubHandler()
        success = handler.push_message(
            "This is a test message from BookChat!",
            "TestUser"
        )
        if success:
            print("Message successfully pushed to GitHub!")
        else:
            print("Failed to push message to GitHub")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_github_message()
