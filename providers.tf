terraform {
  required_providers {
    temporary = {
      source  = "kota65535/temporary"
      version = "~> 1.0"
    }
  }
}

provider "temporary" {
  base = local.terraform_tmp_dir
}
