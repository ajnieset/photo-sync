from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

value_holder = {"code": None}


class CodeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == "/callback":
            query_params = parse_qs(parsed_url.query)
            code = query_params.get("code", [None])[0]

            if code:
                value_holder["code"] = code
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Authorization received. You can close this tab.")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing code parameter.")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args):
        pass  # silence logs


def start_server():
    server = HTTPServer(("localhost", 8081), CodeHandler)
    print("Waiting for OAuth redirect on http://localhost:8081/callback")
    server.handle_request()  # Handle one request then exit
