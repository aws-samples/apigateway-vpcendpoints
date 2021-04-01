#!/usr/bin/env python3
import os

from aws_cdk import (
    aws_autoscaling as autoscaling,
    aws_dynamodb as dynamodb,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elb,
    aws_iam as iam,
    core,
)

from apigw_vpce_helpers import helpers

# The port on which the Flask application listens
PORT = 8080

with open('user-data.sh', 'r') as fh:
    aws_region = helpers.get_env("AWS_REGION")
    USER_DATA = fh.read().replace("__AWS_DEFAULT_REGION_PLACEHOLDER__", aws_region)


class LoadBalancedTodoAppStack(core.Stack):

    def __init__(self, app: core.App, id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(app, id, **kwargs)

        self._vpc = vpc

        ddb_table = self._create_dynamodb_table()

        asg = self._create_autoscaling_group(ddb_table)

        nlb = self._create_load_balancer()
        core.CfnOutput(
            self, "load-balancer", export_name="LoadBalancer", value=nlb.load_balancer_dns_name
        )

        self._add_nlb_listener(nlb, asg)

        apigw_account_arn = helpers.get_env("API_GATEWAY_ACCOUNT_ARN")
        vpce_service = self._create_vpce_service(apigw_account_arn, nlb)

        core.CfnOutput(
            self,
            'ec2-vpc-endpoint-service-name',
            export_name='VPCEndpointServiceName',
            value=vpce_service.vpc_endpoint_service_name
        )

    def _create_dynamodb_table(self) -> dynamodb.Table:
        """Create a DynamoDB table for use with the Todo application.

        Note, there is a tight coupling between the table_name and partition_key and the applicaiton
        code which lives in the `user-data.sh` file. Do not change the table_name or partition_key
        without also updating the application code. As this is merely an example, it's best to
        leave this configuration as-is.

        """
        table = dynamodb.Table(
            self,
            "todo-table",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            table_name='TodoTable',
            removal_policy=core.RemovalPolicy.DESTROY,
        )
        return table

    def _create_autoscaling_group(self, ddb_table: dynamodb.Table) -> autoscaling.AutoScalingGroup:
        """Creates an Autoscaling group for the Todo application"""
        role = iam.Role(
            self,
            'todo-instance-role',
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
        )
        role.add_to_policy(
            iam.PolicyStatement(
                resources=[ddb_table.table_arn],
                actions=[
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:Scan",
                ]
            )
        )

        return autoscaling.AutoScalingGroup(
            self,
            "todo-asg",
            vpc=self._vpc,
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
            machine_image=self._get_image(),
            user_data=self._get_user_data(),
            security_group=self._create_sg(),
            role=role,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
            desired_capacity=2,
        )

    def _create_load_balancer(self) -> elb.NetworkLoadBalancer:
        return elb.NetworkLoadBalancer(self, "todo-nlb", vpc=self._vpc, internet_facing=False)

    def _add_nlb_listener(
        self, nlb: elb.NetworkLoadBalancer, asg: autoscaling.AutoScalingGroup
    ) -> elb.NetworkTargetGroup:
        listener = nlb.add_listener(f"port-{PORT}-listener", port=PORT)
        target_group = listener.add_targets("target", port=PORT, targets=[asg])
        return target_group

    def _get_image(self):
        """Lookup the latest Amazon Linux AMI, which is owned by Amazon."""
        ami_name = 'amzn2-ami-hvm-2.0.20210126.0-x86_64-gp2'
        return ec2.MachineImage.lookup(
            name=ami_name,
            owners=['137112412989'],
            filters={
                'virtualization-type': ['hvm'],
                'architecture': ['x86_64']
            }
        )

    def _get_user_data(self) -> ec2.UserData:
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(USER_DATA)
        return user_data

    def _create_sg(self) -> ec2.SecurityGroup:
        """Create a security group for the Todo EC2 instances"""
        sg = ec2.SecurityGroup(self, 'vpc-inbound-sg', vpc=self._vpc)

        sg.add_ingress_rule(
            ec2.Peer.ipv4(self._vpc.vpc_cidr_block),
            ec2.Port(
                protocol=ec2.Protocol.TCP,
                string_representation="Allow inbound 8080 from VPC CIDR block",
                from_port=PORT,
                to_port=PORT,
            )
        )

        return sg

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
