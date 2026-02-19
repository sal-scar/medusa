# **Medusa v1.0**
Medusa is designed to demonstrate the vulnerability of certain IoT cameras (specifically those using AltoBeam/V380 chips) to network-based Resource Exhaustion.

By leveraging hping3 to launch a high-speed SYN flood with randomized source IPs, Medusa overwhelms the device's network stack, causing the system to hang and eventually trigger a hardware watchdog reset.

**🛠️ Prerequisites**
You will need the following tools installed:

* hping3
* arp-scan

Install them using:
```
sudo apt update && sudo apt install hping3 arp-scan -y
```

**📖 How to Use**

```
git clone https://github.com/sal-scar/medusa.git
cd medusa
chmod +x medusa.sh
sudo ./medusa.sh
```
**⚙️ Customization (Attack & Rest Times)**
If the attack takes too long or recovering too quickly, you can fine-tune the script. Open the script in a text editor (like nano or vim) and locate the CONFIGURATION block at the top:
```
# --- CONFIGURATION ---
CCTV_PREFIX="38:54:f5"  # AltoBeam MAC prefix
TARGET_PORT=8089        # Target service port
ATTACK_TIME=60          # Duration of the flood (Increase if freeze is too short)
REST_TIME=30            # Duration of the pause (Decrease to hit it faster)
# ---------------------
```
* ATTACK_TIME: Set this to at least 10-20 seconds longer than the time it takes for your camera to "freeze." If the camera reboots at 50 seconds, a 60 or 90 second hammer ensures it never stabilizes.

* REST_TIME: This is the "breather." If your camera reboots and starts recording immediately, lower this number (e.g., 10) so the script strikes again sooner.



> ⚠️ Disclaimer
> EDUCATIONAL PURPOSES ONLY. This tool is intended for legal, authorized security testing in a controlled lab environment. Unauthorized access to or disruption of computer systems is illegal. The author is not >
> responsible for any misuse. This script was tested specifically on AltoBeam/V380 hardware; it is NOT a universal exploit.
