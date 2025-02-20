# Section 2: CI/CD Pipeline for Django Web Application

## **Overview**

This section implements a **CI/CD pipeline** using **GitHub Actions** to automate the deployment of a Django-based web application named `django_auth`. The pipeline performs the following tasks:

1. **Linting** the code to ensure best practices are followed.
2. **Running unit tests** to verify application functionality.
3. **Building a Docker image** for the Django application.
4. **Pushing the image to AWS Elastic Container Registry (ECR)**.
5. **Deploying the container to AWS Elastic Kubernetes Service (EKS)** using Kubernetes manifests.

## **Project Structure**

```
section2/
│-- django_auth/       # Django project
│   ├── manage.py      # Django management script
│   ├── requirements.txt  # Python dependencies
│   ├── Dockerfile     # Dockerfile for containerizing the app
│-- .github/workflows/
│   ├── cicd.yml       # GitHub Actions workflow for CI/CD
│-- kubernetes/
│   ├── deployment.yaml   # Kubernetes Deployment manifest
│   ├── service.yaml      # Kubernetes Service manifest
│   ├── ingress.yaml      # Ingress manifest for backend.drugstoc.com
```

## **CI/CD Workflow Explained**

The CI/CD pipeline is defined in `.github/workflows/cicd.yml`. It automates testing, building, pushing, and deploying the application.

### **Workflow Trigger**

Unlike **Section 1**, where the workflow triggers on **push to `main`**, in **Section 2**, it triggers on **push to `staging`** to avoid conflicts between different projects.

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

#### **2. Set Up Python Environment & Install Dependencies**

```yaml
- name: Set up Python
  uses: actions/setup-python@v3
  with:
    python-version: "3.10"

- name: Install Dependencies
  run: |
    pip install -r django_auth/requirements.txt
```

#### **3. Run Code Linting**

Ensures code follows best practices using `flake8`:

```yaml
- name: Lint Code
  run: flake8 django_auth/
```

#### **4. Run Unit Tests**

Runs Django unit tests:

```yaml
- name: Run Tests
  run: |
    cd django_auth
    python manage.py test
```

#### **5. Authenticate with AWS ECR & Push Docker Image**

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

1. **Update Kubernetes Deployment YAML**

   - The **Docker image URI** is referenced in the `deployment.yaml` file.
   - The image name matches the pushed Docker image.

2. **Apply Kubernetes Manifests**

```yaml
- name: Apply Kubernetes Deployment
  run: |
    aws eks --region us-east-1 update-kubeconfig --name my-cluster
    kubectl apply -f kubernetes/deployment.yaml
    kubectl apply -f kubernetes/service.yaml
    kubectl apply -f kubernetes/ingress.yaml
```

## **Kubernetes Configuration**

### **Deployment Manifest (`deployment.yaml`)**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: django-auth
spec:
  replicas: 2
  selector:
    matchLabels:
      app: django-auth
  template:
    metadata:
      labels:
        app: django-auth
    spec:
      containers:
        - name: django-auth
          image: "${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com/backend-drugstoc:latest"
          ports:
            - containerPort: 8000
```

### **Service Manifest (`service.yaml`)**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: django-auth-service
spec:
  type: ClusterIP
  selector:
    app: django-auth
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
```

### **Ingress Manifest (`ingress.yaml`)**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: django-auth-ingress
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
spec:
  rules:
    - host: backend.drugstoc.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: django-auth-service
                port:
                  number: 80
```

## **Deployment Process**

1. **Push code to `staging` branch**
   ```bash
   git add .
   git commit -m "Deploy update"
   git push origin staging
   ```
2. GitHub Actions triggers the CI/CD pipeline automatically.
3. AWS ECR stores the **Docker image**.
4. Kubernetes pulls the image and deploys it.
5. The service is available at **https://backend.drugstoc.com**.

## **Summary**

✅ **CI/CD Triggers**:

- **Section 1:** Triggers on `main`
- **Section 2:** Triggers on `staging`

✅ **Pipeline Steps**:

- Lint, test, build Docker image
- Push to **AWS ECR**
- Deploy to **AWS EKS Kubernetes**

🚀 **Final Result:** The Django app is accessible at `https://backend.drugstoc.com`

---

## **Next Steps**

- Implement database migrations
- Add monitoring and logging for the Kubernetes cluster
- Enhance security with IAM roles and secrets management
