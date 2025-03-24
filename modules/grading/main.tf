module "jupyter_grading" {
  depends_on = [module.s3]
  source     = "../jupyter_grader"

  s3bucket_name = module.s3.s3bucket_name
}

module "s3" {
  source = "../publics3"

  name = "${var.prefix_name}-ayed-grading"
}
