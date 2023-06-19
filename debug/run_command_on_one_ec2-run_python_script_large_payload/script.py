# -*- coding: utf-8 -*-

import json
import fire
import boto3


def say_hello(name: str) -> str:
    """
    The application code logic for this script. Taking any input and return any
    output.
    """
    return f"Hello {name}!"


def run(s3uri_in: str, s3uri_out: str):
    # get input data
    parts = s3uri_in.split("/", 3)
    bucket, key = parts[2], parts[3]

    s3_client = boto3.client("s3")
    res = s3_client.get_object(Bucket=bucket, Key=key)
    name_list = json.loads(res["Body"].read().decode("utf-8"))

    # run core application code logic
    results = [say_hello(name) for name in name_list]

    # write output data
    parts = s3uri_out.split("/", 3)
    bucket, key = parts[2], parts[3]
    s3_client.put_object(Bucket=bucket, Key=key, Body=json.dumps(results))


if __name__ == "__main__":
    # convert your function into a CLI script
    fire.Fire(run)
