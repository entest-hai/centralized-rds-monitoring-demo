"""
haimtran 07/09/2024
Get RDS performance insight and send to cloudwatch or log file
"""

import time
import uuid
from datetime import datetime, timedelta
import boto3
import json
import logging
from botocore.exceptions import ClientError

# Should be change to environment variables
LOG_BUCKET_NAME = "centralized-rds-monitoring-demo"
MEMBER_ACCOUNT_ROLE_NAME = "CentralizedPerformanceInsightsRole"
TARGET_METRIC_NAME_SPACE = "demo/PerformanceInsights1"
PI_REPORT_PERIOD = 60 * 5
OFFSET_VALUE_TESTING = 0.5
REGION = "ap-southeast-1"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# cloudwatch client
cw_client = boto3.client("cloudwatch", region_name=REGION)
# s3 client
s3_client = boto3.client("s3", region_name=REGION)
# slice group for mysql engine
dbSliceGroup = {
    "db.sql_tokenized",
    "db.wait_event",
    "db.user",
    "db.host",
    "db",
}


def str_encode(string):
    encoded_str = string.encode("ascii", "ignore")
    return remove_non_ascii(encoded_str.decode())


def remove_non_ascii(string):
    non_ascii = ascii(string)
    return non_ascii


def get_source_accounts():
    """
    Get source account ids
    """
    return ["1111222233334"]


def get_pi_client(account_id, region, assume_role=MEMBER_ACCOUNT_ROLE_NAME):
    """
    Create PI client by assume role to source account
    """
    # create sts client
    sts_client = boto3.client("sts", region_name=region)
    partition = sts_client.meta.partition
    # assume role
    assumed_role_object = sts_client.assume_role(
        RoleArn=f"arn:{partition}:iam::{account_id}:role/{assume_role}",
        RoleSessionName=f"AssumeRoleSession{uuid.uuid4()}",
    )
    # credentials
    credentials = assumed_role_object["Credentials"]
    # pi client
    pi_client = boto3.client(
        "pi",
        region_name=region,
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )
    # return
    return pi_client


def get_rds_client(account_id, region, assume_role=MEMBER_ACCOUNT_ROLE_NAME):
    """
    Create PI client by assume role to source account
    """
    # create sts client
    sts_client = boto3.client("sts", region_name=region)
    partition = sts_client.meta.partition
    # assume role
    assumed_role_object = sts_client.assume_role(
        RoleArn=f"arn:{partition}:iam::{account_id}:role/{assume_role}",
        RoleSessionName=f"AssumeRoleSession{uuid.uuid4()}",
    )
    # credentials
    credentials = assumed_role_object["Credentials"]
    # pi client
    rds_client = boto3.client(
        "rds",
        region_name=region,
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )
    # return
    return rds_client


def get_pi_instances(account_id, region):
    """
    Get database instances which performance insights have been enabled
    """
    # Get rds client
    rds_client = get_rds_client(
        account_id=account_id,
        region=region,
        assume_role=MEMBER_ACCOUNT_ROLE_NAME,
    )
    # Get list of rds database instances
    dbInstancesResponse = rds_client.describe_db_instances()
    # get database with performance insight enabled
    dbInstanceList = [
        {"DbiResourceId": item["DbiResourceId"], "DBInstanceArn": item["DBInstanceArn"]}
        for item in dbInstancesResponse["DBInstances"]
        if item.get("PerformanceInsightsEnabled") == True
        and ("mysql" in item.get("Engine"))
    ]
    return dbInstanceList


