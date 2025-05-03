# import streamlit as st

# # Must be the first Streamlit command
# st.set_page_config(page_title="☁️ OpenStack LLM Manager", layout="centered")

# import os
# from dotenv import load_dotenv
# from groq import Groq
# import openstack
# from openstack import connection
# # === Load Environment Variables ===
# load_dotenv()
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# if not GROQ_API_KEY:
#     st.error("⚠️ GROQ_API_KEY not found in .env file. Please add it and restart the app.")

# # === Connect to OpenStack ===
# @st.cache_resource
# def connect_openstack():
#     try:
#         return openstack.connect(cloud='openstack')  # set in clouds.yaml
#     except Exception as e:
#         st.error(f"⚠️ Failed to connect to OpenStack: {str(e)}")
#         return None

# # === Streamlit UI ===
# st.title("☁️ OpenStack Manager with LLaMA 3.1")
# st.markdown("Manage your VMs, Volumes, and Networks using natural language.")

# # Try to connect to OpenStack
# conn = connect_openstack()

# # === LLaMA 3.1 Client Setup ===
# try:
#     llm = Groq(api_key=GROQ_API_KEY)
# except Exception as e:
#     st.error(f"⚠️ Failed to initialize Groq client: {str(e)}")
#     llm = None

# def parse_command_with_llama(user_input):
#     system_prompt = (
#          "You are an assistant that converts user instructions into OpenStack cloud operations. "
#         "The supported operations are: "
#         "- VM Provisioning: Create a VM and return its ID and IP."
#         "- VM Resizing: Resize a VM to a specific flavor."
#         "- VM Deletion: Delete a VM and confirm its destruction."
#         "- Network Creation: Create a network and subnet."
#         "- Volume Operations: Create or delete volumes."
#         "- Usage Query: Return resource usage details such as vCPUs, RAM, GPU, and volume usage."
#         "Respond with the following format: action: <action>, type: <vm|volume|network>, name: <resource_name>, size/flavor: <size/flavor>, ip: <ip>, usage: <usage_details>."
#     )

#     response = llm.chat.completions.create(
#         model="llama3-70b-8192",
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_input}
#         ],
#         temperature=0.2,
#         max_tokens=256
#     )

#     return response.choices[0].message.content.strip()


# def dispatch_command(parsed_output):
#     try:
#         lines = parsed_output.lower().split(',')
#         args = {k.strip(): v.strip() for k, v in (line.split(':') for line in lines)}

#         action = args.get("action")
#         res_type = args.get("type")
#         name = args.get("name")
#         size = args.get("size")
#         flavor = args.get("flavor")
#         ip = args.get("ip")
#         usage = args.get("usage")

#         if action == "create":
#             if res_type == "vm":
#                 create_vm(conn, name, flavor)
#             elif res_type == "volume":
#                 create_volume(conn, name)
#             elif res_type == "network":
#                 create_network(conn, name)

#         elif action == "resize":
#             if res_type == "vm":
#                 resize_vm(conn, name, flavor)

#         elif action == "delete":
#             if res_type == "vm":
#                 delete_vm(conn, name)
#             elif res_type == "volume":
#                 delete_volume(conn, name)

#         elif action == "usage":
#             query_usage(conn)

#         else:
#             st.error("Unsupported action or resource type.")
#     except Exception as e:
#         st.error(f"Command parsing error: {e}")

# # === OpenStack Operations ===
# # === Setup connection ===
# conn = connection.Connection(
#     auth_url="https://api-ap-south-mum-1.openstack.acecloudhosting.com:5000/v3",
#     project_name="ACE_HACKATHON_AIML",
#     username="Hackathon_AIML_1",
#     password="Hackathon_AIML_1@567",
#     user_domain_name="Default",
#     project_domain_name="Default",
#     region_name="ap-south-mum-1",
#     interface="public",
#     identity_api_version=3
# )

# def create_vm(vm_name="dev-box", image_name="Ubuntu-22.04", flavor_name="S.4", network_name="green-net", volume_size=20):
#     image = conn.compute.find_image(image_name)
#     flavor = conn.compute.find_flavor(flavor_name)
    
#     networks = list(conn.network.networks(name=network_name))
#     if len(networks) == 0:
#         raise Exception(f"❌ Network '{network_name}' not found.")
#     elif len(networks) > 1:
#         print(f"⚠️ Warning: Multiple networks named '{network_name}' found. Using the first one.")
    
#     network = networks[0]

