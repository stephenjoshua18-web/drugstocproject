# Section 3: Monitoring and Logging

## Overview

This section focuses on setting up a monitoring solution for our application using Prometheus and Grafana. The goal was to:

- Collect CPU, Memory, and Network usage metrics\*\* from our EC2 instances.
- Set up Prometheus as a monitoring tool to gather metrics from Node Exporter
- Use Grafana as a visualization tool to create a monitoring dashboard.
- Generate an alert when CPU usage exceeds 80%
- Integrate Slack notifications to send alerts to the `#engineering` channel.
- Automate deployment using Ansible and GitHub Actions CI/CD

## Infrastructure Setup

This monitoring solution was deployed on two EC2 instances provisioned in Section 1

components deployed:

- Prometheus: Collects and stores time-series metrics.
- Node Exporter: Gathers system-level metrics from EC2 instances.
- Grafana: Provides a UI for monitoring dashboards.
- Slack Alerts: Sends notifications when CPU usage is high.

## How It Was Done

### 1️ Provisioning EC2 Instances

We referenced the EC2 instances created in Section 1 and stored their IP addresses in `inventory.ini` for Ansible to use.

### 2️ Deploying Monitoring Tools with Ansible

We created an Ansible playbook to install and configure \*\*Prometheus, Node Exporter, and Grafana

- Prometheus installation
- Node Exporter installation
- Grafana installation and configuration\*\*
- Setting up Slack alerts

### 3️ Configuring Prometheus to Scrape Metrics

We configured Prometheus to collect metrics from Node Exporter running on the EC2 instances by defining them in the `prometheus.yml` file.

### 4️ Setting Up Grafana Dashboard

- Added Prometheus as a data source
- Created a dashboard to visualize CPU, Memory, and Network usage.
- Set up an alert rule to trigger an alert when CPU usage exceeds 80%.

### 5️ Integrating Slack for Alerts

- We configured Grafana Alerting to send notifications to **Slack** using a Webhook.
- The alert is triggered when CPU usage > 80%.

### 6️ Automating Deployment with GitHub Actions

- A GitHub Actions pipeline was created to deploy this setup automatically whenever code is pushed to the infra branch.
- The pipeline:
  - SSHs into the EC2 instances.
  - Runs the Ansible playbook to deploy monitoring tools.
  - Configures the Slack Webhook for alerts

## How to Access Monitoring Tools

### Accessing Grafana

1. Find the public IP of the EC2 instance where Grafana is installed.
2. Open your browser and go to:

   http:ip:3000

3. Login credentials (default):
   - Username: `admin`
   - Password: `admin`

### 🔍 Checking Prometheus

1. Find the public IP of the EC2 instance running Prometheus.
2. Open your browser and go to:

   http://<PROMETHEUS_IP>:9090

3. Click Status → targets to check if the Node Exporter is being scraped.

### Creating the Grafana Dashboard

1. Go to Grafana
2. Click `+` to Create Dashboard
3. Click Add a New Panel
4. Under `Query`, select Prometheus as the data source
5. Use the query to track CPU usage:

   100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[2m])) \* 100)

6. Save the dashboard.

## Slack Alert Configuration

### Setting Up Alerts in Grafana

1. Navigate to Alerting → Notification Channels
2. Click New Notification Channel
3. Set:
   - Name: Slack Alerts
   - Type: Slack
   - Webhook URL: (Use the Slack Webhook stored in GitHub Secrets)\*
   - Channel: `#engineering`
4. Save the configuration.

### Creating an Alert Rule

1. Click Alerting → Alert Rules
2. Click New Alert Rule
3. Set CPU Usage > 80%:

   100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[2m])) \* 100) > 80

4. Assign Notification Channel: Slack Alerts
5. Save and activate.

## Achievements

Deployed Prometheus and Node Exporter for system monitoring
Set up Grafana for visualization
Created a real-time dashboard for CPU, Memory, and Network usage
Configured Slack alerts for CPU threshold breaches
Automated deployment using Ansible and GitHub Actions

Monitoring is now fully set up for our application and the pipeline will only
trigger when its been pushed to 'infra branch' to avoid conflicts and runner misuse
