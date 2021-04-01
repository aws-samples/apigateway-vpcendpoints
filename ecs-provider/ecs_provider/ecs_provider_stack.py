import os

from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_elasticloadbalancingv2 as elb,
    aws_iam as iam,
    core,
)

from apigw_vpce_helpers.helpers import get_env

# The port on which the container application listens
CONTAINER_PORT = 8080


class EcsProviderStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self._vpc = vpc

        # Environment variables which are required to run this. Using the included Makefile
        # makes this simple but this is easy to adjust.
        apigw_account_arn = get_env("API_GATEWAY_ACCOUNT_ARN")
        image_tag = get_env("IMAGE_TAG")
        repository_arn = f'arn:aws:ecr:{get_env("AWS_REGION")}:{get_env("AWS_ACCOUNT")}:repository/dog-names'

        cluster = self._create_cluster()
        nlb = self._create_fargate_service(cluster, repository_arn, image_tag)

        vpce_service = self._create_vpce_service(apigw_account_arn, nlb)
        core.CfnOutput(
            self,
            'ecs-vpc-endpoint-service-name',
            export_name='VPCEndpointServiceName',
            value=vpce_service.vpc_endpoint_service_name
        )

    def _create_cluster(self) -> ecs.Cluster:
        return ecs.Cluster(self, "ecs-cluser", vpc=self._vpc)

    def _create_fargate_service(
        self, cluster: ecs.Cluster, repository_arn: str, image_tag: str
    ) -> elb.NetworkLoadBalancer:
        ecr_repo = ecr.Repository.from_repository_arn(
            self, 'dog-name-repo', repository_arn=repository_arn
        )

        options = ecs_patterns.NetworkLoadBalancedTaskImageOptions(
            image=ecs.ContainerImage.from_ecr_repository(ecr_repo, tag=image_tag),
            container_port=CONTAINER_PORT,
            enable_logging=True,
            container_name="dog-names",
        )

        # Create a **private** NLB-backed Fargate service
        fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
            self,
            "dog-names",
            cluster=cluster,
            listener_port=CONTAINER_PORT,
            public_load_balancer=False,
            task_image_options=options,
            cpu=512,
            memory_limit_mib=1024,
            desired_count=1,
        )

        # Use CDK escape hatch to set the target group deregistration delay low. This makes
        # deploying new containers much faster as the default is 300 seconds.
        #
        # See:
        #
        #   https://docs.aws.amazon.com/cdk/latest/guide/cfn_layer.html
        #
        cfn_target_group = fargate_service.target_group.node.default_child
        cfn_target_group.add_override(
            "Properties.TargetGroupAttributes",
            [{
                "Key": "deregistration_delay.timeout_seconds",
                "Value": "10"
            }],
        )

        # Allow inbound connections to port 8080 from the entire VPC
        fargate_service.service.connections.allow_from(
            ec2.Peer.ipv4(self._vpc.vpc_cidr_block),
            ec2.Port(
                protocol=ec2.Protocol.TCP,
                string_representation="Allow inbound 8080 from VPC CIDR block",
                from_port=CONTAINER_PORT,
                to_port=CONTAINER_PORT,
            )
        )

        return fargate_service.load_balancer

    def _create_vpce_service(self, allow_arn: str, load_balancer: elb.NetworkLoadBalancer) -> None:
        """Create the VPC Endpoint Service, which will allow the root account to create a VPC
        Endpoint.

        Note that this is setup so that the acceptence on the root (APIGW) account is not required.
        Once the VPC Endpoint is created in the integration account, it's ready to use.
        """
        return ec2.VpcEndpointService(
            self,
            "vpc-endpoint-service",
            vpc_endpoint_service_load_balancers=[load_balancer],
            acceptance_required=False,
            whitelisted_principals=[iam.ArnPrincipal(allow_arn)],
        )
