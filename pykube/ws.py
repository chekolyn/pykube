import websocket
import ssl
import collections
import six
import logging

from .exceptions import WSError
from .utils import get_kwargs


class WSClient(object):
    """
    Websocket Client for interfacing with the Kubernetes API.
    """

    def __init__(self, **kwargs):

        self.url = kwargs['url']
        self.url = self.url.replace('http://', 'ws://')
        self.url = self.url.replace('https://', 'wss://')

        self.session = kwargs['session']
        self.trace = kwargs['trace'] if "trace" in kwargs else False
        self.messages = []
        self.errors = []

        # Trace when enabled:
        websocket.enableTrace(self.trace)

        # Get token from session headers:
        if 'Authorization' in self.session.headers:
            header = "Authorization: " + self.session.headers['Authorization']

        self.ws = websocket.WebSocketApp(self.url,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close,
                                    header=[header] if header else None
                                    )
        #TODO revisit if ws should be a property
        #when we init http; we will trigger an invalid ws connection
        #to self.config.cluster["server"] via WSClient init and on_open
        # Check for valid ws url connections
        # Prevents errors on init with short url
        if "exec" in self.url:
            self.ws.on_open = self.on_open
            ssl_opts = {'cert_reqs': ssl.CERT_NONE}
            self.ws.run_forever(sslopt=ssl_opts)
        else:
            pass


    def on_message(self, ws, message):

        if message[0] == '\x01':
            message = message[1:]
        if message:
            if six.PY3 and isinstance(message, six.binary_type):
                message = message.decode('utf-8')
            self.messages.append(message)


    def on_error(self, ws, error):
        self.errors.append(error)

    def on_close(self, ws):
        pass


    def on_open(self, ws):
        pass


    def get(self, *args, **kwargs):

        client = WSClient(session=self.session, **get_kwargs(self, **kwargs))
        if client.errors:
            raise WSError(
                status=0,
                reason='\n'.join([str(error) for error in client.errors])
            )

            print client.errors

        return client.messages