#     if not image:
#         raise Exception(f"❌ Image '{image_name}' not found.")
#     if not flavor:
#         raise Exception(f"❌ Flavor '{flavor_name}' not found.")

#     volume = conn.block_store.create_volume(
#         size=volume_size,
#         name=f"{vm_name}-volume",
#         image_id=image.id
#     )
#     conn.block_store.wait_for_status(volume, status='available')
    
#     server = conn.compute.create_server(
#         name=vm_name,
#         flavor_id=flavor.id,
#         networks=[{"uuid": network.id}],
#         block_device_mapping_v2=[{
#             "boot_index": 0,
#             "uuid": volume.id,
#             "source_type": "volume",
#             "destination_type": "volume",
#             "delete_on_termination": True
#         }]
#     )
#     server = conn.compute.wait_for_server(server)

#     # Extract IP address
#     ip = None
#     for net_info in server.addresses.values():
#         for addr in net_info:
#             if addr.get("OS-EXT-IPS:type") == "fixed":
#                 ip = addr.get("addr")
#                 break

#     print(f"✅ VM Created: ID={server.id}, Name={vm_name}, IP={ip}")


# def list_flavors():
#     print("\n📦 Available Flavors:")
#     for f in conn.compute.flavors():
#         print(f"- {f.name}")

# def resize_vm(conn, vm_name, new_flavor_name):
#     # Get all matching servers
#     servers = list(conn.compute.servers(name=vm_name))
    
#     if len(servers) == 0:
#         raise Exception(f"❌ No server found with name '{vm_name}'.")
#     elif len(servers) > 1:
#         print(f"⚠️ Multiple servers found with name '{vm_name}', selecting the first one.")
    
#     server = servers[0]

#     # Get the target flavor
#     flavor = conn.compute.find_flavor(new_flavor_name)
#     if not flavor:
#         raise Exception(f"❌ Flavor '{new_flavor_name}' not found.")
    
#     print(f"🔁 Resizing '{vm_name}' to flavor '{new_flavor_name}'...")

# def delete_vm(conn, vm_name):
#     servers = list(conn.compute.servers(name=vm_name))

#     if not servers:
#         print(f"❌ No VM found with name '{vm_name}'.")
#         return

#     print(f"⚠️ Found {len(servers)} VM(s) with the name '{vm_name}':")
#     for s in servers:
#         print(f"- ID: {s.id}, Status: {s.status}, Created: {s.created_at}")

#     vm_ids = [s.id for s in servers]

#     while True:
#         user_input = input("Enter the full **VM ID** to delete (or 'q' to cancel): ").strip()
#         if user_input.lower() == 'q':
#             print("❎ Deletion cancelled.")
#             return
#         if user_input in vm_ids:
#             conn.compute.delete_server(user_input)
#             print(f"✅ Deletion requested for VM ID: {user_input}")
#             return
#         print("⚠️ Invalid VM ID. Please enter a valid one from the list.")


# # === FR-4: Network Creation ===

# def create_network(conn, network_name="blue-net", subnet_name="blue-subnet", cidr="192.168.1.0/24", gateway_ip="192.168.1.1", dns_nameservers=None):
#     if dns_nameservers is None:
#         dns_nameservers = ['8.8.8.8']

#     net = conn.network.create_network(name=network_name)
#     subnet = conn.network.create_subnet(
#         name=subnet_name,
#         network_id=net.id,
#         ip_version=4,
#         cidr=cidr,
#         gateway_ip=gateway_ip,
#         dns_nameservers=dns_nameservers
#     )
#     print(f"🌐 Network created: {net.name}, Subnet: {subnet.name}, CIDR: {subnet.cidr}")

# # === FR-5: Volume Operations ===

# def create_volume(volume_name="data-disk", size=100):
#     vol = conn.block_store.create_volume(name=volume_name, size=size)
#     conn.block_store.wait_for_status(vol, status='available')
#     print(f"💾 Volume created: {vol.name} (ID: {vol.id})")


# def delete_volume(volume_name="data-disk"):
#     vol = conn.block_store.find_volume(volume_name)
#     if not vol:
#         print(f"⚠️ Volume '{volume_name}' not found.")
#         return
#     conn.block_store.delete_volume(vol, ignore_missing=True)
#     print(f"🗑️ Volume {vol.name} deleted.")


# # === FR-6: Usage Query ===
# def get_usage():
#     limits = conn.compute.get_limits()
#     usage = limits.absolute

