#!/bin/sh

CONFIG_FILE="/etc/wifi-config"
GROUP_NAME="netdev"
PID_FILE="/var/run/wpa_supplicant"
MAX_TRIES=5
TRIES=0
CONNECTED=0

# Create default empty config if it doesn't exist
if [ ! -f "$CONFIG_FILE" ]; then
    echo "WiFi config file '$CONFIG_FILE' not found. Creating empty config and exiting."
    cat <<EOF > "$CONFIG_FILE"
network={
    ssid=""
    psk=""
}
EOF
    exit 0
fi

# Exit if the config file is empty or missing required fields
if [ ! -s "$CONFIG_FILE" ]; then
    echo "WiFi config file is empty. Skipping WiFi setup."
    exit 0
fi

SSID=$(grep 'ssid=' "$CONFIG_FILE" | sed -n 's/.*ssid="\([^"]*\)".*/\1/p')
PSK=$(grep 'psk=' "$CONFIG_FILE" | sed -n 's/.*psk="\([^"]*\)".*/\1/p')

if [ -z "$SSID" ] || [ -z "$PSK" ]; then
    echo "WiFi config is invalid or missing SSID/PSK. Skipping WiFi setup."
    exit 0
fi

# Clean up any old wpa_supplicant process
[ -f "$PID_FILE" ] && rm -f "$PID_FILE"
killall wpa_supplicant 2>/dev/null

# Ensure the group for wpa_supplicant control interface exists
if ! getent group "$GROUP_NAME" >/dev/null 2>&1; then
    addgroup "$GROUP_NAME"
fi

# Generate wpa_supplicant configuration from static file
cat <<EOF > /etc/wpa_supplicant.conf
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=$GROUP_NAME
update_config=1
country=CZ
p2p_disabled=1
$(cat "$CONFIG_FILE")
EOF

echo "Starting wpa_supplicant..."
/usr/sbin/wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant.conf

# Attempt to acquire IP address via DHCP
while [ $TRIES -lt $MAX_TRIES ]; do
    echo "Attempt $((TRIES+1)) to get IP address..."
    /sbin/udhcpc -i wlan0 -q -n -T 3 -t 1
    if ip addr show wlan0 | grep -q "inet "; then
        CONNECTED=1
        echo "WiFi connected successfully."
        break
    fi
    TRIES=$((TRIES+1))
    sleep 2
done

# Fallback if connection failed
if [ $CONNECTED -eq 0 ]; then
    echo "Failed to connect to WiFi after $MAX_TRIES attempts. Continuing boot..."
    killall wpa_supplicant
fi