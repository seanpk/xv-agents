"""The JSON API the household's devices call, on the household's own machine."""

import json
import threading
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from pantry.store import Store


def make_handler(store):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, status, body):
            data = json.dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def read_json(self):
            length = int(self.headers.get("Content-Length") or 0)
            return json.loads(self.rfile.read(length) or b"{}")

        def do_GET(self):
            url = urlparse(self.path)
            query = parse_qs(url.query)
            if url.path == "/items":
                return self.send(200, [i.as_dict() for i in store.items()])
            if url.path == "/items/expiring":
                try:
                    days = int(query.get("days", ["3"])[0])
                    today = date.fromisoformat(query["today"][0]) if "today" in query else date.today()
                except ValueError as e:
                    return self.send(400, {"error": str(e)})
                return self.send(200, [i.as_dict() for i in store.expiring(days, today)])
            return self.send(404, {"error": "not found"})

        def do_POST(self):
            url = urlparse(self.path)
            try:
                body = self.read_json()
                if url.path == "/items":
                    item = store.add(body["name"], body["qty"], date.fromisoformat(body["expires_on"]))
                    return self.send(201, item.as_dict())
                parts = url.path.strip("/").split("/")
                if len(parts) == 3 and parts[0] == "items" and parts[2] == "use":
                    item = store.use(parts[1], body.get("qty", 1))
                    return self.send(200, item.as_dict())
            except KeyError as e:
                return self.send(404, {"error": f"no item {e}"})
            except (ValueError, TypeError) as e:
                return self.send(400, {"error": str(e)})
            return self.send(404, {"error": "not found"})

    return Handler


def serve(store=None, port=0):
    """Start the API in a background thread. Returns the server; its port is server.server_port."""
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(store or Store()))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


if __name__ == "__main__":
    s = serve(port=8077)
    print(f"pantry on http://127.0.0.1:{s.server_port}")
    threading.Event().wait()
