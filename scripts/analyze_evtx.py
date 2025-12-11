#!/usr/bin/env python3
import os
import time
import subprocess

# ------------------------------
# 보고서 저장 폴더 생성
# ------------------------------
def prepare_report_folder():
    base = os.path.expanduser("~/openedr_v1/evidence")
    report_dir = os.path.join(base, "reports")
    os.makedirs(report_dir, exist_ok=True)
    return report_dir

# ------------------------------
# 메인 로직
# ------------------------------
def main():
    print("\n===== EVTX Chainsaw 분석기 (Mini-EDR v1) =====\n")

    # 분석 대상 EVTX 폴더 입력
    evtx_dir = input("분석할 EVTX 폴더 경로를 입력하세요: ").strip()

    if not os.path.isdir(evtx_dir):
        print(f"[!] 유효한 폴더가 아닙니다: {evtx_dir}")
        return

    # Sigma rule 폴더 (Windows 전용)
    sigma_dir = os.path.expanduser("~/openedr_v1/tools/sigma/rules/windows")
    if not os.path.isdir(sigma_dir):
        print(f"[!] Sigma 룰 폴더가 없습니다: {sigma_dir}")
        return

    # Chainsaw 매핑 파일 (너의 실제 위치 그대로 반영)
    mapping_file = os.path.expanduser(
        "~/openedr_v1/tools/chainsaw/mappings/sigma-event-logs-all.yml"
    )
    if not os.path.isfile(mapping_file):
        print(f"[!] Chainsaw 매핑 파일을 찾을 수 없습니다: {mapping_file}")
        return

    # 출력 JSON 경로 생성
    report_dir = prepare_report_folder()
    ts = time.strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(report_dir, f"report_{ts}.json")

    print("\n[+] Chainsaw 분석 시작...")
    print(f"    - 입력 폴더: {evtx_dir}")
    print(f"    - Sigma 룰:  {sigma_dir}")
    print(f"    - Mapping:   {mapping_file}")
    print(f"    - 결과 JSON: {output_file}\n")

    # -------------------------
    # Chainsaw 실행 명령 작성
    # -------------------------
    cmd = [
        "chainsaw",
        "hunt",
        evtx_dir,                         # 분석 대상 폴더
        "--sigma", sigma_dir,             # Sigma 윈도우 룰
        "--mapping", mapping_file,        # Chainsaw Sigma 매핑 파일
        "--output", output_file           # JSON 출력
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"[✓] 분석 완료! 결과 저장됨 → {output_file}\n")
    except subprocess.CalledProcessError as e:
        print("[!] Chainsaw 실행 중 오류 발생")
        print(f"    오류 코드: {e.returncode}")
        print(f"    명령어: {' '.join(cmd)}\n")

if __name__ == "__main__":
    main()

