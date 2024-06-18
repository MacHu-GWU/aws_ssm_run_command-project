# -*- coding: utf-8 -*-

"""
This module improves the original boto3 SSM client and makes it more pythonic.
"""

import typing as T
import math
import sys
import enum
import time
import dataclasses
from datetime import datetime

from func_args import resolve_kwargs, NOTHING
from ..vendor.waiter import Waiter
from ..exc import RunCommandError
from .response import Command, CommandInvocationStatusEnum, CommandInvocation
from .waiters import wait_until_send_command_succeeded

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_ssm.client import SSMClient
    from mypy_boto3_ssm.type_defs import (
        TargetTypeDef,
        NotificationConfigTypeDef,
        CloudWatchOutputConfigTypeDef,
        AlarmConfigurationTypeDef,
    )


def run_shell_script(
    ssm_client: "SSMClient",
    commands: T.Union[str, T.List[str]],
    instance_ids: T.Union[str, T.List[str]] = NOTHING,
    targets: T.Sequence["TargetTypeDef"] = NOTHING,
    timeout_seconds: int = NOTHING,
    comment: str = NOTHING,
    output_s3_bucket_name: str = NOTHING,
    output_s3_key_prefix: str = NOTHING,
    max_concurrency: str = NOTHING,
    max_errors: str = NOTHING,
    service_role_arn: str = NOTHING,
    notification_config: "NotificationConfigTypeDef" = NOTHING,
    cloudwatch_output_config: "CloudWatchOutputConfigTypeDef" = NOTHING,
    alarm_configuration: "AlarmConfigurationTypeDef" = NOTHING,
) -> Command:
    """
    :param ssm_client: ``boto3.client("ssm")`` object
    :param commands: the shell script command to run. If you want to run multiple
        commands, you can pass a list of commands.
    :param instance_ids: the EC2 instance where you want to send command. You can
        pass a single instance id or a list of instance ids.
    :param targets: see ``send_command`` API reference.
    :param timeout_seconds: see ``send_command`` API reference.
    :param comment: see ``send_command`` API reference.
    :param output_s3_bucket_name: see ``send_command`` API reference.
    :param output_s3_key_prefix: see ``send_command`` API reference.
    :param max_concurrency: see ``send_command`` API reference.
    :param max_errors: see ``send_command`` API reference.
    :param service_role_arn: see ``send_command`` API reference.
    :param notification_config: see ``send_command`` API reference.
    :param cloudwatch_output_config: see ``send_command`` API reference.
    :param alarm_configuration: see ``send_command`` API reference.

    Reference:

    - `send_command <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm/client/send_command.html>`_
    - `aws:runShellScript document schema <https://docs.aws.amazon.com/systems-manager/latest/userguide/documents-command-ssm-plugin-reference.html#aws-runShellScript>`_

    """
    if isinstance(commands, str):
        commands = [commands]
    if instance_ids is not NOTHING:
        if isinstance(instance_ids, str):
            instance_ids = [instance_ids]
    kwargs = resolve_kwargs(
        InstanceIds=instance_ids,
        Targets=targets,
        Parameters={"commands": commands},
        DocumentName="AWS-RunShellScript",
        DocumentVersion="1",
        TimeoutSeconds=timeout_seconds,
        Comment=comment,
        OutputS3BucketName=output_s3_bucket_name,
        OutputS3KeyPrefix=output_s3_key_prefix,
        MaxConcurrency=max_concurrency,
        MaxErrors=max_errors,
        ServiceRoleArn=service_role_arn,
        NotificationConfig=notification_config,
        CloudWatchOutputConfig=cloudwatch_output_config,
        AlarmConfiguration=alarm_configuration,
    )
    response = ssm_client.send_command(**kwargs)
    command = Command.from_send_command_response(response=response)
    return command


run_shell_script_async = run_shell_script


