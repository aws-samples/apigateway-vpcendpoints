#!/usr/bin/env python3
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#

import os

from aws_cdk import core

from ec2_provider.vpc_stack import VpcStack
from ec2_provider.todo_app_stack import LoadBalancedTodoAppStack

env = core.Environment(account=os.environ['AWS_ACCOUNT'], region=os.environ['AWS_REGION'])

app = core.App()

vpc_stack = VpcStack(app, "ec2-vpc-stack", env=env)
LoadBalancedTodoAppStack(app, "ec2-provider", vpc=vpc_stack.vpc, env=env)

app.synth()
