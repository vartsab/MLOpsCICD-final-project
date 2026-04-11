# MLOps CICD Final Project — ML Inference Service with GitOps

## Project Overview
This project implements an end-to-end MLOps pipeline for deploying, monitoring, and retraining a machine learning model using modern DevOps and GitOps practices.

The system includes:
- FastAPI inference service
- Model retraining pipeline
- Dockerized deployment
- Kubernetes deployment via Helm
- ArgoCD GitOps automation
- Prometheus metrics
- Drift detection logic
- GitLab CI/CD pipeline
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
- Drift detection is rule-based (mock)
- Retrain is manual trigger (not fully automated)
- CI uses GitLab registry but Helm uses Docker Hub
- No model version registry (MLflow optional)
---
## Result

The system successfully demonstrates:
- Automated ML deployment
- Monitoring and observability
- Controlled retraining
- GitOps-based continuous delivery
---
