"""TranslateGemma 12B の llama.cpp 用言語指定を加える録画時のローカル中継。"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen

UPSTREAM = "http://127.0.0.1:8001"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.forward()

    def do_POST(self):
        self.forward()

    def forward(self):
        data = self.rfile.read(int(self.headers.get("Content-Length", 0))) or None
        if data and self.path.startswith("/v1/chat/completions"):
            body = json.loads(data)
            body["chat_template_kwargs"] = {
                "source_lang_code": "en", "target_lang_code": "ja"
            }
            data = json.dumps(body).encode()
        headers = {"Content-Type": "application/json"} if data else {}
        try:
            with urlopen(Request(UPSTREAM + self.path, data=data, headers=headers,
                                 method=self.command), timeout=120) as result:
                body = result.read()
                self.send_response(result.status)
                self.send_header("Content-Type", result.headers.get("Content-Type", "application/json"))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        except Exception as exc:
            self.send_error(502, str(exc))


ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
