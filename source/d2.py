from lib import *
d = Diagram("DevOps Case Study · CI/CD",
            "GitHub Actions Pipeline: Build & Publish Images",
            "Every push to main builds the API and client images in parallel and publishes them to Docker Hub")

# Trigger
d.node(80, 515, 250, 190, "src", "branch", "Code Push", "Any push to branch <b>main</b>", chips=["on: push"])

d.zone(400, 250, 1110, 720, "Workflow · Build and Push Docker Images", "ci", dashed=False, fill="#FAFAFF",
       note=".github/workflows/docker-publish.yml")

def lane(y, label, df, img):
    d.zone(435, y, 1040, 300, label, "ci", fill="#FFFFFF")
    sy, sh = y + 55, 205
    d.node(465, sy, 250, sh, "ci", "server", "Runner", "GitHub-hosted virtual machine", chips=["ubuntu-latest"])
    d.node(780, sy, 270, sh, "ci", "clone", "Checkout", "Fetches the repository source", chips=["actions/checkout@v2"])
    d.node(1115, sy, 330, sh, "reg", "cube", "Build & Push Image",
           f"Builds <span class='mono'>{df}</span>, logs in to Docker Hub and pushes",
           chips=["docker-build-push@v5", img])
    m = sy + sh // 2
    d.arrow([(715, m), (776, m)]); d.arrow([(1050, m), (1111, m)])
    return m

m1 = lane(300, "Job 1 · build-api", "./api/Dockerfile", "walidali123/api")
m2 = lane(635, "Job 2 · build-client", "./client/Dockerfile", "walidali123/client")

# fan-out from trigger
d.arrow([(330, 610), (372, 610), (372, m1), (461, m1)])
d.arrow([(372, 610), (372, m2), (461, m2)])
d.pill(372, 610, "parallel", "ci")

# Registry
d.node(1590, 490, 250, 240, "reg", "layers", "Docker Hub", "Container registry (docker.io)",
       chips=["walidali123/api", "walidali123/client"])
d.arrow([(1445, m1), (1540, m1), (1540, 585), (1586, 585)], color="#0284C7")
d.arrow([(1445, m2), (1540, m2), (1540, 640), (1586, 640)], color="#0284C7")
d.pill(1540, 470, "docker push", "reg")

d.legend([("src", "Trigger"), ("ci", "Pipeline job / step"), ("reg", "Image build & registry")], y=1000)
d.text(900, 996, 900, "Credentials: <span class='mono'>DOCKER_USERNAME</span> / <span class='mono'>DOCKER_PASSWORD</span> stored as GitHub encrypted secrets", 15, "#64748B", 500)
d.render("/home/claude/portfolio/devops/02-cicd-pipeline.png")
