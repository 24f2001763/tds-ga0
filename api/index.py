import json, os
from http.server import BaseHTTPRequestHandler

DATA = json.load(open(os.path.join(os.path.dirname(__file__), "q-vercel-latency.json")))

def p95(xs):
    xs = sorted(xs); r = (len(xs) - 1) * 0.95; i = int(r); f = r - i
    return xs[i] + f * (xs[i + 1] - xs[i]) if i + 1 < len(xs) else xs[i]

class handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        thr = body.get("threshold_ms", 180)
        out = []
        for region in body.get("regions", []):
            rows = [r for r in DATA if r["region"] == region]
            lat = [r["latency_ms"] for r in rows]; up = [r["uptime_pct"] for r in rows]
            out.append({
                "region": region,
                "avg_latency": round(sum(lat) / len(lat), 2) if lat else 0,
                "p95_latency": round(p95(lat), 2) if lat else 0,
                "avg_uptime": round(sum(up) / len(up), 3) if up else 0,
                "breaches": sum(1 for x in lat if x > thr),
            })
        payload = json.dumps({"regions": out}).encode()
        self.send_response(200); self._cors()
        self.send_header("Content-Type", "application/json"); self.end_headers()
        self.wfile.write(payload)
