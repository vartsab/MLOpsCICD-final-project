# MLOps CICD Final Project — ML Inference Service with GitOps

## Project Overview
This project implements an end-to-end MLOps pipeline for deploying, monitoring, and retraining a machine learning model using modern DevOps and GitOps practices.

### The system includes:
- FastAPI inference service
- Model retraining pipeline
- Dockerized deployment
- Kubernetes deployment via Helm
- ArgoCD GitOps automation
- Prometheus metrics
- Drift detection logic
- GitLab CI/CD pipeline
### Repositories and Delivery Flow
This project uses two Git platforms for different responsibilities:
- **GitHub** stores the GitOps source of truth for Kubernetes deployment:
  - Helm chart
  - ArgoCD application
  - deployment configuration
- **GitLab** is used for CI/CD:
  - model training
  - Docker image build
  - Helm values update automation
  - manual retrain job
### Current flow
1. Code changes are pushed to GitLab and/or GitHub
2. GitLab CI builds a new Docker image
3. GitLab CI updates `helm/values.yaml` with a new image tag
4. The updated configuration is pushed to GitHub
5. ArgoCD detects the GitHub change and redeploys the application
### Project links
- **GitHub repository (GitOps source):** `https://github.com/vartsab/MLOpsCICD-final-project`
- **GitLab project (CI/CD):** `https://gitlab.com/vartsab/mlops-final-project`
---
##  Architecture
Flow:
1. User sends request → FastAPI `/predict`
2. Model generates prediction
3. Drift detection is evaluated
4. Metrics + logs are recorded
5. If drift detected → retrain pipeline can be triggered
6. CI builds new image → updates Helm → ArgoCD redeploys
---
## Repository Structure
```
aiops-quality-project/
├── app/ # FastAPI service
│ └── main.py
├── model/ # Training logic
│ └── train.py
├── helm/ # Helm chart
├── argocd/ # ArgoCD application
├── grafana/ # Dashboard config
├── prometheus/ # Scrape config
├── scripts/ # Helper scripts
├── .gitlab-ci.yml # CI pipeline
├── Dockerfile
└── README.md
```
---
## Prerequisites

- Docker
- Kubernetes cluster (EKS / local)
- kubectl
- Helm
- ArgoCD installed
- GitLab project (for CI)
- GitHub repo (for GitOps)
---
##  Local Run
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Test
```
curl http://127.0.0.1:8000/health
```
---
## Docker
Build
```
docker build -t mlops-quality-service:local .
```
Run
```
docker run -p 8000:8000 mlops-quality-service:local
```
---
## Kubernetes Deployment
```
helm upgrade --install aiops-quality-service ./helm \
  --namespace mlops-final \
  --create-namespace
```
---
## ArgoCD Deployment
Apply application:
```
kubectl apply -f argocd/application.yaml
```
Verify:
```
kubectl get applications -n infra-tools
```
---
## API Testing
```
kubectl port-forward svc/aiops-quality-service -n mlops-final 8000:8000
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features":[0.1,0.2,0.3]}'
```
## Logging Check
```
kubectl logs deployment/aiops-quality-service -n mlops-final
```
Look for:

- Incoming request
- Prediction
- Drift detected
---
## Drift Detection
Trigger drift:
```
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features":[10,0.2,0.3]}'
```
Expected log:
```
Drift detected
```
---
## Metrics (Prometheus)
```
curl http://127.0.0.1:8000/metrics
```
Metrics:
- inference_requests_total
- inference_drift_detected_total
- inference_request_latency_seconds
---
## GitLab CI Pipeline

Stages:
- train → builds model
- build → builds Docker image
- gitops → updates Helm values
- retrain → manual retrain job

Manual retrain:
```
GitLab → Pipelines → Run retrain-model
```
---
## Model Update Flow
1. Drift detected (optional trigger)
2. Retrain pipeline runs
3. New Docker image is built
4. Helm values updated with new tag
5. ArgoCD detects change
6. Kubernetes rollout happens automatically
---
## Key Features
- GitOps deployment with ArgoCD
- CI/CD automation with GitLab
- Drift-aware retraining workflow
- Metrics and observability
- Fully containerized ML service
---
## Known Limitations
- Drift detection is currently rule-based and serves as a lightweight placeholder rather than a production-grade statistical detector.
- The retrain pipeline is manual and controlled through GitLab CI. This is intentional for safety and demonstration purposes.
- The project currently uses a mixed registry approach:
  - deployment images are pulled from Docker Hub
  - GitLab CI is responsible for CI/CD orchestration
- Full production hardening is not implemented yet:
  - no secret manager integration
  - no ML model registry
  - no automatic approval gate before redeploying retrained models
- Loki/Promtail integration is represented through stdout-compatible logging and project structure, but may require additional cluster-side installation depending on the environment.
---
## Result
The system successfully demonstrates:
- Automated ML deployment
- Monitoring and observability
- Controlled retraining
- GitOps-based continuous delivery
---
## Verification Summary

The following project capabilities were verified during implementation:
- FastAPI inference service runs in Kubernetes
- `/health`, `/predict`, and `/metrics` endpoints work
- logs are available through `kubectl logs`
- drift events are visible in logs
- Prometheus-compatible metrics are exported
- Helm chart deploys successfully
- ArgoCD auto-sync works after Git changes
- GitLab CI runs training, build, GitOps update, and manual retrain jobs
- image tag updates trigger ArgoCD-driven rollout
---
