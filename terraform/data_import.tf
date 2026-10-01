# Bucket containing data to be imported into database.
# Accessed via pre-signed URL.
resource "aws_s3_bucket" "data_import" {
  bucket = "${var.project_name}-data-import-${data.aws_caller_identity.current.account_id}"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "data_import" {
  bucket = aws_s3_bucket.data_import.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Expire objects to avoid having PII sit in bucket indefinitely.
resource "aws_s3_bucket_lifecycle_configuration" "data_import" {
  bucket = aws_s3_bucket.data_import.id

  rule {
    id     = "expire-after-7-days"
    status = "Enabled"

    filter {}

    expiration {
      days = 7
    }
  }
}
