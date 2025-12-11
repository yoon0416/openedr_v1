#!/usr/bin/env python3
import winrm
import getpass
import os
import sys
import base64
import time

# --------------------------------------------------
# 1. OSQuery 실행 파일 경로 (고정)
# --------------------------------------------------
OSQUERY_PATH = r"C:\Program Files\osquery\osqueryi.exe"

# --------------------------------------------------
# 2. 수집할 OSQuery 쿼리 세트
#    - key: 파일 이름 prefix
#    - value: 실제 OSQuery 쿼리
# --------------------------------------------------
OSQUERY_QUERIES = {
    # --- 프로세스 / 네트워크 ---
    "processes": """
        SELECT pid, name, path, cmdline, parent, uid, gid, start_time
        FROM processes;
    """,
    "process_open_sockets": """
        SELECT pid, family, protocol, local_address, local_port,
               remote_address, remote_port, state
        FROM process_open_sockets;
    """,
    "listening_ports": """
        SELECT pid, address, port, protocol, path
        FROM listening_ports;
    """,
    "connections": """
        SELECT pid, family, protocol, local_address, local_port,
               remote_address, remote_port, state
        FROM connections;
    """,

    # --- 서비스 / 드라이버 / 모듈 ---
    "services": """
        SELECT name, display_name, path, status, start_type, user_account
        FROM services;
    """,
    "drivers": """
        SELECT name, display_name, path, service_key, start_type
        FROM drivers;
    """,
    "kernel_drivers": """
        SELECT name, path, service_key, start_type
        FROM kernel_drivers;
    """,

    # --- 계정 / 권한 / 로그인 ---
    "users": """
        SELECT uid, username, description, directory, shell
        FROM users;
    """,
    "groups": """
        SELECT gid, groupname, group_sid
        FROM groups;
    """,
    "user_groups": """
        SELECT ug.uid, u.username, ug.gid, g.groupname
        FROM user_groups ug
        JOIN users u ON ug.uid = u.uid
        JOIN groups g ON ug.gid = g.gid;
    """,
    "logged_in_users": """
        SELECT * FROM logged_in_users;
    """,
    "logon_sessions": """
        SELECT * FROM logon_sessions;
    """,

    # --- 자동 실행 / 스케줄러 ---
    "startup_items": """
        SELECT name, path, args, type, source
        FROM startup_items;
    """,
    "scheduled_tasks": """
        SELECT name, path, state, enabled, action, next_run_time
        FROM scheduled_tasks;
    """,

    # --- 시스템 / OS / 패치 / 프로그램 ---
    "os_version": """
        SELECT * FROM os_version;
    """,
    "system_info": """
        SELECT * FROM system_info;
    """,
    "patches": """
        SELECT * FROM patches;
    """,
    "programs": """
        SELECT name, version, install_location, publisher, install_date
        FROM programs;
    """,

    # --- 디스크 / 파일시스템 ---
    "disks": """
        SELECT * FROM disks;
    """,
    "logical_drives": """
        SELECT * FROM logical_drives;
    """,
    "mounts": """
        SELECT * FROM mounts;
    """,

    # --- 보안 제품 / 윈도우 보안 ---
    "windows_security_products": """
        SELECT * FROM windows_security_products;
    """,

    # --- 레지스트리 (Run 키, RDP 설정 등) ---
    "registry_run_hklm": """
        SELECT key, name, data
        FROM registry
        WHERE key LIKE 'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\Run%';
    """,
    "registry_run_hkcu": """
        SELECT key, name, data
        FROM registry
        WHERE key LIKE 'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run%';
    """,
    "registry_rdp": """
        SELECT key, name, data
        FROM registry
        WHERE key LIKE 'HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Control\\Terminal Server%';
    """,

    # --- 네임서버 / 네트워크 설정 ---
    "dns_resolvers": """
        SELECT * FROM dns_resolvers;
    """,
    "interface_addresses": """
        SELECT * FROM interface_addresses;
    """,

    # --- USB / 디바이스 흔적 ---
    "usb_devices": """
        SELECT * FROM usb_devices;
    """,
    "usb_devices_history": """
        SELECT * FROM usb_devices_history;
    """,

    # --- 브라우저 포렌식 (Chrome 기준, 있으면) ---
    "chrome_extensions": """
        SELECT * FROM chrome_extensions;
    """,
    "chrome_history": """
        SELECT * FROM chrome_history
        ORDER BY last_visit_time DESC
        LIMIT 100;
    """,
    "chrome_cookies": """
        SELECT host_key, name, path, encrypted_value, expires_utc
        FROM chrome_cookies
        LIMIT 100;
    """,

    # --- 공격 흔적 / DFIR 테이블들 (빌드에 따라 없을 수 있음) ---
    "prefetch": """
        SELECT * FROM prefetch;
    """,
    "shimcache": """
        SELECT * FROM shimcache;
    """,
    "amcache": """
        SELECT * FROM amcache;
    """,
    "powershell_events": """
        SELECT * FROM powershell_events
        ORDER BY time DESC
        LIMIT 200;
    """,
    "powershell_scripts": """
        SELECT * FROM powershell_scripts
        ORDER BY time DESC
        LIMIT 200;
    """,
}

