#!/usr/bin/env python3

import os
from datetime import datetime
from github import Github
from dotenv import load_dotenv
import base64
import json

# Load environment variables
load_dotenv()

class GitHubHandler:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        if not self.github_token:
            raise ValueError("GitHub token not found in environment variables")
        
        self.g = Github(self.github_token)
        self.repo_name = os.getenv('GITHUB_REPO', 'bookchat-messages')
        self.user = self.g.get_user()
        
        # Try to get the repository, create it if it doesn't exist
        try:
            self.repo = self.user.get_repo(self.repo_name)
            print(f"Connected to repository: {self.repo_name}")
        except Exception:
            self.repo = self.user.create_repo(
                self.repo_name,
                description="BookChat Messages Repository",
                private=True
            )
            print(f"Created new repository: {self.repo_name}")

    def push_message(self, message_content, author_name, metadata=None):
        """Push a message to the GitHub repository"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"messages/{timestamp}_{author_name}.json"
        
        try:
            # Create message content with metadata
            message_data = {
                "author": author_name,
                "timestamp": datetime.utcnow().isoformat(),
                "content": message_content,
                "metadata": metadata or {}
            }
            
            # Convert to JSON
            content = json.dumps(message_data, indent=2)
            
            # Create or update the file in the repository
            self.repo.create_file(
                path=filename,
                message=f"Add message from {author_name}",
                content=content.encode('utf-8')
            )
            print(f"Successfully pushed message to {filename}")
            return True
        except Exception as e:
            print(f"Error pushing message to GitHub: {e}")
            return False

    def get_messages(self, limit=50):
        """Get recent messages from the repository"""
        try:
            # Get all files in the messages directory
            contents = self.repo.get_contents("messages")
            messages = []
            
            for content in contents:
                if content.name.endswith('.json'):
                    try:
                        # Get file content
                        file_content = base64.b64decode(content.content).decode('utf-8')
                        message_data = json.loads(file_content)
                        messages.append(message_data)
                    except Exception as e:
                        print(f"Error reading message {content.name}: {e}")
            
            # Sort messages by timestamp (newest first)
            messages.sort(key=lambda x: x['timestamp'], reverse=True)
            return messages[:limit]
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []

    def search_messages(self, query):
        """Search messages for specific content"""
        try:
            messages = self.get_messages(limit=1000)  # Get more messages for search
            return [
                msg for msg in messages
                if query.lower() in msg['content'].lower()
            ]
        except Exception as e:
            print(f"Error searching messages: {e}")
            return []

    def get_message_stats(self):
        """Get statistics about messages"""
        try:
            messages = self.get_messages(limit=1000)
            authors = {}
            total_messages = len(messages)
            total_length = 0
            
            for msg in messages:
                author = msg['author']
                authors[author] = authors.get(author, 0) + 1
                total_length += len(msg['content'])
            
            return {
                'total_messages': total_messages,
                'total_authors': len(authors),
                'author_stats': authors,
                'average_length': total_length / total_messages if total_messages > 0 else 0
            }
        except Exception as e:
            print(f"Error getting message stats: {e}")
            return {}

    def clone_repo(self, local_path):
        """Clone the repository to a local path"""
        if not os.path.exists(local_path):
            os.makedirs(local_path)
        
        clone_url = self.repo.clone_url.replace(
            'https://',
            f'https://{self.github_token}@'
        )
        
        # Use os.system to run git clone
        clone_command = f'git clone {clone_url} {local_path}'
        return os.system(clone_command) == 0

def setup_github_repo():
    """Setup and test GitHub repository connection"""
    try:
        handler = GitHubHandler()
        
        # Clone the repository
        local_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'github_messages')
        if handler.clone_repo(local_path):
            print(f"Repository cloned successfully to {local_path}")
            
            # Create messages directory if it doesn't exist in the repo
            messages_dir = os.path.join(local_path, 'messages')
            if not os.path.exists(messages_dir):
                os.makedirs(messages_dir)
                # Create a README file
                readme_content = """# BookChat Messages

This directory contains messages from the BookChat application.
Each message is stored in a separate JSON file with the format: YYYYMMDD_HHMMSS_author.json

File format:
```json
{
    "author": "username",
    "timestamp": "ISO-8601 timestamp",
    "content": "message content",
    "metadata": {
        // Additional metadata
    }
}
"""
                with open(os.path.join(messages_dir, 'README.md'), 'w') as f:
                    f.write(readme_content)
                
                # Commit and push the new directory
                os.system(f'cd {local_path} && git add . && git commit -m "Initialize messages directory" && git push')
            
            return handler
        else:
            print("Failed to clone repository")
            return None
    except Exception as e:
        print(f"Error setting up GitHub repository: {e}")
        return None

if __name__ == "__main__":
    setup_github_repo()
