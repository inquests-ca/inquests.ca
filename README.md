# inquests.ca

## Infrastructure

AWS infrastructure is managed with Terraform, in [`terraform/`](./terraform).

### Bootstrapping Remote State

The S3 bucket containing Terraform state must be bootstrapped before it can be configured as a backend for Terraform.

To bootstrap the Terraform S3 backend:

1. Comment out the `backend "s3" { ... }` block in [`terraform/versions.tf`](./terraform/versions.tf).
2. Create the state bucket: `terraform apply`.
3. Uncomment the `backend "s3"` block.
4. Move local state to the new backend: `terraform init -migrate-state`. 