# --------------------------------------------------
# Evidence/osquery/sweep 폴더 생성
# --------------------------------------------------
def prepare_osquery_sweep_folder():
    base = os.path.expanduser("~/openedr_v1/evidence/osquery")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    sweep_dir = os.path.join(base, f"sweep_{timestamp}")
    os.makedirs(sweep_dir, exist_ok=True)
    return sweep_dir

# --------------------------------------------------
# 한 개 OSQuery 쿼리를 WinRM + PowerShell로 실행
#   - 결과(JSON 문자열)를 Base64로 받아온 뒤 리턴
# --------------------------------------------------
def run_osquery_query(session, query):
    ps_cmd = f"""
$Output = & "{OSQUERY_PATH}" --json "{query.strip().replace('"', '\\"')}"
$Bytes = [System.Text.Encoding]::UTF8.GetBytes($Output)
[Convert]::ToBase64String($Bytes)
"""
    result = session.run_ps(ps_cmd)

    if result.status_code != 0:
        # stderr 내용도 같이 반환해서 디버깅에 활용
        stderr = result.std_err.decode(errors="ignore").strip()
        raise Exception(f"OSQuery 실행 실패 (exit={result.status_code})\n{stderr}")

    return result.std_out.decode().strip()

# --------------------------------------------------
# 메인 로직
# --------------------------------------------------
def main():
    print("\n===== OSQuery Windows 수집기 (Mini-EDR v1.1.x) =====\n")

    target = input("Target IP: ").strip()
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ").strip()

    print("\n[+] WinRM 연결 중...")

    try:
        session = winrm.Session(
            f"http://{target}:5985/wsman",
            auth=(username, password),
            transport="ntlm",
            server_cert_validation="ignore",
        )
    except Exception as e:
        print(f"[!] WinRM 연결 실패: {e}")
        sys.exit(1)

    # Sweep 폴더 준비
    sweep_dir = prepare_osquery_sweep_folder()
    print(f"[+] OSQuery 결과 저장 폴더: {sweep_dir}\n")

    success = []
    failed = []

    # --------------------------------------------------
    # 모든 OSQUERY_QUERIES 를 순회하면서 수집
    # --------------------------------------------------
    for name, query in OSQUERY_QUERIES.items():
        print(f"[+] [{name}] 쿼리 실행 중...")

        try:
            b64 = run_osquery_query(session, query)
            if not b64:
                raise Exception("빈 응답(Base64) 수신")

            data = base64.b64decode(b64)

            out_path = os.path.join(sweep_dir, f"{name}.json")
            with open(out_path, "wb") as f:
                f.write(data)

            print(f"    → 저장 완료: {out_path}\n")
            success.append(name)

        except Exception as e:
            print(f"    [!] {name} 수집 실패: {e}\n")
            failed.append(name)
            # 실패해도 다음 쿼리 계속 진행

    # --------------------------------------------------
    # 요약 출력
    # --------------------------------------------------
    print("\n===== OSQuery Sweep 요약 =====")
    print(f"[+] 저장 폴더: {sweep_dir}")
    print(f"[+] 성공한 쿼리: {len(success)} 개")
    if success:
        print("    - " + ", ".join(success))

    print(f"[+] 실패한 쿼리: {len(failed)} 개")
    if failed:
        print("    - " + ", ".join(failed))

    print("\n[✓] OSQuery 수집 작업 완료!\n")


if __name__ == "__main__":
    main()
