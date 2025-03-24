# Configuration using provider functions must include required_providers configuration.
terraform {
  required_providers {
    local = {
      source = "hashicorp/local"
    }
  }
  required_version = ">= 1.8.0"
}
