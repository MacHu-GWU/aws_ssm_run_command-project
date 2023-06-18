# -*- coding: utf-8 -*-

from aws_ssm_run_command import api


def test():
    _ = api


if __name__ == "__main__":
    from aws_ssm_run_command.tests import run_cov_test

    run_cov_test(__file__, "aws_ssm_run_command.api", preview=False)
