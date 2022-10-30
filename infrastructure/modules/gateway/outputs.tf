output "rest_api_url" {
  value = "${aws_api_gateway_deployment.sales_pred_deployment.invoke_url}${aws_api_gateway_stage.rest_api_stage.stage_name}${aws_api_gateway_resource.rest_api_predict_resource.path}"
}
