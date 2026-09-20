#!/bin/bash

set -euxo pipefail

dnf install -y docker git unzip
systemctl enable --now docker
usermod -aG docker ec2-user

mkdir -p /usr/local/lib/docker/cli-plugins
curl -fsSL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m)" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Unattended security patching.
dnf install -y dnf-automatic
sed -i 's/^apply_updates = no/apply_updates = yes/' /etc/dnf/automatic.conf
systemctl enable --now dnf-automatic.timer

# AL2023 ships the AWS CLI v2 by default, but install it defensively
# rather than assume -- the SSM fetch below is load-bearing.
if ! command -v aws >/dev/null 2>&1; then
  curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-$(uname -m).zip" -o /tmp/awscliv2.zip
  unzip -q /tmp/awscliv2.zip -d /tmp
  /tmp/aws/install
fi

git clone ${git_repo_url} /opt/inquests
cd /opt/inquests

DB_PASSWORD=$(aws ssm get-parameter --name "/${project_name}/db_password" --with-decryption --query 'Parameter.Value' --output text --region ${aws_region})
DJANGO_SECRET_KEY=$(aws ssm get-parameter --name "/${project_name}/django_secret_key" --with-decryption --query 'Parameter.Value' --output text --region ${aws_region})

# Wrap secret values in single quotes to avoid unintended interpolation.
# https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/
cat > docker/.env <<ENV
POSTGRES_DB=${db_name}
POSTGRES_USER=${db_user}
POSTGRES_PASSWORD='$DB_PASSWORD'
POSTGRES_HOST=db
POSTGRES_PORT=5432
DJANGO_SECRET_KEY='$DJANGO_SECRET_KEY'
DJANGO_ALLOWED_HOSTS=${allowed_hosts}
APP_IMAGE=${ecr_repository_url}:latest
ENV
chmod 600 docker/.env

# The instance role's ecr:GetAuthorizationToken/pull permissions (see
# iam.tf) let it fetch a token, but `docker pull` itself still needs an
# actual `docker login` -- IAM permissions alone aren't sufficient.
aws ecr get-login-password --region ${aws_region} | docker login --username AWS --password-stdin ${ecr_repository_url}

# The app image is built and pushed manually for now (not here) -- see
# the ecr_login_command Terraform output.
docker compose -f docker/docker-compose.prod.yml pull
docker compose -f docker/docker-compose.prod.yml up -d
