terraform {
  backend "s3" {
    key            = "terraform/ayedgrading/dev.tfstate"
    bucket         = "personal-aanzolaavila-terraform-state"
    dynamodb_table = "personal-aanzolaavila-terraform-state-locks"

    region  = "us-east-1"
    encrypt = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.83"
    }
  }
}

provider "aws" {
  profile = "default"
  region  = "us-east-1"
}
