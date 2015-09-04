import cPickle as pickle
import logging
import logging.handlers
import SocketServer
import struct
import Queue
import traceback


logs = Queue.Queue()


class QueuedLogStreamHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unPickle(chunk)
            record = logging.makeLogRecord(obj)
            self.handleLogRecord(record)

    def unPickle(self, data):
        return pickle.loads(data)

    def handleLogRecord(self, record):
        payload = self._payload(record)
        logs.put(payload)

    def _payload(self, record):
        payload = {
            'log': self._name(record),
            'level': logging.getLevelName(record.levelno),
            'message': record.getMessage()
        }

        tb = self._traceback(record)
        if tb:
            payload['traceback'] = tb

        return payload

    def _name(self, record):
        if self.server.logname is not None:
            return self.server.logname
        else:
            return record.name

    def _traceback(self, record):
        if record.exc_info:
            return traceback.format_exc()
        return None


class QueuedLogSocketReceiver(SocketServer.ThreadingTCPServer):
    allow_reuse_address = 1

    def __init__(self, host='localhost',
                 port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                 handler=QueuedLogStreamHandler):
        SocketServer.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = 0
        self.timeout = 1
        self.logname = None

    def serve_until_stopped(self):
        import select
        while not self.abort:
            rd, wr, ex = select.select([self.socket.fileno()],
                                       [], [],
                                       self.timeout)
            if rd:
                self.handle_request()


if __name__ == '__main__':
    logging.basicConfig(
        format='%(relativeCreated)5d %(name)-15s %(levelname)-8s %(message)s')
    tcpserver = QueuedLogSocketReceiver()
    tcpserver.serve_until_stopped()
