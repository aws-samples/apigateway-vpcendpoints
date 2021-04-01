import pathlib
from typing import List

from aws_cdk import (
    aws_apigatewayv2 as apigw2,
    aws_apigatewayv2_integrations as apigw2_integrations,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_elasticloadbalancingv2_targets as elbv2_targets,
    aws_iam as iam,
    aws_lambda as lambda_,
    core,
)


def setup_vpce_integration(
    stack,
    name: str,
    vpc: ec2.Vpc,
    vpc_endpoint_service_name: str,
    vpc_link: apigw2.VpcLink,
    http_api: apigw2.HttpApi,
    health_check_path: str,
    integration_port: int,
    routes: List[str],
):
    """Create the integration between an HTTP API and VPC Endpoint Service running in another account.

    This manages several things:

    - VPC Endpoint which connects to the service's VPC Endpoint Service
    - Application Load Balancer for that VPC Endpoint, using the VPCE's private IPs
    - HTTP Api Integration to the global API Gateway HTTP API
    - creating HTTP Api routes to the endpoint service

    There is a fair amount of complexity in here, much around the custom resource which will return
    private IPs from the ENIs created in the VPC Endpoint. While it's possible to get the ENIs
    in raw CloudFormation, it's not possible to get the IPs associated with those ENIs without
    making an API call.

    See:

    https://github.com/aws-cloudformation/aws-cloudformation-coverage-roadmap/issues/109

    Note, all of this can easily be ported to a CDK stack by changing the functions to class methods
    and renaming `stack` to `self`.

    """

    vpc_endpoint = _createvpc_endpoint(
        stack, name, vpc, vpc_endpoint_service_name, integration_port
    )

    # The VPC Endpoint creates multiple private IP addresses across the private subnets. These are
    # needed to setup our ALB. To fetch the IPs, we need a custom CFN resource.
    vpc_endpoint_ips = _create_custom_resource(
        stack, name=name, vpce_enis=vpc_endpoint.vpc_endpoint_network_interface_ids
    )
    private_ips = [
        vpc_endpoint_ips.get_att_string("IP0"),
        vpc_endpoint_ips.get_att_string("IP1"),
    ]

    # Now, create the ALB for the VPC Endpoint
    target_group = _create_target_group(
        stack, name, vpc, private_ips, health_check_path, integration_port
    )
    listener = _create_alb(stack, name, vpc, target_group)

    # Create the private HTTP API and integration
    _create_http_api_routes(stack, name, http_api, listener, vpc_link, routes)


def _createvpc_endpoint(
    stack, name: str, vpc: ec2.Vpc, service_name: str, integration_port: int
) -> ec2.InterfaceVpcEndpoint:
    """Create the VPC Endpoint which connects to a VPC Endpoint service.

    Note that the vpc.add_interface_endpoint method is slightly simpler to use, but has created
    circular references between child and the parent stack which owns the VPC.

    """
    sg = ec2.SecurityGroup(stack, f'{name}-vpce-sg', vpc=vpc)
    sg.add_ingress_rule(ec2.Peer.ipv4(vpc.vpc_cidr_block), ec2.Port.tcp(integration_port))

    endpoint_service = ec2.InterfaceVpcEndpointService(service_name)

    return vpc.add_interface_endpoint(
        f'{service_name}-interface-endpoint',
        service=endpoint_service,
        lookup_supported_azs=True,
        security_groups=[sg]
    )


def _create_custom_resource(stack, name: str, **kwargs) -> core.CustomResource:
    parent_dir = pathlib.Path(__file__).parent
    code_dir = str(parent_dir.joinpath('custom_resource'))
    code = lambda_.Code.from_asset(code_dir)

    custom_resource_func = lambda_.SingletonFunction(
        stack,
        f"{name}-CustomResourceFunction",
        uuid='f150930b-586f-4d65-b701-d44cb44057e6',
        code=code,
        handler="handler.main_handler",
        timeout=core.Duration.seconds(15),
        runtime=lambda_.Runtime.PYTHON_3_8,
    )
    custom_resource_func.add_to_role_policy(
        iam.PolicyStatement(
            actions=["ec2:DescribeNetworkInterfaces"],
            effect=iam.Effect.ALLOW,
            resources=['*'],
        )
    )

    return core.CustomResource(
        stack,
        f"{name}-ENIPrivateIPResource",
        service_token=custom_resource_func.function_arn,
        properties=kwargs,
    )


def _create_target_group(
    stack, name: str, vpc: ec2.Vpc, vpc_endpoint_ips: List[str], health_check_path: str,
    integration_port: int
) -> elbv2.ApplicationTargetGroup:
    targets = [elbv2_targets.IpTarget(ip_address=ip) for ip in vpc_endpoint_ips]

    health_check = elbv2.HealthCheck(
        healthy_threshold_count=3,
        interval=core.Duration.seconds(15),
        path=health_check_path,
        timeout=core.Duration.seconds(2),
    )
    return elbv2.ApplicationTargetGroup(
        stack,
        f'{name}-target-group',
        port=integration_port,
        targets=targets,
        deregistration_delay=core.Duration.seconds(10),
        vpc=vpc,
        health_check=health_check,
    )


def _create_alb(
    stack, name: str, vpc: ec2.Vpc, target_group: elbv2.ApplicationTargetGroup
) -> elbv2.ApplicationListener:
    """Create Application Load Balancer for integration to the service's API"""
    sg = ec2.SecurityGroup(stack, f'{name}-http-public-sg', vpc=vpc)
    sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80))

    alb = elbv2.ApplicationLoadBalancer(
        stack,
        f'{name}-service-alb',
        vpc=vpc,
        internet_facing=False,
        vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
        idle_timeout=core.Duration.seconds(10),
        security_group=sg,
    )

    alb_listener = alb.add_listener(
        f'{name}-alb-listener',
        port=80,
        default_action=elbv2.ListenerAction.forward(target_groups=[target_group])
    )

    return alb_listener


def _create_http_api_routes(
    stack, name: str, http_api: apigw2.HttpApi, listener: elbv2.ApplicationListener,
    vpc_link: apigw2.VpcLink, routes: List[str]
):

    integration = apigw2_integrations.HttpAlbIntegration(
        listener=listener,
        method=apigw2.HttpMethod.ANY,
        vpc_link=vpc_link,
    )
    for i, route_key in enumerate(routes):
        route = apigw2.HttpRoute(
            stack,
            f"{name}-route-{i+1}",
            http_api=http_api,
            route_key=apigw2.HttpRouteKey.with_(route_key, apigw2.HttpMethod.ANY),
            integration=integration,
        )
        integration.bind(route=route, scope=stack)
