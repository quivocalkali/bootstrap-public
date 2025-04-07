'''
Export AWS kali secrets environment variables before running
'''
import os
import subprocess
import sys
import time
import webbrowser

# *********************************

user_home = os.path.expanduser("~")

os.system('sudo echo "[*] User password accepted"')

print('[*] Installing AWS cli')

aws_version_result = subprocess.run(['which', 'aws'], capture_output=True, text=True)

install_aws_cmd = '''
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "~/awscliv2.zip"
    unzip ~/awscliv2.zip
    sudo ./aws/install
'''

aws_cli_installed = aws_version_result.returncode == 0

if not aws_cli_installed:
    install_aws_cli_result = subprocess.run(install_aws_cmd, shell=True, capture_output=True, text=True)

if aws_cli_installed:
    print("[*] AWS CLI already installed")
elif install_aws_cli_result.returncode == 0:
    print("[+] AWS CLI install successful!")
else:
    print("[-] AWS CLI install error:")
    print(install_aws_cli_result.stderr)

print('[*] Installing gh cli')

install_gh_cmd = '''
    (type -p wget >/dev/null || (sudo apt update && sudo apt-get install wget -y)) \
        && sudo mkdir -p -m 755 /etc/apt/keyrings \
            && out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
            && cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
        && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
        && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
        && sudo apt update \
        && sudo apt install gh -y
'''

install_gh_result = subprocess.run(install_aws_cmd, shell=True, capture_output=True, text=True)

if install_gh_result.returncode == 0:
    print("[+] GitHub CLI install successful!")
else:
    print("[-] GitHub CLI install error:")
    print(install_gh_result.stderr)

print('[*] Fetching PAT from AWS', file=sys.stderr)

get_pat_cmd = f'aws ssm get-parameters --name "/kali/tomguerneykali-pat" --with-decryption --query "Parameters[*].Value" --output text'
get_pat_result = subprocess.run(get_pat_cmd, shell=True, capture_output=True, text=True)

if get_pat_result.returncode == 0:
    print("[+] PAT retrieval successful!")
else:
    print("[-] PAT retrieval error:")
    print(get_pat_result.stderr)

# *********************************

print('[*] Opening and closing firefox to create initial profile')

time.sleep(1)
webbrowser.get('firefox').open_new("http://www.example.com")
time.sleep(6)
os.system("pkill firefox")

# *********************************

print('[*] Cloning ansible repo')

os.system("gh repo clone tomguerneykali/ansible")

# *********************************

print('[*] Updating apt')
os.system('sudo apt update')

print('[*] Installing ansible')
os.system('sudo apt install ansible-core -y')

print('[*] Symlinking python')
if not os.path.exists('/usr/bin/python'):
    os.system('sudo ln -s /usr/bin/python3 /usr/bin/python')

print('[*] Run ansible playbook: ansible-playbook ./ansible/playbook.yml (with --skip-tags if necessary)')