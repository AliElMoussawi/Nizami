import os
from io import StringIO

import paramiko

# EC2 SSH details
EC2_HOST = "api.app.nizami.ai"
EC2_USER = "ubuntu"
EC2_KEY = os.getenv("EC2_KEY")


def deploy(ec2_key):
    key = paramiko.RSAKey.from_private_key(StringIO(ec2_key))

    with paramiko.SSHClient() as client:
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(EC2_HOST, username=EC2_USER, pkey=key, banner_timeout=120)

        # Pull the latest changes from GitLab
        command = ' && '.join([
            "cd /home/ubuntu/app_python/current/",
            "git pull origin master",
            "python3 -m venv .venv",
            "source .venv/bin/activate",  # Activate virtualenv
            "pip install -r requirements.txt",  # Install dependencies
            "python3 manage.py migrate",  # Apply migrations
            "sudo systemctl restart uvicorn",  # Restart Uvicorn to pick up changes
            'sudo supervisorctl reload', # Reload supervisor
        ])

        # for command in commands:
        print('executing', command)

        stdin, stdout, stderr = client.exec_command(command)
        print(stdout.read().decode())
        exit_status = stdout.channel.recv_exit_status()

        if exit_status:
            raise Exception(exit_status)


if __name__ == '__main__':
    deploy(EC2_KEY)
