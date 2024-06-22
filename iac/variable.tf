# General Variables
variable "region" {
  description = "The AWS region to deploy infrastructure into"
  default     = "us-east-1"
}

# Domain & SSL Certificate Variables
variable "custom_domain_name" {
  description = "Domain name for the website and SSL certificate"
}


variable "hosted_zone_id" {
  description = "Route53 hosted zone ID"
}

