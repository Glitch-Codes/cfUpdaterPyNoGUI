import requests
from threading import Event, Thread
from getkey import getkey, keys
import time
import configparser
import os

global DEBUG
DEBUG = True

SHUTDOWN = Event()

def get_public_ip():
    try:
        return requests.get("https://api.ipify.org").text
    except requests.RequestException as e:
        print(f"ERROR: Failed to get public IP: {e}")
        return None

def load_config():
    global api_key
    global email
    global zone_id
    global record_names
    global record_type
    global interval
    config = configparser.ConfigParser()
    config.read('config.ini')
    if 'DEFAULT' in config:
        api_key = config['DEFAULT'].get('ApiKey', '')
        email = config['DEFAULT'].get('Email', '')
        zone_id = config['DEFAULT'].get('ZoneId', '')
        record_names = config['DEFAULT'].get('RecordNames', '')
        record_type = config['DEFAULT'].get('RecordType', '')
        interval = config['DEFAULT'].get('Interval', '')
        print("INFO: Configuration loaded successfully.")

def get_dns_record_id(api_key, email, zone_id, record_name, record_type):
    headers = {
        "X-Auth-Email": email,
        "X-Auth-Key": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type={record_type}&name={record_name}", headers=headers)
        if response.status_code == 200:
            records = response.json()["result"]
            if records:
                return records[0]["id"]
            else:
                print("INFO: No matching DNS record found")
                return None
        else:
            print(f"ERROR: Failed to fetch DNS records: {response.text}")
            return None
    except requests.RequestException as e:
        print(f"ERROR: API request failed: {e}")
        return None

def check_dns_record(api_key, email, zone_id, record_name, record_type):
    headers = {
        "X-Auth-Email": email,
        "X-Auth-Key": api_key,
        "Content-Type": "application/json"
    }
    response = requests.get(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type={record_type}&name={record_name}", headers=headers)
    if response.status_code == 200:
        records = response.json()["result"]
        if records:
            return records[0]['content']  # Return the IP address of the DNS record
    return None


def update_dns_record():
    content = get_public_ip()

    for record_name in record_names:
        record_name = record_name.strip()  # Removing leading/trailing whitespace
        dns_record_ip = check_dns_record(api_key, email, zone_id, record_name, record_type)
        
        if dns_record_ip == content:
            print(f"INFO: The IP address already matches the A record for {record_name}.\n")
            continue
        elif dns_record_ip is None:
            print(f"ERROR: Could not retrieve the DNS record for {record_name}.\n")
            continue

        record_id = get_dns_record_id(api_key, email, zone_id, record_name, record_type)
        if not record_id:
            continue

        headers = {
            "X-Auth-Email": email,
            "X-Auth-Key": api_key,
            "Content-Type": "application/json"
        }

        data = {
            "type": record_type,
            "name": record_name,
            "content": content,
            "ttl": 1,
            "proxied": False
        }

        try:
            response = requests.put(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}", json=data, headers=headers)
            if response.status_code == 200:
                print(f"INFO: Success: DNS record for {record_name} updated successfully.\n")
            else:
                print(f"ERROR: Failed to update DNS record for {record_name}: {response.text}\n")
        except requests.RequestException as e:
            print(f"ERROR: API request failed for {record_name}: {e}\n")


def auto_update():
    interval_sec = int(interval) * 60  # Convert minutes to seconds
    while not SHUTDOWN.is_set():
        for remaining in range(int(interval_sec), 0, -1):
            mins, secs = divmod(remaining, 60)
            print(f"Next check in: {mins:02d}:{secs:02d}", end = '\r')
            time.sleep(1)
            if SHUTDOWN.is_set():
                quit() # Quit Script, closing auto_update Daemon
                
        if not SHUTDOWN.is_set():
            current_ip = get_public_ip()
            update_performed = False
            for record_name in record_names.split(","):
                record_name = record_name.strip()
                dns_record_ip = check_dns_record(api_key, email, zone_id, record_name, record_type)
                if current_ip != dns_record_ip:
                    update_dns_record()
                    update_performed = True
            if not update_performed:
                print(f"INFO: No update necessary at {time.strftime('%Y-%m-%d %H:%M:%S')}.\n")

def key_watcher():
    while True:   
        key = getkey()
        if key == 'q':
            SHUTDOWN.set()
            print("Shutting down daemon...")
            exit(1) # Exit key_watcher Daemon 
    
# Check for config.ini and load if exists
if os.path.exists('config.ini'):
    load_config()
    if DEBUG:
            print(f'API Key: {api_key}\n')
            print(f'Email: {email}\n')
            print(f'Zone ID: {zone_id}\n')
            print(f'Record Name(s): {record_names}\n')
            print(f'Record Type: {record_type}\n')
            print(f'Interval: {interval} minute(s)\n')
            print(f'\n')
    print('### Press q to stop script ###\n')
    Thread(target=key_watcher).start()
    Thread(target=auto_update).start()
 