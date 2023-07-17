# -*- coding: utf-8 -*-

from boto_session_manager import BotoSesManager
from rich import print as rprint

import aws_ssm_run_command.api as aws_ssm_run_command

bsm = BotoSesManager(profile_name="bmt_app_dev_us_east_1")

instance_id = "i-043cd58afbc720a48"

command_invocation = aws_ssm_run_command.better_boto.send_command_sync(
    ssm_client=bsm.ssm_client,
    instance_id=instance_id,
    commands=[
        "whoami",
        "sudo -H -u ubuntu whoami",
    ],
)
rprint(command_invocation)
