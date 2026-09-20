output "instance_id" {
  value = aws_instance.app.id
}

output "public_ip" {
  description = "Static Elastic IP at which app can be accessed"
  value       = aws_eip.app.public_ip
}

output "ssm_connect_command" {
  description = "Command for shell access via SSM"
  value       = "aws ssm start-session --target ${aws_instance.app.id} --region ${var.aws_region}"
}

output "ecr_repository_url" {
  description = "Push app images here, tagged :latest (what the instance pulls)."
  value       = aws_ecr_repository.app.repository_url
}

output "ecr_login_command" {
  description = "Authenticate Docker locally against this ECR repository."
  value       = "aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.app.repository_url}"
}

output "ecr_build_and_push_commands" {
  description = "Build and push the app image, from the repo root."
  value = join("\n", [
    "docker build -f docker/app.Dockerfile -t ${aws_ecr_repository.app.repository_url}:latest .",
    "docker push ${aws_ecr_repository.app.repository_url}:latest",
  ])
}

# TEMPORARY, troubleshooting only -- see ssh_debug.tf.
output "ssh_debug_private_key" {
  description = "Save with: terraform output -raw ssh_debug_private_key > debug_key.pem && chmod 600 debug_key.pem"
  value       = tls_private_key.ssh_debug.private_key_openssh
  sensitive   = true
}

output "ssh_debug_connect_command" {
  description = "Run after saving the private key per ssh_debug_private_key above."
  value       = "ssh -i debug_key.pem ec2-user@${aws_eip.app.public_ip}"
}
