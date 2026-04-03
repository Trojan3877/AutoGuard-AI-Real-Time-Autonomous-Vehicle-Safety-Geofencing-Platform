output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.autoguard.repository_url
}

output "eks_cluster_name" {
  description = "Name of the EKS cluster"
  value       = aws_eks_cluster.autoguard_cluster.name
}

output "eks_cluster_endpoint" {
  description = "Endpoint URL for the EKS API server"
  value       = aws_eks_cluster.autoguard_cluster.endpoint
}

output "eks_cluster_ca_data" {
  description = "Base64-encoded certificate authority data for the EKS cluster"
  value       = aws_eks_cluster.autoguard_cluster.certificate_authority[0].data
  sensitive   = true
}
