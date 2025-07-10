# 14 - Automation with Python
#### This project is for the Devops Bootcamp module "14-Automation with Python" 


## 📄 Included PDF Resources

CAPSTONE PROJECT-6

## Evidence / Proof

Here are my notes, work, solutions, and test results for the module **"Automation with Python"**:  
👉 [PDF Link to Module Notes & Work](./14-Automation_with_Python.pdf)


All of my notes, work, solutions, and test results can be found in the PDF 14-Automation with Python. 
My complete documentation, including all notes and tests from the bootcamp, is available in this repository: https://github.com/Saban39/my_devops-bootcamp-pdf-notes-and-solutions.git



## My notes, work, solutions, and test results for Module "14-Automation with Python"


<details>
<summary>Solution 1: Working with Subnets in AWS </summary>
 <br>

> EXERCISE 1: Working with Subnets in AWS

- Get all the subnets in your default region
- Print the subnet Ids

Step 1: In the first step, I installed the Boto3 library. Then, I ran the Python script to list the subnets.

```sh
pip install boto3 
```
![Bildschirmfoto 2025-05-12 um 15 12 03](https://github.com/user-attachments/assets/e69e1f5c-7cf9-49b0-9425-4a5a656e4bdc)


Step 2: In the second step, I executed my Python script.
```sh
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

```


![Bildschirmfoto 2025-05-12 um 15 18 15](https://github.com/user-attachments/assets/56ee31cb-35fc-4d1e-859e-c1f4a7077961)



</details>




<details>
<summary>Solution 2:  Working with IAM in AWS </summary>
 <br>

> EXERCISE 2: Working with IAM in AWS

- Get all the IAM users in your AWS account
- For each user, print out the name of the user and when they were last active (hint: Password Last Used attribute)
- Print out the user ID and name of the user who was active the most recently

With my script, I listed the IAM users along with their attributes.

```sh
import boto3
from datetime import datetime

# Initialize IAM client
iam = boto3.client('iam')

# Get list of IAM users
response = iam.list_users()
users = response.get("Users", [])

last_active_user = None

print(f"{'UserName':<25} {'PasswordLastUsed'}")
print("-" * 50)

for user in users:
    username = user["UserName"]
    last_used = user.get("PasswordLastUsed")

    # Print user and last login time (or 'Never')
    if last_used:
        print(f"{username:<25} {last_used}")
    else:
        print(f"{username:<25} Never logged in")

    # Find the most recently active user
    if last_used:
        if last_active_user is None or last_used > last_active_user["PasswordLastUsed"]:
            last_active_user = user

print("\nMost recently active user:")
if last_active_user:
    print(f"User ID   : {last_active_user['UserId']}")
    print(f"Username  : {last_active_user['UserName']}")
    print(f"Last Used : {last_active_user['PasswordLastUsed']}")
else:
    print("No user has logged in yet.")



```

![Bildschirmfoto 2025-05-12 um 15 22 05](https://github.com/user-attachments/assets/4f5288cd-e7d2-4455-b904-311d191dfaed)




</details>




<details>
<summary>Solution 3: Automate Running and Monitoring Application on EC2 instance </summary>
 <br>

> EXERCISE 3: Automate Running and Monitoring Application on EC2 instance
Write Python program which automatically creates EC2 instance, install Docker inside and starts Nginx application as Docker container and starts monitoring the application as a scheduled task. Write the program with the following steps:

- Start EC2 instance in default VPC
- Wait until the EC2 server is fully initialized
- Install Docker on the EC2 server
- Start nginx container
- Open port for nginx to be accessible from browser
- Create a scheduled function that sends request to the nginx application and checks the status is OK
- If status is not OK 5 times in a row, it restarts the nginx application

Step 1: As the first step, I created a security group (ID: sg-0ef4366a5265883ed) within my default VPC.

![Bildschirmfoto 2025-05-14 um 10 37 14](https://github.com/user-attachments/assets/88dab047-9a48-4f03-bd1e-45700c9855d8)

Step 2: In step 2, I created an SSH key pair to securely connect to my EC2 instance.

![Bildschirmfoto 2025-05-14 um 10 38 52](https://github.com/user-attachments/assets/5d48ce5d-f3c1-4eb4-834e-1460a41148da)

Step 3: In step 3, I prepared the Python script with my data.

![Bildschirmfoto 2025-05-14 um 12 17 05](https://github.com/user-attachments/assets/936e56b1-985d-43d7-a87c-ca7e17e09e53)

I used ami-0ef32de3e8ab0640e debian(12) template.
!!!! That's why I also had to use the admin user for Debian and replace yum with apt.


```sh

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



```
Step 4: In step 4, I executed my script, and Nginx was publicly accessible, as shown in the screenshots.

![Bildschirmfoto 2025-05-14 um 11 48 59](https://github.com/user-attachments/assets/36bc274a-273f-431a-a580-081751487340)



and my logs:

```sh
/Users/sgworker/PycharmProjects/chapter-14-automation-with-pyhton/venv/bin/python /Users/sgworker/PycharmProjects/chapter-14-automation-with-pyhton/exercise-3.py 
2025-05-14 11:44:44,177 [INFO] Found credentials in shared credentials file: ~/.aws/credentials
Instance already exists.
Waiting for instance to initialize...
2025-05-14 11:44:44,682 [INFO] Instance already exists.
2025-05-14 11:44:44,682 [INFO] Waiting for instance to initialize...
2025-05-14 11:44:44,794 [INFO] Instance fully initialized.
Instance fully initialized.
2025-05-14 11:44:44,879 [INFO] Public IP: 18.192.13.199
Public IP: 18.192.13.199
2025-05-14 11:44:44,933 [INFO] Connected (version 2.0, client OpenSSH_9.2p1)
Running setup commands on EC2...
Executing command: sudo apt update -y && sudo apt install -y docker.io
2025-05-14 11:44:45,135 [INFO] Authentication (publickey) successful!
2025-05-14 11:44:45,135 [INFO] Running setup commands on EC2...
2025-05-14 11:45:11,166 [INFO] Get:1 file:/etc/apt/mirrors/debian.list Mirrorlist [38 B]
Get:5 file:/etc/apt/mirrors/debian-security.list Mirrorlist [47 B]
Get:2 https://cdn-aws.deb.debian.org/debian bookworm InRelease [151 kB]
Get:3 https://cdn-aws.deb.debian.org/debian bookworm-updates InRelease [55.4 kB]
Get:4 https://cdn-aws.deb.debian.org/debian bookworm-backports InRelease [59.4 kB]
Get:6 https://cdn-aws.deb.debian.org/debian-security bookworm-security InRelease [48.0 kB]
Get:7 https://cdn-aws.deb.debian.org/debian bookworm/main Sources [9495 kB]
Get:8 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 Packages [8792 kB]
Get:9 https://cdn-aws.deb.debian.org/debian bookworm/main Translation-en [6109 kB]
Get:10 https://cdn-aws.deb.debian.org/debian bookworm-updates/main Sources [796 B]
Get:11 https://cdn-aws.deb.debian.org/debian bookworm-updates/main amd64 Packages [512 B]
Get:12 https://cdn-aws.deb.debian.org/debian bookworm-updates/main Translation-en [360 B]
Get:13 https://cdn-aws.deb.debian.org/debian bookworm-backports/main Sources [282 kB]
Get:14 https://cdn-aws.deb.debian.org/debian bookworm-backports/main amd64 Packages [285 kB]
Get:15 https://cdn-aws.deb.debian.org/debian bookworm-backports/main Translation-en [242 kB]
Get:16 https://cdn-aws.deb.debian.org/debian-security bookworm-security/main Sources [129 kB]
Get:17 https://cdn-aws.deb.debian.org/debian-security bookworm-security/main amd64 Packages [258 kB]
Get:18 https://cdn-aws.deb.debian.org/debian-security bookworm-security/main Translation-en [155 kB]
Fetched 26.1 MB in 4s (7332 kB/s)
Reading package lists...
Building dependency tree...
Reading state information...
6 packages can be upgraded. Run 'apt list --upgradable' to see them.
Reading package lists...
Building dependency tree...
Reading state information...
The following additional packages will be installed:
  binutils binutils-common binutils-x86-64-linux-gnu cgroupfs-mount containerd
  criu git git-man libbinutils libctf-nobfd0 libctf0 liberror-perl
  libgdbm-compat4 libgprofng0 libintl-perl libintl-xs-perl libjansson4
  libmodule-find-perl libnet1 libnftables1 libnl-3-200 libperl5.36
  libproc-processtable-perl libprotobuf32 libsort-naturally-perl
  libterm-readkey-perl needrestart patch perl perl-base perl-modules-5.36
  python3-protobuf runc tini
Suggested packages:
  binutils-doc containernetworking-plugins docker-doc aufs-tools btrfs-progs
  debootstrap rinse rootlesskit xfsprogs zfs-fuse | zfsutils-linux
  git-daemon-run | git-daemon-sysvinit git-doc git-email git-gui gitk gitweb
  git-cvs git-mediawiki git-svn needrestart-session | libnotify-bin
  iucode-tool ed diffutils-doc perl-doc libterm-readline-gnu-perl
  | libterm-readline-perl-perl make libtap-harness-archive-perl
The following NEW packages will be installed:
  binutils binutils-common binutils-x86-64-linux-gnu cgroupfs-mount containerd
  criu docker.io git git-man libbinutils libctf-nobfd0 libctf0 liberror-perl
  libgdbm-compat4 libgprofng0 libintl-perl libintl-xs-perl libjansson4
  libmodule-find-perl libnet1 libnftables1 libnl-3-200 libperl5.36
  libproc-processtable-perl libprotobuf32 libsort-naturally-perl
  libterm-readkey-perl needrestart patch perl perl-modules-5.36
  python3-protobuf runc tini
The following packages will be upgraded:
  perl-base
1 upgraded, 34 newly installed, 0 to remove and 5 not upgraded.
Need to get 93.1 MB of archives.
After this operation, 406 MB of additional disk space will be used.
Get:1 file:/etc/apt/mirrors/debian-security.list Mirrorlist [47 B]
Get:6 file:/etc/apt/mirrors/debian.list Mirrorlist [38 B]
Get:2 https://cdn-aws.deb.debian.org/debian-security bookworm-security/main amd64 perl-base amd64 5.36.0-7+deb12u2 [1609 kB]
Get:3 https://cdn-aws.deb.debian.org/debian-security bookworm-security/main amd64 perl-modules-5.36 all 5.36.0-7+deb12u2 [2815 kB]
Get:4 https://cdn-aws.deb.debian.org/debian-security bookworm-security/main amd64 libperl5.36 amd64 5.36.0-7+deb12u2 [4207 kB]
Get:5 https://cdn-aws.deb.debian.org/debian-security bookworm-security/main amd64 perl amd64 5.36.0-7+deb12u2 [239 kB]
Get:7 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libgdbm-compat4 amd64 1.23-3 [48.2 kB]
Get:8 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 runc amd64 1.1.5+ds1-1+deb12u1 [2710 kB]
Get:9 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 containerd amd64 1.6.20~ds1-1+deb12u1 [25.9 MB]
Get:10 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 tini amd64 0.19.0-1 [255 kB]
Get:11 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 docker.io amd64 20.10.24+dfsg1-1+deb12u1 [36.2 MB]
Get:12 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 binutils-common amd64 2.40-2 [2487 kB]
Get:13 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libbinutils amd64 2.40-2 [572 kB]
Get:14 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libctf-nobfd0 amd64 2.40-2 [153 kB]
Get:15 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libctf0 amd64 2.40-2 [89.8 kB]
Get:16 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libgprofng0 amd64 2.40-2 [812 kB]
Get:17 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libjansson4 amd64 2.14-2 [40.8 kB]
Get:18 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 binutils-x86-64-linux-gnu amd64 2.40-2 [2246 kB]
Get:19 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 binutils amd64 2.40-2 [65.0 kB]
Get:20 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 cgroupfs-mount all 1.4 [6276 B]
Get:21 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libprotobuf32 amd64 3.21.12-3 [932 kB]
Get:22 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 python3-protobuf amd64 3.21.12-3 [245 kB]
Get:23 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libnet1 amd64 1.1.6+dfsg-3.2 [60.3 kB]
Get:24 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libnftables1 amd64 1.0.6-2+deb12u2 [299 kB]
Get:25 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libnl-3-200 amd64 3.7.0-0.2+b1 [63.1 kB]
Get:26 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 criu amd64 3.17.1-2+deb12u1 [665 kB]
Get:27 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 liberror-perl all 0.17029-2 [29.0 kB]
Get:28 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 git-man all 1:2.39.5-0+deb12u2 [2053 kB]
Get:29 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 git amd64 1:2.39.5-0+deb12u2 [7260 kB]
Get:30 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libintl-perl all 1.33-1 [720 kB]
Get:31 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libintl-xs-perl amd64 1.33-1 [15.6 kB]
Get:32 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libmodule-find-perl all 0.16-2 [10.6 kB]
Get:33 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libproc-processtable-perl amd64 0.634-1+b2 [43.1 kB]
Get:34 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libsort-naturally-perl all 1.03-4 [13.1 kB]
Get:35 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libterm-readkey-perl amd64 2.38-2+b1 [24.5 kB]
Get:36 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 needrestart all 3.6-4+deb12u3 [60.5 kB]
Get:37 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 patch amd64 2.7.6-7 [128 kB]
apt-listchanges: Reading changelogs...
Fetched 93.1 MB in 1s (64.4 MB/s)
(Reading database ... 29492 files and directories currently installed.)
Preparing to unpack .../perl-base_5.36.0-7+deb12u2_amd64.deb ...
Unpacking perl-base (5.36.0-7+deb12u2) over (5.36.0-7+deb12u1) ...
Setting up perl-base (5.36.0-7+deb12u2) ...
Selecting previously unselected package perl-modules-5.36.
(Reading database ... 29492 files and directories currently installed.)
Preparing to unpack .../00-perl-modules-5.36_5.36.0-7+deb12u2_all.deb ...
Unpacking perl-modules-5.36 (5.36.0-7+deb12u2) ...
Selecting previously unselected package libgdbm-compat4:amd64.
Preparing to unpack .../01-libgdbm-compat4_1.23-3_amd64.deb ...
Unpacking libgdbm-compat4:amd64 (1.23-3) ...
Selecting previously unselected package libperl5.36:amd64.
Preparing to unpack .../02-libperl5.36_5.36.0-7+deb12u2_amd64.deb ...
Unpacking libperl5.36:amd64 (5.36.0-7+deb12u2) ...
Selecting previously unselected package perl.
Preparing to unpack .../03-perl_5.36.0-7+deb12u2_amd64.deb ...
Unpacking perl (5.36.0-7+deb12u2) ...
Selecting previously unselected package runc.
Preparing to unpack .../04-runc_1.1.5+ds1-1+deb12u1_amd64.deb ...
Unpacking runc (1.1.5+ds1-1+deb12u1) ...
Selecting previously unselected package containerd.
Preparing to unpack .../05-containerd_1.6.20~ds1-1+deb12u1_amd64.deb ...
Unpacking containerd (1.6.20~ds1-1+deb12u1) ...
Selecting previously unselected package tini.
Preparing to unpack .../06-tini_0.19.0-1_amd64.deb ...
Unpacking tini (0.19.0-1) ...
Selecting previously unselected package docker.io.
Preparing to unpack .../07-docker.io_20.10.24+dfsg1-1+deb12u1_amd64.deb ...
Unpacking docker.io (20.10.24+dfsg1-1+deb12u1) ...
Selecting previously unselected package binutils-common:amd64.
Preparing to unpack .../08-binutils-common_2.40-2_amd64.deb ...
Unpacking binutils-common:amd64 (2.40-2) ...
Selecting previously unselected package libbinutils:amd64.
Preparing to unpack .../09-libbinutils_2.40-2_amd64.deb ...
Unpacking libbinutils:amd64 (2.40-2) ...
Selecting previously unselected package libctf-nobfd0:amd64.
Preparing to unpack .../10-libctf-nobfd0_2.40-2_amd64.deb ...
Unpacking libctf-nobfd0:amd64 (2.40-2) ...
Selecting previously unselected package libctf0:amd64.
Preparing to unpack .../11-libctf0_2.40-2_amd64.deb ...
Unpacking libctf0:amd64 (2.40-2) ...
Selecting previously unselected package libgprofng0:amd64.
Preparing to unpack .../12-libgprofng0_2.40-2_amd64.deb ...
Unpacking libgprofng0:amd64 (2.40-2) ...
Selecting previously unselected package libjansson4:amd64.
Preparing to unpack .../13-libjansson4_2.14-2_amd64.deb ...
Unpacking libjansson4:amd64 (2.14-2) ...
Selecting previously unselected package binutils-x86-64-linux-gnu.
Preparing to unpack .../14-binutils-x86-64-linux-gnu_2.40-2_amd64.deb ...
Unpacking binutils-x86-64-linux-gnu (2.40-2) ...
Selecting previously unselected package binutils.
Preparing to unpack .../15-binutils_2.40-2_amd64.deb ...
Unpacking binutils (2.40-2) ...
Selecting previously unselected package cgroupfs-mount.
Preparing to unpack .../16-cgroupfs-mount_1.4_all.deb ...
Unpacking cgroupfs-mount (1.4) ...
Selecting previously unselected package libprotobuf32:amd64.
Preparing to unpack .../17-libprotobuf32_3.21.12-3_amd64.deb ...
Unpacking libprotobuf32:amd64 (3.21.12-3) ...
Selecting previously unselected package python3-protobuf.
Preparing to unpack .../18-python3-protobuf_3.21.12-3_amd64.deb ...
Unpacking python3-protobuf (3.21.12-3) ...
Selecting previously unselected package libnet1:amd64.
Preparing to unpack .../19-libnet1_1.1.6+dfsg-3.2_amd64.deb ...
Unpacking libnet1:amd64 (1.1.6+dfsg-3.2) ...
Selecting previously unselected package libnftables1:amd64.
Preparing to unpack .../20-libnftables1_1.0.6-2+deb12u2_amd64.deb ...
Unpacking libnftables1:amd64 (1.0.6-2+deb12u2) ...
Selecting previously unselected package libnl-3-200:amd64.
Preparing to unpack .../21-libnl-3-200_3.7.0-0.2+b1_amd64.deb ...
Unpacking libnl-3-200:amd64 (3.7.0-0.2+b1) ...
Selecting previously unselected package criu.
Preparing to unpack .../22-criu_3.17.1-2+deb12u1_amd64.deb ...
Unpacking criu (3.17.1-2+deb12u1) ...
Selecting previously unselected package liberror-perl.
Preparing to unpack .../23-liberror-perl_0.17029-2_all.deb ...
Unpacking liberror-perl (0.17029-2) ...
Selecting previously unselected package git-man.
Preparing to unpack .../24-git-man_1%3a2.39.5-0+deb12u2_all.deb ...
Unpacking git-man (1:2.39.5-0+deb12u2) ...
Selecting previously unselected package git.
Preparing to unpack .../25-git_1%3a2.39.5-0+deb12u2_amd64.deb ...
Unpacking git (1:2.39.5-0+deb12u2) ...
Selecting previously unselected package libintl-perl.
Preparing to unpack .../26-libintl-perl_1.33-1_all.deb ...
Unpacking libintl-perl (1.33-1) ...
Selecting previously unselected package libintl-xs-perl.
Preparing to unpack .../27-libintl-xs-perl_1.33-1_amd64.deb ...
Unpacking libintl-xs-perl (1.33-1) ...
Selecting previously unselected package libmodule-find-perl.
Preparing to unpack .../28-libmodule-find-perl_0.16-2_all.deb ...
Unpacking libmodule-find-perl (0.16-2) ...
Selecting previously unselected package libproc-processtable-perl:amd64.
Preparing to unpack .../29-libproc-processtable-perl_0.634-1+b2_amd64.deb ...
Unpacking libproc-processtable-perl:amd64 (0.634-1+b2) ...
Selecting previously unselected package libsort-naturally-perl.
Preparing to unpack .../30-libsort-naturally-perl_1.03-4_all.deb ...
Unpacking libsort-naturally-perl (1.03-4) ...
Selecting previously unselected package libterm-readkey-perl.
Preparing to unpack .../31-libterm-readkey-perl_2.38-2+b1_amd64.deb ...
Unpacking libterm-readkey-perl (2.38-2+b1) ...
Selecting previously unselected package needrestart.
Preparing to unpack .../32-needrestart_3.6-4+deb12u3_all.deb ...
Unpacking needrestart (3.6-4+deb12u3) ...
Selecting previously unselected package patch.
Preparing to unpack .../33-patch_2.7.6-7_amd64.deb ...
Unpacking patch (2.7.6-7) ...
Setting up binutils-common:amd64 (2.40-2) ...
Setting up libctf-nobfd0:amd64 (2.40-2) ...
Setting up libnet1:amd64 (1.1.6+dfsg-3.2) ...
Setting up runc (1.1.5+ds1-1+deb12u1) ...
Setting up libjansson4:amd64 (2.14-2) ...
Setting up perl-modules-5.36 (5.36.0-7+deb12u2) ...
Setting up tini (0.19.0-1) ...
Setting up patch (2.7.6-7) ...
Setting up libgdbm-compat4:amd64 (1.23-3) ...
Setting up libprotobuf32:amd64 (3.21.12-3) ...
Setting up libnl-3-200:amd64 (3.7.0-0.2+b1) ...
Setting up git-man (1:2.39.5-0+deb12u2) ...
Setting up cgroupfs-mount (1.4) ...
Setting up libbinutils:amd64 (2.40-2) ...
Setting up python3-protobuf (3.21.12-3) ...
Setting up containerd (1.6.20~ds1-1+deb12u1) ...
Created symlink /etc/systemd/system/multi-user.target.wants/containerd.service → /lib/systemd/system/containerd.service.
Setting up libperl5.36:amd64 (5.36.0-7+deb12u2) ...
Setting up libctf0:amd64 (2.40-2) ...
Setting up libnftables1:amd64 (1.0.6-2+deb12u2) ...
Setting up docker.io (20.10.24+dfsg1-1+deb12u1) ...
Adding group `docker' (GID 109) ...
Done.
Created symlink /etc/systemd/system/multi-user.target.wants/docker.service → /lib/systemd/system/docker.service.
Created symlink /etc/systemd/system/sockets.target.wants/docker.socket → /lib/systemd/system/docker.socket.
Setting up perl (5.36.0-7+deb12u2) ...
Setting up libgprofng0:amd64 (2.40-2) ...
Setting up libmodule-find-perl (0.16-2) ...
Setting up libproc-processtable-perl:amd64 (0.634-1+b2) ...
Setting up criu (3.17.1-2+deb12u1) ...
Setting up libintl-perl (1.33-1) ...
Setting up libterm-readkey-perl (2.38-2+b1) ...
Setting up libsort-naturally-perl (1.03-4) ...
Setting up binutils-x86-64-linux-gnu (2.40-2) ...
Setting up binutils (2.40-2) ...
Setting up libintl-xs-perl (1.33-1) ...
Setting up liberror-perl (0.17029-2) ...
Setting up git (1:2.39.5-0+deb12u2) ...
Setting up needrestart (3.6-4+deb12u3) ...
Processing triggers for man-db (2.11.2-2) ...
Processing triggers for libc-bin (2.36-9+deb12u10) ...

Get:1 file:/etc/apt/mirrors/debian.list Mirrorlist [38 B]
Get:5 file:/etc/apt/mirrors/debian-security.list Mirrorlist [47 B]
Get:2 https://cdn-aws.deb.debian.org/debian bookworm InRelease [151 kB]
Get:3 https://cdn-aws.deb.debian.org/debian bookworm-updates InRelease [55.4 kB]
Get:4 https://cdn-aws.deb.debian.org/debian bookworm-backports InRelease [59.4 kB]
Get:6 https://cdn-aws.deb.debian.org/debian-security bookworm-security InRelease [48.0 kB]
Get:7 https://cdn-aws.deb.debian.org/debian bookworm/main Sources [9495 kB]
Get:8 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 Packages [8792 kB]
Get:9 https://cdn-aws.deb.debian.org/debian bookworm/main Translation-en [6109 kB]
Get:10 https://cdn-aws.deb.debian.org/debian bookworm-updates/main Sources [796 B]
Get:11 https://cdn-aws.deb.debian.org/debian bookworm-updates/main amd64 Packages [512 B]
Get:12 https://cdn-aws.deb.debian.org/debian bookworm-updates/main Translation-en [360 B]
Get:13 https://cdn-aws.deb.debian.org/debian bookworm-backports/main Sources [282 kB]
Get:14 https://cdn-aws.deb.debian.org/debian bookworm-backports/main amd64 Packages [285 kB]
Get:15 https://cdn-aws.deb.debian.org/debian bookworm-backports/main Translation-en [242 kB]
Get:16 https://cdn-aws.deb.debian.org/debian-security bookworm-security/main Sources [129 kB]
Get:17 https://cdn-aws.deb.debian.org/debian-security bookworm-security/main amd64 Packages [258 kB]
Get:18 https://cdn-aws.deb.debian.org/debian-security bookworm-security/main Translation-en [155 kB]
Fetched 26.1 MB in 4s (7332 kB/s)
Reading package lists...
Building dependency tree...
Reading state information...
6 packages can be upgraded. Run 'apt list --upgradable' to see them.
Reading package lists...
Building dependency tree...
Reading state information...
The following additional packages will be installed:
  binutils binutils-common binutils-x86-64-linux-gnu cgroupfs-mount containerd
  criu git git-man libbinutils libctf-nobfd0 libctf0 liberror-perl
  libgdbm-compat4 libgprofng0 libintl-perl libintl-xs-perl libjansson4
  libmodule-find-perl libnet1 libnftables1 libnl-3-200 libperl5.36
  libproc-processtable-perl libprotobuf32 libsort-naturally-perl
  libterm-readkey-perl needrestart patch perl perl-base perl-modules-5.36
  python3-protobuf runc tini
Suggested packages:
  binutils-doc containernetworking-plugins docker-doc aufs-tools btrfs-progs
  debootstrap rinse rootlesskit xfsprogs zfs-fuse | zfsutils-linux
  git-daemon-run | git-daemon-sysvinit git-doc git-email git-gui gitk gitweb
  git-cvs git-mediawiki git-svn needrestart-session | libnotify-bin
  iucode-tool ed diffutils-doc perl-doc libterm-readline-gnu-perl
  | libterm-readline-perl-perl make libtap-harness-archive-perl
The following NEW packages will be installed:
  binutils binutils-common binutils-x86-64-linux-gnu cgroupfs-mount containerd
  criu docker.io git git-man libbinutils libctf-nobfd0 libctf0 liberror-perl
  libgdbm-compat4 libgprofng0 libintl-perl libintl-xs-perl libjansson4
  libmodule-find-perl libnet1 libnftables1 libnl-3-200 libperl5.36
  libproc-processtable-perl libprotobuf32 libsort-naturally-perl
  libterm-readkey-perl needrestart patch perl perl-modules-5.36
  python3-protobuf runc tini
The following packages will be upgraded:
  perl-base
1 upgraded, 34 newly installed, 0 to remove and 5 not upgraded.
Need to get 93.1 MB of archives.
After this operation, 406 MB of additional disk space will be used.
Get:1 file:/etc/apt/mirrors/debian-security.list Mirrorlist [47 B]
Get:6 file:/etc/apt/mirrors/debian.list Mirrorlist [38 B]
Get:2 https://cdn-aws.deb.debian.org/debian-security bookworm-security/main amd64 perl-base amd64 5.36.0-7+deb12u2 [1609 kB]
Get:3 https://cdn-aws.deb.debian.org/debian-security bookworm-security/main amd64 perl-modules-5.36 all 5.36.0-7+deb12u2 [2815 kB]
Get:4 https://cdn-aws.deb.debian.org/debian-security bookworm-security/main amd64 libperl5.36 amd64 5.36.0-7+deb12u2 [4207 kB]
Get:5 https://cdn-aws.deb.debian.org/debian-security bookworm-security/main amd64 perl amd64 5.36.0-7+deb12u2 [239 kB]
Get:7 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libgdbm-compat4 amd64 1.23-3 [48.2 kB]
Get:8 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 runc amd64 1.1.5+ds1-1+deb12u1 [2710 kB]
Get:9 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 containerd amd64 1.6.20~ds1-1+deb12u1 [25.9 MB]
Get:10 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 tini amd64 0.19.0-1 [255 kB]
Get:11 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 docker.io amd64 20.10.24+dfsg1-1+deb12u1 [36.2 MB]
Get:12 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 binutils-common amd64 2.40-2 [2487 kB]
Get:13 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libbinutils amd64 2.40-2 [572 kB]
Get:14 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libctf-nobfd0 amd64 2.40-2 [153 kB]
Get:15 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libctf0 amd64 2.40-2 [89.8 kB]
Get:16 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libgprofng0 amd64 2.40-2 [812 kB]
Get:17 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libjansson4 amd64 2.14-2 [40.8 kB]
Get:18 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 binutils-x86-64-linux-gnu amd64 2.40-2 [2246 kB]
Get:19 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 binutils amd64 2.40-2 [65.0 kB]
Get:20 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 cgroupfs-mount all 1.4 [6276 B]
Get:21 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libprotobuf32 amd64 3.21.12-3 [932 kB]
Get:22 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 python3-protobuf amd64 3.21.12-3 [245 kB]
Get:23 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libnet1 amd64 1.1.6+dfsg-3.2 [60.3 kB]
Get:24 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libnftables1 amd64 1.0.6-2+deb12u2 [299 kB]
Get:25 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libnl-3-200 amd64 3.7.0-0.2+b1 [63.1 kB]
Get:26 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 criu amd64 3.17.1-2+deb12u1 [665 kB]
Get:27 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 liberror-perl all 0.17029-2 [29.0 kB]
Get:28 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 git-man all 1:2.39.5-0+deb12u2 [2053 kB]
Get:29 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 git amd64 1:2.39.5-0+deb12u2 [7260 kB]
Get:30 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libintl-perl all 1.33-1 [720 kB]
Get:31 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libintl-xs-perl amd64 1.33-1 [15.6 kB]
Get:32 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libmodule-find-perl all 0.16-2 [10.6 kB]
Get:33 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libproc-processtable-perl amd64 0.634-1+b2 [43.1 kB]
Get:34 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libsort-naturally-perl all 1.03-4 [13.1 kB]
Get:35 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 libterm-readkey-perl amd64 2.38-2+b1 [24.5 kB]
Get:36 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 needrestart all 3.6-4+deb12u3 [60.5 kB]
Get:37 https://cdn-aws.deb.debian.org/debian bookworm/main amd64 patch amd64 2.7.6-7 [128 kB]
apt-listchanges: Reading changelogs...
Fetched 93.1 MB in 1s (64.4 MB/s)
(Reading database ... 29492 files and directories currently installed.)
Preparing to unpack .../perl-base_5.36.0-7+deb12u2_amd64.deb ...
Unpacking perl-base (5.36.0-7+deb12u2) over (5.36.0-7+deb12u1) ...
Setting up perl-base (5.36.0-7+deb12u2) ...
Selecting previously unselected package perl-modules-5.36.
(Reading database ... 29492 files and directories currently installed.)
Preparing to unpack .../00-perl-modules-5.36_5.36.0-7+deb12u2_all.deb ...
Unpacking perl-modules-5.36 (5.36.0-7+deb12u2) ...
Selecting previously unselected package libgdbm-compat4:amd64.
Preparing to unpack .../01-libgdbm-compat4_1.23-3_amd64.deb ...
Unpacking libgdbm-compat4:amd64 (1.23-3) ...
Selecting previously unselected package libperl5.36:amd64.
Preparing to unpack .../02-libperl5.36_5.36.0-7+deb12u2_amd64.deb ...
Unpacking libperl5.36:amd64 (5.36.0-7+deb12u2) ...
Selecting previously unselected package perl.
Preparing to unpack .../03-perl_5.36.0-7+deb12u2_amd64.deb ...
Unpacking perl (5.36.0-7+deb12u2) ...
Selecting previously unselected package runc.
Preparing to unpack .../04-runc_1.1.5+ds1-1+deb12u1_amd64.deb ...
Unpacking runc (1.1.5+ds1-1+deb12u1) ...
Selecting previously unselected package containerd.
Preparing to unpack .../05-containerd_1.6.20~ds1-1+deb12u1_amd64.deb ...
Unpacking containerd (1.6.20~ds1-1+deb12u1) ...
Selecting previously unselected package tini.
Preparing to unpack .../06-tini_0.19.0-1_amd64.deb ...
Unpacking tini (0.19.0-1) ...
Selecting previously unselected package docker.io.
Preparing to unpack .../07-docker.io_20.10.24+dfsg1-1+deb12u1_amd64.deb ...
Unpacking docker.io (20.10.24+dfsg1-1+deb12u1) ...
Selecting previously unselected package binutils-common:amd64.
Preparing to unpack .../08-binutils-common_2.40-2_amd64.deb ...
Unpacking binutils-common:amd64 (2.40-2) ...
Selecting previously unselected package libbinutils:amd64.
Preparing to unpack .../09-libbinutils_2.40-2_amd64.deb ...
Unpacking libbinutils:amd64 (2.40-2) ...
Selecting previously unselected package libctf-nobfd0:amd64.
Preparing to unpack .../10-libctf-nobfd0_2.40-2_amd64.deb ...
Unpacking libctf-nobfd0:amd64 (2.40-2) ...
Selecting previously unselected package libctf0:amd64.
Preparing to unpack .../11-libctf0_2.40-2_amd64.deb ...
Unpacking libctf0:amd64 (2.40-2) ...
Selecting previously unselected package libgprofng0:amd64.
Preparing to unpack .../12-libgprofng0_2.40-2_amd64.deb ...
Unpacking libgprofng0:amd64 (2.40-2) ...
Selecting previously unselected package libjansson4:amd64.
Preparing to unpack .../13-libjansson4_2.14-2_amd64.deb ...
Unpacking libjansson4:amd64 (2.14-2) ...
Selecting previously unselected package binutils-x86-64-linux-gnu.
Preparing to unpack .../14-binutils-x86-64-linux-gnu_2.40-2_amd64.deb ...
Unpacking binutils-x86-64-linux-gnu (2.40-2) ...
Selecting previously unselected package binutils.
Preparing to unpack .../15-binutils_2.40-2_amd64.deb ...
Unpacking binutils (2.40-2) ...
Selecting previously unselected package cgroupfs-mount.
Preparing to unpack .../16-cgroupfs-mount_1.4_all.deb ...
Unpacking cgroupfs-mount (1.4) ...
Selecting previously unselected package libprotobuf32:amd64.
Preparing to unpack .../17-libprotobuf32_3.21.12-3_amd64.deb ...
Unpacking libprotobuf32:amd64 (3.21.12-3) ...
Selecting previously unselected package python3-protobuf.
Preparing to unpack .../18-python3-protobuf_3.21.12-3_amd64.deb ...
Unpacking python3-protobuf (3.21.12-3) ...
Selecting previously unselected package libnet1:amd64.
Preparing to unpack .../19-libnet1_1.1.6+dfsg-3.2_amd64.deb ...
Unpacking libnet1:amd64 (1.1.6+dfsg-3.2) ...
Selecting previously unselected package libnftables1:amd64.
Preparing to unpack .../20-libnftables1_1.0.6-2+deb12u2_amd64.deb ...
Unpacking libnftables1:amd64 (1.0.6-2+deb12u2) ...
Selecting previously unselected package libnl-3-200:amd64.
Preparing to unpack .../21-libnl-3-200_3.7.0-0.2+b1_amd64.deb ...
Unpacking libnl-3-200:amd64 (3.7.0-0.2+b1) ...
Selecting previously unselected package criu.
Preparing to unpack .../22-criu_3.17.1-2+deb12u1_amd64.deb ...
Unpacking criu (3.17.1-2+deb12u1) ...
Selecting previously unselected package liberror-perl.
Preparing to unpack .../23-liberror-perl_0.17029-2_all.deb ...
Unpacking liberror-perl (0.17029-2) ...
Selecting previously unselected package git-man.
Preparing to unpack .../24-git-man_1%3a2.39.5-0+deb12u2_all.deb ...
Unpacking git-man (1:2.39.5-0+deb12u2) ...
Selecting previously unselected package git.
Preparing to unpack .../25-git_1%3a2.39.5-0+deb12u2_amd64.deb ...
Unpacking git (1:2.39.5-0+deb12u2) ...
Selecting previously unselected package libintl-perl.
Preparing to unpack .../26-libintl-perl_1.33-1_all.deb ...
Unpacking libintl-perl (1.33-1) ...
Selecting previously unselected package libintl-xs-perl.
Preparing to unpack .../27-libintl-xs-perl_1.33-1_amd64.deb ...
Unpacking libintl-xs-perl (1.33-1) ...
Selecting previously unselected package libmodule-find-perl.
Preparing to unpack .../28-libmodule-find-perl_0.16-2_all.deb ...
Unpacking libmodule-find-perl (0.16-2) ...
Selecting previously unselected package libproc-processtable-perl:amd64.
Preparing to unpack .../29-libproc-processtable-perl_0.634-1+b2_amd64.deb ...
Unpacking libproc-processtable-perl:amd64 (0.634-1+b2) ...
Selecting previously unselected package libsort-naturally-perl.
Preparing to unpack .../30-libsort-naturally-perl_1.03-4_all.deb ...
Unpacking libsort-naturally-perl (1.03-4) ...
Selecting previously unselected package libterm-readkey-perl.
Preparing to unpack .../31-libterm-readkey-perl_2.38-2+b1_amd64.deb ...
Unpacking libterm-readkey-perl (2.38-2+b1) ...
Selecting previously unselected package needrestart.
Preparing to unpack .../32-needrestart_3.6-4+deb12u3_all.deb ...
Unpacking needrestart (3.6-4+deb12u3) ...
Selecting previously unselected package patch.
Preparing to unpack .../33-patch_2.7.6-7_amd64.deb ...
Unpacking patch (2.7.6-7) ...
Setting up binutils-common:amd64 (2.40-2) ...
Setting up libctf-nobfd0:amd64 (2.40-2) ...
Setting up libnet1:amd64 (1.1.6+dfsg-3.2) ...
Setting up runc (1.1.5+ds1-1+deb12u1) ...
Setting up libjansson4:amd64 (2.14-2) ...
Setting up perl-modules-5.36 (5.36.0-7+deb12u2) ...
Setting up tini (0.19.0-1) ...
Setting up patch (2.7.6-7) ...
Setting up libgdbm-compat4:amd64 (1.23-3) ...
Setting up libprotobuf32:amd64 (3.21.12-3) ...
Setting up libnl-3-200:amd64 (3.7.0-0.2+b1) ...
Setting up git-man (1:2.39.5-0+deb12u2) ...
Setting up cgroupfs-mount (1.4) ...
Setting up libbinutils:amd64 (2.40-2) ...
Setting up python3-protobuf (3.21.12-3) ...
Setting up containerd (1.6.20~ds1-1+deb12u1) ...
Created symlink /etc/systemd/system/multi-user.target.wants/containerd.service → /lib/systemd/system/containerd.service.
Setting up libperl5.36:amd64 (5.36.0-7+deb12u2) ...
Setting up libctf0:amd64 (2.40-2) ...
Setting up libnftables1:amd64 (1.0.6-2+deb12u2) ...
Setting up docker.io (20.10.24+dfsg1-1+deb12u1) ...
Adding group `docker' (GID 109) ...
Done.
Created symlink /etc/systemd/system/multi-user.target.wants/docker.service → /lib/systemd/system/docker.service.
Created symlink /etc/systemd/system/sockets.target.wants/docker.socket → /lib/systemd/system/docker.socket.
Setting up perl (5.36.0-7+deb12u2) ...
Setting up libgprofng0:amd64 (2.40-2) ...
Setting up libmodule-find-perl (0.16-2) ...
Setting up libproc-processtable-perl:amd64 (0.634-1+b2) ...
Setting up criu (3.17.1-2+deb12u1) ...
Setting up libintl-perl (1.33-1) ...
Setting up libterm-readkey-perl (2.38-2+b1) ...
Setting up libsort-naturally-perl (1.03-4) ...
Setting up binutils-x86-64-linux-gnu (2.40-2) ...
Setting up binutils (2.40-2) ...
Setting up libintl-xs-perl (1.33-1) ...
Setting up liberror-perl (0.17029-2) ...
Setting up git (1:2.39.5-0+deb12u2) ...
Setting up needrestart (3.6-4+deb12u3) ...
Processing triggers for man-db (2.11.2-2) ...
Processing triggers for libc-bin (2.36-9+deb12u10) ...

Executing command: sudo systemctl start docker

Executing command: sudo usermod -aG docker admin
2025-05-14 11:45:11,293 [INFO] 
2025-05-14 11:45:11,436 [INFO] 

Executing command: docker run -d -p 8080:80 --name nginx nginx

2025-05-14 11:45:11,563 [INFO] 
Starting health check monitor loop...
2025-05-14 11:45:11,634 [INFO] Starting health check monitor loop...
Connection error: HTTPConnectionPool(host='18.192.13.199', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a2633e0>: Failed to establish a new connection: [Errno 61] Connection refused'))
2025-05-14 11:45:21,660 [ERROR] Connection error: HTTPConnectionPool(host='18.192.13.199', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a2633e0>: Failed to establish a new connection: [Errno 61] Connection refused'))
2025-05-14 11:45:31,682 [ERROR] Connection error: HTTPConnectionPool(host='18.192.13.199', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a263ad0>: Failed to establish a new connection: [Errno 61] Connection refused'))
Connection error: HTTPConnectionPool(host='18.192.13.199', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a263ad0>: Failed to establish a new connection: [Errno 61] Connection refused'))
2025-05-14 11:45:41,700 [ERROR] Connection error: HTTPConnectionPool(host='18.192.13.199', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x107cb2cc0>: Failed to establish a new connection: [Errno 61] Connection refused'))
Connection error: HTTPConnectionPool(host='18.192.13.199', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x107cb2cc0>: Failed to establish a new connection: [Errno 61] Connection refused'))
2025-05-14 11:45:51,727 [ERROR] Connection error: HTTPConnectionPool(host='18.192.13.199', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a2634a0>: Failed to establish a new connection: [Errno 61] Connection refused'))
Connection error: HTTPConnectionPool(host='18.192.13.199', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a2634a0>: Failed to establish a new connection: [Errno 61] Connection refused'))
2025-05-14 11:46:01,754 [ERROR] Connection error: HTTPConnectionPool(host='18.192.13.199', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a2b0380>: Failed to establish a new connection: [Errno 61] Connection refused'))
2025-05-14 11:46:01,754 [WARNING] Restarting the nginx container...
Connection error: HTTPConnectionPool(host='18.192.13.199', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a2b0380>: Failed to establish a new connection: [Errno 61] Connection refused'))
Restarting the nginx container...
2025-05-14 11:46:01,805 [INFO] Connected (version 2.0, client OpenSSH_9.2p1)
2025-05-14 11:46:01,996 [INFO] Authentication (publickey) successful!
2025-05-14 11:46:02,079 [INFO] 

2025-05-14 11:46:12,098 [ERROR] Connection error: HTTPConnectionPool(host='18.192.13.199', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a2b18b0>: Failed to establish a new connection: [Errno 61] Connection refused'))
Connection error: HTTPConnectionPool(host='18.192.13.199', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a2b18b0>: Failed to establish a new connection: [Errno 61] Connection refused'))
2025-05-14 11:46:22,128 [ERROR] Connection error: HTTPConnectionPool(host='18.192.13.199', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a219f70>: Failed to establish a new connection: [Errno 61] Connection refused'))
Connection error: HTTPConnectionPool(host='18.192.13.199', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a219f70>: Failed to establish a new connection: [Errno 61] Connection refused'))
Connection error: HTTPConnectionPool(host='18.192.13.199', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a2637a0>: Failed to establish a new connection: [Errno 61] Connection refused'))
2025-05-14 11:46:32,158 [ERROR] Connection error: HTTPConnectionPool(host='18.192.13.199', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a2637a0>: Failed to establish a new connection: [Errno 61] Connection refused'))
Connection error: HTTPConnectionPool(host='18.192.13.199', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a263c50>: Failed to establish a new connection: [Errno 61] Connection refused'))
2025-05-14 11:46:42,182 [ERROR] Connection error: HTTPConnectionPool(host='18.192.13.199', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a263c50>: Failed to establish a new connection: [Errno 61] Connection refused'))
Connection error: HTTPConnectionPool(host='18.192.13.199', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a2b1370>: Failed to establish a new connection: [Errno 61] Connection refused'))
Restarting the nginx container...
2025-05-14 11:46:52,208 [ERROR] Connection error: HTTPConnectionPool(host='18.192.13.199', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a2b1370>: Failed to establish a new connection: [Errno 61] Connection refused'))
2025-05-14 11:46:52,208 [WARNING] Restarting the nginx container...
2025-05-14 11:46:52,269 [INFO] Connected (version 2.0, client OpenSSH_9.2p1)
2025-05-14 11:46:52,478 [INFO] Authentication (publickey) successful!
2025-05-14 11:46:52,604 [INFO] 

Nginx is running.
2025-05-14 11:47:02,667 [INFO] Nginx is running.
Nginx is running.
2025-05-14 11:47:12,709 [INFO] Nginx is running.
2025-05-14 11:47:22,766 [INFO] Nginx is running.
Nginx is running.
2025-05-14 11:47:32,812 [INFO] Nginx is running.
Nginx is running.
Nginx is running.
2025-05-14 11:47:42,866 [INFO] Nginx is running.
```

</details>








<details>
<summary>Solution 4: Working with ECR in AWS </summary>
 <br>

> EXERCISE 4: Working with ECR in AWS

- Get all the repositories in ECR
- Print the name of each repository
- Choose one specific repository and for that repository, list all the image tags inside, sorted by date. Where the most recent image tag is on top

Step 1: I created my own ecr repo: 524196012679.dkr.ecr.eu-central-1.amazonaws.com/sg/java-app-demos 

![Bildschirmfoto 2025-05-14 um 15 42 18](https://github.com/user-attachments/assets/5410a0bd-9e49-4da9-96bc-e5b61dd342d1)

my tagged images: 

![Bildschirmfoto 2025-05-14 um 15 53 20](https://github.com/user-attachments/assets/b9f70f21-2adc-4505-b6db-ab2d8a1f5813)



Step 2: Executed my script with my new created ecr-repo: sg/java-app-demos

```sh
import boto3
import logging
from operator import itemgetter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)

ecr_client = boto3.client('ecr')

# Get all ECR repositories
try:
    repos = ecr_client.describe_repositories()['repositories']
    logging.info("Fetched ECR repositories successfully.")
    print("Available ECR repositories:")
    for repo in repos:
        print(repo['repositoryName'])
        logging.info(f"Repository found: {repo['repositoryName']}")
except Exception as e:
    logging.error(f"Error fetching ECR repositories: {e}")
    raise

print("-----------------------")

# For one specific repo, get all the images and print them sorted by date
repo_name = "sg/java-app-demos"

try:
    images = ecr_client.describe_images(repositoryName=repo_name)
    logging.info(f"Fetched images from repository: {repo_name}")
except Exception as e:
    logging.error(f"Error fetching images from repository '{repo_name}': {e}")
    raise

image_tags = []

for image in images['imageDetails']:
    tags = image.get('imageTags', ['<untagged>'])  # Handle images with no tag
    pushed_at = image['imagePushedAt']
    image_tags.append({
        'tag': tags,
        'pushed_at': pushed_at
    })
    logging.debug(f"Image found - Tags: {tags}, Pushed At: {pushed_at}")

# Sort images by pushed date descending
images_sorted = sorted(image_tags, key=itemgetter("pushed_at"), reverse=True)

print(f"Images for repository '{repo_name}' sorted by date:")
for image in images_sorted:
    print(image)
    logging.info(f"Image: {image}")



```
Output of my exercise-4.py script:

![Bildschirmfoto 2025-05-14 um 15 53 11](https://github.com/user-attachments/assets/fac74bf4-71a0-4ec5-a7be-212a23a830ba)



</details>


<details>
<summary>Solution 5: Python in Jenkins Pipeline </summary>
 <br>

> EXERCISE 5: Python in Jenkins Pipeline
Create a Jenkins job that fetches all the available images from your application's ECR repository using Python. It allows the user to select the image from the list through user input and deploys the selected image to the EC2 server using Python.

Instructions

Do the following preparation manually:

- Start EC2 instance and install Docker on it
- Install Python, Pip and all needed Python dependencies in Jenkins
- Create 3 Docker images with tags 1.0, 2.0, 3.0 from one of the previous projects


Once all the above is configured, create a Jenkins Pipeline with the following steps:

- Fetch all 3 images from the ECR repository (using Python)
- Let the user select the image from the list (hint: https://www.jenkins.io/doc/pipeline/steps/pipeline-input-step/)
- SSH into the EC2 server (using Python)
- Run docker login to authenticate with ECR repository (using Python)
- Start the container from the selected image from step 2 on EC2 instance (using Python)
- Validate that the application was successfully started and is accessible by sending a request to the application (using Python)




Code

# In exercise repo you will find the Jenkinsfile that executes 3 python scripts for different stages:
- get-images.py
- deploy.py
- validate.py

# Before executing the Jenkins pipeline, set the following environment variable values inside Jenkinsfile
- ECR_REPO_NAME
- EC2_SERVER
- ECR_REGISTRY
- CONTAINER_PORT
- HOST_PORT
- AWS_DEFAULT_REGION

Step 1: In Step 1, I installed Python 3 and then used pip3 to install the following packages, since my Jenkins is installed on my Mac.

![Bildschirmfoto 2025-05-15 um 09 36 41](https://github.com/user-attachments/assets/07d1d6ad-d19e-4650-abc8-7d9f158fde60)

Step2 :In step 2, I modified  the Jenkinsfile to reflect the required changes for deployment.

```sh
#!/usr/bin/env groovy

pipeline {
    agent any
    environment {
        ECR_REPO_NAME = 'sg/java-app-demos' // SET VALUE
        EC2_SERVER = '3.122.118.194' // SET VALUE
        EC2_USER = 'admin'

        // will be set to the location of the SSH key file that is temporarily created
        SSH_KEY_FILE = credentials('ssh_aws_access')

        ECR_REGISTRY = '524196012679.dkr.ecr.eu-central-1.amazonaws.com' // SET VALUE
        DOCKER_USER = 'AWS'
        DOCKER_PWD = credentials('ecr-repo-pwd')
        CONTAINER_PORT = '80' // SET VALUE
        HOST_PORT = '8080' // SET VALUE

        AWS_ACCESS_KEY_ID = credentials('jenkins_aws_access_key_id')
        AWS_SECRET_ACCESS_KEY = credentials('jenkins_aws_secret_access_key')
        AWS_DEFAULT_REGION = 'eu-central-1' // SET VALUE
    }
    stages {
        stage('select image version') {
            steps {
               script {
                  echo 'fetching available image versions'
                  def result = sh(script: 'python3 get-images.py', returnStdout: true).trim()
                  // split returns an Array, but choices expects either a List or String, so we do "as List"
                  def tags = result.split('\n') as List
                  version_to_deploy = input message: 'Select version to deploy', ok: 'Deploy', parameters: [choice(name: 'Select version', choices: tags)]
                  // put together the full image name
                  env.DOCKER_IMAGE = "${ECR_REGISTRY}/${ECR_REPO_NAME}:${version_to_deploy}"
                  echo env.DOCKER_IMAGE
               }
            }
        }
        stage('deploying image') {
            steps {
                script {
                   echo 'deploying docker image to EC2...'
                   def result = sh(script: 'python3 deploy.py', returnStdout: true).trim()
                   echo result
                }
            }
        }
        stage('validate deployment') {
            steps {
                script {
                   echo 'validating that the application was deployed successfully...'
                   def result = sh(script: 'python3 validate.py', returnStdout: true).trim()
                   echo result
                }
            }
        }
    }
}
```

Step 3: In step 3, I created my own repo for Jenkins in github : 

![Bildschirmfoto 2025-05-15 um 10 29 21](https://github.com/user-attachments/assets/f7d8368b-998f-41f4-9085-aa93c698925a)

Step 4: In step 4, I created my Jenkins pipeline job from Github and the credentials: 


![Bildschirmfoto 2025-05-15 um 12 06 56](https://github.com/user-attachments/assets/e80aa830-723c-4de2-b9eb-169b88a6ad9d)


![Bildschirmfoto 2025-05-15 um 12 07 15](https://github.com/user-attachments/assets/f46df8a1-606e-444c-85e9-2f03f706435d)


Step 5: In step 5, I executed my Jenkins pipeline job: 

![Bildschirmfoto 2025-05-15 um 11 52 50](https://github.com/user-attachments/assets/a2597974-e5a8-4469-9ea3-7c3d69f06c77)

My results are visible in the Jenkins job. I selected the tag v1 for deployment, and my NGINX container was successfully deployed, as shown in the screenshots and Jenkins logs.

![Bildschirmfoto 2025-05-15 um 11 53 19](https://github.com/user-attachments/assets/8ef7de91-451c-45b9-9eb3-90c9f7efe59d)

![Bildschirmfoto 2025-05-15 um 11 53 44](https://github.com/user-attachments/assets/a886e0bb-5e01-4a31-b6f8-a2390b16c1b0)

![Bildschirmfoto 2025-05-15 um 11 51 46](https://github.com/user-attachments/assets/a31ce3b3-a938-45c4-8254-cf5b3b01591c)

my jenkins logs:
```sh
Started by user SG

Obtained Jenkinsfile from git https://github.com/Saban39/python-boto3-automation.git/
[Pipeline] Start of Pipeline
[Pipeline] node
Running on Jenkins
 in /var/root/.jenkins/workspace/python-boto3-automation
[Pipeline] {
[Pipeline] stage
[Pipeline] { (Declarative: Checkout SCM)
[Pipeline] checkout
The recommended git tool is: NONE
using credential jenkins-access
 > git rev-parse --resolve-git-dir /var/root/.jenkins/workspace/python-boto3-automation/.git # timeout=10
Fetching changes from the remote Git repository
 > git config remote.origin.url https://github.com/Saban39/python-boto3-automation.git/ # timeout=10
Fetching upstream changes from https://github.com/Saban39/python-boto3-automation.git/
 > git --version # timeout=10
 > git --version # 'git version 2.39.5 (Apple Git-154)'
using GIT_ASKPASS to set credentials 
 > git fetch --tags --force --progress -- https://github.com/Saban39/python-boto3-automation.git/ +refs/heads/*:refs/remotes/origin/* # timeout=10
 > git rev-parse refs/remotes/origin/main^{commit} # timeout=10
Checking out Revision 0da61964ee559da857b92d0e667481ab2f135b31 (refs/remotes/origin/main)
 > git config core.sparsecheckout # timeout=10
 > git checkout -f 0da61964ee559da857b92d0e667481ab2f135b31 # timeout=10
Commit message: "test"
 > git rev-list --no-walk 0da61964ee559da857b92d0e667481ab2f135b31 # timeout=10
[Pipeline] }
[Pipeline] // stage
[Pipeline] withEnv
[Pipeline] {
[Pipeline] withCredentials
Masking supported pattern matches of $AWS_ACCESS_KEY_ID or $AWS_SECRET_ACCESS_KEY or $DOCKER_PWD or $SSH_KEY_FILE or $SSH_KEY_FILE_PSW
[Pipeline] {
[Pipeline] withEnv
[Pipeline] {
[Pipeline] stage
[Pipeline] { (select image version)
[Pipeline] script
[Pipeline] {
[Pipeline] echo
fetching available image versions
[Pipeline] sh
+ python3 get-images.py
[Pipeline] input
Input requested
Approved by SG

Did you forget the `def` keyword? WorkflowScript seems to be setting a field named version_to_deploy (to a value of type String) which could lead to memory leaks or other issues.
[Pipeline] echo
524196012679.dkr.ecr.eu-central-1.amazonaws.com/sg/java-app-demos:v1
[Pipeline] }

[Pipeline] // script
[Pipeline] }
[Pipeline] // stage
[Pipeline] stage
[Pipeline] { (deploying image)
[Pipeline] script
[Pipeline] {

[Pipeline] echo
deploying docker image to EC2...
[Pipeline] sh
+ python3 deploy.py

Exception ignored in: <function BufferedFile.__del__ at 0x102d6a940>
Traceback (most recent call last):
  File "/Library/Python/3.9/site-packages/paramiko/file.py", line 67, in __del__
  File "/Library/Python/3.9/site-packages/paramiko/channel.py", line 1390, in close
  File "/Library/Python/3.9/site-packages/paramiko/channel.py", line 989, in shutdown_write
  File "/Library/Python/3.9/site-packages/paramiko/channel.py", line 965, in shutdown
  File "/Library/Python/3.9/site-packages/paramiko/transport.py", line 1971, in _send_user_message
AttributeError: 'NoneType' object has no attribute 'time'
[Pipeline] echo
['Login Succeeded\n']
['62290ca54e43b71c21551c8b36043216214ca0eccb429c7e7f45b13a7f8b8975\n']
['Login Succeeded\n']
['2f0eaba845a5a12ff559b340fa875377d4ba4167db3991adbae9512e481da87f\n']
[Pipeline] }
[Pipeline] // script
[Pipeline] }
[Pipeline] // stage

[Pipeline] stage
[Pipeline] { (validate deployment)
[Pipeline] script
[Pipeline] {
[Pipeline] echo
validating that the application was deployed successfully...
[Pipeline] sh

+ python3 validate.py

[Pipeline] echo
Application is running successfully!
[Pipeline] }
[Pipeline] // script
[Pipeline] }

[Pipeline] // stage
[Pipeline] }
[Pipeline] // withEnv
[Pipeline] }
[Pipeline] // withCredentials
[Pipeline] }
[Pipeline] // withEnv

[Pipeline] }
[Pipeline] // node
[Pipeline] End of Pipeline
Finished: SUCCESS



```

</details>

