# Weather ML App — Setup & CI/CD Guide

## 1. Project Overview

This repository contains the Weather ML App, a Flask-based application containerised using Docker and deployed to Kubernetes using Minikube running on an AWS EC2 instance.

The project uses GitHub Actions for Continuous Integration (CI) and Continuous Deployment (CD).

### Technologies Used
- Python / Flask
- Docker
- DockerHub
- GitHub Actions
- Kubernetes
- Minikube
- AWS EC2 (Ubuntu)
- Self-hosted GitHub Actions runner

---

## Continuous Integration (CI)

The CI workflow is located at:

```text
.github/workflows/CI.yml
```

CI runs automatically when changes are pushed to the configured branches.

The CI pipeline performs the following steps:

1. Checks out the repository.
2. Sets up Python 3.11.
3. Installs the project dependencies from `requirements.txt`.
4. Runs the smoke tests.
5. Runs the unit tests.
6. Runs the integration tests.
7. Logs in to DockerHub using GitHub repository secrets.
8. Builds the Docker image.
9. Starts a Docker container for testing.
10. Executes a command inside the running container.
11. Pushes the image to DockerHub.

The Docker image is published to:

```text
eviegeraghty10/weather-ml-app
```

Images are tagged using the commit SHA and `latest`.

### CI GitHub Secrets

The CI workflow requires the following repository secrets:

| Secret | Purpose |
|---|---|
| `DOCKERHUB_USERNAME` | DockerHub username |
| `DOCKERHUB_TOKEN` | DockerHub access token used to push images |

These can be configured under:

**GitHub Repository → Settings → Secrets and variables → Actions**

Never commit DockerHub tokens or passwords to the repository.

---

## Continuous Deployment (CD)

The CD workflow is located at:

```text
.github/workflows/CD.yml
```

CD runs following a successful CI workflow.

The deployment process:

1. Runs on the self-hosted GitHub Actions runner on EC2.
2. Checks the Kubernetes cluster.
3. Updates the Kubernetes Deployment to use the newly built Docker image.
4. Waits for the Kubernetes rolling deployment to complete.
5. Checks the deployed pods and Deployment.
6. Confirms successful deployment.

The image is deployed using its commit SHA tag.

The Kubernetes Deployment is called:

```text
weather-ml-app
```

The deployment uses three replicas and a rolling update strategy to minimise disruption during updates.

---

## Kubernetes / Minikube

Kubernetes runs through Minikube on the EC2 server.

### Check Minikube status

```bash
minikube status
```

### Start Minikube if it is stopped

```bash
minikube start
```

### Check Kubernetes nodes

```bash
kubectl get nodes
```

The node should show a status of `Ready`.

### Check application pods

```bash
kubectl get pods
```

### Check the Deployment

```bash
kubectl get deployment weather-ml-app
```

### Check the Service

```bash
kubectl get services
```

The application uses Kubernetes NodePort `30080` for access through the cluster's NodePort service.

---

## Self-Hosted GitHub Actions Runner

A self-hosted runner is installed on the EC2 server so that CD can deploy directly to Kubernetes without GitHub-hosted runners needing to connect to EC2 over SSH.

The runner is registered to this repository and is configured with the `self-hosted`, `Linux`, and `X64` labels.

### Runner directory

```bash
~/actions-runner
```

### Start the runner manually

If the runner is not running as a service:

```bash
cd ~/actions-runner
./run.sh
```

Keep the terminal open while the runner is running.

### Runner service

The runner should ideally be installed as a service so it can run in the background.

To install:

```bash
cd ~/actions-runner
sudo ./svc.sh install ubuntu
```

To start:

```bash
sudo ./svc.sh start
```

To check the service status:

```bash
sudo ./svc.sh status
```

To stop:

```bash
sudo ./svc.sh stop
```

To check whether GitHub sees the runner:

**GitHub Repository → Settings → Actions → Runners**

The runner should show as online/idle when available to receive jobs.

---

## EC2 Server Information

The deployment environment runs on an AWS EC2 Ubuntu server.

The server's public IP address may change if the EC2 instance is stopped and restarted, unless an Elastic IP is configured.

When the public IP changes:

1. Open the AWS Console.
2. Go to EC2 → Instances.
3. Select the relevant instance.
4. Find its current Public IPv4 address.
5. Update any configuration or GitHub secrets that use the old IP address.

### GitHub Secrets relating to EC2

The following secrets were previously configured for SSH-based deployment:

| Secret | Purpose |
|---|---|
| `EC2_HOST` | EC2 public IP address |
| `EC2_USER` | EC2 SSH username (normally `ubuntu`) |
| `EC2_SSH_KEY` | SSH private key |

**The current CD workflow uses the self-hosted runner rather than SSH from a GitHub-hosted runner.** Therefore, these SSH secrets are not currently required by the self-hosted CD workflow, unless another workflow or process uses them.

If the deployment method is changed back to SSH, the `EC2_HOST` secret must be updated when the public IP changes. The SSH key must correspond to a public key authorised on EC2.

---

## Updating the Application

To make a change:

1. Make the required changes to the application code.
2. Commit the changes.
3. Push to the configured branch.
4. GitHub Actions runs CI.
5. If CI succeeds, CD is triggered.
6. CD deploys the new image to Kubernetes.

Check the Actions tab on GitHub to view the CI and CD logs.

---

##  Security

- Do not commit private SSH keys.
- Do not commit DockerHub tokens.
- Store credentials in GitHub repository secrets.
- Only add trusted public SSH keys to EC2.
- Do not unnecessarily expose SSH to all IP addresses.
- Ensure the self-hosted runner is only used for trusted repository workflows.
- Do not share private keys between team members.

---

## Useful Links

- GitHub Repository: https://github.com/weather-ml/weather-ml-app
- DockerHub Repository: https://hub.docker.com/r/eviegeraghty10/weather-ml-app
- GitHub Actions: Open the Actions tab in the repository
- Runner Settings: Repository Settings → Actions → Runners
- EC2: AWS Console → EC2 → Instances

