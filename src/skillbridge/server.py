"""Optional Python in-process exposure for local agents (token protected)."""
import hmac
import json
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class Bridge:
    def __init__(self, app: str, token: str | None = None):
        self.app = app
        self.token = token or secrets.token_urlsafe(32)
        self._skills = {}

    def expose(self, name: str, description: str, fn, inputs: dict[str, str]):
        if not callable(fn) or not name or not description:
            raise ValueError("A named callable and description are required")
        if not all(t in ("string", "integer", "boolean") for t in inputs.values()):
            raise ValueError("Unsupported input type")
        self._skills[name] = (description, fn, inputs)

    def serve(self, host="127.0.0.1", port=8765):
        if host not in ("127.0.0.1", "localhost", "::1"):
            raise ValueError("This MVP only binds to loopback")
        bridge = self
        class Handler(BaseHTTPRequestHandler):
            def reply(self, code, payload):
                data = json.dumps(payload).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            def authorized(self):
                return hmac.compare_digest(self.headers.get("Authorization", ""), "Bearer " + bridge.token)
            def do_GET(self):
                if not self.authorized(): return self.reply(401, {"error": "Unauthorized"})
                if self.path != "/manifest": return self.reply(404, {"error": "Not found"})
                self.reply(200, {"app": bridge.app, "skills": [{"name": n, "description": d, "inputs": i} for n, (d, _, i) in bridge._skills.items()]})
            def do_POST(self):
                if not self.authorized(): return self.reply(401, {"error": "Unauthorized"})
                if self.path != "/call": return self.reply(404, {"error": "Not found"})
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    if not 0 < length <= 65536: return self.reply(413, {"error": "Invalid request size"})
                    body = json.loads(self.rfile.read(length))
                    name, args = body["skill"], body["args"]
                    if name not in bridge._skills or not isinstance(args, dict): return self.reply(400, {"error": "Invalid skill or arguments"})
                    _, fn, schema = bridge._skills[name]
                    if set(args) != set(schema): return self.reply(400, {"error": "Argument mismatch"})
                    for k, t in schema.items():
                        v = args[k]
                        if not ((t == "string" and isinstance(v, str)) or (t == "integer" and type(v) is int) or (t == "boolean" and type(v) is bool)):
                            return self.reply(400, {"error": "Invalid argument type"})
                    self.reply(200, {"result": fn(**args)})
                except (ValueError, KeyError, TypeError) as exc:
                    self.reply(400, {"error": str(exc)})
                except Exception:
                    self.reply(500, {"error": "Skill execution failed"})
        server = ThreadingHTTPServer((host, port), Handler)
        print(f"SkillBridge listening at http://{host}:{port}; token: {self.token}")
        server.serve_forever()
