output "ebs_attachment" {
  value       = aws_volume_attachment.ebs_attachments
  description = "All EBS volume attachmets"
}
