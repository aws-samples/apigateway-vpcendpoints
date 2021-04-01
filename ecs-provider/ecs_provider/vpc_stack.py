from aws_cdk import (
    core,
    aws_ec2 as ec2,
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
            nat_gateways=1,
        )
