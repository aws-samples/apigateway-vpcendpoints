# Simple Go API running on ECS Fargate

This is a simple read-only REST API authored in [Go](https://golang.org/) running on ECS Fargate.
The actual API is less important than the connection mechansim that it provides as explained in
the [top-level README](../README.md). All of the configuration is made via environment variables.

`API_GATEWAY_ACCOUNT_ARN` is the ARN for the account you will use to deploy the `global-apigw` component. You will need to know this account ID before creating anything.

## Setup

1. Export three environment variables:

   `API_GATEWAY_ACCOUNT_ARN` is the ARN for the account which owns the single API Gateway HTTP API.
   We will call this the "API Gateway Account". This API Gateway will be created _after_ creating both
   this stack and the [EC2 Provider](../ec2-provider) stack.

   ```bash
   $ export API_GATEWAY_ACCOUNT_ARN="arn:aws:iam::111111111111:root"
   $ export AWS_ACCOUNT=222222222222
   $ export AWS_REGION=us-west-2
   ```

2. Create a _new_ ECR repo using the helper script in `bin/` or using the AWS CLI command below.
   Copy the `ARN` of the new reposotory which will take the form `arn:aws:ecr:AWS_REGION:AWS_ACCOUNT_ID:repository/dog-names`

   **NOTE**: Both methods below rely on the [AWS Command Line Interface](https://aws.amazon.com/cli/).
   In addtion to having the AWS CLI installed, you will need to
   [configure it](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html) with the correct
   AWS Account and Region. In this example, we would configure the AWS CLI to use Account ID `222222222222`
   with the `us-west-2` region.

   ```bash
   $ # Create the ECR repo using the AWS CLI
   $ aws ecr create-repository --repository-name dog-names
   ```

   _or_

   ```bash
   $ cd bin
   $ ./create-ecr-repo.sh

   {
       "repository": {
           "repositoryArn": "arn:aws:ecr:AWS_REGION:222222222222:repository/dog-names",
           "repositoryUri": "462233287333.dkr.ecr.us-west-2.amazonaws.com/dog-names",
           ...
       }
   }
   ```

3. Build your Docker image and push it to ECR. Use the helpers in the `Makefile` from the root of
   this repository. If you don't have `make` installed, you can copy the command and run them in
   your shell manually.

```bash
$ make image
$ make login
$ make push
```

4. Deploy the stacks:

   ```bash
   $ make deploy
   ```

   Once deployed, there will be two stacks: 1) VPC Stack and 2) ECS API stack. You will be able to see
   the running containers by navigating to ECS and clicking into the service which was created. Note
   there is also a Network Load Balancer created and VPC Endpoint Service.

   Remember that the ECS Taks run in private subnets and the only way to get network access
   is to be inside the VPC. Without a bastion host, you will access this Todo API via the global API Gateway endpoint
   created from the [Global API Gateway](../global-apigw) application.
