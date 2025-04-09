'''
Export AWS kali secrets environment variables before running
'''
import os
import getpass
import subprocess
import sys
import time
import webbrowser

def run_cmd(cmd, name, input=None, check=True, capture_output=None):
    result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True, input=input, check=check)
    success = result.returncode == 0
    
    if success:
        print(f"[+] {name} command successful")
    else:
        if check:
            print(f"[-] {name} command error:")
            if result.stderr: print(result.stderr)
        else:
            print(f"[!] {name} command returned code {result.returncode}")

    return { "success": success, "stdout": result.stdout }

# *********************************

user_home = os.path.expanduser("~")

# *********************************

password = getpass.getpass("Enter password: ")

run_cmd(f'sudo -S echo "[*] User password accepted"', "Validate password", password)

# *********************************

print('[*] Installing AWS CLI')

aws_cli_installed = run_cmd('which aws', "Check AWS CLI installation", check=False)["success"]

if not aws_cli_installed:
    install_aws_cli_result = run_cmd(f'''
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "{user_home}/awscliv2.zip"
        unzip {user_home}/awscliv2.zip
        sudo ./aws/install
    ''', "Install AWS CLI")
else:
    print("[*] AWS CLI already installed")


# *********************************

print('[*] Removing existing gnome keyring')

run_cmd("rm ~/.local/share/keyrings/login.keyring", "Remove existing gnome keyring")

print('[*] Unlocking gnome keyring')

run_cmd(f'gnome-keyring-daemon --replace --unlock', "Unlock gnome keyring", password)

# *********************************

print('[*] Installing GitHub CLI')

gh_cli_installed = run_cmd('which gh', "Check GitHub CLI installation", check=False, capture_output=False)["success"]

if not gh_cli_installed:
    run_cmd('''
        sudo mkdir -p -m 755 /etc/apt/keyrings \
        && out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        && cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
        && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
        && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
        && sudo apt update \
        && sudo apt install gh -y
    ''', "Install GitHub CLI")
else:
    print("[*] GitHub CLI already installed")

# *********************************

print('[*] Fetching PAT from AWS', file=sys.stderr)

github_pat = run_cmd(f'aws ssm get-parameters --name "/kali/tomguerneykali-pat" --with-decryption --query "Parameters[*].Value" --output text', "Fetch GitHub PAT from AWS", capture_output=True)["stdout"]

# *********************************

print('[*] Authing GitHub CLI', file=sys.stderr)

run_cmd('gh auth login --with-token', "Auth GitHub CLI", github_pat)

# *********************************

print('[*] Opening and closing firefox to create initial profile')

time.sleep(1)
webbrowser.get('firefox').open_new("http://www.example.com")
time.sleep(6)
os.system("pkill firefox")

# *********************************

print('[*] Cloning ansible repo')

run_cmd("gh repo clone tomguerneykali/ansible", "Clone ansible repo")

# *********************************

print('[*] Updating apt')
run_cmd('sudo apt update', "Update apt")

print('[*] Installing ansible')
run_cmd('sudo apt install ansible-core -y', "Install ansible")

if not os.path.exists('/usr/bin/python'):
    print('[*] Symlinking python')
    run_cmd('sudo ln -s /usr/bin/python3 /usr/bin/python', "Symlink python")

print('[*] Run ansible playbook: ansible-playbook ./ansible/playbook.yml (with --skip-tags if necessary)')
