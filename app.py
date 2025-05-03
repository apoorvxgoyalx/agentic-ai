import streamlit as st

# Must be the first Streamlit command
st.set_page_config(page_title="☁️ OpenStack LLM Manager", layout="centered")

import os
from dotenv import load_dotenv
from groq import Groq
import openstack

# === Load Environment Variables ===
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("⚠️ GROQ_API_KEY not found in .env file. Please add it and restart the app.")

# === Connect to OpenStack ===
@st.cache_resource
def connect_openstack():
    try:
        return openstack.connect(cloud='openstack')  # set in clouds.yaml
    except Exception as e:
        st.error(f"⚠️ Failed to connect to OpenStack: {str(e)}")
        return None

# === Streamlit UI ===
st.title("☁️ OpenStack Manager with LLaMA 3.1")
st.markdown("Manage your VMs, Volumes, and Networks using natural language.")

# Try to connect to OpenStack
conn = connect_openstack()

# === LLaMA 3.1 Client Setup ===
try:
    llm = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error(f"⚠️ Failed to initialize Groq client: {str(e)}")
    llm = None

def parse_command_with_llama(user_input):
    system_prompt = (
         "You are an assistant that converts user instructions into OpenStack cloud operations. "
        "The supported operations are: "
        "- VM Provisioning: Create a VM and return its ID and IP."
        "- VM Resizing: Resize a VM to a specific flavor."
        "- VM Deletion: Delete a VM and confirm its destruction."
        "- Network Creation: Create a network and subnet."
        "- Volume Operations: Create or delete volumes."
        "- Usage Query: Return resource usage details such as vCPUs, RAM, GPU, and volume usage."
        "Respond with the following format: action: <action>, type: <vm|volume|network>, name: <resource_name>, size/flavor: <size/flavor>, ip: <ip>, usage: <usage_details>."
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


def dispatch_command(parsed_output):
    try:
        lines = parsed_output.lower().split(',')
        args = {k.strip(): v.strip() for k, v in (line.split(':') for line in lines)}

        action = args.get("action")
        res_type = args.get("type")
        name = args.get("name")
        size = args.get("size")
        flavor = args.get("flavor")
        ip = args.get("ip")
        usage = args.get("usage")

        if action == "create":
            if res_type == "vm":
                create_vm(conn, name, flavor)
            elif res_type == "volume":
                create_volume(conn, name)
            elif res_type == "network":
                create_network(conn, name)

        elif action == "resize":
            if res_type == "vm":
                resize_vm(conn, name, flavor)

        elif action == "delete":
            if res_type == "vm":
                delete_vm(conn, name)
            elif res_type == "volume":
                delete_volume(conn, name)

        elif action == "usage":
            query_usage(conn)

        else:
            st.error("Unsupported action or resource type.")
    except Exception as e:
        st.error(f"Command parsing error: {e}")

# === OpenStack Operations ===

def create_vm(conn, name, flavor):
    st.info(f"Creating VM '{name}' with flavor '{flavor}'...")
    server = conn.create_server(
        name=name,
        image='ubuntu-22.04',
        flavor=flavor,
        network='private-net',
        wait=True,
        auto_ip=True
    )
    st.success(f"VM '{name}' created successfully! ID: {server.id}, IP: {server.networks['private-net'][0]}")

def resize_vm(conn, name, flavor):
    servers = list(conn.compute.servers(name=name))
    if not servers:
        st.error(f"No VM found with name '{name}'")
        return
    server = servers[0]
    conn.compute.resize_server(server.id, flavor=flavor)
    st.success(f"VM '{name}' resized to '{flavor}' successfully.")

def delete_vm(conn, name):
    servers = list(conn.compute.servers(name=name))
    if not servers:
        st.error(f"No VM found with name '{name}'")
        return
    server = servers[0]
    conn.compute.delete_server(server.id)
    st.success(f"Deleted VM '{name}' (ID: {server.id})")

def create_network(conn, name):
    st.info(f"Creating network '{name}'...")
    network = conn.network.create_network(name=name)
    subnet = conn.network.create_subnet(
        name=f"{name}-subnet", 
        network_id=network.id, 
        ip_version='4', 
        cidr='192.168.1.0/24'
    )
    st.success(f"Network '{name}' created with subnet '{subnet.name}'. ID: {network.id}, Subnet ID: {subnet.id}")

def delete_network(conn, name):
    networks = list(conn.network.networks(name=name))
    if not networks:
        st.error(f"No network found with name '{name}'")
        return
    conn.network.delete_network(networks[0].id)
    st.success(f"Deleted network '{name}'")

def create_volume(conn, name):
    st.info(f"Creating volume '{name}' with size 100GB...")
    volume = conn.block_storage.create_volume(name=name, size=100)
    st.success(f"Volume '{name}' created. ID: {volume.id}")

def delete_volume(conn, name):
    volumes = list(conn.block_storage.volumes(name=name))
    if not volumes:
        st.error(f"No volume found with name '{name}'")
        return
    conn.block_storage.delete_volume(volumes[0].id)
    st.success(f"Deleted volume '{name}'")

def query_usage(conn):
    vcpu = conn.compute.get_flavor('vcpus')
    ram = conn.compute.get_flavor('ram')
    gpu = conn.compute.get_flavor('gpu')  # Replace with actual GPU query if needed
    volume_usage = conn.block_storage.get_usage()
    st.write(f"vCPU Usage: {vcpu}, RAM Usage: {ram}, GPU Usage: {gpu}, Volume Usage: {volume_usage}")

# === Streamlit UI ===

user_input = st.text_input("Enter your cloud command", placeholder="e.g., Delete VM dev-box")

if st.button("Execute"):
    if not conn:
        st.error("⚠️ Cannot execute command: Not connected to OpenStack")
    elif not llm:
        st.error("⚠️ Cannot execute command: Groq LLM client not initialized")
    elif not user_input:
        st.warning("Please enter a command.")
    else:
        with st.spinner("Processing with LLaMA 3.1..."):
            parsed = parse_command_with_llama(user_input)
            st.code(parsed, language="yaml")
            dispatch_command(parsed)

st.caption("Powered by Groq LLaMA 3.1 + OpenStack + Streamlit")