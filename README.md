python-logstream
================

Some insanely simple event stream of python logs.

## Disclaimer

This is very much a work in progress. Lots of bugs and probably no complete
features. You have been warned. Proceed with extreme caution.

## Setup

Docker or manual setup instructions to be written.

## Integration

Using this application _should_ be simple. Add a `SocketHandler` to a new or an
existing python logger instance, making sure the correct address and port
is used.

```python
import logging
import logging.handlers


logger = logging.getLogger('socket_logger')
logger.setLevel(logging.INFO)

socketHandler = logging.handlers.SocketHandler(
    'localhost',
    logging.handlers.DEFAULT_TCP_LOGGING_PORT)

logger.addHandler(socketHandler)

logger.info('logged to socket')
```

## Local Debugging

The whole stack isn't neccessary for debugging. All that is required is to
run the Flask app.

```bash
git clone https://github.com/gobbledygook88/python-logstream.git
cd python-logstream
virtualenv venv
source ./venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then any logs to the default TCP logging port will be streamed out via a
local address and port: `http://localhost:5000/subscribe`.

## Tests

As of writing, there are no tests. _shrugs_.
