# -*- coding: utf-8 -*-

import typing as T

if T.TYPE_CHECKING:  # pragma: no cover
    from .better_boto.response import CommandInvocation


class RunCommandError(SystemError):
    """
    raises when ssm_client.send_command() eventually fails.
    """

    @classmethod
    def from_command_invocation(
        cls,
        command_invocation: "CommandInvocation",
    ):
        msg = (
            f"return code: {command_invocation.ResponseCode}, "
            f"output: {command_invocation.StandardOutputContent!r}, "
            f"error: {command_invocation.StandardErrorContent!r}, "
        )
        return cls(msg)
