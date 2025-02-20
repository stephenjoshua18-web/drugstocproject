# Section 2: CI/CD Pipeline for Django backend Application

## Overview

This section implements a CI/CD pipeline using GitHub Actions to automate the deployment of a Django-based backend authentication application which i wrote a while ago named `django_auth`. The pipeline performs the following tasks:

1. Linting the code with flake8 to ensure best practices are followed.
2. Running unit tests to verify application functionality.
3. Building a Docker image for the Django application.
4. Pushing the image to AWS Elastic Container Registry (ECR)
5. Deploying the container to AWS Elastic Kubernetes Service (EKS) using Kubernetes manifests.

## Project Structure

```
section2/
│-- django_auth/       # Django project
│   ├── manage.py      # Django management script
│   ├── requirements.txt  # Python dependencies
│   ├── Dockerfile     # Dockerfile for containerizing the app
│-- .github/workflows/
│   ├── deploy.yml       # GitHub Actions workflow for CI/CD
│-- kubernetes/
│   ├── deployment.yaml   # Kubernetes Deployment manifest
│   ├── ingress.yaml      # Ingress manifest for backend.drugstoc.com
```

## **CI/CD Workflow Explained**

The CI/CD pipeline is defined in `.github/workflows/cicd.yml`. It automates testing, building, pushing, and deploying the application.

### **Workflow Trigger**

Unlike Section 1, where the workflow triggers on **push to `main`**, in Section 2, it triggers on push to `staging` to avoid conflicts between different projects.

```yaml
on:
  push:
    branches:
      - staging
```

### **Steps in the CI/CD Pipeline**

#### **1. Checkout Repository**

Clones the repository into the CI/CD runner:

```yaml
- name: Checkout repository
  uses: actions/checkout@v3
```

#### 2. Set Up Python Environment & Install Dependencies\*\*

```yaml
- name: Set up Python
  uses: actions/setup-python@v3
  with:
    python-version: "3.10"

- name: Install Dependencies
  run: |
    pip install -r django_auth/requirements.txt
```

#### 3. Run Code Linting

Ensures code follows best practices using `flake8`:

```yaml
- name: Lint Code
  run: flake8 django_auth/
```

#### 4. Run Unit Tests

Runs Django unit tests:

```yaml
- name: Run Tests
  run: |
    cd django_auth
    python manage.py test
```

#### 5. Authenticate with AWS ECR & Push Docker Image

AWS requires authentication before pushing Docker images to **Elastic Container Registry (ECR)**.

1. **Log in to AWS ECR**:

```yaml
- name: Authenticate with AWS ECR
  run: |
    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com
```

2. **Build and Push the Docker Image**:

```yaml
- name: Build & Push Docker Image
  run: |
    IMAGE_URI=${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com/backend-drugstoc:latest
    docker build -t $IMAGE_URI -f django_auth/Dockerfile .
    docker push $IMAGE_URI
```

The **AWS Account ID** is stored in **GitHub Secrets** to enhance security.

#### **6. Deploy to AWS Kubernetes (EKS)**

1. Update Kubernetes Deployment YAML

   - The **Docker image URI** is referenced in the `deployment.yaml` file.
   - The image name matches the pushed Docker image.

2. Apply Kubernetes Manifests\*\*

3. Push code to `staging` branch
   ```bash
   git add .
   git commit -m "Deploy update"
   git push origin staging
   ```
4. GitHub Actions triggers the CI/CD pipeline automatically.
5. AWS ECR stores the Docker image
6. Kubernetes pulls the image and deploys it.
7. The service would be available at https://backend.drugstoc.com (it is not available as i do not have the domain conf)
   i have tested it internally

## **Summary**

CI/CD Triggers:

- Section 1:Triggers on `main`
- Section 2: Triggers on `staging`

Pipeline Steps:

- Lint, test, build Docker image
- Push to AWS ECR
- Deploy to AWS EKS Kubernetes
