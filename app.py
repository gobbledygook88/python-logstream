from flask import Flask, Response
from events import ServerSentEvent
from queued_log_socket_receiver import logs, QueuedLogSocketReceiver
import threading
import json
import time


app = Flask(__name__)


@app.route("/debug")
def debug():
    template = """
     <html>
       <head>
       </head>
       <body>
         <h1>Server sent events</h1>
         <div id="event"></div>
         <script type="text/javascript">

         var eventOutputContainer = document.getElementById("event");
         var evtSrc = new EventSource("/subscribe");

         evtSrc.onmessage = function(e) {
             console.log(e.data);
             eventOutputContainer.innerHTML = e.data;
         };

         </script>
       </body>
     </html>
    """
    return(template)


@app.route('/subscribe')
def subscribe():
    def gen():
        try:
            while True:
                if not logs.empty():
                    log = logs.get()
                    ev = ServerSentEvent(json.dumps(log))
                    yield ev.encode()
                time.sleep(1)
        except GeneratorExit:
            pass

    return Response(gen(), mimetype='text/event-stream')


def start_app():
    receiver = QueuedLogSocketReceiver()
    threading.Thread(target=receiver.serve_until_stopped).start()
    return app


if __name__ == '__main__':
    app = start_app()
    app.run(host='0.0.0.0', port=5000, debug=False)
