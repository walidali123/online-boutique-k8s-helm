from lib import *
d = Diagram("DevOps Case Study · Architecture",
            "Containerized Full-Stack Delivery Architecture",
            "Automated image builds on GitHub, and a four-service Docker Compose stack served over HTTPS through Nginx")

# ---- Zone A: build & delivery
d.zone(80, 250, 1760, 250, "Build & delivery · automated", "ci")
y, h = 286, 184
d.node(120, y, 250, h, "src", "user", "Developer", "Commits API, client and infrastructure config")
d.node(480, y, 370, h, "src", "branch", "GitHub Repository", "Branch <b>main</b>", chips=["api/", "client/", "docker-compose.yml"])
d.node(960, y, 400, h, "ci", "play", "GitHub Actions", "Two parallel jobs on ubuntu-latest", chips=["build-api", "build-client"])
d.node(1470, y, 330, h, "reg", "layers", "Docker Hub", "Published container images", chips=["walidali123/api", "walidali123/client"])
my = y + h // 2
d.arrow([(370, my), (476, my)]); d.pill(423, my - 30, "git push")
d.arrow([(850, my), (956, my)]); d.pill(903, my - 30, "on push")
d.arrow([(1360, my), (1466, my)]); d.pill(1413, my - 30, "push")

# ---- Zone B: runtime
d.zone(400, 580, 1440, 370, "Runtime · Docker Compose host", "proxy", note="network: app-network")
ny, nh = 655, 220
d.node(450, ny, 290, nh, "proxy", "shield", "Nginx", "Reverse proxy. Redirects HTTP to HTTPS and terminates TLS",
       chips=["nginx:alpine", ":80", ":443"])
d.node(850, ny, 260, nh, "web", "globe", "Nuxt.js Client", "Frontend application container", chips=["node:20", ":3000"])
d.node(1220, ny, 260, nh, "api", "code", "Laravel API", "Backend API on PHP 8.1 + Apache", chips=["php:8.1-apache", ":8000"])
d.node(1590, ny, 220, nh, "db", "db", "MySQL 8", "Data persisted in a named volume", chips=["mysql:8", "db_data"])
ay = ny + nh // 2
d.node(100, ay - 85, 230, 170, "src", "user", "End User", "Web browser", center=True)
d.arrow([(330, ay), (446, ay)], color="#059669"); d.pill(388, ay - 30, "HTTPS", "proxy")
d.arrow([(740, ay), (846, ay)]); d.pill(793, ay - 30, ":3000", mono=True)
d.arrow([(1110, ay), (1216, ay)]); d.pill(1163, ay - 30, ":8000", mono=True)
d.arrow([(1480, ay), (1586, ay)]); d.pill(1533, ay - 30, ":3306", mono=True)

# repo -> runtime (manual bring-up from source)
d.arrow([(665, 470), (665, 576)], dashed=True)
d.pill(665, 540, "git clone  →  docker compose up --build", mono=True)

d.legend([("src", "Source"), ("ci", "CI pipeline"), ("reg", "Image registry"), ("proxy", "Reverse proxy"),
          ("web", "Frontend"), ("api", "Backend API"), ("db", "Database")], y=1000)
d.render("/home/claude/portfolio/devops/01-devops-architecture.png")
