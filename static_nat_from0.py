from netmiko import ConnectHandler

# Define the credentials
username = "manager"
password = "test123"
enable_secret = "cisco"

# Define the list of routers and their specific configurations
routers = [
    {
        "ip": "10.230.230.18",
        "hostname": "R8-PRD",
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
            "ip address 10.230.230.18 255.255.255.192",
            "duplex auto",
            "no shutdown",
            "ip route 0.0.0.0 0.0.0.0 10.1.8.2"
        ]
    },
    {
        "ip": "10.230.230.11",
        "hostname": "R1-PRD",
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
            "ip address 10.230.230.11 255.255.255.192",
            "duplex auto",
            "no shutdown",
            "ip route 0.0.0.0 0.0.0.0 10.1.12.2",
            "ip route 10.10.10.0 255.255.255.0 10.1.8.1"
        ]
    },
    {
        "ip": "10.230.230.12",
        "hostname": "R2-PRD",
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
            "ip address 10.230.230.12 255.255.255.192",
            "duplex auto",
            "no shutdown",
            "ip route 0.0.0.0 0.0.0.0 10.1.27.2",
            "ip route 10.10.10.0 255.255.255.0 10.1.12.1"
        ]
    },
    {
        "ip": "10.230.230.17",
        "hostname": "R7-PRD-inet",
        "commands": [
            "interface Ethernet0/1",
            "description Link to R2",
            "ip address 10.1.27.2 255.255.255.252",
            "ip nat inside",
            "ip virtual-reassembly in",
            "duplex auto",
            "no shutdown",
            "interface Ethernet0/2",
            "description Link to Internet",
            "mac-address aabb.cc00.1621",
            "ip address dhcp",
            "ip nat outside",
            "ip virtual-reassembly in",
            "duplex auto",
            "no shutdown",
            "interface Ethernet0/3",
            "ip address 10.230.230.17 255.255.255.192",
            "ip nat inside",
            "ip virtual-reassembly in",
            "duplex auto",
            "no shutdown",
            "ip route 10.10.10.0 255.255.255.0 10.1.27.1",
            "access-list 10 permit 10.10.10.0 0.0.0.255",
            "ip nat inside source list 10 interface Ethernet0/2 overload"
        ]
    }
]

# Loop through each router and apply the configuration
for router in routers:
    print(f"Connecting to {router['hostname']} ({router['ip']})...")
    device = {
        "device_type": "cisco_ios",
        "host": router["ip"],
        "username": username,
        "password": password,
        "secret": enable_secret,
    }

    try:
        with ConnectHandler(**device) as net_connect:
            net_connect.enable()
            output = net_connect.send_config_set(router["commands"])
            print(f"Configuration applied to {router['hostname']} successfully.")
            print(output)
            net_connect.save_config()
            print(f"Configuration saved on {router['hostname']}.")
    except Exception as e:
        print(f"Failed to connect or configure {router['hostname']}: {e}")

print("\nAll routers have been configured.")
