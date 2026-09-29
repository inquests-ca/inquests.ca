data "aws_route53_zone" "app" {
  name         = "${var.domain_name}."
  private_zone = false
}

# Route hostname to EIP.
resource "aws_route53_record" "app" {
  zone_id = data.aws_route53_zone.app.zone_id
  name    = var.app_hostname
  type    = "A"
  ttl     = 300
  records = [aws_eip.app.public_ip]
}
