#!/usr/bin/env python3
import getpass
import sys
import os
import time

# -----------------------------
# Import pipeline modules
# -----------------------------
import remote_evtx_collect
import analyze_evtx
import osquery_collect


# ---------------------------------------------------------
# v2 Report Root Folder 생성
# ---------------------------------------------------------
def prepare_v2_report_root(username):
    """
    ~/openedr_v1/evidence/v2_report/<username>_<YYYYMMDD_HHMM>/ 구조 생성
    내부에 evtx, chainsaw, osquery, misc 폴더 자동 생성
    """

    # 한국시간(UTC+9) 기준 타임스탬프
    ts = time.strftime("%Y%m%d_%H%M")

    base = os.path.expanduser("~/openedr_v1/evidence/v2_report")
    root = os.path.join(base, f"{username}_{ts}")

    # 생성
    os.makedirs(root, exist_ok=True)
    os.makedirs(os.path.join(root, "evtx"), exist_ok=True)
    os.makedirs(os.path.join(root, "chainsaw"), exist_ok=True)
    os.makedirs(os.path.join(root, "osquery"), exist_ok=True)
    os.makedirs(os.path.join(root, "misc"), exist_ok=True)

    print(f"\n[+] v2 Report Root 생성됨 → {root}\n")
    return root


# -----------------------------
# Mini-EDR v2 Pipeline
# -----------------------------
def main():
    print("\n===== Mini-EDR v2 : One-Click Full Pipeline (Unified Evidence Folder) =====\n")

    # -----------------------------
    # 1) Single Input (once only)
    # -----------------------------
    target_ip = input("Target IP: ").strip()
    username  = input("Username: ").strip()
    password  = getpass.getpass("Password: ").strip()

    # -----------------------------
    # 2) 통합 Evidence Root 생성
    # -----------------------------
    report_root = prepare_v2_report_root(username)

    print("\n[1/3] EVTX 수집 단계 시작...\n")

    # -----------------------------
    # 3) EVTX 수집 / ZIP 다운로드 / 압축해제
    # -----------------------------
    evtx_folder = remote_evtx_collect.run(target_ip, username, password, report_root)

    if not evtx_folder:
        print("\n[!] EVTX 수집 단계 실패 → 파이프라인 종료")
        sys.exit(1)

    print(f"[✓] EVTX 수집 완료 → {evtx_folder}\n")

    # -----------------------------
    # 4) Chainsaw 분석
    # -----------------------------
    print("\n[2/3] Chainsaw + Sigma 분석 단계 시작...\n")

    report_json = analyze_evtx.run(evtx_folder, report_root)

    if not report_json:
        print("\n[!] Chainsaw 분석 실패 → 파이프라인 종료")
        sys.exit(1)

    print(f"[✓] Chainsaw JSON 생성됨 → {report_json}\n")

    # -----------------------------
    # 5) OSQuery Sweep
    # -----------------------------
    print("\n[3/3] OSQuery Sweep 단계 시작...\n")

    osquery_folder = osquery_collect.run(target_ip, username, password, report_root)

    if not osquery_folder:
        print("\n[!] OSQuery Sweep 실패 → 파이프라인 종료")
        sys.exit(1)

    print(f"[✓] OSQuery Sweep 결과 저장됨 → {osquery_folder}\n")

    # -----------------------------
    # 6) Final Summary
    # -----------------------------
    print("\n===== Mini-EDR v2 통합 Evidence 저장 완료 =====\n")
    print("✔ EVTX 수집 및 저장 성공")
    print("✔ Chainsaw Sigma 분석보고서 저장 성공")
    print("✔ OSQuery Sweep 결과 저장 성공")
    print("--------------------------------------------")
    print(f"Unified Evidence Root : {report_root}")
    print(f"EVTX Folder           : {evtx_folder}")
    print(f"Chainsaw Report JSON  : {report_json}")
    print(f"OSQuery Sweep Folder  : {osquery_folder}")
    print("--------------------------------------------")
    print("\n[✓] Mini-EDR v2 모든 작업 완료!\n")


# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    main()
