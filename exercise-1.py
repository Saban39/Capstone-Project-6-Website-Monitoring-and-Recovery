import boto3

# Initialize EC2 client
ec2 = boto3.client('ec2')

# Describe all subnets
subnets = ec2.describe_subnets()

# Print header
print(f"{'Subnet ID':<20} {'AZ':<20} {'CIDR Block':<18} {'VPC ID':<20} {'Default?':<10}")

# Iterate and print details
for subnet in subnets["Subnets"]:
    subnet_id = subnet["SubnetId"]
    az = subnet["AvailabilityZone"]
    cidr = subnet["CidrBlock"]
    vpc_id = subnet["VpcId"]
    is_default = subnet["DefaultForAz"]

    print(f"{subnet_id:<20} {az:<20} {cidr:<18} {vpc_id:<20} {str(is_default):<10}")
