# Server Alert Bot

Simple alert service so server automations/services can send error warnings to telegram

Contains:
- Telegram bot 
- Alert Server (HTTP server)

Send a POST request to the alert server to broadcast an alert

Example: 
`curl -X POST http://localhost:8080/alert -H "Content-Type: application/json" -d '{"program": "backup", "message": "Backup completed"}'`

Authorized telegram users are stored in `authorized_users.txt`. See `@userinfobot` for your user id
