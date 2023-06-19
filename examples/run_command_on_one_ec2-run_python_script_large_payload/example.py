# -*- coding: utf-8 -*-

import json
from pathlib import Path
from s3pathlib import S3Path, context
from boto_session_manager import BotoSesManager
from aws_ssm_run_command.patterns.run_command_on_one_ec2 import (
    run_python_script_large_payload,
)

bsm = BotoSesManager(profile_name="bmt_app_dev_us_east_1")
context.attach_boto_session(bsm.boto_ses)

instance_id = "i-00f591fc972902fc5"
path_aws = "/home/ubuntu/.pyenv/shims/aws"
path_python = "/home/ubuntu/.pyenv/shims/python"
code = Path(__file__).absolute().parent.joinpath("script.py").read_text()

input_data = json.dumps([f"alice{i}" for i in range(1000)])
s3uri_script = f"s3://{bsm.aws_account_id}-{bsm.aws_region}-data/projects/aws_ssm_run_command/patterns/run_command_on_one_ec2/script.py"
s3uri_in = f"s3://{bsm.aws_account_id}-{bsm.aws_region}-data/projects/aws_ssm_run_command/patterns/run_command_on_one_ec2/input.json"
s3uri_out = f"s3://{bsm.aws_account_id}-{bsm.aws_region}-data/projects/aws_ssm_run_command/patterns/run_command_on_one_ec2/output.json"

command_invocation = run_python_script_large_payload(
    ssm_client=bsm.ssm_client,
    s3_client=bsm.s3_client,
    instance_id=instance_id,
    path_aws=path_aws,
    path_python=path_python,
    code=code,
    input_data=input_data,
    s3uri_script=s3uri_script,
    s3uri_in=s3uri_in,
    s3uri_out=s3uri_out,
)
assert command_invocation.ResponseCode == 0

output_data = json.loads(S3Path(s3uri_out).read_text())
assert len(output_data) == 1000
