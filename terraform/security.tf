resource "aws_security_group" "app" {
  name_prefix = "${var.project_name}-app-"
  description = "Inbound HTTP/HTTPS for app."
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-app"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Open port 80 for cert issuance and HTTP->HTTPS redirect.
resource "aws_vpc_security_group_ingress_rule" "http" {
  for_each = toset(var.allowed_http_cidrs)

  security_group_id = aws_security_group.app.id
  description       = "HTTP"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
  cidr_ipv4         = each.value
}

resource "aws_vpc_security_group_ingress_rule" "https" {
  for_each = toset(var.allowed_http_cidrs)

  security_group_id = aws_security_group.app.id
  description       = "HTTPS"
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
  cidr_ipv4         = each.value
}

# HTTP/3 (QUIC; enabled automatically by Caddy).
resource "aws_vpc_security_group_ingress_rule" "https_quic" {
  for_each = toset(var.allowed_http_cidrs)

  security_group_id = aws_security_group.app.id
  description       = "HTTPS (HTTP/3 / QUIC)"
  from_port         = 443
  to_port           = 443
  ip_protocol       = "udp"
  cidr_ipv4         = each.value
}

resource "aws_vpc_security_group_egress_rule" "all_outbound" {
  security_group_id = aws_security_group.app.id
  description       = "Allow all outbound traffic."
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}
