# Syntagma y
> 프로젝트 기간 : 25-12-10 ~ ing  
> 현재 레파지토리에 적용된 아키텍처 버전은 v2이다.  
> 현재 파일 time은 UTC-5 (동부 표준시, 미국ㆍ캐나다ㆍ중남미)이며 추후 패치 예정

---

# AI-Driven EDR Research Project (Full Architecture v1.5)
## Open-Source EDR + DFIR + LLM + Threat Intelligence System

본 문서는 WinRM 기반 원격 수집, Chainsaw/Sigma 기반 행위 탐지, Osquery 기반 시스템 상태 분석, Velociraptor 기반 DFIR 수집을 중심으로  
LLM 기반 Threat Intelligence 시스템을 연구·구축하기 위한 v1~v6 전체 아키텍처 로드맵을 정의한다.

본 버전 README은 기존 문서 대비  
AI 세팅, 학습, 추론, 데이터 구성, 최적화 전략을 모두 포함한 Full Version이다.

본 프로젝트는 v2까지 구현되었으며, v3~v6는 Research 단계로 설계되어 있다.  
v2.2.0 이후부터 MISP Threat Intelligence Pipeline이 포함될 예정이다.

---

# 사용된 오픈소스 목록
- chainsaw  
  https://github.com/WithSecureLabs/chainsaw  
- sigma  
  https://github.com/SigmaHQ/sigma  
- osquery  
  https://github.com/osquery/osquery  
- velociraptor  
  https://github.com/Velocidex/velociraptor  
- MISP (Threat Intelligence Platform)  
  https://github.com/MISP/MISP  

---

# 디렉토리 구조

```
openedr_v1/
│
├── tools/                 # 외부 도구(Chainsaw, Sigma, Osquery, YARA 등)
│   ├── chainsaw/
│   ├── sigma/
│   ├── osquery/
│   └── yara/
│
├── collectors/            # WinRM·SSH 기반 원격 수집 스크립트 (v1~v2 핵심)
│   ├── windows/
│   └── linux/
│
├── pipelines/             # v2~v3 자동화 파이프라인
│   ├── collect/           # 데이터 수집 단계
│   ├── merge/             # Evidence JSON 병합 단계 (v3~ MISP Input용)
│   └── analyze/           # LLM 및 TI 분석 단계
│
├── evidence/              # 수집된 JSON, EVTX, 로그 (절대 git 추적 금지)
│   ├── raw/
│   └── processed/
│
├── rules/                 # Sigma/YARA 커스텀 룰
│   ├── sigma/
│   └── yara/
│
├── models/                # LLM 관련 데이터 (v3~v6)
│   ├── datasets/
│   ├── adapters/
│   └── configs/
│
├── scripts/               # 실험용 스크립트
│
├── config/                # 설정 파일 (hosts, winrm.conf 등)
│
└── docs/                  # 아키텍처 문서, PDF, 연구 로그

```

---

# 0. System Environment Overview

## Software / Host
- Windows 11 (Agent)
- Kali Linux / Ubuntu (Server)
- Python 3.x
- WinRM Remote Execution
- Chainsaw + Sigma Rules
- Osquery
- YARA 4.5+
- Velociraptor Artifact Collection
- MISP (Threat Intelligence Integration v2.2+)
- Pandoc (PDF Export)
- Hugging Face Transformers
- llama.cpp / llama-cpp-python

## AI / Hardware
- GPU: RTX 4070 Ti 12GB VRAM
- Recommended Model: Llama 3 8B
- Fine-tuning: QLoRA 4-bit
- Quantization: GGUF 4-bit / 8-bit

## Storage Layout
- Evidence JSON Repository  
- DFIR Dataset Repository  
- Threat Intelligence Dataset (v5~)  
- Attack Pattern Knowledge Base (v6)

---

# 1. Research Objective

본 연구의 목적은 다음과 같다:

1. 원격 보안 데이터 수집 구조 구축  
2. Sigma 기반 행위 탐지 자동화  
3. Osquery 기반 정형 텔레메트리 확보  
4. Velociraptor 기반 DFIR 아티팩트 수집  
5. Evidence JSON 구조 통합(result.json)  
6. LLM 기반 위협 보고서 자동화  
7. MISP 기반 Threat Intelligence 강화(v2.2+)  
8. DFIR Timeline Reconstruction(v4)  
9. Adaptive Monitoring 및 Risk Scoring(v5)  
10. Attack Learning AI 및 룰 생성(v6)

---

# 2. Baseline Architecture

```
Windows Agent ── WinRM ──> Central Server
  |                                |
  |                     Evidence Aggregation
  |                                |
Chainsaw/Sigma            LLM Threat Intelligence Engine
Osquery                   Automated Report Generator (MD/PDF)
Velociraptor              MISP Threat Intel Enrichment (v2.2+)
```

---

# 3. Core Components

## 3.1 WinRM Remote Execution
EDR Agent 설치 없이 Windows 원격 조작 가능.  
기능:
- Osquery 실행  
- Chainsaw 실행  
- DFIR 아티팩트 수집  
- JSON Export  

---

## 3.2 Chainsaw + Sigma
EVTX 기반 빠르고 강력한 행위 탐지 엔진.

출력 파일:
- sigma_findings.json
- evtx_hunt.json

탐지 항목:
- 권한 상승
- RCE 시도
- 악성 스크립트
- Suspicious PowerShell
- 계정 공격
- Lateral Movement

---

## 3.3 Osquery
운영체제 내부를 테이블 기반으로 조사하는 보안 텔레메트리 엔진.

수집 대상:
- Process List  
- Network Sockets  
- Services  
- Registry Keys  
- Startup Items  

