#!/usr/bin/env python3
import winrm
import getpass
import sys
import textwrap

# ------------------------------
# PowerShell Script Template
# ------------------------------
PS_SCRIPT = r'''
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$rand = -join ((65..90) | Get-Random -Count 2 | ForEach-Object {[char]$_})
$baseName = "logs_${timestamp}_${rand}"

$root = "C:\EDR_TEMP\exports"
New-Item -ItemType Directory -Force -Path $root | Out-Null

$evtxFolder = "$root\$baseName"
New-Item -ItemType Directory -Force -Path $evtxFolder | Out-Null

# Extract EVTX
wevtutil epl Security    "$evtxFolder\Security.evtx"
wevtutil epl System      "$evtxFolder\System.evtx"
wevtutil epl Application "$evtxFolder\Application.evtx"

# ZIP
$zipPath = "$root\$baseName.zip"
Compress-Archive -Path "$evtxFolder\*" -DestinationPath $zipPath -Force

Write-Output "ZIP_CREATED:$zipPath"
'''

# ------------------------------
# Main Logic
# ------------------------------
def main():
    print("\n===== 원격 EVTX 수집기 (WinRM) =====\n")

    target = input("Target IP: ").strip()
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ").strip()

    print("\n[+] WinRM 연결 중...")

    try:
        session = winrm.Session(
            target,
            auth=(username, password),
            transport='ntlm',
            server_cert_validation='ignore'
        )
    except Exception as e:
        print(f"[!] WinRM 연결 실패: {e}")
        sys.exit(1)

    print("[+] PowerShell 명령 실행 중...\n")

    try:
        result = session.run_ps(PS_SCRIPT)
    except Exception as e:
        print(f"[!] PowerShell 실행 실패: {e}")
        sys.exit(1)

    # 결과 확인
    output = result.std_out.decode(errors="ignore").strip()
    error = result.std_err.decode(errors="ignore").strip()

    if error:
        print("[!] PowerShell 오류 발생:")
        print(error)

    # ZIP 경로 추출
    zip_path = None
    for line in output.splitlines():
        if line.startswith("ZIP_CREATED:"):
            zip_path = line.replace("ZIP_CREATED:", "").strip()

    print("\n===== 결과 =====")
    print(output)

    if zip_path:
        print(f"\n[+] ZIP 파일 생성됨: {zip_path}")
    else:
        print("\n[!] ZIP 경로를 찾지 못했습니다. 출력 로그를 확인하세요.")

    print("\n[+] 원격 EVTX 수집 완료!\n")


if __name__ == "__main__":
    main()
