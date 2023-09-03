variable "configuration" {
  description = "The total configuration, List of Objects/Dictionary"
  type        = list(map(string))
  default     = [{}]
}
