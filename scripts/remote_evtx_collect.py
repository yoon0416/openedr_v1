#!/usr/bin/env python3
import winrm
import getpass
import sys
import os
import base64

# ------------------------------
# PowerShell Script Template
# (EVTX Export + ZIP 생성)
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
# Base64 변환 PS Script
# ------------------------------
def build_b64_script(zip_path):
    return fr"""
[Convert]::ToBase64String([IO.File]::ReadAllBytes('{zip_path}'))
"""

# ------------------------------
# Kali evidence 폴더 준비
# ------------------------------
def prepare_kali_folder():
    base_dir = os.path.expanduser("~/openedr_v1/evidence")
    raw_dir = os.path.join(base_dir, "raw")

    if not os.path.isdir(base_dir):
        os.makedirs(base_dir, exist_ok=True)

    if not os.path.isdir(raw_dir):
        os.makedirs(raw_dir, exist_ok=True)

    return raw_dir

# ------------------------------
# ZIP 파일 다운로드(Base64→파일)
# ------------------------------
def download_zip(session, zip_path, save_dir):
    print(f"\n[+] ZIP Base64 전송 요청...\n   → {zip_path}")

    b64_script = build_b64_script(zip_path)
    result = session.run_ps(b64_script)

    if result.status_code != 0:
        print(result.std_err.decode())
        raise Exception("[-] ZIP Base64 변환 실패")

    b64_data = result.std_out.decode().strip()

    # 로컬 저장 경로
    file_name = os.path.basename(zip_path)
    local_path = os.path.join(save_dir, file_name)

    with open(local_path, "wb") as f:
        f.write(base64.b64decode(b64_data))

    print(f"[+] ZIP 다운로드 완료 → {local_path}")
    return local_path

# ------------------------------
# Main Logic
# ------------------------------
def main():
    print("\n===== 원격 EVTX 수집 및 ZIP 다운로드기 (WinRM) =====\n")

    target_ip = input("Target IP: ").strip()
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ").strip()

    print("\n[+] WinRM 연결 중...")

    try:
        session = winrm.Session(
            f"http://{target_ip}:5985/wsman",
            auth=(username, password),
            transport='ntlm',
            server_cert_validation='ignore'
        )
    except Exception as e:
        print(f"[!] WinRM 연결 실패: {e}")
        sys.exit(1)

    print("[+] PowerShell 명령 실행 중...\n")

    # ---------- EVTX Export + ZIP 생성 ----------
    try:
        result = session.run_ps(PS_SCRIPT)
    except Exception as e:
        print(f"[!] PowerShell 실행 실패: {e}")
        sys.exit(1)

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

    if not zip_path:
        print("\n[!] ZIP 경로 추출 실패: 출력 로그를 확인하세요.")
        sys.exit(1)

    print(f"\n[+] 원격 ZIP 생성됨 → {zip_path}")

    # ---------- Kali evidence 폴더 준비 ----------
    save_dir = prepare_kali_folder()
    print(f"[+] Evidence 저장 폴더: {save_dir}")

    # ---------- ZIP 다운로드 ----------
    try:
        local_saved_path = download_zip(session, zip_path, save_dir)
    except Exception as e:
        print(f"[!] ZIP 다운로드 실패: {e}")
        sys.exit(1)

    print("\n[+] 원격 EVTX 수집 + ZIP 다운로드 완료!")
    print(f"[+] 로컬 저장 경로: {local_saved_path}\n")


if __name__ == "__main__":
    main()
