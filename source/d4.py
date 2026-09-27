from lib import *
d = Diagram("DevOps Case Study · Deployment Flow",
            "How a New Version Reaches a Running Environment",
            "Automated image publishing on every push, plus a repeatable, documented bring-up of the full stack")

xs = [80, 445, 810, 1175, 1540]; w = 300

def lane(y, label, cat, steps, note):
    d.zone(55, y - 45, 1810, 310, label, cat, fill="#FFFFFF00", note=note)
    for i, (x, (c, ic, t, s, ch)) in enumerate(zip(xs, steps)):
        d.node(x, y, w, 225, c, ic, f"<span style='color:{C[c][0]};font-weight:800'>{i+1:02d}</span>&nbsp; {t}", s, chips=ch)
    m = y + 112
    for a, b in zip(xs, xs[1:]):
        d.arrow([(a + w, m), (b - 4, m)])

lane(300, "Track A · Continuous integration (automated)", "ci", [
    ("src", "user", "Commit", "Developer commits API, client or config changes", ["git commit"]),
    ("src", "branch", "Push to main", "Push to the main branch triggers the workflow", ["git push origin main"]),
    ("ci", "play", "Workflow runs", "GitHub Actions starts two parallel jobs", ["build-api", "build-client"]),
    ("reg", "cube", "Images built", "Each job builds its image from the project Dockerfile", ["api/Dockerfile", "client/Dockerfile"]),
    ("reg", "layers", "Publish", "Images pushed to Docker Hub for reuse", ["walidali123/api", "walidali123/client"]),
], "trigger: push → main")

lane(700, "Track B · Environment bring-up (documented, repeatable)", "proxy", [
    ("src", "clone", "Get the code", "Clone the repository onto the Docker host", ["git clone"]),
    ("sec", "cert", "TLS cert", "Generate key and self-signed certificate into ./certs", ["openssl genrsa", "openssl req -x509"]),
    ("proxy", "terminal", "Compose up", "Builds api and client images and creates the network and volume", ["docker compose up --build"]),
    ("api", "cube", "Services start", "Started in dependency order via depends_on", ["db → api", "client → nginx"]),
    ("proxy", "shield", "HTTPS live", "Nginx serves the app on :443 and redirects :80 to HTTPS", [":443", "301 ← :80"]),
], "defined in docker-compose.yml")

d.render("/home/claude/portfolio/devops/04-deployment-flow.png")
