# Cloudflare DNS Updater - GUI & No GUI options 

## Overview
This Python script provides a graphical user interface (GUI) or an automatic CLI script to update DNS records in Cloudflare. It retrieves the public IP address of the user's machine using the ipify service and updates a specified DNS record in Cloudflare with this IP address. 

## No GUI Version
Created for running alongside a Reverse Proxy but it can run on any server! For now you must create your config using the GUI version, then you can copy the No-GUI version along with the config to your server and setup a service to start on boot.

TO DO: 
- Add built-in config creation to the No-GUI version so you don't need to run the GUI version first
- Add optional auto-create service option during config setup - Export to .service file or insert into systemctl automatically if running on the intended server

## Features
- Retrieves the current public IP address.
- Updates a specified DNS record in Cloudflare with the current IP.
- GUI for easy interaction.

## Prerequisites
- Python 3.x
- `requests` library (Install using `pip install requests`)

## Setup
1. Clone or download this repository to your local machine.
2. Install the required Python packages: `pip install requests`.

## Configuration
Before running the script, ensure you have the following Cloudflare account details:
- API Key
- Email associated with Cloudflare account
- Zone ID of the domain
- Record Name and Record Type you wish to update

## Usage
1. Run the script using Python: `python cfUpdater.py`.
2. Enter your Cloudflare API Key, Email, Zone ID, Record Name(s), and Record Type in the respective fields in the GUI.
 Multiple record names can be entered seperated by commas (e.g. test.example.com, test2.example.com) 
3. The script will display your current public IP. If you want to update the specified DNS records to this IP, click on the "Update DNS Record" button or "Start Auto Update" button to run at the set interval.
4. Results of the operation will be displayed in the GUI.

## Troubleshooting
- Ensure all entered credentials and information are correct. 
- Make sure your Cloudflare API key has the necessary permissions. If you're having trouble with Zone keys, use Global API key.
- Check your internet connection if the script fails to retrieve the public IP.

## License
[MIT License](LICENSE.md)
