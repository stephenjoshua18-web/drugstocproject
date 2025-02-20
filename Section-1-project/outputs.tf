output "load_balancer_dns" {
  description = "The DNS name of the load balancer"
  value       = aws_lb.web_lb.dns_name
}

output "web_server_1_ip" {
  description = "Public IP of Web Server 1"
  value       = aws_instance.web1.public_ip
}

output "web_server_2_ip" {
  description = "Public IP of Web Server 2"
  value       = aws_instance.web2.public_ip
}

output "database_endpoint" {
  description = "The connection endpoint for the database"
  value       = aws_db_instance.db.endpoint
  sensitive   = true  # Marked sensitive to hide in Terraform CLI output
}
