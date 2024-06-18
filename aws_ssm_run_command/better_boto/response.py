# -*- coding: utf-8 -*-

"""
Data model for API responses.
"""

import typing as T
import enum
import dataclasses
from datetime import datetime

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_ssm import SSMClient


@dataclasses.dataclass
class Command:
    """
    Represents a Command details returned from a
    `send_command <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm/client/send_command.html>`_
    API call.
    """

    # fmt: off
    CommandId: str = dataclasses.field()
    DocumentName: T.Optional[str] = dataclasses.field(default=None)
    DocumentVersion: T.Optional[str] = dataclasses.field(default=None)
    Comment: T.Optional[str] = dataclasses.field(default=None)
    ExpiresAfter: T.Optional[datetime] = dataclasses.field(default=None)
    Parameters: T.Dict[str, T.List[str]] = dataclasses.field(default_factory=dict)
    InstanceIds: T.List[str] = dataclasses.field(default_factory=list)
    Targets: T.List[T.Dict[str, T.Union[str, T.List[str]]]] = dataclasses.field(default_factory=list)
    RequestedDateTime: T.Optional[datetime] = dataclasses.field(default=None)
    Status: T.Optional[str] = dataclasses.field(default=None)
    StatusDetails: T.Optional[str] = dataclasses.field(default=None)
    OutputS3Region: T.Optional[str] = dataclasses.field(default=None)
    OutputS3BucketName: T.Optional[str] = dataclasses.field(default=None)
    OutputS3KeyPrefix: T.Optional[str] = dataclasses.field(default=None)
    MaxConcurrency: T.Optional[str] = dataclasses.field(default=None)
    MaxErrors: T.Optional[str] = dataclasses.field(default=None)
    TargetCount: T.Optional[int] = dataclasses.field(default=None)
    CompletedCount: T.Optional[int] = dataclasses.field(default=None)
    ErrorCount: T.Optional[int] = dataclasses.field(default=None)
    DeliveryTimedOutCount: T.Optional[int] = dataclasses.field(default=None)
    ServiceRole: T.Optional[str] = dataclasses.field(default=None)
    NotificationConfig: T.Dict[str, T.Any] = dataclasses.field(default_factory=dict)
    CloudWatchOutputConfig: T.Dict[str, T.Any] = dataclasses.field(default_factory=dict)
    TimeoutSeconds: T.Optional[int] = dataclasses.field(default=None)
    AlarmConfiguration: T.Dict[str, T.Any] = dataclasses.field(default_factory=dict)
    TriggeredAlarms: T.List[T.Dict[str, T.Any]] = dataclasses.field(default_factory=list)
    data: T.Dict[str, T.Any] = dataclasses.field(default_factory=dict)
    # fmt: on

    @classmethod
    def from_send_command_response(
        cls,
        response: dict,
    ):
        """
        Reference:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm/client/get_command_invocation.html
        """
        command = response["Command"]
        return cls(
            CommandId=command["CommandId"],
            DocumentName=command.get("DocumentName"),
            DocumentVersion=command.get("DocumentVersion"),
            Comment=command.get("Comment"),
            ExpiresAfter=command.get("ExpiresAfter"),
            Parameters=command.get("Parameters", {}),
            InstanceIds=command.get("InstanceIds", []),
            Targets=command.get("Targets", []),
            RequestedDateTime=command.get("RequestedDateTime"),
            Status=command.get("Status"),
            StatusDetails=command.get("StatusDetails"),
            OutputS3Region=command.get("OutputS3Region"),
            OutputS3BucketName=command.get("OutputS3BucketName"),
            OutputS3KeyPrefix=command.get("OutputS3KeyPrefix"),
            MaxConcurrency=command.get("MaxConcurrency"),
            MaxErrors=command.get("MaxErrors"),
            TargetCount=command.get("TargetCount"),
            CompletedCount=command.get("CompletedCount"),
            ErrorCount=command.get("ErrorCount"),
            DeliveryTimedOutCount=command.get("DeliveryTimedOutCount"),
            ServiceRole=command.get("ServiceRole"),
            NotificationConfig=command.get("NotificationConfig", {}),
            CloudWatchOutputConfig=command.get("CloudWatchOutputConfig", {}),
            TimeoutSeconds=command.get("TimeoutSeconds"),
            AlarmConfiguration=command.get("AlarmConfiguration", {}),
            TriggeredAlarms=command.get("TriggeredAlarms", []),
            data=command,
        )


class CommandInvocationStatusEnum(str, enum.Enum):
    """
    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm/client/get_command_invocation.html
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
    `get_command_invocation <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm/client/get_command_invocation.html>`_
    API call.
    """

    CommandId: str = dataclasses.field()
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
    CloudWatchOutputConfig: dict = dataclasses.field(default_factory=dict)

    @classmethod
    def from_get_command_invocation_response(
        cls,
        response: dict,
    ):
        """
        Reference:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm/client/get_command_invocation.html
        """
        return cls(
            CommandId=response["CommandId"],
            InstanceId=response.get("InstanceId"),
            Comment=response.get("Comment"),
            DocumentName=response.get("DocumentName"),
            DocumentVersion=response.get("DocumentVersion"),
            PluginName=response.get("PluginName"),
            ResponseCode=response.get("ResponseCode"),
            ExecutionStartDateTime=response.get("ExecutionStartDateTime"),
            ExecutionElapsedTime=response.get("ExecutionElapsedTime"),
            ExecutionEndDateTime=response.get("ExecutionEndDateTime"),
            Status=response.get("Status"),
            StatusDetails=response.get("StatusDetails"),
            StandardOutputContent=response.get("StandardOutputContent"),
            StandardOutputUrl=response.get("StandardOutputUrl"),
            StandardErrorContent=response.get("StandardErrorContent"),
            StandardErrorUrl=response.get("StandardErrorUrl"),
            CloudWatchOutputConfig=response.get("CloudWatchOutputConfig", {}),
        )

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

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm/client/get_command_invocation.html
        """
        response = ssm_client.get_command_invocation(
            CommandId=command_id,
            InstanceId=instance_id,
        )
        return cls.from_get_command_invocation_response(response)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    def is_pending(self) -> bool:
        """
        Check if the command is pending
        """
        return self.Status == CommandInvocationStatusEnum.Pending.value

    def is_in_progress(self) -> bool:
        """
        Check if the command is in progress.
        """
        return self.Status == CommandInvocationStatusEnum.InProgress.value

    def is_delayed(self) -> bool:
        """
        Check if the command is delayed.
        """
        return self.Status == CommandInvocationStatusEnum.Delayed.value

    def is_success(self) -> bool:
        """
        Check if the command is successful.
        """
        return self.Status == CommandInvocationStatusEnum.Success.value

    def is_cancelled(self) -> bool:
        """
        Check if the command is cancelled.
        """
        return self.Status == CommandInvocationStatusEnum.Cancelled.value

    def is_timed_out(self) -> bool:
        """
        Check if the command is timed out.
        """
        return self.Status == CommandInvocationStatusEnum.TimedOut.value

    def is_failed(self) -> bool:
        """
        Check if the command failed.
        """
        return self.Status == CommandInvocationStatusEnum.Failed.value

    def is_cancelling(self) -> bool:
        """
        Check if the command is in the process of cancelling.
        """
        return self.Status == CommandInvocationStatusEnum.Cancelling.value
