output "outdir" {
  value = local.outdir
}

output "replace_trigger" {
  value = null_resource.docker_getbuild
}
