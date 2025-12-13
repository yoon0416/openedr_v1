# Llama 초기 추론능력 테스트 메모
> 나중에 위키로 뺼 예정


### 세팅
1. 초기에는 인풋 아웃풋을 한글로 하였으나 개멍청해서 포기
2. 영어로 인풋 아웃풋 받으니 한글보단 괜찮아서 영어로 일단 진행


```run_infer_eng.py
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from datetime import datetime

MODEL_DIR = r"D:\krino_llm_train\model\llama-3.1-8b-base"

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_DIR,
    dtype=torch.bfloat16,
    device_map="auto"
)
model.eval()

# ===== 전체 테스트 시작 시간 (시스템 기준) =====
global_start_time = datetime.now()
print(f"\n[+] 전체 테스트 시작 시간 : {global_start_time.isoformat(timespec='seconds')}\n")


def ask(q):
    start_time = datetime.now()

    prompt = f"""Question:
{q}

Answer:
"""

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=120,            # 답변 길이 제한
            do_sample=False,               # 결정적 추론
            repetition_penalty=1.1,        # 반복 억제
            no_repeat_ngram_size=3,         # 문구 반복 방지
            early_stopping=True,            # EOS 만나면 종료
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id
        )

    gen = outputs[0][inputs["input_ids"].shape[-1]:]
    answer = tokenizer.decode(gen, skip_special_tokens=True)

    end_time = datetime.now()
    elapsed_sec = (end_time - start_time).total_seconds()

    print("=" * 80)
    print(f"[질문 시작 시간] {start_time.isoformat(timespec='seconds')}")
    print(f"[질문 종료 시간] {end_time.isoformat(timespec='seconds')}")
    print(f"[추론 소요 시간] {elapsed_sec:.2f} 초")
    print(f"[질문] {q}")
    print(f"[응답] {answer.strip()}")
    print("=" * 80 + "\n")

# 테스트 질문들
# Test questions (English)

# Cybersecurity – 30 Questions
ask("What is the difference between confidentiality, integrity, and availability?")
ask("Why is defense in depth important in cybersecurity architecture?")
ask("How does attack surface reduction improve security posture?")
ask("Why are misconfigurations a major cause of security breaches?")
ask("What is the role of threat modeling in secure system design?")
ask("Why is least privilege critical in enterprise environments?")
ask("How do zero-day vulnerabilities differ from known vulnerabilities?")
ask("Why is patch management considered a security control?")
ask("What risks arise from exposed administrative interfaces?")
ask("How does encryption protect data at rest and in transit?")
ask("Why is identity considered the new security perimeter?")
ask("How do attackers abuse trust relationships in networks?")
ask("What is lateral movement and why is it dangerous?")
ask("Why are backups a critical security control against ransomware?")
ask("How does supply chain risk affect cybersecurity?")
ask("What is the difference between authentication and authorization?")
ask("Why is logging essential for security monitoring?")
ask("How do attackers bypass traditional security controls?")
ask("Why are human factors a major security risk?")
ask("What is security hardening and why is it necessary?")
ask("Why is asset visibility important for security operations?")
ask("How do attackers weaponize publicly available information?")
ask("Why are legacy systems high-risk in modern environments?")
ask("What role does automation play in modern cybersecurity?")
ask("Why is continuous monitoring more effective than periodic audits?")
ask("How do attackers exploit default credentials?")
ask("Why is network segmentation important?")
ask("What is the purpose of security baselines?")
ask("How does threat intelligence improve defensive decision-making?")
ask("Why must security controls be validated continuously?")

#Digital Forensics – 30 Questions
ask("What is digital forensics and its primary objective?")
ask("Why is evidence integrity critical in forensic investigations?")
ask("What is the difference between live and dead forensics?")
ask("Why is chain of custody important?")
ask("How does time synchronization affect forensic analysis?")
ask("Why is volatile data important in investigations?")
ask("What challenges exist when performing memory forensics?")
ask("Why must forensic tools be validated?")
ask("What is the role of hashing in forensics?")
ask("Why is context important when interpreting artifacts?")
ask("How can user activity be reconstructed from artifacts?")
ask("Why are timestamps often unreliable in isolation?")
ask("What is the importance of timeline analysis?")
ask("Why do attackers attempt to destroy forensic evidence?")
ask("How does encryption complicate forensic investigations?")
ask("What is the difference between artifacts and indicators?")
ask("Why is attribution difficult in digital forensics?")
ask("How do file system artifacts support investigations?")
ask("Why is log correlation critical in forensics?")
ask("What risks exist when analyzing compromised systems?")
ask("Why must forensic analysis be repeatable?")
ask("What is the significance of persistence artifacts?")
ask("How does malware obfuscation affect forensic analysis?")
ask("Why is environment knowledge important in investigations?")
ask("What is the role of forensic triage?")
ask("Why are deleted files still valuable evidence?")
ask("How does anti-forensics impact investigations?")
ask("Why must investigators avoid altering evidence?")
ask("What challenges arise in cloud forensics?")
ask("Why is reporting a critical forensic deliverable?")

#EDR – 30 Questions
ask("What is Endpoint Detection and Response?")
ask("How does EDR differ from traditional antivirus?")
ask("Why is behavioral detection critical for endpoints?")
ask("How does EDR detect fileless attacks?")
ask("Why is process lineage important in EDR?")
ask("How does EDR support incident response?")
ask("Why are LOLBins difficult to detect?")
ask("How does EDR correlate endpoint events?")
ask("Why is visibility more important than prevention alone?")
ask("How does EDR detect lateral movement?")
ask("Why does EDR rely heavily on telemetry?")
ask("How does EDR reduce dwell time?")
ask("Why is command-line logging important for EDR?")
ask("How does EDR help identify compromised accounts?")
ask("Why are false positives common in EDR systems?")
ask("How does EDR integrate with SIEM?")
ask("Why is endpoint isolation a critical response action?")
ask("How does EDR handle encrypted payloads?")
ask("Why is baseline behavior important for detection?")
ask("How does EDR support threat hunting?")
ask("Why are signed binaries still dangerous?")
ask("How does EDR detect privilege escalation?")
ask("Why is memory inspection useful for EDR?")
ask("How does EDR assist in root cause analysis?")
ask("Why does EDR need real-time response capabilities?")
ask("How do attackers attempt to evade EDR?")
ask("Why is continuous endpoint monitoring necessary?")
ask("How does EDR support MITRE ATT&CK mapping?")
ask("Why is endpoint telemetry noisy?")
ask("How does EDR improve post-incident reporting?")

#DFIR – 30 Questions
ask("What does DFIR stand for and why is it important?")
ask("How does DFIR differ from traditional forensics?")
ask("Why is incident scoping critical?")
ask("How is root cause analysis performed in DFIR?")
ask("Why is containment prioritized over eradication?")
ask("How does DFIR reduce organizational risk?")
ask("Why is timeline reconstruction essential?")
ask("How does DFIR support legal and compliance needs?")
ask("Why is communication important during incidents?")
ask("How does DFIR handle incomplete evidence?")
ask("Why must DFIR processes be documented?")
ask("How does DFIR integrate threat intelligence?")
ask("Why is attacker dwell time significant?")
ask("How does DFIR identify patient zero?")
ask("Why is persistence analysis critical?")
ask("How does DFIR prioritize evidence collection?")
ask("Why is hypothesis-driven analysis useful?")
ask("How does DFIR manage evidence at scale?")
ask("Why are playbooks useful in DFIR?")
ask("How does DFIR handle insider threats?")
ask("Why is automation important in DFIR?")
ask("How does DFIR support business continuity?")
ask("Why must DFIR teams understand attacker behavior?")
ask("How does DFIR leverage endpoint telemetry?")
ask("Why is post-incident review important?")
ask("How does DFIR improve security posture?")
ask("Why is DFIR multidisciplinary?")
ask("How does DFIR differ across attack types?")
ask("Why is evidence prioritization necessary?")
ask("How does DFIR support executive reporting?")

#Penetration Testing – 30 Questions
ask("What is the goal of penetration testing?")
ask("How does penetration testing differ from vulnerability scanning?")
ask("Why is reconnaissance critical in attacks?")
ask("How do attackers chain vulnerabilities?")
ask("Why is privilege escalation important?")
ask("How does lateral movement enable full compromise?")
ask("Why do attackers exploit misconfigurations?")
ask("How does credential harvesting work?")
ask("Why is post-exploitation analysis important?")
ask("How do attackers maintain persistence?")
ask("Why are phishing attacks effective?")
ask("How do attackers evade detection?")
ask("Why is payload obfuscation used?")
ask("How do attackers abuse trusted binaries?")
ask("Why is command execution a critical phase?")
ask("How does privilege context affect attacks?")
ask("Why are internal networks high-value targets?")
ask("How do attackers pivot between systems?")
ask("Why is stealth important for attackers?")
ask("How do attackers exploit weak authentication?")
ask("Why is exploit reliability important?")
ask("How do attackers abuse administrative tools?")
ask("Why is cleanup important after exploitation?")
ask("How does red teaming differ from pentesting?")
ask("Why is impact demonstration important?")
ask("How do attackers bypass endpoint security?")
ask("Why are fileless attacks popular?")
ask("How do attackers exploit PowerShell?")
ask("Why is enumeration continuous?")
ask("How do attackers validate successful compromise?")

#Logs & Telemetry – 30 Questions
ask("Why are logs critical for security analysis?")
ask("What is log normalization?")
ask("Why is log correlation important?")
ask("How do attackers manipulate logs?")
ask("Why is timestamp accuracy critical?")
ask("What challenges exist in centralized logging?")
ask("Why are missing logs a security concern?")
ask("How do logs support incident response?")
ask("Why is context important in log analysis?")
ask("How do false positives occur in log analysis?")
ask("Why is process execution logging important?")
ask("How do authentication logs reveal attacks?")
ask("Why is command-line logging valuable?")
ask("How do logs help detect lateral movement?")
ask("Why is DNS logging important?")
ask("How do network logs complement endpoint logs?")
ask("Why are application logs useful?")
ask("How do attackers blend into normal logs?")
ask("Why is log retention important?")
ask("How does log volume impact analysis?")
ask("Why is parsing accuracy critical?")
ask("How do logs support forensic timelines?")
ask("Why is user behavior analysis log-driven?")
ask("How do logs help detect persistence?")
ask("Why are error logs valuable?")
ask("How does logging support compliance?")
ask("Why is encryption relevant to logging?")
ask("How do attackers evade log-based detection?")
ask("Why must logs be protected from tampering?")
ask("How do logs enable threat hunting?")

#Computer Science (Security-Relevant) – 30 Questions
ask("What is a process and how does it differ from a thread?")
ask("How does memory management impact security?")
ask("Why are race conditions dangerous?")
ask("How does operating system privilege separation work?")
ask("Why are system calls important?")
ask("How does virtual memory work?")
ask("Why is stack vs heap distinction important?")
ask("How do buffers overflow vulnerabilities occur?")
ask("Why is input validation critical?")
ask("How does concurrency affect security?")
ask("Why are pointers dangerous in low-level languages?")
ask("How does compilation affect binary behavior?")
ask("Why does undefined behavior cause security issues?")
ask("How does the OS enforce access control?")
ask("Why is entropy important in cryptography?")
ask("How do file systems manage permissions?")
ask("Why is CPU architecture relevant to security?")
ask("How does caching affect side-channel attacks?")
ask("Why do sandbox escapes occur?")
ask("How does IPC work and why is it risky?")
ask("Why is randomness hard to implement securely?")
ask("How do interpreters differ from compiled programs?")
ask("Why does abstraction leak in security?")
ask("How does scheduling affect system behavior?")
ask("Why are legacy protocols insecure?")
ask("How does serialization cause vulnerabilities?")
ask("Why is type safety important?")
ask("How does memory corruption lead to exploits?")
ask("Why is system complexity a security risk?")
ask("How does performance optimization impact security?")
```

결과

```

진행중

````
