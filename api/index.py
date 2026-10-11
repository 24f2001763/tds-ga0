import json
from http.server import BaseHTTPRequestHandler

DATA = [{"region": k, "latency_ms": l, "uptime_pct": u} for k, v in json.loads('{"apac":[[172.69,97.698],[215.67,97.403],[181.52,97.391],[214.08,97.51],[229.69,97.245],[118.47,98.927],[205.58,99.422],[188.45,98.716],[174.56,99.08],[218.01,99.462],[141.18,98.808],[188.9,99.027]],"emea":[[135.89,99.283],[119.33,98.999],[163.07,97.738],[142.66,99.202],[191.76,98.124],[209.14,97.347],[226.32,97.171],[188.54,98.058],[210.55,98.745],[182.47,98.164],[211.1,97.124],[191.41,98.432]],"amer":[[157.78,99.437],[155.46,99],[182.33,97.704],[211.78,99.121],[194.61,98.71],[173.7,99.392],[209.75,98.263],[166.37,99.495],[177.7,98.239],[113.93,98.823],[213.82,99.444],[160.26,97.393]]}').items() for l, u in v]

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
