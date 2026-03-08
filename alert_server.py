#!/usr/bin/env python3
"""
Simple HTTP Server module for receiving alerts.
Exports run_alert_server(bot, host, port).
"""

import os
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AlertHandler(BaseHTTPRequestHandler):
    bot = None  # Will be set by run_alert_server

    def _send_response(self, status_code: int, message: str):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": message}).encode())

    def do_POST(self):
        if self.path != '/alert':
            self._send_response(404, "Endpoint not found")
            return

        # Read and parse content
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self._send_response(400, "Empty request body")
            return

        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data)
            program = data.get('program', 'unknown')
            message = data.get('message', '')
        except json.JSONDecodeError:
            try:
                params = parse_qs(post_data.decode())
                program = params.get('program', ['unknown'])[0]
                message = params.get('message', [''])[0]
            except:
                self._send_response(400, "Invalid data format")
                return

        if not message:
            self._send_response(400, "Message is required")
            return

        logger.info(f"Received alert - Program: {program}, Message: {message}")

        if AlertHandler.bot:
            # Call the synchronous wrapper – it schedules the actual send in the bot's loop
            AlertHandler.bot.send_alert(program, message)
            self._send_response(200, "Alert forwarded")
        else:
            logger.error("Bot reference not set")
            self._send_response(500, "Bot not available")

    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")

def run_alert_server(bot, host: str = None, port: int = None):
    """
    Start the HTTP server in the current thread (blocks).
    Sets AlertHandler.bot to the given bot instance.
    """
    if host is None:
        host = os.getenv('ALERT_SERVER_HOST', 'localhost')
    if port is None:
        port = int(os.getenv('ALERT_SERVER_PORT', 8080))

    AlertHandler.bot = bot
    server = HTTPServer((host, port), AlertHandler)
    logger.info(f"Starting alert server on {host}:{port} (NO AUTHENTICATION)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down alert server...")
        server.shutdown()
