locals {
  image_tag = var.name
  sha       = sha1(join("", [for f in fileset(var.working_directory, "**") : filesha1("${var.working_directory}/${f}")]))
  outdir    = abspath(data.external.temp_dir.result["dir"])
  arguments = join(" ", [for key, value in var.docker_arguments : format("--build-arg %s=%s", key, value)])
}

data "external" "temp_dir" {
  program = ["bash", "${path.module}/temp.sh"]
}

resource "null_resource" "docker_build" {
  triggers = {
    sha    = local.sha
    always = timestamp()
  }

  provisioner "local-exec" {
    command     = <<EOF
    set -xe
    docker build --platform linux/amd64 \
      --tag ${local.image_tag} \
      ${local.arguments} \
      .
    EOF
    environment = var.docker_arguments
    working_dir = var.working_directory
    on_failure  = fail
  }
}

resource "null_resource" "docker_getbuild" {
  depends_on = [null_resource.docker_build]
  triggers = {
    sha    = local.sha
    always = timestamp()
  }

  provisioner "local-exec" {
    command    = <<EOF
    set -xe
    cname=$(docker run -d ${local.image_tag})
    docker cp "$${cname}":${var.output_location} ${local.outdir}/
    docker rm -f $${cname}
    EOF
    on_failure = fail
  }
}
