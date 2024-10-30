import pexpect
command = f"sudo nmcli -t -f SSID,SIGNAL,CHAN,ACTIVE,SECURITY dev wifi"
child = pexpect.spawn(command)
child.expect_exact("[sudo] password for hao: ")
child.sendline("1")
child.expect(pexpect.EOF)
print(child.before.decode('utf-8'))