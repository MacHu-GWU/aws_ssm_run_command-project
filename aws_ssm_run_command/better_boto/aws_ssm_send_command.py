# -*- coding: utf-8 -*-

"""
todo: doc string
"""

import typing as T
import sys
import enum
import time
import dataclasses

from ..vendor.waiter import Waiter
from ..exc import RunCommandError

if T.TYPE_CHECKING:
    from mypy_boto3_ssm.client import SSMClient


def send_command(
    ssm_client: "SSMClient",
    instance_id: str,
    commands: T.List[str],
) -> str:
    """
    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm/client/send_command.html
    """
    res = ssm_client.send_command(
        InstanceIds=[
            instance_id,
        ],
        DocumentName="AWS-RunShellScript",
        DocumentVersion="1",
        Parameters={"commands": commands},
    )
    command_id = res["Command"]["CommandId"]
    return command_id


class CommandInvocationStatusEnum(str, enum.Enum):
    """
    Reference:

    - get_command_invocation_
    """

    Pending = "Pending"
    InProgress = "InProgress"
    Delayed = "Delayed"
    Success = "Success"
    Cancelled = "Cancelled"
    TimedOut = "TimedOut"
    Failed = "Failed"
    Cancelling = "Cancelling"


@dataclasses.dataclass
class CommandInvocation:
    """
    Represents a Command Invocation details returned from a
    get_command_invocation_ API call.
    """

    CommandId: T.Optional[str] = dataclasses.field(default=None)
    InstanceId: T.Optional[str] = dataclasses.field(default=None)
    Comment: T.Optional[str] = dataclasses.field(default=None)
    DocumentName: T.Optional[str] = dataclasses.field(default=None)
    DocumentVersion: T.Optional[str] = dataclasses.field(default=None)
    PluginName: T.Optional[str] = dataclasses.field(default=None)
    ResponseCode: T.Optional[int] = dataclasses.field(default=None)
    ExecutionStartDateTime: T.Optional[str] = dataclasses.field(default=None)
    ExecutionElapsedTime: T.Optional[str] = dataclasses.field(default=None)
    ExecutionEndDateTime: T.Optional[str] = dataclasses.field(default=None)
    Status: T.Optional[str] = dataclasses.field(default=None)
    StatusDetails: T.Optional[str] = dataclasses.field(default=None)
    StandardOutputContent: T.Optional[str] = dataclasses.field(default=None)
    StandardOutputUrl: T.Optional[str] = dataclasses.field(default=None)
    StandardErrorContent: T.Optional[str] = dataclasses.field(default=None)
    StandardErrorUrl: T.Optional[str] = dataclasses.field(default=None)
    CloudWatchOutputConfig: T.Optional[dict] = dataclasses.field(default=None)

    @classmethod
    def from_get_command_invocation_response(
        cls,
        response: dict,
    ) -> "CommandInvocation":
        """
        Reference:

        - get_command_invocation_
        """
        kwargs = {
            field.name: response.get(field.name) for field in dataclasses.fields(cls)
        }
        return cls(**kwargs)

    @classmethod
    def get(
        cls,
        ssm_client: "SSMClient",
        command_id: str,
        instance_id: str,
    ) -> "CommandInvocation":
        """
        A wrapper around get_command_invocation_ API call.

        Reference:

        - get_command_invocation_
        """
        response = ssm_client.get_command_invocation(
            CommandId=command_id,
            InstanceId=instance_id,
        )
        return cls.from_get_command_invocation_response(response)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def wait_until_command_succeeded(
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

    - get_command_invocation_

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


send_command_async = send_command


def send_command_sync(
    ssm_client: "SSMClient",
    instance_id: str,
    commands: T.List[str],
    gap: int = 1,
    raises: bool = True,
    delays: int = 3,
    timeout: int = 60,
    verbose: bool = True,
) -> CommandInvocation:
    """
    Send command and wait until it succeeds.

    See :func:`send_command` and :func:`wait_until_command_succeeded` for input
    arguments detail.

    :param gap: the gap between each ``send_command`` api and the first
        ``get_command_invocation`` api call. Because it takes some time to have
        the command invocation fired to SSM agent.
    """
    command_id = send_command(
        ssm_client=ssm_client,
        instance_id=instance_id,
        commands=commands,
    )
    time.sleep(gap)
    return wait_until_command_succeeded(
        ssm_client=ssm_client,
        command_id=command_id,
        instance_id=instance_id,
        raises=raises,
        delays=delays,
        timeout=timeout,
        verbose=verbose,
    )
