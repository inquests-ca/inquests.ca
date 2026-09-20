# Holds the app image. Built and pushed manually for now (see the
# ecr_login_command output) -- CI/CD would push here instead.
resource "aws_ecr_repository" "app" {
  name                 = "${var.project_name}-app"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  # Convenience for this single-maintainer, still-iterating project --
  # lets `terraform destroy` tear this down without manually deleting
  # images first.
  force_delete = true
}
