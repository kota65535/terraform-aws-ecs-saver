terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.0"
    }
    temporary = {
      source  = "kota65535/temporary"
      version = "~> 1.0"
    }
  }
}

provider "temporary" {
  base = local.terraform_tmp_dir
}
