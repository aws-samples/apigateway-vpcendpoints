from aws_cdk import (
    aws_apigatewayv2 as http_api,
    aws_ec2 as ec2,
    core,
)

from apigw_vpce_helpers import helpers, vpce_helpers


class GlobalAPIGWStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = self._create_vpc()

        global_http_api = http_api.HttpApi(self, 'global-api', api_name='global-http-api')
        core.CfnOutput(self, "HttpApiEndpoint", value=global_http_api.url)

        vpc_link = http_api.VpcLink(self, 'http-api-vpc-link', vpc=vpc)

        dogname_vpce_service_name = helpers.get_env('DOGNAME_SERVICE_NAME')
        vpce_helpers.setup_vpce_integration(
            self,
            name="dog-svc",
            vpc=vpc,
            vpc_endpoint_service_name=dogname_vpce_service_name,
            vpc_link=vpc_link,
            http_api=global_http_api,
            health_check_path="/dogs",
            integration_port=8080,
            routes=["/dogs/females", "/dogs/males", "/dogs"],
        )

        todo_vpce_service_name = helpers.get_env('TODO_SERVICE_NAME')
        vpce_helpers.setup_vpce_integration(
            self,
            name="todo-svc",
            vpc=vpc,
            vpc_endpoint_service_name=todo_vpce_service_name,
            vpc_link=vpc_link,
            http_api=global_http_api,
            health_check_path="/todo",
            integration_port=8080,
            routes=["/todo", "/todo/{todoId}"],
        )

    def _create_vpc(self) -> ec2.Vpc:
        return ec2.Vpc(
            self,
            "VPC",
            max_azs=4,
            cidr="10.0.0.0/16",
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PUBLIC,
                    name="Public",
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PRIVATE,
                    name="Private",
                    cidr_mask=24,
                ),
            ],
            nat_gateways=1,
        )
