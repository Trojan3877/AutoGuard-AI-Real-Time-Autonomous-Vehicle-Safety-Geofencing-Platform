provider "aws" {
  region = var.aws_region
}

resource "aws_ecr_repository" "autoguard" {
  name                 = var.ecr_repository_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = var.environment
    Project     = "autoguard-ai"
  }
}

resource "aws_eks_cluster" "autoguard_cluster" {
  name     = var.cluster_name
  role_arn = var.eks_role_arn

  vpc_config {
    subnet_ids = var.eks_subnet_ids
  }

  tags = {
    Environment = var.environment
    Project     = "autoguard-ai"
  }
}
