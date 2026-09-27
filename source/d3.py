from lib import *
d = Diagram("DevOps Case Study · Infrastructure",
            "Docker Compose Service Topology",
            "Four containers on a shared bridge network, with persistent database storage and mounted configuration")

d.zone(80, 245, 1760, 735, "Docker Compose host", "src", dashed=False, fill="#FCFDFE", note="docker-compose.yml")

# published ports
d.node(115, 330, 200, 330, "src", "server", "Ports", "Published to the host machine",
       chips=[":80 → nginx", ":443 → nginx", ":3000 → client", ":8000 → api"])

d.zone(350, 300, 1460, 400, "Network · app-network", "proxy", note="service-name DNS: db · api · client")
cy, ch = 350, 305
xs = [385, 745, 1105, 1465]
d.node(xs[0], cy, 320, ch, "proxy", "shield", "nginx", "Reverse proxy from <b>nginx:alpine</b>. Routes all traffic to <span class='mono'>client:3000</span>",
       chips=["ports 80, 443", "depends_on: client"])
d.node(xs[1], cy, 320, ch, "web", "globe", "client", "Nuxt.js app built from <span class='mono'>./client</span> on <b>node:20</b>",
       chips=["port 3000", "VITE_API_URL → api:8000"])
d.node(xs[2], cy, 320, ch, "api", "code", "api", "Laravel app built from <span class='mono'>./api</span> on <b>php:8.1-apache</b> with Composer",
       chips=["port 8000", "DB_HOST → db", "depends_on: db"])
d.node(xs[3], cy, 320, ch, "db", "db", "db", "Official <b>mysql:8</b> image. No host port published: reachable only inside the network",
       chips=["3306 internal", "database: bookapi"])
m = cy + 150
for a, b in zip(xs, xs[1:]):
    d.arrow([(a + 320, m), (b - 4, m)])

d.text(385, 728, 900, "STORAGE & CONFIGURATION MOUNTS", 14, "#475569", 700)
sy, sh = 765, 180
d.node(xs[0], sy, 320, sh, "store", "file", "Bind mounts", "Proxy config and TLS certificates", chips=["./nginx.conf", "./certs"])
d.node(xs[1], sy, 320, sh, "store", "disk", "Bind mount", "Client source", chips=["./client → /usr/src/app"])
d.node(xs[2], sy, 320, sh, "store", "disk", "Bind mount", "API source", chips=["./api → /var/www/html"])
d.node(xs[3], sy, 320, sh, "db", "db", "Named volume", "Database files survive container rebuilds", chips=["db_data → /var/lib/mysql"])
for x in xs:
    d.arrow([(x + 160, sy - 2), (x + 160, cy + ch + 6)], color="#94A3B8", dashed=True)

d.legend([("proxy", "Reverse proxy"), ("web", "Frontend"), ("api", "Backend API"), ("db", "Database / persistent data"),
          ("store", "Mounted files")], y=1003)
d.render("/home/claude/portfolio/devops/03-infrastructure.png")
