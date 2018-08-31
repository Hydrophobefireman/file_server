import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs as _parse_qs

HOST_NAME = "localhost"
PORT_NUMBER = os.environ.get("PORT", 8000)

paths = {"/": "index.html", "/files": "files.html"}
try:
    with open("mimetypes.json", "r") as f:
        mimes = json.loads(f.read())
except:
    mimes = {}


class Handler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html;charset=utf-8")
        self.send_header("X-Served-By", "Python Base HTTP Server")
        self.end_headers()

    def do_GET(self):
        paths = {
            "/index": {"status": 200},
            "static": {"status": 200},
            "/files": {"status": 200},
            "/": {"status": 200},
        }
        _path = self.path.split("?")[0]
        if _path in paths:
            self.respond(paths[_path])
        else:
            self.send_response(500)

    def handle_http(self, status_code, path):
        self.send_response(status_code)
        content = self.check_content(path)
        return bytes(content, "UTF-8")

    def respond(self, opts):
        response = self.handle_http(opts["status"], self.path)
        self.wfile.write(response)

    def check_content(self, qspath):
        to_serve = ""
        self.send_header("Content-type", "text/html")
        self.send_header("X-Served-By", "Python:Base HTTP Server")
        path = qspath.split("?")[0]
        if path == "/":
            files = [s for s in os.listdir() if os.path.isfile(s)]
            for f in files:
                to_serve += """<a href="/files?f={f}">{f}</a><br>""".format(f=f)
            self.end_headers()
            return to_serve
        elif path == "/files":
            name = parse_qs(qspath)["f"][0]
            with open(name, "rb") as files:
                extension = "." + name.split(".")[-1]
                ct = mimes.get(extension, "application/octet-stream")
                self.send_header("Content-Type", ct)
                self.send_header("Accept-Ranges", "None")
                self.end_headers()
                self.wfile.write(files.read())


def parse_qs(_path):
    path = _path.split("?")[1]
    return _parse_qs(path)


if __name__ == "__main__":
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), Handler)
    print(time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))
