# BookChat

A simple and intuitive chat application that allows users to communicate in real-time.

## Features

- Real-time messaging
- Simple and clean user interface
- Easy to set up and use

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- GitHub Personal Access Token (for pushing changes)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/bookchat.git
cd bookchat
```

2. Set up your GitHub token:
   - Go to GitHub Settings > Developer Settings > Personal Access Tokens
   - Generate a new token with 'repo' scope
   - Copy your token
   - Open the `.env` file in the project root
   - Replace `your_token_here` with your actual token:
   ```
   GITHUB_TOKEN=your_actual_token
   ```
   Note: The `.env` file is already in `.gitignore` to ensure your token remains private

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

If you have any questions or suggestions, please open an issue in the repository# BookChat - Git-Backed Messaging Application

A lightweight, Git-backed web-based messaging application that allows users to communicate through a simple interface while storing messages in a Git repository.

## Features

- Simple web-based messaging interface
- Git-backed message storage
- SQLite database for user management
- Real-time message updates
- Markdown support for messages
- User authentication
- Message history

## Tech Stack

- Backend: Python (No frameworks)
- Database: SQLite
- Frontend: HTML, CSS, JavaScript (Vanilla)
- Version Control: Git (via GitHub API)
- Authentication: GitHub OAuth

## Project Structure

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/bookchat.git
   cd bookchatpython -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activatepip install -r requirements.txtGITHUB_CLIENT_ID=your_client_id
   GITHUB_CLIENT_SECRET=your_client_secretpython src/database.pypython src/app.py
   Once you've saved your current changes, please let me know and I can help you implement this structure. We'll proceed step by step, creating each component of the application. Would you like to start with setting up the basic project structure or would you prefer to begin with a specific component?.