#     print("📊 Project Usage:")
#     print(f"• vCPUs Used: {usage['totalCoresUsed']}")
#     print(f"• RAM Used: {usage['totalRAMUsed']} MB")
#     print(f"• Instances Used: {usage['totalInstancesUsed']}")
    
#     volumes = list(conn.block_store.volumes())
#     vol_size = sum(v.size for v in volumes)
#     print(f"• Volumes: {len(volumes)} used, {vol_size} GB total")


# # def create_vm(conn, name, flavor):
# #     st.info(f"Creating VM '{name}' with flavor '{flavor}'...")
# #     server = conn.create_server(
# #         name=name,
# #         image='ubuntu-22.04',
# #         flavor=flavor,
# #         network='private-net',
# #         wait=True,
# #         auto_ip=True
# #     )
# #     st.success(f"VM '{name}' created successfully! ID: {server.id}, IP: {server.networks['private-net'][0]}")

# # def resize_vm(conn, name, flavor):
# #     servers = list(conn.compute.servers(name=name))
# #     if not servers:
# #         st.error(f"No VM found with name '{name}'")
# #         return
# #     server = servers[0]
# #     conn.compute.resize_server(server.id, flavor=flavor)
# #     st.success(f"VM '{name}' resized to '{flavor}' successfully.")

# # def delete_vm(conn, name):
# #     servers = list(conn.compute.servers(name=name))
# #     if not servers:
# #         st.error(f"No VM found with name '{name}'")
# #         return
# #     server = servers[0]
# #     conn.compute.delete_server(server.id)
# #     st.success(f"Deleted VM '{name}' (ID: {server.id})")

# # def create_network(conn, name):
# #     st.info(f"Creating network '{name}'...")
# #     network = conn.network.create_network(name=name)
# #     subnet = conn.network.create_subnet(
# #         name=f"{name}-subnet", 
# #         network_id=network.id, 
# #         ip_version='4', 
# #         cidr='192.168.1.0/24'
# #     )
# #     st.success(f"Network '{name}' created with subnet '{subnet.name}'. ID: {network.id}, Subnet ID: {subnet.id}")

# # def delete_network(conn, name):
# #     networks = list(conn.network.networks(name=name))
# #     if not networks:
# #         st.error(f"No network found with name '{name}'")
# #         return
# #     conn.network.delete_network(networks[0].id)
# #     st.success(f"Deleted network '{name}'")

# # def create_volume(conn, name):
# #     st.info(f"Creating volume '{name}' with size 100GB...")
# #     volume = conn.block_storage.create_volume(name=name, size=100)
# #     st.success(f"Volume '{name}' created. ID: {volume.id}")

# # def delete_volume(conn, name):
# #     volumes = list(conn.block_storage.volumes(name=name))
# #     if not volumes:
# #         st.error(f"No volume found with name '{name}'")
# #         return
# #     conn.block_storage.delete_volume(volumes[0].id)
# #     st.success(f"Deleted volume '{name}'")

# # def query_usage(conn):
# #     vcpu = conn.compute.get_flavor('vcpus')
# #     ram = conn.compute.get_flavor('ram')
# #     gpu = conn.compute.get_flavor('gpu')  # Replace with actual GPU query if needed
# #     volume_usage = conn.block_storage.get_usage()
# #     st.write(f"vCPU Usage: {vcpu}, RAM Usage: {ram}, GPU Usage: {gpu}, Volume Usage: {volume_usage}")

# # === Streamlit UI ===

# user_input = st.text_input("Enter your cloud command", placeholder="e.g., Delete VM dev-box")

# if st.button("Execute"):
#     if not conn:
#         st.error("⚠️ Cannot execute command: Not connected to OpenStack")
#     elif not llm:
#         st.error("⚠️ Cannot execute command: Groq LLM client not initialized")
#     elif not user_input:
#         st.warning("Please enter a command.")
#     else:
#         with st.spinner("Processing with LLaMA 3.1..."):
#             parsed = parse_command_with_llama(user_input)
#             st.code(parsed, language="yaml")
#             dispatch_command(parsed)

# st.caption("Powered by Groq LLaMA 3.1 + OpenStack + Streamlit")


import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
import openstack

# === Page Config ===
st.set_page_config(page_title="☁️ OpenStack LLM Manager", layout="centered")

# === Load Environment Variables ===
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("⚠️ GROQ_API_KEY not found in .env file. Please add it to .env.")
    st.stop()

