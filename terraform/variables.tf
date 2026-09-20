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
  description = "CIDR blocks allowed to reach the app on port 80. Defaults to the whole internet, since this is a public site."
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

variable "ssh_debug_source_ip" {
  description = <<-EOT
    TEMPORARY, troubleshooting only (see ssh_debug.tf): a single IP
    address (no /32 suffix -- that's added automatically) allowed to SSH
    into the instance on port 22. Required: there is no default, so this
    has to be deliberately provided. Remove ssh_debug.tf, this variable,
    and the `key_name` line in compute.tf once no longer needed.
  EOT
  type        = string
}
