# -*- coding: utf-8 -*-

from pathlib import Path
from boto_session_manager import BotoSesManager
from aws_ssm_run_command.patterns.run_command_on_one_ec2 import (
    parse_last_line_json_in_output,
    run_python_script,
)
from rich import print as rprint

bsm = BotoSesManager(profile_name="bmt_app_dev_us_east_1")

instance_id = "i-043cd58afbc720a48"
path_aws = "/home/ubuntu/.pyenv/shims/aws"
path_python = "/home/ubuntu/.pyenv/shims/python"
code = Path(__file__).absolute().parent.joinpath("script.py").read_text()
s3uri = f"s3://{bsm.aws_account_id}-{bsm.aws_region}-data/projects/aws_ssm_run_command/patterns/run_command_on_one_ec2/script.py"
args = []

command_invocation = run_python_script(
    ssm_client=bsm.ssm_client,
    s3_client=bsm.s3_client,
    instance_id=instance_id,
    path_aws=path_aws,
    path_python=path_python,
    code=code,
    s3uri=s3uri,
    args=args,
)

rprint(command_invocation)
if command_invocation.ResponseCode == 0:
    output_data = parse_last_line_json_in_output(
        command_invocation.StandardOutputContent
    )
    rprint(output_data)
    weird_string = "\\a\nb\tc\"d'e@f#g:h/i"
    assert output_data["weird_string"] == weird_string
