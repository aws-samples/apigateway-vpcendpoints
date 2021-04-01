from aws_cdk import (
    aws_ec2 as ec2,
    core,
)


class VpcStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.vpc = self._create_vpc()
        core.CfnOutput(self, "VpcId", value=self.vpc.vpc_id)

    def _create_vpc(self) -> ec2.Vpc:
        return ec2.Vpc(
            self,
            "VPC",
            max_azs=2,
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
