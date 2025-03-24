locals {
  python_versions = [
    "3.10",
    "3.11",
    "3.12",
    "3.13",
  ]
  versions_iter = {
    for k in local.python_versions : replace(k, ".", "") => k
  }
}

module "build" {
  for_each = local.versions_iter
  source   = "../docker_builder"

  name              = "python${each.key}"
  working_directory = "${path.module}/project"
  output_location   = "/build/build.zip"
  docker_arguments = {
    PYTHON_VERSION = each.value
  }
}

data "aws_s3_bucket" "selected" {
  bucket = var.s3bucket_name
}

resource "terraform_data" "replace_trigger" {
  for_each = local.versions_iter
  input    = module.build[each.key].replace_trigger
}

resource "aws_s3_object" "object" {
  for_each = local.versions_iter

  bucket       = data.aws_s3_bucket.selected.bucket
  key          = "grading-python${each.key}.zip"
  source       = "${module.build[each.key].outdir}/build.zip"
  content_type = "application/zip"

  lifecycle {
    replace_triggered_by = [terraform_data.replace_trigger[each.key]]
  }
}