# === Initialize OpenStack Connection ===
@st.cache_resource
def connect_openstack():
    try:
        return openstack.connection.Connection(
            auth_url="https://api-ap-south-mum-1.openstack.acecloudhosting.com:5000/v3",
            project_name="ACE_HACKATHON_AIML",
            username="Hackathon_AIML_1",
            password="Hackathon_AIML_1@567",
            user_domain_name="Default",
            project_domain_name="Default",
            region_name="ap-south-mum-1",
            interface="public",
            identity_api_version=3
        )
    except Exception as e:
        st.error(f"❌ OpenStack connection failed: {e}")
        return None

conn = connect_openstack()

# === Initialize Groq LLaMA 3.1 ===
try:
    llm = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error(f"❌ Failed to initialize Groq client: {e}")
    llm = None

# === LLM Instruction Parser ===
def parse_command_with_llama(user_input):
    system_prompt = (
        "You are an assistant that converts user instructions into OpenStack cloud operations. "
        "Supported actions: "
        "- Create, Delete, Resize for VMs "
        "- Create, Delete for Volumes and Networks "
        "- Show usage details\n\n"
        "Format your response exactly like: "
        "action: <action>, type: <vm|volume|network|usage>, name: <resource_name>, flavor: <flavor>, size: <size>, ip: <ip>, usage: <usage_details>"
    )

    response = llm.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0.2,
        max_tokens=256
    )
    return response.choices[0].message.content.strip()

import streamlit as st

def dispatch_command(parsed_output):
    # Ensure confirmation_step and pending_command are initialized in session state
    if "confirmation_step" not in st.session_state:
        st.session_state.confirmation_step = False
    if "pending_command" not in st.session_state:
        st.session_state.pending_command = None

    try:
        # Parsing the command string into a dictionary of arguments
        args = {k.strip(): v.strip() for k, v in (line.split(':') for line in parsed_output.split(','))}
        action = args.get("action")
        res_type = args.get("type")
        name = args.get("name")
        flavor = args.get("flavor", "S.4")
        size_str = args.get("size", "20")

        # Resolve default flavor and size
        flavor = flavor if flavor != "(default)" else "S.4"
        try:
            size = int(size_str)
        except ValueError:
            size = 20

        # Handle usage command (assuming you need to show some usage statistics)
        if action == "show" and res_type == "usage":
            usage = args.get("usage")
            if usage:
                # Extract and display the usage info from the usage string
                usage_info = usage.split(",")
                for info in usage_info:
                    st.write(info)  # Display each usage line

            return

        # Step 1: Store the command and ask for confirmation
        if not st.session_state.confirmation_step:
            st.session_state.pending_command = (action, res_type, name, flavor, size)
            st.session_state.confirmation_step = True
            st.info(f"Do you really want to **{action}** the **{res_type}** named **{name}**?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes, proceed"):
                    dispatch_command(parsed_output)  # Call again to proceed
            with col2:
                if st.button("❌ No, cancel"):
                    st.session_state.confirmation_step = False
                    st.session_state.pending_command = None
                    st.success("Action cancelled.")
            return

        # Step 2: Execute if confirmed
        action, res_type, name, flavor, size = st.session_state.pending_command

        if action == "create":
            if res_type == "vm":
                create_vm(name, flavor_name=flavor)
            elif res_type == "volume":
                create_volume(name, size)
            elif res_type == "network":
                create_network(name)

        elif action == "resize" and res_type == "vm":
            resize_vm(name, flavor)

        elif action == "delete":
            if res_type == "vm":
                delete_vm(name)
            elif res_type == "volume":
                delete_volume(name)

        elif action == "usage":
            query_usage()

        else:
            st.error("❌ Unsupported action or resource type.")

        # Reset confirmation state after execution
        st.session_state.confirmation_step = False
        st.session_state.pending_command = None

    except Exception as e:
        st.error(f"Command dispatch error: {e}")

# Function to execute the command based on confirmation
def execute_command(action, res_type, name, flavor, size):
    try:
        if action == "create":
            if res_type == "vm":
                create_vm(name, flavor_name=flavor)
            elif res_type == "volume":
                create_volume(name, size)
            elif res_type == "network":
                create_network(name)

        elif action == "resize" and res_type == "vm":
            resize_vm(name, flavor)

        elif action == "delete":
            if res_type == "vm":
                delete_vm(name)
            elif res_type == "volume":
                delete_volume(name)

        elif action == "usage":
            query_usage()

        else:
            st.error("❌ Unsupported action or resource type.")

        # If command executed successfully, show confirmation
        st.success(f"Action **{action}** for **{res_type}** **{name}** completed successfully.")
    
    except Exception as e:
        st.error(f"Error while executing command: {e}")


