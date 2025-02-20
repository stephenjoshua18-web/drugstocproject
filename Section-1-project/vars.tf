variable "vpc_cidr" {
  default = "10.0.0.0/16"
}

variable "subnet1_cidr" {
  default = "10.0.1.0/24"
}

variable "subnet2_cidr" {
  default = "10.0.2.0/24"
}

variable "ami_id" {
  default = "ami-0c55b159cbfafe1f0"
}

variable "instance_type" {
  default = "t2.micro"
}

variable "db_storage" {
  default = 10
}

variable "db_instance_class" {
  default = "db.t2.micro"
}

variable "db_username" {
  default = "admin"
}

variable "db_password" {
  description = "Database password from GitHub Secrets"
  type        = string
  default     = ""
}
variable "acm_certificate_arn" {
  description = "ARN of the SSL/TLS certificate from AWS Certificate Manager"
  type        = string
  default     = ""
}
