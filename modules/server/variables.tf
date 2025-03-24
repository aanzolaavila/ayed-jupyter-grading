variable "nameprefix" {
  type = string
  validation {
    condition = length(var.nameprefix) > 0
    error_message = "nameprefix must be non empty"
  }
}
