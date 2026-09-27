from lib import *
d = Diagram("DevOps Case Study · Security",
            "Security & Access Configuration",
            "Encrypted web traffic, an internal-only database, and registry credentials kept out of pipeline code")

# request path
d.zone(80, 250, 1760, 225, "Request path", "sec", fill="#FFFFFF00")
y, h = 290, 150
d.node(110, y, 230, h, "src", "user", "Browser", "Client request")
d.node(430, y, 280, h, "proxy", "redirect", "Nginx · :80", "HTTP listener", chips=["301 → https://"])
d.node(800, y, 300, h, "proxy", "lock", "Nginx · :443", "TLS termination", chips=["listen 443 ssl"])
d.zone(1170, 282, 650, 168, "Docker network · app-network", "proxy", fill="#F0FDF8")
for x, c, ic, t in [(1190, "web", "globe", "client"), (1402, "api", "code", "api"), (1614, "db", "db", "db")]:
    d.node(x, 302, 190, 128, c, ic, t, "")
m = y + h // 2
d.arrow([(340, m), (426, m)]); d.pill(383, m - 30, "http")
d.arrow([(710, m), (796, m)], color="#059669"); d.pill(753, m - 30, "https", "proxy")
d.arrow([(1100, m), (1186, m)], color="#059669"); d.pill(1143, m - 30, ":3000", "proxy", mono=True)

# controls
cards = [
    ("proxy", "redirect", "HTTPS enforced", "Every plain-HTTP request on port 80 is permanently redirected to HTTPS.", ["return 301 https://$host$request_uri"]),
    ("sec", "cert", "TLS at the edge", "Nginx terminates TLS using a key and certificate mounted from the host at runtime, not baked into any image.", ["./certs:/etc/nginx/certs", "ssl_certificate"]),
    ("sec", "eye", "Request traceability", "Client IP and protocol are forwarded upstream, and every request is written to the Nginx access log.", ["X-Real-IP", "X-Forwarded-For", "X-Forwarded-Proto"]),
    ("db", "db", "Database not exposed", "MySQL publishes no host port. It is reachable only by services on the internal Docker network.", ["db: no ports", "DB_HOST=db"]),
    ("ci", "key", "Pipeline credentials as secrets", "Docker Hub credentials are injected from GitHub encrypted secrets and never written in the workflow file.", ["secrets.DOCKER_USERNAME", "secrets.DOCKER_PASSWORD"]),
    ("proxy", "net", "Name-based service discovery", "Services reach each other by service name on a dedicated network, with no hard-coded IP addresses.", ["client:3000", "api:8000", "db:3306"]),
]
for i, (c, ic, t, s, ch) in enumerate(cards):
    cx = 80 + (i % 3) * 600; cy = 520 + (i // 3) * 225
    d.node(cx, cy, 560, 195, c, ic, t, s, chips=ch)

d.text(80, 985, 1300, "Certificate in this environment: self-signed, generated with OpenSSL during setup (suited to local / demo use).", 15, "#64748B", 500)
d.render("/home/claude/portfolio/devops/05-security.png")
