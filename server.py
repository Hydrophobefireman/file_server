import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs as _parse_qs
import re

HOST_NAME = "0.0.0.0"
PORT_NUMBER = os.environ.get("PORT", 8080)

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
        self.protocol_version = "HTTP/1.1"
        _path = self.path.split("?")[0]
        if _path in paths:
            self.respond(paths[_path])
        else:
            self.send_response(404)

    def handle_http(self, status_code, path):
        self.send_response(status_code)

        content = self.check_content(path)
        if content:
            return bytes(content, "UTF-8")

    def respond(self, opts):
        response = self.handle_http(opts["status"], self.path)
        if response:
            print(response)
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
            file_size = os.path.getsize(name)
            extension = "." + name.split(".")[-1]
            ct = mimes.get(extension, "application/octet-stream")
            if (
                not self.headers.get("range")
                or self.headers.get("range", "none").lower() == "none"
            ):
                with open(name, "rb") as files:
                    self.send_header("Content-Type", ct)
                    self.send_header("Accept-Ranges", "Bytes")
                    self.send_header("Content-Length", file_size)
                    self.end_headers()
                    self.wfile.write(files.read())
            else:
                rangeA, rangeB, content_length = parse_range(
                    self.headers.get("range", "bytes=0-").lower().split("bytes=")[1],
                    file_size,
                )
                with open(name, "rb") as files:
                    self.send_header("Content-Type", ct)
                    self.send_header("Accept-Range", "Bytes")
                    self.send_header("Content-Length", content_length)
                    self.send_header(
                        "Content-Range", f"bytes {rangeA}-{rangeB}/{file_size}"
                    )
                    self.end_headers()
                    files.seek(rangeA)
                    self.send_response(206)
                    self.wfile.write(files.read(content_length))


def parse_range(range_str, file_length):
    rng = re.search(r"(?P<start>\d+)-(?P<end>\d+|)", range_str)
    start = int(rng.group("start"))
    _end = rng.group("end")
    end = file_length - 1 if not _end else int(_end)
    return start, end, (end - start + 1)


def parse_qs(_path):
    path = _path.split("?")[1]
    return _parse_qs(path)


if __name__ == "__main__":
    server_class = HTTPServer
    server = server_class((HOST_NAME, PORT_NUMBER), Handler)
    app = server.serve_forever
    print(time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER))
    try:
        app()
    except KeyboardInterrupt:
        pass
    server.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))
