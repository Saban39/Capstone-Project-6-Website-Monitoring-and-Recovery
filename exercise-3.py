import boto3
import time
import paramiko
import requests
import schedule
import logging

# ---------- LOGGING SETUP ----------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

# ---------- AWS SETUP ----------
ec2_resource = boto3.resource('ec2')
ec2_client = boto3.client('ec2')

image_id = 'ami-0ef32de3e8ab0640e'
key_name = 'my_phython_automate_key'
instance_type = 't2.small'
ssh_private_key_path = '/Users/sgworker/PycharmProjects/chapter-14-automation-with-pyhton/my_phython_automate_key.pem'
ssh_user = 'admin'
ssh_host = ''

# ---------- CHECK FOR EXISTING INSTANCE ----------
response = ec2_client.describe_instances(
    Filters=[{'Name': 'tag:Name', 'Values': ['my-server-2']}]
)

instance_exists = bool(response["Reservations"]) and bool(response["Reservations"][0]["Instances"])
instance_id = ""

if not instance_exists:
    logging.info("Creating a new EC2 instance...")
    print("Creating a new EC2 instance...")
    instances = ec2_resource.create_instances(
        ImageId=image_id,
        KeyName=key_name,
        MinCount=1,
        MaxCount=1,
        InstanceType=instance_type,
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': 'my-server-2'}]
        }]
    )
    instance = instances[0]
    instance_id = instance.id
else:
    instance = response["Reservations"][0]["Instances"][0]
    instance_id = instance["InstanceId"]
    logging.info("Instance already exists.")
    print("Instance already exists.")

# ---------- WAIT FOR INSTANCE ----------
logging.info("Waiting for instance to initialize...")
print("Waiting for instance to initialize...")
while True:
    status = ec2_client.describe_instance_status(InstanceIds=[instance_id])
    if status["InstanceStatuses"]:
        instance_status = status["InstanceStatuses"][0]
        if (instance_status['InstanceStatus']['Status'] == 'ok' and
            instance_status['SystemStatus']['Status'] == 'ok' and
            instance_status['InstanceState']['Name'] == 'running'):
            break
    logging.info("Still initializing... waiting 30 seconds.")
    print("Still initializing... waiting 30 seconds.")
    time.sleep(30)
logging.info("Instance fully initialized.")
print("Instance fully initialized.")

# ---------- GET PUBLIC IP ----------
response = ec2_client.describe_instances(
    Filters=[{'Name': 'tag:Name', 'Values': ['my-server-2']}]
)
ssh_host = response["Reservations"][0]["Instances"][0]["PublicIpAddress"]
logging.info(f"Public IP: {ssh_host}")
print(f"Public IP: {ssh_host}")

# ---------- INSTALL DOCKER & RUN NGINX ----------
commands = [
    'sudo apt update -y && sudo apt install -y docker.io',
    'sudo systemctl start docker',
    'sudo usermod -aG docker admin',
    'docker run -d -p 8080:80 --name nginx nginx'
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=ssh_host, username=ssh_user, key_filename=ssh_private_key_path)

logging.info("Running setup commands on EC2...")
print("Running setup commands on EC2...")
for cmd in commands:
    logging.debug(f"Executing: {cmd}")
    print(f"Executing command: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode()
    print(output)
    logging.info(output)

ssh.close()

# ---------- OPEN PORT 8080 ----------
sg_list = ec2_client.describe_security_groups(GroupNames=['SSHAccess'])

port_open = any(
    'FromPort' in perm and perm['FromPort'] == 8080
    for perm in sg_list['SecurityGroups'][0]['IpPermissions']
)

if not port_open:
    logging.info("Opening port 8080 in default security group...")
    print("Opening port 8080 in default security group...")
    ec2_client.authorize_security_group_ingress(
        GroupName='SSHAccess',
        IpProtocol='tcp',
        FromPort=8080,
        ToPort=8080,
        CidrIp='0.0.0.0/0'
    )

# ---------- MONITOR APP ----------
app_not_accessible_count = 0

def restart_container():
    global app_not_accessible_count
    logging.warning("Restarting the nginx container...")
    print("Restarting the nginx container...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ssh_host, username=ssh_user, key_filename=ssh_private_key_path)
    stdin, stdout, stderr = ssh.exec_command('docker start nginx')
    output = stdout.read().decode()
    logging.info(output)
    print(output)
    ssh.close()
    app_not_accessible_count = 0

def monitor_application():
    global app_not_accessible_count
    try:
        response = requests.get(f"http://{ssh_host}:8080")
        if response.status_code == 200:
            logging.info("Nginx is running.")
            print("Nginx is running.")
            app_not_accessible_count = 0
        else:
            logging.warning("Nginx responded but not with 200.")
            print("Nginx returned an error status.")
            app_not_accessible_count += 1
    except Exception as ex:
        logging.error(f"Connection error: {ex}")
        print(f"Connection error: {ex}")
        app_not_accessible_count += 1

    if app_not_accessible_count >= 5:
        restart_container()

schedule.every(10).seconds.do(monitor_application)

logging.info("Starting health check monitor loop...")
print("Starting health check monitor loop...")
while True:
    schedule.run_pending()