def get_resource_metrics(account_id, instance, start_time, end_time):
    """
    Get performance insight using pi client

    :param str instance: db instance id
    :param timestamp start_time: starting of pi report
    :param timestamp end_time: end time of pi report
    """
    # Get pi client
    pi_client = get_pi_client(
        account_id=account_id, region=REGION, assume_role=MEMBER_ACCOUNT_ROLE_NAME
    )
    # Build metric query list
    metric_queries = [
        {"Metric": "db.load.avg", "GroupBy": {"Group": group}} for group in dbSliceGroup
    ]
    # Get performance insights from pi client
    response = pi_client.get_resource_metrics(
        ServiceType="RDS",
        Identifier=instance,
        StartTime=start_time,
        EndTime=end_time,
        PeriodInSeconds=60,
        MetricQueries=metric_queries,
    )
    # return
    return response


def get_metric_dimensions_name(source_account_id, db_instance_arn, metric):
    """
    Get and format dimensions from pi response
    """
    dimensions = metric.get("Dimensions")
    # init dimensions with source account id
    formatted_dimensions = [
        dict(Name="SourceAccountId", Value=source_account_id),
        dict(Name="DBInstanceArn", Value=db_instance_arn),
    ]
    # There is no dimensions data
    if dimensions == None:
        metric_name = metric["Metric"].replace("avg", "")
        return metric_name, formatted_dimensions
    # There is dimensions data
    for key in dimensions:
        formatted_dimensions.append(dict(Name=key, Value=str_encode(dimensions[key])))
    metric_name = dimensions.popitem()[0].split(".")[1]
    return metric_name, formatted_dimensions


def send_cloudwatch_data(source_account_id, db_instance_arn, pi_response, name_space):
    """
    Parse and write performance insights to json file.

    :param PI_RESPONSE pi_response: response from pi client
    PI_RESPONSE [{'Key': {'Metric': 'db.load.avg', 'Dimension': []}:  'DataPoints':[]}]
    """
    metric_data = []

    for metric in pi_response["MetricList"]:
        # Get dimensions
        metric_name, formatted_dimensions = get_metric_dimensions_name(
            db_instance_arn, source_account_id, metric["Key"]
        )
        # Get data points
        for data_point in metric["DataPoints"]:
            # Get value
            value = data_point["Value"]
            # Get timestamp
            timestamp = data_point["Timestamp"]
            # There is dimensions data
            if formatted_dimensions != None:
                metric_data.append(
                    {
                        "MetricName": metric_name,
                        "Dimensions": formatted_dimensions,
                        "Timestamp": timestamp,
                        "Value": value,
                    }
                )
            else:
                metric_data.append(
                    {
                        "MetricName": metric_name,
                        "Timestamp": timestamp,
                        "Value": value,
                    }
                )
    # Send metric data to cloudwatch
    if metric_data:
        logger.info("## sending data to cloudwatch ...")
        try:
            cw_client.put_metric_data(Namespace=name_space, MetricData=metric_data)
        except ClientError as error:
            raise ValueError(f"The parameters you provided are incorrect: {error}")
    else:
        logger.info("## No Metric Data ##")
    return metric_data


def write_metric_to_s3(source_account_id, db_instance_arn, pi_response, log_file_name):
    """
    Parse and write performance insights to json file.

    :param PI_RESPONSE pi_response: response from pi client
    PI_RESPONSE [{'Key': {'Metric': 'db.load.avg', 'Dimension': []}:  'DataPoints':[]}]
    """
    metric_data = []

    for metric in pi_response["MetricList"]:
        # Get dimensions
        metric_name, formatted_dimensions = get_metric_dimensions_name(
            source_account_id, db_instance_arn, metric["Key"]
        )
        # print(formatted_dimensions)
        # Get data points
        for data_point in metric["DataPoints"]:
            # Get value
            value = data_point["Value"]
            # Get timestamp
            timestamp = data_point["Timestamp"]
            # There is dimensions data
            if formatted_dimensions != None:
                metric_data.append(
                    {
                        "MetricName": metric_name,
                        "Dimensions": formatted_dimensions,
                        "Timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"),
                        "Value": value,
                    }
                )
            else:
                metric_data.append(
                    {
                        "MetricName": metric_name,
                        "Timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"),
                        "Value": value,
                    }
                )
    # Write json to s3
    # s3_client.put_object(
    #     Body=json.dumps(metric_data), Bucket=LOG_BUCKET_NAME, Key=log_file_name
    # )
    # Write to json file
    with open(log_file_name, "w") as file:
        json.dump(metric_data, file, indent=4)
    return metric_data


