# -*- coding: utf-8 -*-

"""
This module allow you to run a Python script on EC2 via SSM run command.
"""

import typing as T
import json
import time
import uuid

from ..better_boto.api import (
    send_command_sync,
    CommandInvocation,
    wait_until_command_succeeded,
)
from ..exc import RunCommandError

if T.TYPE_CHECKING:
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
    return send_command_sync(
        ssm_client=ssm_client,
        instance_id=instance_id,
        commands=commands,
        gap=gap,
        raises=raises,
        delays=delays,
        timeout=timeout,
        verbose=verbose,
    )


def run_python_script_large_payload(
    ssm_client: "SSMClient",
    s3_client: "S3Client",
    instance_id: str,
    path_aws: str,
    path_python: str,
    code: str,
    input_data: str,
    s3uri_script: str,
    s3uri_in: str,
    s3uri_out: str,
    gap: int = 1,
    raises: bool = True,
    delays: int = 3,
    timeout: int = 60,
    verbose: bool = True,
) -> CommandInvocation:
    """
    Run a Python script on EC2 via SSM run command. But this version can handle
    very large input and output data. It will upload the input data to S3, then
    pass the s3uri_in and s3uri_out as a command line arguments to the script.
    And the script will write the output data to s3uri_out. And then you can
    download output data from it.

    .. note::

        Your Python script has to be a CLI script, and take only two arguments
        s3uri_in (str) and s3uri_out (str). Here's an example:

    .. code-block:: python

        # -*- coding: utf-8 -*-

        import json
        import fire
        import boto3

        # The application code logic for this script. Taking any input and return any
        # output.
        def say_hello(name: str) -> str:
            return f"Hello {name}!"


        def run(s3uri_in: str, s3uri_out: str):
            # get input data
            parts = s3uri_in.split("/", 3)
            bucket, key = parts[2], parts[3]

            s3_client = boto3.client("s3")
            res = s3_client.get_object(Bucket=bucket, Key=key)
            name_list = json.loads(res["Body"].read().decode("utf-8"))

            # run core application code logic
            results = [say_hello(name) for name in name_list]

            # write output data
            parts = s3uri_out.split("/", 3)
            bucket, key = parts[2], parts[3]
            s3_client.put_object(Bucket=bucket, Key=key, Body=json.dumps(results))


        if __name__ == "__main__":
            # convert your function into a CLI script
            fire.Fire(run)

    :param ssm_client: boto3.client("ssm") object
    :param s3_client: boto3.client("s3") object
    :param instance_id: EC2 instance id
    :param path_aws: the path to the AWS cli on EC2
    :param path_python: the path to python interpreter on EC2, it is the one
        you want to use to run your script
    :param code: the source code of your Python script (has to be single file)
    :param input_data: the input data in json encoded string you want to pass to your Python script
    :param s3uri_script: the S3 location you want to upload this Python script to.
    :param s3uri_in: the S3 location you want to download the input data from.
    :param s3uri_out: the S3 location you want to upload the output data to.
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
    # upload your source code to S3
    parts = s3uri_script.split("/", 3)
    bucket, key = parts[2], parts[3]
    s3_client.put_object(Bucket=bucket, Key=key, Body=code)

    # upload your input data to S3
    parts = s3uri_in.split("/", 3)
    bucket, key = parts[2], parts[3]
    s3_client.put_object(Bucket=bucket, Key=key, Body=input_data)

    # download your source code to ec2
    path_code = f"/tmp/{uuid.uuid4().hex}.py"
    command1 = f"{path_aws} s3 cp {s3uri_script} {path_code} 2>&1 > /dev/null"

    # construct the command to run your Python script
    args_ = [
        f"{path_python}",
        f"{path_code}",
        "--s3uri_in",
        s3uri_in,
        "--s3uri_out",
        s3uri_out,
    ]
    command2 = " ".join(args_)
    commands = [
        command1,
        command2,
    ]
    return send_command_sync(
        ssm_client=ssm_client,
        instance_id=instance_id,
        commands=commands,
        gap=gap,
        raises=raises,
        delays=delays,
        timeout=timeout,
        verbose=verbose,
    )
