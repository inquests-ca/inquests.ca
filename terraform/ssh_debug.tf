# TEMPORARY: SSH access for troubleshooting the SSM connectivity issue.
# To remove: delete this file, the `key_name` line and its comment in
# compute.tf, and the `ssh_debug_source_ip` variable in variables.tf, then
# `terraform apply` (this replaces the instance, same as any other
# user_data/key_name change).

resource "tls_private_key" "ssh_debug" {
  algorithm = "ED25519"
}

resource "aws_key_pair" "ssh_debug" {
  key_name_prefix = "${var.project_name}-debug-"
  public_key      = tls_private_key.ssh_debug.public_key_openssh

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_vpc_security_group_ingress_rule" "ssh_debug" {
  security_group_id = aws_security_group.app.id
  description       = "TEMPORARY: SSH for troubleshooting."
  from_port         = 22
  to_port           = 22
  ip_protocol       = "tcp"
  cidr_ipv4         = "${var.ssh_debug_source_ip}/32"
}