# Example placeholder functions for VM, volume, and network operations
def create_vm(name, flavor_name):
    st.write(f"Creating VM: {name} with flavor {flavor_name}")

def create_volume(name, size):
    st.write(f"Creating volume: {name} with size {size}")

def create_network(name):
    st.write(f"Creating network: {name}")

def resize_vm(name, flavor):
    st.write(f"Resizing VM: {name} to flavor {flavor}")

def delete_vm(name):
    st.write(f"Deleting VM: {name}")

def delete_volume(name):
    st.write(f"Deleting volume: {name}")

def query_usage():
    st.write("Querying usage details...")

# === OpenStack Operations ===
def create_vm(vm_name, image_name="Ubuntu-22.04", flavor_name="S.4", network_name="green-net", volume_size=20):
    image = conn.compute.find_image(image_name)
    flavor = conn.compute.find_flavor(flavor_name)
    network = next(iter(conn.network.networks(name=network_name)), None)

    if not image or not flavor or not network:
        st.error("❌ Missing image, flavor, or network.")
        return

    volume = conn.block_store.create_volume(
        size=volume_size,
        name=f"{vm_name}-volume",
        image_id=image.id
    )
    conn.block_store.wait_for_status(volume, status='available')

    server = conn.compute.create_server(
        name=vm_name,
        flavor_id=flavor.id,
        networks=[{"uuid": network.id}],
        block_device_mapping_v2=[{
            "boot_index": 0,
            "uuid": volume.id,
            "source_type": "volume",
            "destination_type": "volume",
            "delete_on_termination": True
        }]
    )
    server = conn.compute.wait_for_server(server)

    ip = next((addr['addr'] for net in server.addresses.values() for addr in net if addr.get("OS-EXT-IPS:type") == "fixed"), None)
    st.success(f"✅ VM Created: {vm_name}, IP: {ip}")

def create_volume(name, size):
    volume = conn.block_store.create_volume(name=name, size=size)
    conn.block_store.wait_for_status(volume, status='available')
    st.success(f"📦 Volume '{name}' created with size {size} GB.")

def delete_vm(vm_name):
    servers = list(conn.compute.servers(name=vm_name))
    if not servers:
        st.error(f"❌ No VM found with name {vm_name}")
        return
    conn.compute.delete_server(servers[0])
    st.success(f"🗑️ VM '{vm_name}' deleted.")

def delete_volume(name):
    volume = conn.block_store.find_volume(name)
    if not volume:
        st.error(f"❌ Volume '{name}' not found.")
        return
    conn.block_store.delete_volume(volume, ignore_missing=True)
    st.success(f"🗑️ Volume '{name}' deleted.")

def create_network(name):
    net = conn.network.create_network(name=name)
    subnet = conn.network.create_subnet(
        name=f"{name}-subnet",
        network_id=net.id,
        ip_version="4",
        cidr="192.168.100.0/24"
    )
    st.success(f"🌐 Network '{name}' with subnet created.")

def resize_vm(vm_name, new_flavor):
    server = next(iter(conn.compute.servers(name=vm_name)), None)
    flavor = conn.compute.find_flavor(new_flavor)

    if not server or not flavor:
        st.error("❌ VM or flavor not found.")
        return

    conn.compute.resize_server(server, flavor.id)
    st.success(f"🔁 Resize initiated for VM '{vm_name}' to flavor '{new_flavor}'.")

def query_usage():
    limits = conn.compute.get_limits()
    used = limits.absolute
    st.info(f"""
    📊 **Usage Summary**:
    - vCPUs Used: {used['totalCoresUsed']}
    - RAM Used: {used['totalRAMUsed']} MB
    - Instances Used: {used['totalInstancesUsed']}
    """)

# === UI ===
st.title("☁️ OpenStack Manager with LLaMA 3.1")
st.markdown("Enter a natural language command like:\n- 'Create a VM named test-vm with S.2 flavor'\n- 'Delete volume backup-vol'\n- 'Resize dev-vm to S.4'\n- 'Show usage'")

user_input = st.text_input("💬 Your instruction:")

if st.button("Execute"):
    if user_input:
        parsed = parse_command_with_llama(user_input)
        st.markdown(f"🧠 **Parsed:** `{parsed}`")
        dispatch_command(parsed)
    else:
        st.warning("Please enter a command first.")

