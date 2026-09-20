# For EC2 AMI, use Amazon Linux 2023, arm64 (compatible with t4g instances)
data "aws_ami" "al2023_arm64" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-arm64"]
  }

  filter {
    name   = "architecture"
    values = ["arm64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_eip" "app" {
  domain = "vpc"

  tags = {
    Name = "${var.project_name}-app"
  }
}

resource "aws_instance" "app" {
  ami                    = data.aws_ami.al2023_arm64.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.app.id]
  iam_instance_profile   = aws_iam_instance_profile.instance.name

  # Normally no SSH keypair -- shell access is via SSM Session Manager (see
  # iam.tf). key_name below is TEMPORARY, for troubleshooting SSM
  # connectivity (see ssh_debug.tf); remove it along with that file once
  # no longer needed.
  key_name = aws_key_pair.ssh_debug.key_name

  user_data = templatefile("${path.module}/user_data.sh.tpl", {
    git_repo_url       = var.git_repo_url
    project_name       = var.project_name
    aws_region         = var.aws_region
    db_name            = var.db_name
    db_user            = var.db_user
    allowed_hosts      = aws_eip.app.public_ip
    ecr_repository_url = aws_ecr_repository.app.repository_url
  })
  user_data_replace_on_change = true

  root_block_device {
    volume_type           = "gp3"
    volume_size           = var.root_volume_size_gb
    encrypted             = true
    delete_on_termination = true
  }

  metadata_options {
    http_tokens = "required" # IMDSv2 only
  }

  tags = {
    Name = "${var.project_name}-app"
  }
}

# Associate elastic IP to instance
resource "aws_eip_association" "app" {
  instance_id   = aws_instance.app.id
  allocation_id = aws_eip.app.id
}