def run_shell_script_sync(
    ssm_client: "SSMClient",
    commands: T.Union[str, T.List[str]],
    instance_ids: T.Union[str, T.List[str]] = NOTHING,
    targets: T.Sequence["TargetTypeDef"] = NOTHING,
    timeout_seconds: int = NOTHING,
    comment: str = NOTHING,
    output_s3_bucket_name: str = NOTHING,
    output_s3_key_prefix: str = NOTHING,
    max_concurrency: str = NOTHING,
    max_errors: str = NOTHING,
    service_role_arn: str = NOTHING,
    notification_config: "NotificationConfigTypeDef" = NOTHING,
    cloudwatch_output_config: "CloudWatchOutputConfigTypeDef" = NOTHING,
    alarm_configuration: "AlarmConfigurationTypeDef" = NOTHING,
    allow_fails_config: T.Union[int, float, T.Union[str, T.List[str]]] = 0,
    gap: int = 1,
    raises: bool = True,
    delays: int = 3,
    timeout: int = 60,
    verbose: bool = True,
) -> T.List[CommandInvocation]:
    """
    Send command and wait until it succeeds. The original
    `send_command <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm/client/send_command.html>`_
    is asynchronous, this function is synchronous.

    See :func:`send_command` and :func:`wait_until_command_succeeded` for input
    arguments detail.

    :param ssm_client: ``boto3.client("ssm")`` object
    :param commands: the shell script command to run. If you want to run multiple
        commands, you can pass a list of commands.
    :param instance_ids: the EC2 instance where you want to send command. You can
        pass a single instance id or a list of instance ids.
    :param targets: see ``send_command`` API reference.
    :param timeout_seconds: see ``send_command`` API reference.
    :param comment: see ``send_command`` API reference.
    :param output_s3_bucket_name: see ``send_command`` API reference.
    :param output_s3_key_prefix: see ``send_command`` API reference.
    :param max_concurrency: see ``send_command`` API reference.
    :param max_errors: see ``send_command`` API reference.
    :param service_role_arn: see ``send_command`` API reference.
    :param notification_config: see ``send_command`` API reference.
    :param cloudwatch_output_config: see ``send_command`` API reference.
    :param alarm_configuration: see ``send_command`` API reference.
    :param allow_fails_config: how do you want to handle the failed command?
        if it is 0, then raise exception when any of the instance failed.
        if it is an integer equal to 1 or greater than 1, then allow that many
        instance to fail.
        if it is a float between 0 and 1 (cannot be 0.0 or 1.0), then allow that
        percentage of instance to fail.
        if it is a str or list of str, then allow the provided instance id to fail.
        To allow all instances to fail, you can pass the value of ``instance_ids``
         to it.
    :param gap: the gap between each ``send_command`` api and the first
        ``get_command_invocation`` api call. Because it takes some time to have
        the command invocation fired to SSM agent.
    :param raises: if True, raises exception when the command invocation failed.
    :param delays: how many seconds to wait between each ``get_command_invocation``
    :param timeout: how many seconds to wait until the command invocation is succeeded.
    :param verbose: do you want to print the waiting message?
    """
    command = run_shell_script(
        ssm_client=ssm_client,
        commands=commands,
        instance_ids=instance_ids,
        targets=targets,
        timeout_seconds=timeout_seconds,
        comment=comment,
        output_s3_bucket_name=output_s3_bucket_name,
        output_s3_key_prefix=output_s3_key_prefix,
        max_concurrency=max_concurrency,
        max_errors=max_errors,
        service_role_arn=service_role_arn,
        notification_config=notification_config,
        cloudwatch_output_config=cloudwatch_output_config,
        alarm_configuration=alarm_configuration,
    )
    time.sleep(gap)

    is_counter_mode = False
    is_instance_id_mode = False
    max_allow_fails = None
    allow_fail_instance_ids = set()

    if isinstance(allow_fails_config, int):
        max_allow_fails = allow_fails_config
        is_counter_mode = True
    elif isinstance(allow_fails_config, float):
        if allow_fails_config <= 0 or allow_fails_config >= 1:
            raise ValueError("allow_fails_config should be between 0 and 1")
        max_allow_fails = math.floor(len(instance_ids) * allow_fails_config)
        is_counter_mode = True
    elif isinstance(allow_fails_config, str):
        allow_fail_instance_ids = {allow_fails_config}
    else:
        allow_fail_instance_ids = set(allow_fails_config)

    command_invocations = []

    if is_counter_mode:
        failed_counter = 0
        for instance_id in command.InstanceIds:
            try:
                command_invocation = wait_until_send_command_succeeded(
                    ssm_client=ssm_client,
                    command_id=command.CommandId,
                    instance_id=instance_id,
                    raises=raises,
                    delays=delays,
                    timeout=timeout,
                    verbose=verbose,
                )
                command_invocations.append(command_invocation)
            except RunCommandError as e:
                failed_counter += 1
                if failed_counter > max_allow_fails:
                    raise e
                else:
                    command_invocation = CommandInvocation.get(
                        ssm_client=ssm_client,
                        command_id=command.CommandId,
                        instance_id=instance_id,
                    )
                    command_invocations.append(command_invocation)
        return command_invocations

    if is_instance_id_mode:
        for instance_id in command.InstanceIds:
            try:
                command_invocation = wait_until_send_command_succeeded(
                    ssm_client=ssm_client,
                    command_id=command.CommandId,
                    instance_id=instance_id,
                    raises=raises,
                    delays=delays,
                    timeout=timeout,
                    verbose=verbose,
                )
                command_invocations.append(command_invocation)
            except RunCommandError as e:
                if instance_id not in allow_fail_instance_ids:
                    raise e
        return command_invocations
