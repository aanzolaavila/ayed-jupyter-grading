resource "aws_lambda_function" "server" {
  function_name = "${var.nameprefix}"
  role = aws_iam_role.for_lambda.name
}

resource "aws_iam_role" "for_lambda" {
  name = "${var.nameprefix}_lambda-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}
