# -*- coding: utf-8 -*-

from aws_ssm_run_command import api


def test():
    _ = api

    _ = api.better_boto.send_command
    _ = api.better_boto.send_command_sync
    _ = api.better_boto.send_command_async
    _ = api.better_boto.CommandInvocationStatusEnum
    _ = api.better_boto.CommandInvocation
    _ = api.better_boto.wait_until_command_succeeded

    _ = api.patterns.run_command_on_one_ec2.run_python_script
    _ = api.patterns.run_command_on_one_ec2.run_python_script_large_payload

    _ = api.exc.RunCommandError


if __name__ == "__main__":
    from aws_ssm_run_command.tests import run_cov_test

    run_cov_test(__file__, "aws_ssm_run_command.api", preview=False)
