# -*- coding: utf-8 -*-

"""
This module allow you to run a Python script on EC2 via SSM run command.
"""

import typing as T
import json
import uuid

from ..better_boto.api import (
    CommandInvocation,
    run_shell_script_sync,
)

if T.TYPE_CHECKING: # pragma: no cover
    from mypy_boto3_ssm.client import SSMClient
    from mypy_boto3_s3.client import S3Client


def parse_last_line_json_in_output(output: str) -> T.Union[dict, list, T.Any]:
    """
    Parse the last line of the Command invocation output as JSON.

    Example::

        >>> output = (
        ...     '{"id": 1}\\n'
        ...     '{"id": 2}\\n'
        ...     '{"id": 3}\\n'
        ... )
        >>> parse_last_line_json_in_output(output)
        {'id': 3}
    """
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
    gap: int = 1,
    raises: bool = True,
    delays: int = 3,
    timeout: int = 60,
    verbose: bool = True,
) -> CommandInvocation:
    """
    Run a Python script on EC2 via SSM run command. It will upload your
    Python script to S3, then download it to EC2, and finally run it. You can
    let the Python script to print data to stdout, and this function will
    capture the return code and stdout in the :class:`CommandInvocation` object.
    Note that the return output data cannot exceed 24000 characters.

    Prerequisites:

    - your EC2 has aws cli installed, and it has S3 read permission.
    - your EC2 has python installed, and it has the necessary packages to run
        your Python script.

    :param ssm_client: boto3.client("ssm") object
    :param s3_client: boto3.client("s3") object
    :param instance_id: EC2 instance id
    :param path_aws: the path to the AWS cli on EC2
    :param path_python: the path to python interpreter on EC2, it is the one
        you want to use to run your script
    :param code: the source code of your Python script (has to be single file)
    :param s3uri: the S3 location you want to upload this Python script to.
    :param args: the arguments you want to pass to your Python script, if
        the final command is 'python /tmp/xxx.py arg1 arg2', then args should
        be ["arg1", "arg2"]
    :param gap: the gap between each ``send_command`` api and the first
        ``get_command_invocation`` api call. Because it takes some time to have
        the command invocation fired to SSM agent.
    :param raises: if True, then raises error if command failed,
        otherwise, just return the :class:`CommandInvocation` represents the failed
        invocation.
    :param delays: time interval in seconds to check the status of the command
    :param timeout: the maximum time in seconds to wait for the command to finish
    :param verbose: whether to print out the status of the command
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
    # we don't want the aws s3 cp command to print out anything
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
        command2,
    ]
    return run_shell_script_sync(
        ssm_client=ssm_client,
        commands=commands,
        instance_ids=instance_id,
        gap=gap,
        raises=raises,
        delays=delays,
        timeout=timeout,
        verbose=verbose,
    )[0]
