resource "random_password" "db_password" {
  length = 32
}

resource "random_password" "django_secret_key" {
  length = 64
}

resource "aws_ssm_parameter" "db_password" {
  name  = "/${var.project_name}/db_password"
  type  = "SecureString"
  value = random_password.db_password.result

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "django_secret_key" {
  name  = "/${var.project_name}/django_secret_key"
  type  = "SecureString"
  value = random_password.django_secret_key.result

  lifecycle {
    ignore_changes = [value]
  }
}
