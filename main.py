#!/usr/bin/env python3
import threading
import logging

from bot import AlertBot
from alert_server import run_alert_server

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    # init bot
    bot = AlertBot()

    # start http server in background thread
    server_thread = threading.Thread(
        target=run_alert_server,
        args=(bot,),
        daemon=True
    )
    server_thread.start()
    logger.info("Alert server thread started")

    # start bot in main thread
    bot.run()

if __name__ == '__main__':
    main()
