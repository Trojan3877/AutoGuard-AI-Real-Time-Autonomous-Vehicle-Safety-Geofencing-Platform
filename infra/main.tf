provider "aws" {
  region = "us-east-1"
}

resource "aws_ecr_repository" "autoguard" {
  name = "autoguard-ai"
}

resource "aws_eks_cluster" "autoguard_cluster" {
  name     = "autoguard-eks"
  role_arn = "arn:aws:iam::123456789012:role/EKSRole"

  vpc_config {
    subnet_ids = ["subnet-abc123"]
  }
}