---

## 3.4 Velociraptor (DFIR Query Engine)
Artifacts 기반으로 고급 포렌식 데이터 확보 가능.  
예: Shimcache, Amcache, Prefetch, SRUM 등.

---

# 4. Evidence Pipeline Architecture

## 4.1 Data Flow

1. Chainsaw → EVTX 분석  
2. Osquery → 정형 텔레메트리  
3. Velociraptor → DFIR 아티팩트  
4. Agent → Server JSON 업로드  
5. Evidence JSON 병합(result.json)  
6. MISP Input으로 IOC 전송 (v2.2~)  
7. MISP Output 기반 Threat Intel 보강  
8. LLM 기반 분석 및 보고서 자동 생성  

---

## 4.2 Evidence Structure

```
evidence/
  raw/
    sigma.json
    processes.json
    network.json
    autoruns.json
    runkeys.json
    velociraptor.json
  processed/
    result.json
```

---

## 4.3 result.json Schema

```
{
  "raw": {
    "sigma": [],
    "processes": [],
    "network": [],
    "autoruns": [],
    "runkeys": [],
    "velociraptor": []
  },
  "metadata": {
    "hostname": "",
    "collected_at": ""
  },
  "ioc": {
    "hashes": [],
    "domains": [],
    "ips": [],
    "file_paths": [],
    "process_cmd": [],
    "registry_keys": [],
    "yara_hits": [],
    "sigma_hits": []
  }
}
```

---

# 5. AI Architecture (Full Stack Overview)

본 항목은 LLM 기반 Threat Intelligence를 위한 핵심 구조이다.

---

## 5.1 Model Selection Strategy

모델 후보:
- Llama 3 8B  
- DeepSeek 7B / 8B  
- Mistral 7B  
- Phi-3  
- Mixtral (optional)

학습/추론 전략:
- 4-bit GGUF for inference  
- QLoRA 4-bit for fine-tuning  
- FlashAttention / KV-Cache 사용  

---

## 5.2 QLoRA Fine-tuning Pipeline

환경:
- GPU: RTX 4070 Ti 12GB
- Batch Size: 1~2  
- LR: 1e-5 ~ 2e-5  

파이프라인:
```
Base Model (4-bit)
      |
    QLoRA
      |
  LoRA Adapters
      |
Fine-tuned Security LLM
```

---

## 5.3 DFIR Dataset 구성 전략

Dataset 요소:
1. Evidence JSON  
2. CoT 기반 DFIR Instruction  
3. 공격 시나리오 재구성  
4. TTP 추론  
5. IOC 분석  
6. 위험도 평가  

---

## 5.4 Inference Optimization

- 4-bit quantization  
- Sliding Window Attention  
- KV Cache 최적화  
- Prompt 통합 템플릿  
- chain-of-thought 압축  

---

## 5.5 Deployment Structure

```
+-----------------------+
| Security LLM Engine   |
|  - Reasoning Module   |
|  - DFIR Timeline      |
|  - Rule Generator     |
|  - Risk Scoring       |
+-----------------------+
          |
      Local Inference
          |
      result.json
```

---

## 5.6 RAG (Optional)

RAG Knowledge Base 예시:
- MITRE ATT&CK  
- CISA Alerts  
- MSRC Updates  
- KISA 보고서  
- DFIR Reference Docs  

---

# 6. Automated Reporting

자동 생성되는 보고서 요소:
1. Summary  
2. Suspicious Behavior  
3. Process Analysis  
4. Network Events  
5. Persistence Evidence  
6. Attack Timeline (v4+)  
7. Attacker Scenario (v4+)  
8. TTP Classification  
9. Recommendations  
10. IOC Summary  

출력 형식:
- Markdown  
- TXT  
- PDF  

---

# 7. Version Roadmap (v1 ~ v6)

v1: Static Mini-EDR  
- WinRM 수동 실행  
- Chainsaw 단독  
- Osquery 단독  
- evidence 수동 병합  
- 보고서 수동 LLM 분석  

v2: Automated Pipeline EDR  
- 전체 자동화 스크립트  
- 수집 → 병합 → 분석 자동화  
- CLI 기반 EDR 구조  

v2.2: MISP Threat Intelligence Integration  
- IOC 추출 및 MISP Input  
- MISP Output 기반 TI 강화  
- APT/TTP 매핑  
- Risk Score 기반 LLM 보고서 강화  

v3: Embedded AI EDR  
- 로컬 LLM 완전 통합  
- Evidence → LLM → 보고서 자동 생성  

v4: DFIR Timeline Reconstruction  
- 공격 흐름 시간순 재구성  
- Process Tree AI 추론  
- Persistence Map  
- Network Storyline  

v5: Risk Scoring & Adaptive Monitoring  
- Host Trust Score  
- Risk 기반 텔레메트리 조절  
- DFIR 모듈 자동 활성화  

v6: Attack Learning AI  
- 공격 패턴 학습  
- Sigma/YARA 룰 자동 생성  
- Threat Simulation  
- RAG 기반 지식 확장  

---

# 8. Conclusion

본 연구 로드맵(v1~v6)은 오픈소스 기반 EDR 구조에  
AI·DFIR·Threat Intelligence(MISP)를 결합하여

1) 원격 수집  
2) 행위 기반 탐지  
3) DFIR 텔레메트리  
4) Threat Intel 강화  
5) 공격 타임라인 재구성  
6) 룰 자동 생성  
7) 적응형 모니터링  

까지 확장하는 고급 연구 프로젝트이다.

v4 이후는 학술적 가치가 매우 높으며,  
v6 단계는 국내에서도 거의 연구되지 않은 난이도를 가진다.

---

