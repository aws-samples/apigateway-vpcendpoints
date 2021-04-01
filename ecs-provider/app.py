#!/usr/bin/env python3
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#

from aws_cdk import core

from ecs_provider.vpc_stack import VpcStack
from ecs_provider.ecs_provider_stack import EcsProviderStack

app = core.App()

vpc_stack = VpcStack(app, 'ecs-vpc-stack')
EcsProviderStack(app, "ecs-provider", vpc=vpc_stack.vpc)

app.synth()
