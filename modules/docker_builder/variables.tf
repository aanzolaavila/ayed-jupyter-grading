variable "working_directory" {
  type        = string
  description = "working directory where Dockerfile is located"
  validation {
    condition     = provider::local::direxists(pathexpand(var.working_directory))
    error_message = "working directory must exist"
  }
}

variable "output_location" {
  type        = string
  description = "location of files in the container to copy"
}

variable "docker_arguments" {
  type        = map(string)
  description = "arguments to pass for build process"
  default     = {}
}

variable "name" {
  type = string
}
