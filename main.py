from lib.phew import access_point, dns, server, connect_to_wifi
from lib.phew.template import render_template
import _thread
import json
from utils.constants import AP_NAME, AP_DOMAIN, AP_TEMPLATE_PATH, KEY, MODE_CBC, IV, WIFI_FILE
from services.crypto import Crypto
import machine

# Instantiate the classes -----------------------------------------------------------------
crypto = Crypto(KEY, MODE_CBC, IV)

# Routes -----------------------------------------------------------------------------------
@server.catchall()
def ap_catch_all(request):
    if request.headers.get("host") != AP_DOMAIN:
        return render_template(f"{AP_TEMPLATE_PATH}/redirect.html", domain = AP_DOMAIN)

    return "Not found.", 404

@server.route("/", methods=["GET"])
def ap_index(request):
    if request.headers.get("host") != AP_DOMAIN:
        return render_template(f"{AP_TEMPLATE_PATH}/redirect.html", domain = AP_DOMAIN)

    return render_template(f"{AP_TEMPLATE_PATH}/index.html")

@server.route("/configure", methods=["POST"])
def ap_configure(request):
    ssid = request.form["ssid"]
    password = request.form["password"]

    print("Attempting to connect to WiFi...")
    ip_address = connect_to_wifi(ssid, password, 10)
    if ip_address is not None:
        print(f"Successfully connected to WiFi! IP address: {ip_address}")
        print("Saving wifi credentials...")
        with open(WIFI_FILE, "w") as f:
            encrypted_ssid = crypto.parse(crypto.encrypt(ssid))
            encrypted_password = crypto.parse(crypto.encrypt(password))
            json.dump({"ssid": encrypted_ssid, "password": encrypted_password}, f)

        # Reboot from new thread after we have responded to the user.
        _thread.start_new_thread(machine_reset, ())
        return render_template(f"{AP_TEMPLATE_PATH}/configured.html", ssid=ssid)
    else:
        print(f"Credentials are incorrect or WiFi is not available.")
        return render_template(f"{AP_TEMPLATE_PATH}/redirect.html", domain = AP_DOMAIN)

# Helper functions -------------------------------------------------------------------------
def machine_reset():
    try:
        print("Stopping server...")
        server.stop()
    except Exception as e:
        print(f"An error occurred while stopping the server: {e}")
    
    print("Stopping program...")

    print("Performing soft reset...")
    machine.soft_reset()

    
# Main logic --------------------------------------------------------------------------------
try:
    # Attempt to read WiFi credentials
    with open(WIFI_FILE, "r") as f:
        wifi_credentials = json.load(f)
except OSError:
    print("WiFi credentials file not found.")
    raise
except ValueError:
    print("An error occurred while decoding the WiFi credentials file.")
    raise
except Exception as e:
    print("An unexpected error occurred while reading WiFi credentials.")
    raise

# If we reach this point, we successfully read the WiFi credentials
try:
    decrypted_ssid = crypto.decrypt(crypto.deparse(wifi_credentials["ssid"]))
    decrypted_password = crypto.decrypt(crypto.deparse(wifi_credentials["password"]))
except Exception as e:
    print("An error occurred while decrypting WiFi credentials.")
    raise

# If we reach this point, we successfully decrypted the WiFi credentials
try:
    print("Attempting to connect to WiFi...")
    ip_address = connect_to_wifi(decrypted_ssid, decrypted_password, 10)
    if ip_address is not None:
        print(f"Successfully connected to WiFi! IP address: {ip_address}")
        exec(open('core.py').read())
    else:
        print(f"Credentials are incorrect or WiFi is not available.")
        raise Exception("Failed to connect to WiFi.")
except Exception as e:
    print("An error occurred while connecting to WiFi.")
    print(e)

    ap = access_point(AP_NAME)
    ip = ap.ifconfig()[0]
    dns.run_catchall(ip)
    server.run()

