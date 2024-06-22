terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.8.0"
    }
  }

  cloud {
    organization = "cloudysky"

    workspaces {
      name = "cloudysetup-workspace"
    }
  }
}
