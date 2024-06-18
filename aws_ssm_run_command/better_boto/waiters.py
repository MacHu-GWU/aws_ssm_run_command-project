# -*- coding: utf-8 -*-

"""
Waiter utilities.
"""

import typing as T
import sys

from ..vendor.waiter import Waiter
from ..exc import RunCommandError
from .response import CommandInvocationStatusEnum, CommandInvocation

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_ssm.client import SSMClient


def wait_until_send_command_succeeded(
    ssm_client: "SSMClient",
    command_id: str,
    instance_id: str,
    raises: bool = True,
    delays: int = 3,
    timeout: int = 60,
    verbose: bool = True,
) -> CommandInvocation:
    """
    After you call send_command_ API, you can use this function to wait until
    it succeeds. If it fails, it will raise an exception.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm/client/get_command_invocation.html

    :param ssm_client:
    :param command_id: the SSM run command "command_id", it is from the
        ssm_client.send_command(...) response
    :param instance_id: ec2 instance id
    :param raises: if True, then raises error if command failed,
        otherwise, just return the :class:`CommandInvocation` represents the failed
        invocation.
    :param delays: check the command invocation status every ``delays`` seconds
    :param timeout: how long we consider this command is timed out
    :param verbose: whether to print the progress

    :raises: :class:`RunCommandError` if ``raises`` is True and command failed.
    """
    for _ in Waiter(delays=delays, timeout=timeout, verbose=verbose):
        command_invocation = CommandInvocation.get(
            ssm_client=ssm_client,
            command_id=command_id,
            instance_id=instance_id,
        )
        if command_invocation.Status == CommandInvocationStatusEnum.Success.value:
            sys.stdout.write("\n")
            return command_invocation
        elif command_invocation.Status in [
            CommandInvocationStatusEnum.Cancelled.value,
            CommandInvocationStatusEnum.TimedOut.value,
            CommandInvocationStatusEnum.Failed.value,
            CommandInvocationStatusEnum.Cancelling.value,
        ]:
            if raises:
                raise RunCommandError.from_command_invocation(command_invocation)
            else:  # let the user to process the failed command_invocation them self
                return command_invocation
        else:
            pass
