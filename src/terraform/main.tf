resource "aws_ssm_parameter" "foo" {
  name  = "foo"
  type  = "String"
  value = "bar"
}

data "archive_file" "python_lambda_package" {
  type        = "zip"
  source_file = "${path.module}/../lambda/main.py"
  output_path = "lambda_main.zip"
}

resource "aws_lambda_function" "hello_lambda_function" {
  function_name    = "HelloWorld"
  filename         = "lambda_main.zip"
  source_code_hash = data.archive_file.python_lambda_package.output_base64sha256
  role             = aws_iam_role.lambda_role.arn
  runtime          = "python3.9"
  handler          = "main.lambda_handler"
  timeout          = 10
}

resource "aws_cloudwatch_event_rule" "cloudwatch_rule" {
  name        = "cloudwatch-rule-lambda"
  description = "Alarms based on ec2 events"
  event_pattern = jsonencode({
    "detail-type" : ["EC2 Instance Launch/terminate Successful"],
    "source" : ["aws.ec2"],
    detail = {
      state = ["running", "terminating"]
    }
  })
}

resource "aws_cloudwatch_event_target" "ec2_cloudevent_target" {
  rule = aws_cloudwatch_event_rule.cloudwatch_rule.name
  arn  = aws_lambda_function.hello_lambda_function.arn
}
