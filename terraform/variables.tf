variable "aws_region" {
  description = "AWS region to deploy into. Matches the region already used in zappa_settings.json."
  type        = string
  default     = "ca-central-1"
}

variable "project_name" {
  description = "Short name used to tag/name resources."
  type        = string
  default     = "inquests"
}

variable "instance_type" {
  description = "EC2 instance type. t4g.* is ARM/Graviton -- cheaper than the x86 t3.* equivalent for the same spec."
  type        = string
  default     = "t4g.micro"
}

variable "root_volume_size_gb" {
  description = "Root EBS volume size in GB. Covers the OS, Docker images, and the self-hosted Postgres data directory."
  type        = number
  default     = 30
}

variable "allowed_http_cidrs" {
  description = "CIDR blocks allowed to reach the app on ports 80 and 443. Defaults to the whole internet, since this is a public site."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "db_name" {
  description = "Postgres database name."
  type        = string
  default     = "inquests"
}

variable "db_user" {
  description = "Postgres role name used by the app."
  type        = string
  default     = "inquests_app"
}

variable "git_repo_url" {
  description = <<-EOT
    HTTPS URL user_data clones on first boot, e.g.
    https://github.com/<you>/<repo>.git. Assumes a PUBLIC repo -- a
    private repo needs auth (deploy key / PAT) that this minimal version
    doesn't set up. Required: there is no default.
  EOT
  type        = string
}

variable "domain_name" {
  description = "Route 53 public hosted zone to create the app's DNS record in. Must already exist in this AWS account."
  type        = string
  default     = "michaeleden.ca"
}

variable "app_hostname" {
  description = "Full hostname the app is reachable at. Must be domain_name itself or a subdomain of it."
  type        = string
  default     = "inquests.michaeleden.ca"
}
