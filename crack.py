import os
import subprocess
import sys

def run_command(command):
    """Runs a shell command and returns the output and error."""
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def main():
    print("=Shadow=")
    print()

    # Step 1: Check if the device is connected
    stdout, stderr, return_code = run_command("deviceinfo.dll -k SerialNumber > info.log 2>&1")
    
    with open("info.log", "r") as log_file:
        log_output = log_file.read()

    if "ERROR: No device found!" in log_output:
        print("Error occurred.")
        print("Device not connected. Connect and try again.")
        print()
        print("Possible Fix: Open iTunes and check if device is connected then try again.")
        cleanup()
        sys.exit(1)

    if "Could not connect to lockdownd" in log_output:
        print("Software cannot connect to device.")
        print("Make sure the device gets detected in iTunes and try again.")
        print()
        print("Possible Fix: Connect the device in Recovery mode and restore it in iTunes. Then try again.")
        cleanup()
        sys.exit(1)

    # Step 2: Retrieve device information
    print()
    print()

    serial, _, _ = run_command("deviceinfo.dll -k SerialNumber")
    udid, _, _ = run_command("deviceinfo.dll -k UniqueDeviceID")
    device_name, _, _ = run_command("deviceinfo.dll -k ProductType")
    ios_version, _, _ = run_command("deviceinfo.dll -k ProductVersion")

    print(f"Device Connected: {device_name}")
    print(f"iOS: {ios_version}")
    print(f"Serial: {serial}")
    print(f"UDID: {udid}")
    print()
    print("Please wait, bypassing...")

    # Step 3: Modify the Manifest.plist file
    run_command('libcon.dll -convert xml1 "206cab4e197a3672ef8c418ffd9564c3f96dd64a\\Manifest.plist" >nul 2>&1')
    run_command(f'down.dll ed -L -u "//key[.=\'SerialNumber\']/following-sibling::string[1]" -v {serial} "206cab4e197a3672ef8c418ffd9564c3f96dd64a\\Manifest.plist" >nul 2>&1')
    run_command(f'down.dll ed -L -u "//key[.=\'UniqueDeviceID\']/following-sibling::string[1]" -v {udid} "206cab4e197a3672ef8c418ffd9564c3f96dd64a\\Manifest.plist" >nul 2>&1')
    run_command('libcon.dll -convert binary1 "206cab4e197a3672ef8c418ffd9564c3f96dd64a\\Manifest.plist" >nul 2>&1')

    # Step 4: Perform the restore
    _, _, return_code = run_command('sys.temp.dll -s 206cab4e197a3672ef8c418ffd9564c3f96dd64a restore --system --settings --skip-apps --no-reboot "%temp%" > test.log')

    if return_code != 0:
        print("An error occurred during the restore process.")
        cleanup()
        sys.exit(1)

    print("Device is rebooting, once it has rebooted MDM should be bypassed.")
    run_command("finish.dll restart > nul")

    print("------------------------------")

    # Cleanup
    cleanup()

def cleanup():
    """Deletes temporary files."""
    try:
        os.remove("info.log")
    except FileNotFoundError:
        pass

if __name__ == "__main__":
    main()