# -*- coding: utf-8 -*-

import typing as T
import json
import time
import uuid

from ..better_boto.api import (
    CommandInvocationFailedError,
    send_command,
    CommandInvocation,
    wait_until_command_succeeded,
)

if T.TYPE_CHECKING:
    from mypy_boto3_ssm.client import SSMClient
    from mypy_boto3_s3.client import S3Client


def parse_last_line_json_in_output(output: str) -> T.Union[dict, list, T.Any]:
    lines = output.splitlines()
    return json.loads(lines[-1])


def run_python_script(
    ssm_client: "SSMClient",
    s3_client: "S3Client",
    instance_id: str,
    path_aws: str,
    path_python: str,
    code: str,
    s3uri: str,
    args: T.Optional[T.List[str]] = None,
    delays: int = 3,
    timeout: int = 60,
    verbose: bool = True,
) -> CommandInvocation:
    """
    这是我们解决方案的主函数

    :param ssm_client: boto3.client("ssm") object
    :param instance_id: EC2 instance id
    :param path_aws: the path to the AWS cli on EC2
    :param path_python: the path to python interpreter on EC2, it is the one
        you want to use to run your script
    :param code: the source code of your Python script (has to be single file)
    :param s3uri: the S3 location you want to upload this Python script to.
    :param args: the arguments you want to pass to your Python script, if
        the final command is 'python /tmp/xxx.py arg1 arg2', then args should
        be ["arg1", "arg2"]
    """
    # prepare arguments
    if args is None:
        args = []

    # upload your source code to S3
    parts = s3uri.split("/", 3)
    bucket, key = parts[2], parts[3]
    s3_client.put_object(Bucket=bucket, Key=key, Body=code)

    # download your source code to ec2
    path_code = f"/tmp/{uuid.uuid4().hex}.py"
    command1 = f"{path_aws} s3 cp {s3uri} {path_code} 2>&1 > /dev/null"

    # construct the command to run your Python script
    args_ = [
        f"{path_python}",
        f"{path_code}",
    ]
    args_.extend(args)
    command2 = " ".join(args_)
    commands = [
        command1,
        command2
    ]
    # run remote command via SSM
    command_id = send_command(
        ssm_client=ssm_client,
        instance_id=instance_id,
        commands=commands,
    )
    time.sleep(1)  # wait 1 second for the command to be submitted
    try:
        command_invocation = wait_until_command_succeeded(
            ssm_client=ssm_client,
            command_id=command_id,
            instance_id=instance_id,
            delays=delays,
            timeout=timeout,
            verbose=verbose,
        )
    except CommandInvocationFailedError as e:
        command_invocation = CommandInvocation.get(
            ssm_client=ssm_client,
            command_id=command_id,
            instance_id=instance_id,
        )
    return command_invocation
