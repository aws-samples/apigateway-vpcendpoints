#!/usr/bin/env python3
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#

import os

from aws_cdk import core

from global_apigw.global_apigw_stack import GlobalAPIGWStack

env = core.Environment(account=os.environ['AWS_ACCOUNT'], region=os.environ['AWS_REGION'])

app = core.App()
GlobalAPIGWStack(app, "global-apigw", env=env)
app.synth()
