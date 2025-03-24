variable "prefix_name" {
  type = string
  validation {
    condition     = length(var.prefix_name) > 0
    error_message = "nameprefix must be non empty"
  }
}
