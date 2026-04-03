variable "aws_region" {
  description = "AWS region to deploy resources into"
  type        = string
  default     = "us-east-1"
}

variable "eks_role_arn" {
  description = "IAM Role ARN that the EKS cluster assumes"
  type        = string
}

variable "eks_subnet_ids" {
  description = "List of VPC subnet IDs for the EKS cluster"
  type        = list(string)
}

variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "autoguard-eks"
}

variable "ecr_repository_name" {
  description = "Name of the ECR repository for AutoGuard images"
  type        = string
  default     = "autoguard-ai"
}

variable "environment" {
  description = "Deployment environment (dev / staging / prod)"
  type        = string
  default     = "prod"
}
