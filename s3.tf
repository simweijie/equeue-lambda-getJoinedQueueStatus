terraform {
  backend "s3" {
    bucket = "nus-iss-equeue-terraform"
    key    = "lambda/getJoinedQueueStatus/tfstate"
    region = "us-east-1"
  }
}
