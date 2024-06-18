# -*- coding: utf-8 -*-

from aws_ssm_run_command import api


def test():
    _ = api

    _ = api.better_boto.Command
    _ = api.better_boto.CommandInvocation
    _ = api.better_boto.CommandInvocationStatusEnum
    _ = api.better_boto.run_shell_script_async
    _ = api.better_boto.run_shell_script_sync
    _ = api.better_boto.wait_until_send_command_succeeded

    _ = api.patterns.run_command_on_one_ec2.run_python_script
    _ = api.patterns.run_command_on_one_ec2.parse_last_line_json_in_output

    _ = api.exc.RunCommandError


if __name__ == "__main__":
    from aws_ssm_run_command.tests import run_cov_test

    run_cov_test(__file__, "aws_ssm_run_command.api", preview=False)
