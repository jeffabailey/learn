locals {
  #key_name = "YourKeyName" // Update to the name of your key pair
  security_groups = ["default"] // Update to your security group
}

provider "aws" {
  profile    = "default"
  region     = "us-east-1"
}

resource "aws_instance" "docker_container_runner" {
  // Get the latest Amazon Linux ami id
  // aws ec2 describe-images --region us-east-1 --owners amazon --filters 'Name=name,Values=amzn-ami-hvm-????.??.?.????????-x86_64-gp2' 'Name=state,Values=available' --query 'reverse(sort_by(Images, &CreationDate))[:1].ImageId' --output text
  ami             = "ami-123"
  instance_type   = "t2.micro"
  key_name        = local.key_name
  security_groups = local.security_groups
  user_data       = file("user_data.sh")
}