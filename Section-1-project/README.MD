SECTION 1 overview

Terraform Infrastructure Deployment on AWS

Project Overview

This Terraform project provisions a cloud-based infrastructure for a web application on AWS. The infrastructure includes:

A Load Balancer (ALB) to distribute traffic.

Two Web Servers (EC2 Amazon Linux Instances running Nginx) for high availability.

A Database Server (RDS MySQL) for data persistence.

Security Groups to control network access.

Additionally, this setup is integrated with GitHub Actions CI/CD to ensure that infrastructure changes are deployed automatically when Terraform files are updated in the main branch.

Infrastructure Components

1. Virtual Private Cloud (VPC)

A VPC (aws_vpc.main) is created with a CIDR block defined in vars.tf. This provides network isolation for our resources.

2. Subnets

Two public subnets are created in different availability zones:

aws_subnet.subnet1 (AZ: us-east-1a)

aws_subnet.subnet2 (AZ: us-east-1b)

3. Security Groups

A security group (aws_security_group.web_sg) is created to allow traffic:

HTTP (80) and HTTPS (443) for web access.

SSH (22) for secure server access.

4. Load Balancer (ALB)

An Application Load Balancer (aws_lb.web_lb) is created to distribute incoming traffic between the two web servers.

5. Web Servers (EC2)

Two EC2 instances (aws_instance.web1 and aws_instance.web2) are created with Nginx installed via User Data.

6. Database Server (RDS MySQL)

A managed MySQL database (aws_db_instance.db) is provisioned with credentials managed via GitHub Secrets for security.

Security Considerations

Why the Database Password is Not in Plain Text

Instead of hardcoding the database password inside Terraform files, it is securely stored in GitHub Secrets and referenced in vars.tf and the CI/CD workflow.

In vars.tf (Variable File):

variable "db_password" {}

Here, db_password is declared without a default value to ensure it is always passed securely.

In main.tf (Database Configuration):

resource "aws_db_instance" "db" {
allocated_storage = var.db_storage
storage_type = "gp2"
engine = "mysql"
engine_version = "8.0"
instance_class = var.db_instance_class
username = var.db_username
password = var.db_password
skip_final_snapshot = true
}

The password references var.db_password, which is passed from GitHub Secrets during deployment.

In .github/workflows/terraform.yml (CI/CD Workflow):

- name: Terraform Plan
  run: terraform plan -var="db_password=${{ secrets.DB_PASSWORD }}"

The GitHub Actions pipeline injects the DB password from GitHub Secrets into the Terraform execution.
This prevents exposing sensitive credentials in the Terraform source code.

File Structure

├── main.tf # Terraform resources (ALB, EC2, RDS, Security Groups)
├── vars.tf # Variables (VPC CIDR, instance type, DB password, etc.)
├── outputs.tf # Outputs (ALB DNS, Web IPs, DB Endpoint)
├── .github/
│ ├── workflows/
│ │ ├── terraform.yml # GitHub Actions CI/CD workflow
├── README.md

How to Deploy

Prerequisites

AWS account with IAM credentials (stored as GitHub Secrets: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY)

Terraform installed (terraform -v to check)

GitHub repository with CI/CD enabled

Conclusion

We provisioned a secure and scalable infrastructure using Terraform on AWS.

GitHub Secrets ensured secure handling of sensitive credentials.

CI/CD automation with GitHub Actions enabled automatic deployment on every push.

The ALB distributes traffic between two web servers, with an RDS MySQL database as the backend.

This setup ensures high availability, security, and automation for our cloud infrastructure.
