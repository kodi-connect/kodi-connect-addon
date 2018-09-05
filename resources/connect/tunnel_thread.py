import threading

from connect import logger

class TunnelThread(threading.Thread):
    """Background thread for Tunnel"""
    def __init__(self, tunnel):
        self.tunnel = tunnel
        threading.Thread.__init__(self)

    def run(self):
        self.tunnel.start()

    def stop(self):
        """Stop tunnel"""
        logger.debug('Stopping tunnel')
        self.tunnel.stop()
        logger.debug('Tunnel stopped')