def test_dashboard(account_id, region):
    """ """
    # get db instance
    dbs = get_pi_instances(account_id=account_id, region=region)
    # start time
    start_time = datetime(2024, 9, 1, 10, 10)
    end_time = datetime(2024, 9, 1, 10, 11)
    for db in dbs:
        print(db)
        for k in range(60):
            print(f"send metric data minute {k}")
            pi_response = get_resource_metrics(
                account_id=account_id,
                instance=db["DbiResourceId"],
                start_time=start_time,
                end_time=end_time,
            )
            # send to cloudwatch
            send_cloudwatch_data(
                source_account_id=account_id,
                db_instance_arn=db["DBInstanceArn"],
                pi_response=pi_response,
                name_space=TARGET_METRIC_NAME_SPACE,
            )
            # write to s3
            dbInstanceId = db["DbiResourceId"]
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            write_metric_to_s3(
                source_account_id=account_id,
                db_instance_arn=db["DBInstanceArn"],
                pi_response=pi_response,
                log_file_name=f"output_{dbInstanceId}_{timestamp}.json",
            )
            # update start time
            start_time += timedelta(minutes=1)
            end_time += timedelta(minutes=1)
            # update end time
            time.sleep(1)


def lambda_handler(event, context):
    """
    Lambda handler get performance insights from source account and send to monitoring account
    """
    source_account_ids = get_source_accounts()
    for account_id in source_account_ids:
        # Get dbs which enabled with performance insights
        dbs = get_pi_instances(account_id=account_id, region=REGION)
        # Loop through all dbs
        for db in dbs:
            print(db)
            # Get db instance id
            dbInstanceId = db["DbiResourceId"]
            # Get performance insights
            pi_response = get_resource_metrics(
                account_id=account_id,
                instance=db["DbiResourceId"],
                start_time=time.time() - PI_REPORT_PERIOD,
                end_time=time.time(),
            )
            # Send metric data to cloudwatch
            send_cloudwatch_data(
                source_account_id=account_id,
                db_instance_arn=db["DBInstanceArn"],
                pi_response=pi_response,
                name_space=TARGET_METRIC_NAME_SPACE,
            )
            # Send metric to json file S3
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            write_metric_to_s3(
                source_account_id=account_id,
                db_instance_arn=db["DBInstanceArn"],
                pi_response=pi_response,
                log_file_name=f"output_{dbInstanceId}_{timestamp}.json",
            )


if __name__ == "__main__":
    # lambda_handler(event=None, context=None)
    test_dashboard(account_id="1111222233334", region=REGION)
    # ids = get_pi_instances(account_id="1111222233334", region=REGION)
    # print(ids)
    # get_pi_client(account_id="1111222233334", region=REGION)
    # response = get_resource_metrics(
    #     account_id="1111222233334",
    #     instance="db-2LUCT6ZWBF5ANKDULZ7AYWWFCE",
    #     start_time=datetime(2024, 9, 1, 10, 10),
    #     end_time=datetime(2024, 9, 1, 10, 30),
    # )
    # print(response)
    # test_dashboard()
    # dbIds = get_pi_instances()
    # pi_response = get_resource_metrics(
    #     instance=dbIds[4],
    #     start_time=datetime(2024, 9, 1, 10, 10),
    #     end_time=datetime(2024, 9, 1, 10, 30),
    # )
    # write_metric_to_json(pi_response, "test.json")
    # while True:
    #     send_cloudwatch_data(pi_response, name_space=TargetMetricNamespace)
    #     time.sleep(60)
