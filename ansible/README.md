# Task 3: Preparing the Production Server with Ansible

| Playbook | Task | What it does |
|---|---|---|
| `01_install_kubectl.yml` | 3(a) | Downloads the latest stable kubectl, checks its SHA256 checksum and confirms it runs |
| `02_install_minikube.yml` | 3(b) | Installs Minikube, adds the user to the `docker` group and starts a cluster with the Docker driver |
| `03_deploy_app.yml` | 3(c) | Runs `kubectl apply -f k8s/deployment.yaml`, which pulls the image from DockerHub, then waits for the rollout |
| `04_create_service.yml` | 3(d) | Applies `k8s/service.yaml` (NodePort 30080) and forwards public port 5000 to it with socat |
| `05_scale_deployment.yml` | 3(e) | Scales the deployment to 3 replicas and shows the RollingUpdate strategy |
| `site.yml` | all | Runs all five playbooks in order |

## Before you run

1. **Set the image.** In `k8s/deployment.yaml`, replace `YOUR_DOCKERHUB_USERNAME/weather-ml-app:v1` with the image Person 1 pushed. The DockerHub repo must be **public**. A private repo also needs an `imagePullSecret`.
2. **Get the repo onto the production server.** `git clone` it there. The playbooks read `../k8s/`, so keep the folder layout.
3. **Docker group.** If your user was only just added to the `docker` group, log out and back in (or run `newgrp docker`) before running 03–05. The `minikube status` and `minikube ip` commands need Docker access.
4. **Use one user throughout.** Run everything as `ubuntu`, not `sudo ansible-playbook`. Minikube refuses the Docker driver as root, and the playbooks ask for root only where they need it.
5. **Security group.** Port 5000 must be open inbound on the Production Server. Stop any container you started by hand with `-p 5000:5000`, or the forwarder can't bind that port.

## Run

```bash
cd ~/weather-ml-app/ansible
ansible-playbook site.yml --ask-become-pass   # on EC2 ubuntu has passwordless sudo, so you can omit the flag
```

For the evidence screenshots (spec 3.1.4), it's clearer to run each one separately and take a screenshot of each `PLAY RECAP` with `failed=0`:

```bash
ansible-playbook 01_install_kubectl.yml
ansible-playbook 02_install_minikube.yml
ansible-playbook 03_deploy_app.yml
ansible-playbook 04_create_service.yml
ansible-playbook 05_scale_deployment.yml
```

The playbooks are idempotent. A second run reports `changed=0`, which is worth one screenshot to show it.

## Check it worked

```bash
kubectl get deploy,pods,svc -l app=weather-ml-app
curl $(minikube ip):30080          # the video's "curl $(minikube ip):NODE_PORT"
# browser: http://<production-public-ip>:5000
```

## Notes for Person 4 (CD.yml)

- Deployment name `weather-ml-app`, container name `weather-ml-app`, service `weather-ml-app-service`, NodePort `30080`.
- A rolling update to v2 is either
  `kubectl set image deployment/weather-ml-app weather-ml-app=<user>/weather-ml-app:v2`
  or, for the YAML bonus, change the tag in `k8s/deployment.yaml` and run `kubectl apply -f k8s/deployment.yaml`.
- The self-hosted runner must run as the same user that started Minikube (`ubuntu`), or kubectl won't find `~/.kube/config`.
- The socat forwarder points at the Service, not at a pod, so the browser keeps working while pods are replaced.

## Common problems

| Symptom | Likely cause |
|---|---|
| `ImagePullBackOff` | Wrong image name or tag, or the DockerHub repo is private |
| `minikube start` fails with "root privileges" | The playbook was run with `sudo`. Run it as `ubuntu` instead |
| `permission denied ... docker.sock` | The `docker` group isn't active in this shell yet. Log out and back in |
| Pods `Pending` | Not enough CPU or memory. Check `kubectl describe pod` and lower the requests |
| Disk full (12 GB server) | Run `docker system prune -a` on the host. Check space with `df -h` |
| Browser can't connect, curl works | Port 5000 is closed in the security group, or `systemctl status weather-app-forward` shows the forwarder isn't running |
