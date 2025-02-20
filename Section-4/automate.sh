#!/bin/bash # Configuration variables 
EMAIL="hello@drugstoc.com" 
THRESHOLD_CPU=80 # CPU usage percentage threshold 
THRESHOLD_MEM=80 # Memory usage percentage threshold
THRESHOLD_DISK=80 # Disk usage percentage 
threshold SERVICE="nginx" # Service to monitor 
HOSTNAME=$(hostname) # Temporary file for email content 
TEMP_FILE="/tmp/health_check_report_$$.txt" # Function to send email 
send_email() { local subject="$1" local message="$2" echo "$message" > "$TEMP_FILE" mail -s "$subject" "$EMAIL" < "$TEMP_FILE" rm -f "$TEMP_FILE" } # Check CPU usage 
cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d. -f1) echo "CPU Usage: $cpu_usage%"
 # Check memory usage 
mem_usage=$(free -m | awk 'NR==2{printf "%.0f", $3*100/$2}') echo "Memory Usage: $mem_usage%" 
# Check disk usage 
disk_usage=$(df -h / | awk 'NR==2{print substr($5, 1, length($5)-1)}') echo "Disk Usage: $disk_usage%" 
# Check service status 
service_status=$(systemctl is-active $SERVICE 2>/dev/null || echo "inactive")
 # Prepare status message 
 status_message="Server Health Check Report - $HOSTNAME Date: $(date) " 
 # Check thresholds and build alert message 
 alert=false alert_message="" if [ "$cpu_usage" -gt "$THRESHOLD_CPU" ]; then alert=true alert_message+="WARNING: CPU usage is at $cpu_usage% (Threshold: $THRESHOLD_CPU%) " fi if [ "$mem_usage" -gt "$THRESHOLD_MEM" ]; then alert=true alert_message+="WARNING: Memory usage is at $mem_usage% (Threshold: $THRESHOLD_MEM%) " fi if [ "$disk_usage" -gt "$THRESHOLD_DISK" ]; then alert=true alert_message+="WARNING: Disk usage is at $disk_usage% (Threshold: $THRESHOLD_DISK%) " fi 
 # Check and restart service if needed 
 if [ "$service_status" != "active" ]; then 
     alert=true
     alert_message+="WARNING: $SERVICE was down. Attempting to restart... " 
     sudo systemctl restart $SERVICE 
     sleep 2 # Wait for service to restart 
     
     new_status=$(systemctl is-active $SERVICE 2>/dev/null || echo "inactive") 
     if [ "$new_status" = "active" ]; then 
         alert_message+="SUCCESS: $SERVICE restarted successfully " 
         
     else 
         alert_message+="ERROR: Failed to restart $SERVICE " 
     
     fi
 else echo "$SERVICE is running" 
 
 fi 
 
 # Send email if there are any alerts 
 
 if [ "$alert" = true ]; then 
 
     status_message+="$alert_message" 
     
     send_email "Server Health Alert - $HOSTNAME" "$status_message" 
     
 fi 
 
 echo "Health check completed"​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​