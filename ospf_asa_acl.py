from netmiko import ConnectHandler

# Define the credentials
username = "manager"
password = "test123"
enable_secret = "cisco"

# Define the list of devices and their specific configurations
devices = [
    {
        "ip": "10.230.230.18",
        "hostname": "R8-PRD",
        "device_type": "cisco_ios",
        "commands": [
            "interface Ethernet0/1",
            "description Link to R1",
            "ip address 10.1.8.1 255.255.255.252",
            "duplex auto",
            "no shutdown",
            "interface Ethernet0/2",
            "description LAN Interface",
            "ip address 10.10.10.1 255.255.255.0",
            "duplex auto",
            "no shutdown",
            "interface Ethernet0/3",
            "duplex auto",
            "no shutdown",
            "no router rip",
            "router ospf 1",
            "network 10.1.8.0 0.0.0.3 area 0",
            "network 10.10.10.0 0.0.0.255 area 0",
            "passive-interface Ethernet0/2",
            "ip access-list standard SSH_ACL",
            "permit host 10.230.230.40",
            "line vty 0 4",
            "access-class SSH_ACL in"
        ]
    },
    {
        "ip": "10.230.230.11",
        "hostname": "R1-PRD",
        "device_type": "cisco_ios",
        "commands": [
            "interface Ethernet0/1",
            "description Link to R8",
            "ip address 10.1.8.2 255.255.255.252",
            "duplex auto",
            "no shutdown",
            "interface Ethernet0/2",
            "description Link to R2",
            "ip address 10.1.12.1 255.255.255.252",
            "duplex auto",
            "no shutdown",
            "interface Ethernet0/3",
            "duplex auto",
            "no shutdown",
            "no router rip",
            "router ospf 1",
            "network 10.1.8.0 0.0.0.3 area 0",
            "network 10.1.12.0 0.0.0.3 area 0",
            "ip access-list standard SSH_ACL",
            "permit host 10.230.230.40",
            "line vty 0 4",
            "access-class SSH_ACL in"
        ]
    },
    {
        "ip": "10.230.230.12",
        "hostname": "R2-PRD",
        "device_type": "cisco_ios",
        "commands": [
            "interface Ethernet0/1",
            "description Link to R7",
            "ip address 10.1.27.1 255.255.255.252",
            "duplex auto",
            "no shutdown",
            "interface Ethernet0/2",
            "description Link to R1",
            "ip address 10.1.12.2 255.255.255.252",
            "duplex auto",
            "no shutdown",
            "interface Ethernet0/3",
            "duplex auto",
            "no shutdown",
            "no router rip",
            "router ospf 1",
            "network 10.1.12.0 0.0.0.3 area 0",
            "network 10.1.27.0 0.0.0.3 area 0",
            "ip access-list standard SSH_ACL",
            "permit host 10.230.230.40",
            "line vty 0 4",
            "access-class SSH_ACL in"
        ]
    },
    {
        "ip": "10.230.230.17",
        "hostname": "R7-PRD-inet",
        "device_type": "cisco_ios",
        "commands": [
            "interface Ethernet0/2",
            "description Link to ASA",
            "ip address 10.254.254.253 255.255.255.252",
            "no shutdown",
            "no router rip",
            "ip route 0.0.0.0 0.0.0.0 10.254.254.254",
            "router ospf 1",
            "network 10.1.27.0 0.0.0.3 area 0",
            "default-information originate",
            "ip access-list standard SSH_ACL",
            "permit host 10.230.230.40",
            "line vty 0 4",
            "access-class SSH_ACL in"
        ]
    },
    {
        "ip": "10.230.230.55",
        "hostname": "ASA_8_4",
        "device_type": "cisco_asa",
        "commands": [
            "hostname FIREWALL-PRD",
            "interface Ethernet0",
            "nameif inside",
            "security-level 100",
            "ip address 10.254.254.254 255.255.255.252",
            "no shutdown",
            "interface Ethernet1",
            "mac-address aabb.cc00.1621",
            "nameif outside",
            "security-level 0",
            "ip address dhcp setroute",
            "no shutdown",
            "object network INSIDE_NET",
            "subnet 10.0.0.0 255.0.0.0",
            "nat (inside,outside) after-auto source dynamic INSIDE_NET interface",
            "access-list INSIDE_OUT extended permit tcp any any eq https",
            "access-list INSIDE_OUT extended permit udp any any eq domain",
            "access-list INSIDE_OUT extended permit icmp any any echo",
            "access-group INSIDE_OUT in interface inside",
            "route inside 10.0.0.0 255.0.0.0 10.254.254.253",
            "ssh 10.230.230.40 255.255.255.255 inside",
                                                                                            # BASE config for ASA
                                                                                            #interface Ethernet3
                                                                                            #ip address 10.230.230.55 255.255.255.192
                                                                                            #nameif management
                                                                                            #security-level 100
                                                                                            #no shutdown
                                                                                            #
                                                                                            #username manager password test123 privilege 15
                                                                                            #enable password test123
                                                                                            #
                                                                                            #domain-name my.local-domain
                                                                                            #crypto key generate rsa modulus 2048
                                                                                            #ssh 10.230.230.0 255.255.255.0 management
                                                                                            #ssh version 2
                                                                                            #aaa authentication ssh console LOCAL
                                                                                            #write memory
        ]
    }
]

# Loop through each device and apply the configuration
for device_config in devices:
    print(f"Connecting to {device_config['hostname']} ({device_config['ip']})...")
    device = {
        "device_type": device_config["device_type"],
        "host": device_config["ip"],
        "username": username,
        "password": password,
        "secret": enable_secret,
    }

    try:
        with ConnectHandler(**device) as net_connect:
            net_connect.enable()
            output = net_connect.send_config_set(device_config["commands"])
            print(f"Configuration applied to {device_config['hostname']} successfully.")
            print(output)
            if device_config["device_type"] == "cisco_asa":
                net_connect.send_command('write memory')
            else:
                net_connect.save_config()
            print(f"Configuration saved on {device_config['hostname']}.")
    except Exception as e:
        print(f"Failed to connect or configure {device_config['hostname']}: {e}")

print("\nAll devices have been configured.")
