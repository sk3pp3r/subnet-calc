# Subnet Calculator 
# Haim Cohen 2024
# https://www.linkedin.com/in/haimc/


import streamlit as st
import ipaddress
import subprocess


st.set_page_config(page_title="Subnet Calculator")

def get_wan_ip():
    try:
        wan_ip = subprocess.check_output(["curl", "-sS", "ifconfig.me/ip"]).decode('utf-8').strip()
        return f"{wan_ip}/32"
    except subprocess.CalledProcessError:
        return "Error: Could not retrieve WAN IP"

def calculate_subnet(ip: str):
    try:

        if '/' in ip:
            network = ipaddress.IPv4Network(ip, strict=False)
            subnet_mask = str(network.netmask)
        else:
            # Assume the format is IP followed by Subnet Mask
            ip_part, subnet_mask = ip.split()
            network = ipaddress.IPv4Network(f'{ip_part}/{subnet_mask}', strict=False)
        
        binary_subnet_mask = '.'.join(format(int(octet), '08b') for octet in subnet_mask.split('.'))
        ip_class = calculate_ip_class(network.network_address)
        ip_type = "Private" if network.is_private else "Public"
        cidr = network.prefixlen
        

        if cidr == 32:
            usable_host_range = "NA"
            usable_host_count = 0
        else:
            usable_host_range = f"{network[1]} - {network[-2]}"
            usable_host_count = network.num_addresses - 2
        
        return {
            "IP Address": ip.split('/')[0],
            "Network Address": str(network.network_address),
            "Usable Host IP Range": usable_host_range,
            "Broadcast Address": str(network.broadcast_address),
            "Total Number of Hosts": network.num_addresses,
            "Number of Usable Hosts": usable_host_count,            
            "Subnet Mask": subnet_mask,
            "Wildcard Mask": str(network.hostmask),
            "Binary Subnet Mask": binary_subnet_mask,
            "IP Class": ip_class,
            "CIDR Notation": f"/{cidr}",
            "IP Type": ip_type
        }
    except ValueError as e:
        st.error(f"Error: {e}")
        return None
    except IndexError:
        st.error("Error: IP address out of range for the given subnet.")
        return None

def calculate_ip_class(network_address):
    first_octet = int(str(network_address).split('.')[0])
    if first_octet < 128:
        return 'A'
    elif first_octet < 192:
        return 'B'
    elif first_octet < 224:
        return 'C'
    elif first_octet < 240:
        return 'D'
    else:
        return 'E'


if 'ip_address' not in st.session_state:
    st.session_state['ip_address'] = get_wan_ip()


st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Subnet Calculator", "About"])

if page == "Subnet Calculator":
    st.title("Subnet Calculator")
    st.subheader("Enter the IP address and subnet mask or CIDR:")

    ip_input = st.text_input("IP Address and Subnet Mask/CIDR", st.session_state['ip_address'])

    if st.button("Calculate"):
        result = calculate_subnet(ip_input)
        if result:
            st.session_state['ip_address'] = ip_input


            result_text = (
                f"IP Address: {result['IP Address']}\n"
                f"Network Address: {result['Network Address']}\n"
                f"Usable Host IP Range: {result['Usable Host IP Range']}\n"
                f"Broadcast Address: {result['Broadcast Address']}\n"
                f"Total Number of Hosts: {result['Total Number of Hosts']}\n"
                f"Number of Usable Hosts: {result['Number of Usable Hosts']}\n"
                f"Subnet Mask: {result['Subnet Mask']}\n"
                f"Wildcard Mask: {result['Wildcard Mask']}\n"
                f"IP Class: {result['IP Class']}\n"
                f"CIDR Notation: {result['CIDR Notation']}\n"
                f"IP Type: {result['IP Type']}\n"
            )
            st.code(result_text, language='text') 

    if st.button("Reset"):
        st.session_state['ip_address'] = get_wan_ip()
        st.experimental_rerun()

elif page == "About":
    st.title("About")
    st.write("""
        **Subnet Calculator**  
        Version: 1.0.0  
        Author: Haim Cohen  
        [GitHub Repository](https://github.com/sk3pp3r/subnet-calc)     
        [LinkedIn](https://www.linkedin.com/in/haimc/)

        This tool allows you to calculate subnets by providing an IP address in CIDR notation or with a subnet mask. It provides information on network address, usable host range, broadcast address, and more.
    """)

st.markdown("***") 
st.caption(f'Develop by Haim Cohen 2024 :sunglasses:')
