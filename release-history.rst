.. _release_history:

Release and Version History
==============================================================================


x.y.z (Backlog)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


0.2.1 (2023-07-17)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add ``aws_ssm_run_command.api.better_boto.send_command_async`` and ``aws_ssm_run_command.api.better_boto.send_command_sync`` API.

**Minor Improvements**

- improve example code


0.1.2 (2023-06-21)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Minor Improvements**

- add ``raises`` argument to ``aws_ssm_run_command.api.better_boto.wait_until_command_succeeded`` function. Allow user to specify whether to raise an exception if the command fails. Default to ``True``.


0.1.1 (2023-06-18)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- First release
- Add the following public api:
    - ``aws_ssm_run_command.api.better_boto.CommandInvocationFailedError``
    - ``aws_ssm_run_command.api.better_boto.send_command``
    - ``aws_ssm_run_command.api.better_boto.CommandInvocationStatusEnum``
    - ``aws_ssm_run_command.api.better_boto.CommandInvocation``
    - ``aws_ssm_run_command.api.better_boto.wait_until_command_succeeded``
    - ``aws_ssm_run_command.api.patterns.run_command_on_one_ec2.run_python_script``
    - ``aws_ssm_run_command.api.patterns.run_command_on_one_ec2.run_python_script_large_payload``
