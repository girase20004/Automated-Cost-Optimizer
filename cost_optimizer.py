import boto3
from datetime import datetime, timedelta

# This code:

# Finds running EC2 instances
# Checks CPU usage
# Stops instances if usage < 5%

ec2 = boto3.client('ec2')
cloudwatch = boto3.client('cloudwatch')

def lambda_handler(event, context):
    
    # Get all running instances
    instances = ec2.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            
            instance_id = instance['InstanceId']
            print(f"Checking Instance: {instance_id}")
            
            # Get CPU Utilization (last 1 hour)
            metrics = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[
                    {'Name': 'InstanceId', 'Value': instance_id}
                ],
                StartTime=datetime.utcnow() - timedelta(hours=1),
                EndTime=datetime.utcnow(),
                Period=300,
                Statistics=['Average']
            )

            datapoints = metrics['Datapoints']
            
            if not datapoints:
                print(f"No data for {instance_id}")
                continue

            avg_cpu = sum([point['Average'] for point in datapoints]) / len(datapoints)
            
            print(f"{instance_id} Avg CPU: {avg_cpu}")

            # Stop instance if CPU < 5%
            if avg_cpu < 5:
                print(f"Stopping Instance: {instance_id}")
                ec2.stop_instances(InstanceIds=[instance_id])
    
    return "Done"