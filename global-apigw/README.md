# Global API Gateway with Private Integrations

This CDK application sets up a central API Gateway with integrations to multiple APIs
in different accounts using VPC Endpoints. All of the network traffic from the central
HTTP ApiGateway is private, using PrivateLink via the VPC Endpoints and VPC Endpoint Services
which are created in the providing accounts.

## Setting up

<div style="color:red">
  <strong>NOTE: </strong>The providing API stacks must be setup <strong>before</strong> this stack is created.
</div>

1. Deploy the backend providing APIs

   - [ EC2 Provider ](../ec2-provider) stack, which exposes a simple Todo API using EC2.
   - [ ECS Provider ](../ecs-provider) stack, which exposes a simple read-only API using ECS Fargate.

2. Export four different environment variables:

   - Your AWS account id
   - Your AWS region
   - The service name of the VPC Endpoint Service created in the `EC2 Provider` stack.
     This is emitted from that stack after doing `cdk deploy`.

     `ec2-provider.ec2vpcendpointservicename = com.amazonaws.vpce.us-west-2.vpce-svc-xxxxxxxxxxxxxxxxx`

   - The service name of the VPC Endpoint Service created in the `ECS Provider` stack.
     This is emitted from that stack after doing `cdk deploy`.

     `ecs-provider.ecsvpcendpointservicename = com.amazonaws.vpce.us-west-2.vpce-svc-xxxxxxxxxxxxxxxxx`

   ```bash
   $ export AWS_ACCOUNT=111111111111
   $ export AWS_REGION=us-west-2
   $ export TODO_SERVICE_NAME=com.amazonaws.vpce.us-west-2.vpce-svc-xxxxxxxxxxxxxxxxx
   $ export DOGNAME_SERVICE_NAME=com.amazonaws.vpce.us-west-2.vpce-svc-xxxxxxxxxxxxxxxxx
   ```

3. Deploy the stacks using the `Makefile` which is much simplier:

   ```bash
   $ make deploy
   ```

   Take note of the URL output from the `global-apigw` stack. This is the URL which
   will be used to access all of the providing APIs

   `global-apigw.HttpApiEndpoint = https://xxxxxxxxxx.execute-api.us-west-2.amazonaws.com/`

## Testing

Once deployed, this creates `global-apigw` stack. You can test it using the below commands:

```bash
$ # Test out the todo stack
$ curl https://xxxxxxxxxx.execute-api.us-west-2.amazonaws.com/todo
$ curl -d data="new data"  https://xxxxxxxxxx.execute-api.us-west-2.amazonaws.com/todo
$ curl https://xxxxxxxxxx.execute-api.us-west-2.amazonaws.com/todo
$
$ # Test the dog name stack
$ curl https://xxxxxxxxxx.execute-api.us-west-2.amazonaws.com/dogs
$ curl https://xxxxxxxxxx.execute-api.us-west-2.amazonaws.com/dogs/males
$ curl https://xxxxxxxxxx.execute-api.us-west-2.amazonaws.com/dogs/females
```
