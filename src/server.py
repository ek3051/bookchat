#!/usr/bin/env python3

import http.server
import socketserver
import json
import os
from urllib.parse import parse_qs, urlparse
from database import get_db_connection, add_message, get_messages, add_user, get_user_by_github_id
from github_handler import GitHubHandler

# Define the port number
PORT = 8080

# Initialize GitHub handler
github_handler = GitHubHandler()

class ChatRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler for our chat application"""

    def _send_response(self, status_code, data):
        """Helper method to send JSON responses"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # Enable CORS
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/messages':
            # Get query parameters
            query_params = parse_qs(parsed_path.query)
            limit = int(query_params.get('limit', [50])[0])
            offset = int(query_params.get('offset', [0])[0])
            
            try:
                # Get messages from both database and GitHub
                db_messages = get_messages(limit, offset)
                github_messages = github_handler.get_messages(limit)
                
                # Convert SQLite Row objects to dictionaries
                messages_list = [{
                    'id': msg['id'],
                    'content': msg['content'],
                    'username': msg['username'],
                    'avatar_url': msg['avatar_url'],
                    'created_at': msg['created_at'],
                    'source': 'database'
                } for msg in db_messages]
                
                # Add GitHub messages
                messages_list.extend([{
                    'id': f"gh_{idx}",
                    'content': msg['content'],
                    'username': msg['author'],
                    'created_at': msg['timestamp'],
                    'source': 'github'
                } for idx, msg in enumerate(github_messages)])
                
                # Sort combined messages by timestamp
                messages_list.sort(key=lambda x: x['created_at'], reverse=True)
                
                self._send_response(200, {'messages': messages_list[:limit]})
            except Exception as e:
                self._send_response(500, {'error': str(e)})
        
        elif parsed_path.path == '/messages/search':
            # Search messages
            query_params = parse_qs(parsed_path.query)
            query = query_params.get('q', [''])[0]
            
            try:
                github_results = github_handler.search_messages(query)
                self._send_response(200, {'messages': github_results})
            except Exception as e:
                self._send_response(500, {'error': str(e)})
        
        elif parsed_path.path == '/messages/stats':
            # Get message statistics
            try:
                stats = github_handler.get_message_stats()
                self._send_response(200, stats)
            except Exception as e:
                self._send_response(500, {'error': str(e)})
        
        elif parsed_path.path == '/':
            # Serve the static HTML file
            self.path = '/templates/index.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        else:
            # Serve static files from the root directory
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self._send_response(400, {'error': 'Invalid JSON'})
            return

        if self.path == '/messages':
            # Add new message
            try:
                if 'user_id' not in data or 'content' not in data:
                    self._send_response(400, {'error': 'Missing required fields'})
                    return
                
                # Add message to database
                message_id = add_message(data['user_id'], data['content'])
                
                # Get user information
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT username FROM users WHERE id = ?
                ''', (data['user_id'],))
                user = cursor.fetchone()
                conn.close()
                
                # Push message to GitHub
                if user:
                    github_handler.push_message(
                        data['content'],
                        user['username'],
                        metadata={'database_id': message_id}
                    )
                
                self._send_response(201, {'id': message_id})
            except Exception as e:
                self._send_response(500, {'error': str(e)})

        elif self.path == '/users':
            # Add new user
            try:
                if 'github_id' not in data or 'username' not in data:
                    self._send_response(400, {'error': 'Missing required fields'})
                    return
                
                user_id = add_user(
                    data['github_id'],
                    data['username'],
                    data.get('avatar_url', '')
                )
                self._send_response(201, {'id': user_id})
            except Exception as e:
                self._send_response(500, {'error': str(e)})

        else:
            self._send_response(404, {'error': 'Not found'})

def run_server():
    """Start the HTTP server"""
    # Change the working directory to the project root
    os.chdir(os.path.dirname(os.path.dirname(__file__)))
    
    # Create the server
    with socketserver.TCPServer(("", PORT), ChatRequestHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down the server...")
            httpd.server_close()

if __name__ == "__main__":
    run_server()
