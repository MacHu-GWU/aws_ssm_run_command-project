.. _run-remote-command-on-ec2-via-ssm:

Run Remote Command on EC2 via SSM
==============================================================================
在开始了解这个库, 我先简略的介绍一下在 AWS 的官方最佳实践中, 是如何使用 AWS SSM Run Command 功能来执行远程命令的, 以及这种方式到底有什么优势.


Overview
------------------------------------------------------------------------------
在服务器上执行命令是一个非常普遍的需求. 通常我们有这么几种方法:

- SSH 登录服务器, 然后在终端里敲命令.
- 用远程执行工具, 例如 `paramiko <https://www.paramiko.org/>`_. 你需要管理好 SSH. 本质上它是一个 ``ssh -t ${command}`` 命令的封装.
- 用 Ansible 一类的自动化工具.

AWS 原生的 System Manager 服务可以用来来执行远程命令. 这种方法的好处有很多:

- 无需管理 SSH. 自己管理 SSH 会有很多安全风险.
- 使用 IAM Role 权限管理, 非常安全.
- 自动化程度高, 可以被嵌入或者编排成各种复杂的脚本.
- 可以和 AWS 的其他服务联动.
- 性能更好, 这个功能是由安装在 EC2 上的 SSM Agent 提供, 它的异步执行效率更高, 并且有更好的错误处理机制.

本文我们就来看看如何用 AWS 的 System Manager 来执行远程命令.


.. _how-it-work:

How it Work
------------------------------------------------------------------------------
AWS 有一个历史悠久的服务 SSM (System Manager), 该服务对标的是 Ansible 之类的服务器运维工具, 用于批量管理虚拟机. 和 Ansible 用 SSH 来执行远程命令的方式不同, SSM 是通过在机器上安装 SSM Agent (一个由 AWS 维护的系统服务软件), 然后让 SSM Agent 将自己自动注册到 SSM Fleet Manager, 然后通过 IAM 鉴权, 然后用 AWS 内部的 API 与 SSM Agent 通信从而执行远程命令.

我们来看一看在启动一台由 SSM 管理的 EC2 的过程中, 到底发生了什么:

- 启动机器, 启动操作系统以及系统服务, 其中系统服务就包括 SSM agent.
- SSM gent 启动后就会调用 IAM 的权限, 尝试将自己注册到 SSM Fleet Manager 上.
- 一旦注册成功, 你就可以用 SSM 来远程操纵 EC2 了.

从以上内容我们可以看出来, 安装 SSM Agent 至关重要. 所幸的事 `AWS 官方提供的一些 AMI <https://docs.aws.amazon.com/systems-manager/latest/userguide/ami-preinstalled-agent.html>`_ (主要是 Amazon Linux) 上会预装 SSM Agent. 包括 AWS 认证过的第三方软件提供商例如 RedHat, Ubuntu 等公司提供的 AMI 也会预装 SSM Agent 并开机自动启动. 但是你用的是你自己或是 Market place 上的 AMI, 里面没有预装 SSM Agent, 你就需要自己安装了. 我们这个项目用的是 Ubuntu Server 20.04, 里面已经预装了 SSM Agent, 所以我们无需做任何额外工作.

在你启动 EC2 的时候 (包括启动新的 EC2, 或是 Stop 之后再 Start, 或是 Reboot 都可以, 因为只要启动系统服务就可以了), 只要你的 IAM Role 里有这个 由 AWS 管理的 IAM Policy ``arn:aws:iam::aws:policy/service-role/AmazonSSMManagedInstanceCore``, 或是你创建一个自己的 Policy 有同样的权限, 那么 SSM Agent 就会自动将自己注册到 SSM Fleet Manager. 虽然 Reference 中的官方文档用的 IAM Role 有特定的名字, 但其实什么名字都可以, 只要有对应的权限就可以.

Reference:

- SSM Agent 的官方文档: https://docs.aws.amazon.com/systems-manager/latest/userguide/ssm-agent.html


Manually Install SSM Agent on EC2
------------------------------------------------------------------------------
下面这些文档介绍了如何手动在 EC2 上安装 SSM Agent, 我并没有动手试过, 仅供参考.

- Linux: https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-manual-agent-install.html
- Windows: https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-install-win.html
- MacOS: https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-manual-agent-install-macos2.html


一些有用的命令
------------------------------------------------------------------------------
你可以用 AWS CLI 来查看哪些 EC2 被注册到了 SSM 管理清单上, 你到 `SSM Fleet Manager Console <https://console.aws.amazon.com/systems-manager/managed-instances?>`_ 中看也是一样的:

.. code-block:: bash

    aws ssm describe-instance-information --output text --profile ${your_aws_profile}

你也可以 SSH 到 EC2 上运行如下命令来检查 SSM Agent 是否已经启用 (该项目基于 ubuntu server 20.04, 其他系统请参考 `官方文档 <https://docs.aws.amazon.com/systems-manager/latest/userguide/ami-preinstalled-agent.html#verify-ssm-agent-status>`_):

.. code-block:: bash

    sudo systemctl status snap.amazon-ssm-agent.amazon-ssm-agent.service


.. _boto3-run-command-example:

用 SSM Agent 执行远程命令
------------------------------------------------------------------------------
下面这段代码展示了如何用 boto3 SDK 通过 SSM 运行远程命令.

.. literalinclude:: ./example.py
   :language: python
   :linenos:

Reference:

- 用 SSM 远程执行命令的官方教程: https://aws.amazon.com/getting-started/hands-on/remotely-run-commands-ec2-instance-systems-manager/
- 发送命令的 Python API 文档: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.send_command


使用 Run Command 功能的全部步骤总结
------------------------------------------------------------------------------
1. 在创建 EC2 之前就要配置好你的 IAM Role.
2. 确保你给 EC2 的 IAM Role 有这个 ``AmazonSSMManagedInstanceCore`` IAM Policy.
3. 启动 EC2 的时候使用这个 IAM Role. 如果启动的时候忘记给 IAM Role, 那么你可以启动后指定 IAM Role 然后重启即可.
4. 然后就可以用 SSM 的 API 来远程执行命令了.


Remote Command 还能用来干什么
------------------------------------------------------------------------------
很多自动化脚本由于网络连接的缘故是必须要在 EC2 上运行的. 所以我们可以在世界的任意地点用 SSM agent 来执行远程命令. 而而关于传输数据, 我建议通过 S3 做媒介, 让 EC2 将命令执行后的数据写入到 S3 上. 这样你就可以在任意地点读取这些数据了.


Why aws_ssm_run_command
------------------------------------------------------------------------------
在 :ref:`boto3-run-command-example` 的例子中可以看出, 我们可以很轻易的将发送命令, 但是还有很多细节并没有解决. 例如:

1. 如何知道这个命令执行是成功了还是失败了? 如何获得命令的 return code 和 stdout / stderr 输出?
2. 如果一个命令执行时间较长, 如何知道命令什么时候执行玩了?
3. 如果要发送的命令本身数据量很大, 超过了 AWS RestAPI 的 payload 限制怎么办?
4. 如果该命令返回的数据量很大, 并不适合放在 stdout 中, 那么如何获得这些数据呢?

现在你可以看出, 在生产实践中你需要处理很多细节问题, 一般很多运维工程师就会临时写一些代码来解决这些问题. 但是这些代码往往是重复的, 而且容易出错. 所以我写了这个库, 用来一次性解决这些问题.
