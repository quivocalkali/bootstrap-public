'''
Export AWS kali secrets environment variables before running
'''
import os
import subprocess
import sys
import time
import webbrowser

user_home = os.path.expanduser("~")
ssh_dir = user_home + "/.ssh"
github_key_path = ssh_dir + "/id_ed25519.github"
ssh_config_path = ssh_dir + "/config"

# *********************************

os.system('sudo echo "[*] User password accepted"')

print('[*] Installing AWS cli')

aws_version_result = subprocess.run(['which', 'aws'], capture_output=True, text=True)

install_aws_cmd = f'''
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "{user_home}/awscliv2.zip"
    unzip {user_home}/awscliv2.zip
    sudo ./aws/install
'''

aws_cli_installed = aws_version_result.returncode == 0

if not aws_cli_installed:
    result = subprocess.run(install_aws_cmd, shell=True, capture_output=True, text=True)

if aws_cli_installed:
    print("[*] AWS CLI already installed")
elif result.returncode == 0:
    print("[+] AWS CLI install successful!")
else:
    print("[-] AWS CLI install error:")
    print(result.stderr)

print('[*] Creating .ssh directory')

if not os.path.exists(ssh_dir):
    os.makedirs(ssh_dir)

print('[*] Fetching secrets from AWS', file=sys.stderr)

secrets = [
    {"name": "/kali/tomguerneykali-github-ssh-private-key", "filepath": github_key_path}
]

for secret in secrets:
    get_secret_cmd = f'aws ssm get-parameters --name "{secret["name"]}" --with-decryption --query "Parameters[*].Value" --output text > {secret["filepath"]}'
    result = subprocess.run(get_secret_cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print("[+] AWS CLI install successful!")
    else:
        print("[-] AWS CLI install error:")
        print(result.stderr)

# *********************************

print('[*] Updating ssh identity file')

with open (ssh_config_path, "w") as file:
    file.write(f"IdentityFile {github_key_path}")

print('[*] Modifying GitHub key permissions')

os.chmod(github_key_path, 0o600)

# *********************************

print('[*] Opening and closing firefox to create initial profile')

time.sleep(1)
webbrowser.get('firefox').open_new("http://www.example.com")
time.sleep(6)
os.system("pkill firefox")

# *********************************

print('[*] Cloning ansible repo and checking out CCX branch')

os.system("GIT_SSH_COMMAND=\"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null\" git clone git@github.com:tomguerneykali/ansible.git")
os.system("git fetch --all")

# *********************************

print('[*] Updating apt')
os.system('sudo apt update')

print('[*] Installing ansible')
os.system('sudo apt install ansible-core -y')

print('[*] Symlinking python')
if not os.path.exists('/usr/bin/python'):
    os.system('sudo ln -s /usr/bin/python3 /usr/bin/python')

print('[*] Run ansible playbook: ansible-playbook playbook.yml (with --skip-tags if necessary)')