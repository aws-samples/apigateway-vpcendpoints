# Simple Flask API with Flask on EC2

This is a simple REST API authored in Python with Flask. The actual API is less important than the
connection mechansim that it provides. The aim of this is to demonstrate how to access this API
using a VPC Endpoint from another AWS Account.

## Setting up

1. Export three environment variables:

   `API_GATEWAY_ACCOUNT_ARN` is the ARN for the account which owns the single API Gateway HTTP API. We will call
   this the "API Gateway Account". That API Gateway will be created later using a different repo/CDK code. Note that this stack must be created first.

   ```bash
   $ export API_GATEWAY_ACCOUNT_ARN="arn:aws:iam::111111111111:root"
   $ export AWS_ACCOUNT=333333333333
   $ export AWS_REGION=us-west-2
   ```

2. Deploy the two stacks. This can be done via the `Makefile` with `make deploy`, or manually with
   `cdk deploy --all`.

   Make note of the outputs from the `todo-stack`. You will need this value when setting up the
   Global API Gateway stack:

   `ec2-provider.ec2vpcendpointservicename = com.amazonaws.vpce.us-west-2.vpce-svc-xxxxxxxxxxxxxxxxx`

3. Once deployed, there will be two stacks: 1) VPC Stack and 2) Todo API stack.
   Remember that the EC2 instances live in private subnets and the only way to get network access
   is to be inside the VPC. You should see that `2 of 2` instances
   are in service when looking at the Network Load Balancer in the AWS console. You can optionally
   create a bastion host within the VPC and make `http` requests to the network load balancer.

   Without a bastion host, you will access this Todo API via the global API Gateway endpoint
   created from the [Global API Gateway](../global-apigw) application.

   ```bash
   $ # assuming you have a bastion host
   $ ssh -i your-key-pair.pem ec2-user@ec2-xx-xx-xx-xx.us-west-2.compute.amazonaws.com
   >
   > # fetch all of the items
   > curl http://nlb-xxxxxxxxxxxxxxxx.elb.us-west-2.amazonaws.com:8080
   >
   > # create new todos
   > curl -d data=one http://nlb-xxxxxxxxxxxxxxxx.elb.us-west-2.amazonaws.com:8080
   > curl -d data=two http://nlb-xxxxxxxxxxxxxxxx.elb.us-west-2.amazonaws.com:8080
   > curl -d data=three http://nlb-xxxxxxxxxxxxxxxx.elb.us-west-2.amazonaws.com:8080
   >
   > # fetch them again
   > curl http://nlb-xxxxxxxxxxxxxxxx.elb.us-west-2.amazonaws.com:8080
   >
   > # fetch a single item
   > curl http://nlb-xxxxxxxxxxxxxxxx.elb.us-west-2.amazonaws.com:8080/ab234df
   >
   ```
