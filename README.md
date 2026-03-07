# **Medusa v2.0**
Medusa is designed to demonstrate the vulnerability of certain IoT cameras (specifically those using AltoBeam/V380 chipsets) to network-based Resource Exhaustion and authentication bypasses on the RTSP protocol.

Unlike previous versions, v2.0 features a Confidence Scoring Engine that accurately identifies targets via banner grabbing and manual handshake verification.

🚀 Key Features
- Advanced Scanning: Leverages Nmap service detection to identify CCTV vendors (Dahua, Hikvision, V380) with up to 100% accuracy.
- Confidence Scoring: Automatic grading system (Confirmed, Likely, Possible) based on open ports and service banner matches.
- Dual-Strike Petrify (DoS): Simultaneously floods Port 554 (RTSP) and Port 8089 (Service) to overwhelm the network stack and trigger a hardware watchdog reset.
- Brute Force: Dictionary attacks on Port 554 using a Direct Ncat Handshake method to eliminate false positives and ensure credential validity.

🛠️ Prerequisites
This framework requires a Linux environment with the following packages installed:

- nmap & ncat
- hping3
- python3 with the rich library

Install Dependencies:

```
sudo apt update && sudo apt install nmap hping3 python3-pip -y
pip install rich
```

📖 How to Use
Clone the Repository:
```
git clone https://github.com/sal-scar/medusa.git
cd medusa
```

Launch the Tool:
```
sudo python3 medusa.py
```

⚙️ Workflow
- Scanning: Medusa scans the network and filters out any results with a 0% confidence score.
- Analysis: The tool provides a "Reasoning" column explaining exactly why a device was flagged as a CCTV.
- Execution:

Mode 1: Launches a Dual-Port SYN flood to freeze the device.

Mode 2: Attempts to crack the RTSP credentials using a specified wordlist.

> ⚠️ Legal Disclaimer
> This tool is created strictly for educational purposes and authorized security auditing. The creator is NOT responsible for any misuse, illegal activities, or criminality. Testing on unauthorized networks is strictly prohibited and may be subject to legal prosecution. Always use your own network and equipment.
