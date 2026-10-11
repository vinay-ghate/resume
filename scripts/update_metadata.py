#!/usr/bin/env python3
"""
Resume Keyword Scraper and Metadata Generator
----------------------------------------------
Synchronizes metadata.json according to the guidelines in agent.md:
- Grounded in explicit mentions from .tex files.
- Normalized to canonical forms.
- Zero private data (no employers, clients, internal projects, or personal info).
- Deduplicated and case-insensitively sorted keyword lists.
- Sorted folder and file keys with 2-space JSON formatting.
"""

import os
import re
import json
import argparse
from typing import Dict, List, Set, Tuple

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
METADATA_PATH = os.path.join(REPO_ROOT, "metadata.json")

# Ignored directories per agent.md
IGNORED_DIRS = {".git", ".github", "scripts", "final_pdfs", "dist", "build", "public", "node_modules", ".vscode", ".agents"}

# Canonical term mappings: (Canonical Name, [Regex / Alias patterns])
# All patterns are matched case-insensitively on cleaned LaTeX text.
TERM_DEFINITIONS: List[Tuple[str, List[str]]] = [
    # --- Languages & Scripting ---
    ("Python", [r"\bpython\b"]),
    ("SQL", [r"\bsql\b"]),
    ("SQL Scripting", [r"\bsql\s+scripting\b"]),
    ("Java", [r"\bjava\b"]),
    ("Bash", [r"\bbash\b"]),
    ("TypeScript", [r"\btypescript\b"]),
    ("JavaScript", [r"\bjavascript\b"]),
    ("HTML", [r"\bhtml\b"]),
    ("CSS", [r"\bcss\b"]),
    ("YAML", [r"\byaml\b"]),

    # --- Backend & Microservices ---
    ("FastAPI", [r"\bfastapi\b"]),
    ("Django", [r"\bdjango\b"]),
    ("Flask", [r"\bflask\b"]),
    ("SQLAlchemy", [r"\bsqlalchemy\b"]),
    ("asyncio", [r"\basyncio\b"]),
    ("REST APIs", [r"\brest\s+apis?\b", r"\brestful\s+apis?\b", r"\brestful\s+endpoints?\b"]),
    ("GraphQL", [r"\bgraphql\b"]),
    ("gRPC", [r"\bgrpc\b"]),
    ("Protocol Buffers", [r"\bprotocol\s+buffers\b", r"\bprotobuf\b"]),
    ("Microservices", [r"\bmicroservices?\b"]),
    ("Event-Driven Architecture", [r"\bevent-driven\s+architecture\b", r"\bevent-driven\s+systems?\b"]),
    ("Event-Driven Processing", [r"\bevent-driven\s+processing\b"]),
    ("Automation Workflows", [r"\bautomation\s+workflows?\b"]),
    ("Modular Design", [r"\bmodular\s+design\b"]),
    ("System Architecture", [r"\bsystem\s+architecture\b"]),
    ("Systems Automation", [r"\bsystems\s+automation\b"]),
    ("SDLC Optimization", [r"\bsdlc\b"]),

    # --- Architecture & Distributed Systems ---
    ("System Design", [r"\bsystem\s+design\b"]),
    ("Distributed Systems", [r"\bdistributed\s+systems\b"]),
    ("Scalability", [r"\bscalability\b"]),
    ("Fault Tolerance", [r"\bfault\s+tolerance\b"]),
    ("Caching", [r"\bcaching\b", r"\bcaching\s+layer\b"]),
    ("Load Balancing", [r"\bload\s+balancing\b"]),
    ("Message Queues", [r"\bmessage\s+queues?\b", r"\bmessaging\b"]),
    ("HLD & LLD", [r"\bhld\s*&\s*lld\b", r"\bhigh-level\s+design\b"]),
    ("OOP", [r"\boop\b", r"\bobject-oriented\s+programming\b"]),
    ("Design Patterns", [r"\bdesign\s+patterns\b"]),
    ("API Design", [r"\bapi\s+design\b"]),
    ("Rate Limiting", [r"\brate\s+limiting\b"]),

    # --- Messaging & Streaming ---
    ("Apache Kafka", [r"\bapache\s+kafka\b", r"\bkafka\b"]),
    ("Strimzi Kafka", [r"\bstrimzi\b", r"\bstrimzi\s+kafka\b"]),
    ("Kafka Partitioning", [r"\bpartitioning\b"]),
    ("Kafka Producers & Consumers", [r"\bproducers/consumers\b", r"\bproducers\s+and\s+consumers\b", r"\bproducer\b.*\bconsumer\b"]),
    ("Kafka Consumer Lag", [r"\bconsumer\s+lag\b"]),
    ("WebSockets", [r"\bwebsockets?\b"]),
    ("Continuous Data Pipelines", [r"\bcontinuous\s+data\s+pipelines?\b", r"\bdata\s+pipelines?\b"]),
    ("Real-Time Processing", [r"\breal-time\s+processing\b", r"\bnear\s+real-time\b"]),

    # --- Databases & Stores ---
    ("PostgreSQL", [r"\bpostgresql\b", r"\bpostgres\b"]),
    ("MySQL", [r"\bmysql\b"]),
    ("MongoDB", [r"\bmongodb\b"]),
    ("ChromaDB", [r"\bchromadb\b"]),
    ("Oracle DB", [r"\boracle\s+db\b", r"\boracle\s+database\b"]),
    ("Hadoop", [r"\bhadoop\b"]),
    ("Vector Databases", [r"\bvector\s+databases?\b"]),
    ("Database Management Systems (DBMS)", [r"\bdatabase\s+management\s+systems\b", r"\bdbms\b"]),
    ("Schema Design", [r"\bschema\s+design\b"]),
    ("Database Design", [r"\bdatabase\s+design\b"]),
    ("Database Indexing", [r"\bdatabase\s+indexing\b", r"\bindexing\b"]),
    ("Database Replication", [r"\breplication\b"]),
    ("Database Sharding", [r"\bsharding\b"]),
    ("Data Extraction", [r"\bdata\s+extraction\b"]),

    # --- Cloud & DevOps ---
    ("Kubernetes", [r"\bkubernetes\b", r"\bk8s\b"]),
    ("Docker", [r"\bdocker\b"]),
    ("Docker Compose", [r"\bdocker\s+compose\b"]),
    ("Helm", [r"\bhelm\b"]),
    ("Linux", [r"\blinux\b"]),
    ("Shell Scripting", [r"\bshell\s+scripting\b", r"\blinux\s*\(\s*shell\b"]),
    ("SSH", [r"\bssh\b"]),
    ("CI/CD", [r"\bci/cd\b", r"\bcontinuous\s+delivery\b"]),
    ("GitHub Actions", [r"\bgithub\s+actions\b"]),
    ("Prometheus", [r"\bprometheus\b"]),
    ("Grafana", [r"\bgrafana\b"]),
    ("AWS APIs", [r"\baws\s+apis?\b", r"\baws\s*,\s*gcp\s+apis\b", r"\bazure\s*,\s*aws\s*,\s*gcp\s+apis\b"]),
    ("Azure APIs", [r"\bazure\s+apis?\b", r"\bazure\s*,\s*aws\b.*?apis\b"]),
    ("GCP APIs", [r"\bgcp\s+apis?\b", r"\b(?:azure\s*,\s*)?(?:aws\s*,\s*)?gcp\s+apis?\b"]),
    ("Git", [r"\bgit\b"]),

    # --- AI, LLM & Agentic AI ---
    ("Agentic AI", [r"\bagentic\s+ai\b"]),
    ("Agentic Workflows", [r"\bagentic\s+workflows?\b"]),
    ("Multi-Agent Systems", [r"\bmulti-agent\s+applications?\b", r"\bmulti-agent\s+systems?\b"]),
    ("Multi-Agent Orchestration", [r"\bmulti-agent\s+orchestration\b"]),
    ("Agent-to-Agent Communication", [r"\bagent-to-agent\s+communication\b"]),
    ("Agent Memory", [r"\bagent\s+memory\b", r"\bshort-term\s+state\s+and\s+long-term\s+memory\b"]),
    ("Model Context Protocol (MCP)", [r"\bmcp\b", r"\bmodel\s+context\s+protocol\b", r"\bmcps\b"]),
    ("Tool Calling", [r"\btool\s+calling\b", r"\btool-using\b"]),
    ("ReAct Framework", [r"\breact\b", r"\breact\s+framework\b"]),
    ("Plan-and-Execute", [r"\bplan-and-execute\b"]),
    ("LangGraph", [r"\blanggraph\b"]),
    ("LangChain", [r"\blangchain\b"]),
    ("CrewAI", [r"\bcrewai\b"]),
    ("AutoGen", [r"\bautogen\b"]),
    ("LlamaIndex", [r"\bllamaindex\b"]),
    ("Large Language Models (LLMs)", [r"\bllms?\b", r"\blarge\s+language\s+models?\b"]),
    ("Small Language Models (SLMs)", [r"\bslms?\b", r"\bsmall\s+language\s+models?\b"]),
    ("Multi-Modal LLMs", [r"\bmulti-modal\s+llms?\b", r"\bmultimodal\b"]),
    ("Generative AI", [r"\bgenerative\s+ai\b", r"\bgen-?ai\b"]),
    ("Prompt Engineering", [r"\bprompt\s+engineering\b"]),
    ("Retrieval-Augmented Generation (RAG)", [r"\brag\b", r"\bretrieval-augmented\s+generation\b", r"\brag\s+pipelines?\b"]),
    ("Modular RAG", [r"\bmodular\s+rag\b"]),
    ("Vector Embeddings", [r"\bvector\s+embeddings?\b", r"\bembeddings?\b"]),
    ("Semantic Search", [r"\bsemantic\s+search\b", r"\bsemantic\s+retrieval\b"]),
    ("text-embedding-3-small", [r"\btext-embedding-3-small\b"]),
    ("Fine-Tuning", [r"\bfine-tuning\b", r"\bfine-tuned\b"]),
    ("PEFT", [r"\bpeft\b", r"\bparameter-efficient\s+fine-tuning\b"]),
    ("LoRA", [r"\blora\b"]),
    ("QLoRA", [r"\bqlora\b"]),
    ("RLHF", [r"\brlhf\b", r"\breinforcement\s+learning\s+from\s+human\s+feedback\b"]),
    ("Cognee", [r"\bcognee\b"]),
    ("NVIDIA NIM", [r"\bnvidia\s+nim\b"]),
    ("Llama 3.1 8B", [r"\bllama\s+3\.1\s+8b\b"]),
    ("OpenAI API", [r"\bopenai\s+apis?\b", r"\bopenai\b"]),
    ("ChatGPT API", [r"\bchatgpt\s+apis?\b", r"\bchatgpt\b"]),
    ("Gemini API", [r"\bgemini\s+apis?\b", r"\bgemini\b"]),
    ("Hugging Face", [r"\bhugging\s*face\b"]),
    ("Streamlit", [r"\bstreamlit\b"]),
    ("NL2SQL", [r"\bnl2sql\b", r"\bnatural\s+language\s+(?:to\s+)?sql\b", r"\bquery\s+sql\s+db\s+using\s+natural\s+language\b"]),
    ("Token Optimization", [r"\btoken\s+usage\b", r"\btoken\s+optimization\b"]),
    ("LLM APIs", [r"\bllm\s+apis?\b"]),
    ("n8n", [r"\bn8n\b"]),
    ("Zapier", [r"\bzapier\b"]),
    ("Google Maps API", [r"\bgoogle\s+maps\s+api\b"]),

    # --- AI Safety, Governance & LLMOps ---
    ("Responsible AI", [r"\bresponsible\s+ai\b"]),
    ("Anti-Hallucination Guardrails", [r"\banti-hallucination\b"]),
    ("LLM Evaluation", [r"\bllm\s+evaluation\b"]),
    ("LLM Guardrails", [r"\bguardrails\b", r"\bllm\s+guardrails\b"]),
    ("SQL Allow-List Guardrail", [r"\bsql\s+allow-list\b"]),
    ("Prompt Injection Defenses", [r"\bprompt\s+injection\b"]),
    ("Pyrit", [r"\bpyrit\b"]),
    ("Microsoft HAX Toolkit", [r"\bhax\s+toolkit\b", r"\bmicrosoft\s+hax\b"]),
    ("BLEU Score", [r"\bbleu\b"]),

    # --- Security & Networking ---
    ("Cyber Security", [r"\bcyber\s+security\b", r"\bcybersecurity\b"]),
    ("mTLS", [r"\bmtls\b"]),
    ("TCP/IP", [r"\btcp/ip\b"]),
    ("HTTP/HTTPS", [r"\bhttp/https\b"]),
    ("Access Control", [r"\baccess\s+control\b"]),
    ("Data Governance", [r"\bdata\s+governance\b"]),
    ("Data Isolation", [r"\bdata\s+isolation\b"]),
    ("Operating Systems", [r"\boperating\s+systems\b"]),
    ("Software Engineering", [r"\bsoftware\s+engineering\b"]),

    # --- Public Certifications ---
    ("Confluent Data Streaming Engineer", [r"\bdata\s+streaming\s+engineer\s*--?\s*confluent\b", r"\bconfluent\b"]),
    ("Microsoft Certified: Azure AI Fundamentals", [r"\bmicrosoft\s+certified:\s*azure\s+ai\s+fundamentals\b", r"\bazure\s+ai\s+fundamentals\b"]),
    ("AWS Certified AI Practitioner", [r"\baws\s+certified\s+ai\s+practitioner\b"]),
    ("OCI Certified AI Foundations Associate", [r"\boci\s+certified\s+ai\s+foundations\s+associate\b"]),
    ("OCI Certified Foundations Associate", [r"\boci\s+certified\s+foundations\s+associate\b"]),
    ("OCI 2025 Generative AI Professional", [r"\boci\s+2025\s+generative\s+ai\s+professional\b"]),
]

def clean_latex(text: str) -> str:
    """Removes comments, structural commands, macros, while preserving text."""
    # Strip comments (% preceded by non-backslash or start of line)
    text = re.sub(r'(?<!\\)%.*$', '', text, flags=re.MULTILINE)
    # Strip formatting commands keeping text: \textbf{X}, \dv{X}, \small{X}, etc.
    # Handle up to 3 levels of nested braces
    for _ in range(3):
        text = re.sub(r'\\(?:textbf|textit|emph|small|scshape|underline|dv|fontsize\{[^}]*\}\{[^}]*\}|href\{[^}]*\})\s*\{([^}]*)\}', r' \1 ', text)
    # Remove structural macros
    text = re.sub(r'\\[a-zA-Z]+', ' ', text)
    # Unescape special characters
    text = text.replace(r'\%', '%').replace(r'\&', '&').replace(r'\$', '$').replace(r'\_', '_').replace(r'\#', '#').replace('~', ' ')
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    return text

def extract_keywords_from_file(file_path: str) -> List[str]:
    """Scrapes grounded, canonically formatted keywords from a single .tex file."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        raw_text = f.read()

    cleaned = clean_latex(raw_text)
    lower_cleaned = cleaned.lower()
    keywords: Set[str] = set()

    for canonical_name, patterns in TERM_DEFINITIONS:
        matched = False
        for pat in patterns:
            if re.search(pat, lower_cleaned, flags=re.IGNORECASE):
                matched = True
                break
        if matched:
            keywords.add(canonical_name)

    # Sort case-insensitively per agent.md
    return sorted(list(keywords), key=str.lower)

def scan_and_generate_metadata() -> Dict[str, Dict[str, List[str]]]:
    """Scans only *.tex files located directly inside top-level track folders."""
    metadata: Dict[str, Dict[str, List[str]]] = {}

    for entry in sorted(os.listdir(REPO_ROOT)):
        track_dir = os.path.join(REPO_ROOT, entry)
        if not os.path.isdir(track_dir) or entry in IGNORED_DIRS or entry.startswith("."):
            continue

        tex_files = [f for f in sorted(os.listdir(track_dir)) if f.endswith(".tex")]
        if not tex_files:
            continue

        metadata[entry] = {}
        for tex_file in sorted(tex_files):
            file_path = os.path.join(track_dir, tex_file)
            keywords = extract_keywords_from_file(file_path)
            metadata[entry][tex_file] = keywords

    return metadata

def save_metadata(metadata: Dict[str, Dict[str, List[str]]], file_path: str = METADATA_PATH):
    """Saves metadata with 2-space indentation and trailing newline."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
        f.write("\n")

def validate_metadata(metadata_path: str = METADATA_PATH) -> bool:
    """Validates the schema, file groundedness, and privacy constraints."""
    if not os.path.exists(metadata_path):
        print(f"[ERROR] metadata file not found at {metadata_path}")
        return False

    with open(metadata_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"[ERROR] Invalid JSON: {e}")
            return False

    if not isinstance(data, dict):
        print("[ERROR] Root of metadata.json must be a JSON object (dict).")
        return False

    # Forbidden terms (privacy: employer/client names, project names)
    FORBIDDEN_TERMS = {
        "tcs", "tata consultancy services", "scrobits", "ericsson", "ericsson enm", "ericsson espe",
        "chikistalaya", "nexyn", "weatherflow", "talkwithdb", "iodump", "gdsc", "gdsc zcoer",
        "amazon ml summer school", "zeal", "vinay", "ghate"
    }

    total_files = 0
    total_keywords = 0

    for folder, files in sorted(data.items()):
        folder_path = os.path.join(REPO_ROOT, folder)
        if not os.path.isdir(folder_path):
            print(f"[WARNING] Track directory '{folder}' listed in metadata.json does not exist.")

        if not isinstance(files, dict):
            print(f"[ERROR] Value for folder '{folder}' must be an object of filenames.")
            return False

        for filename, kw_list in sorted(files.items()):
            file_path = os.path.join(folder_path, filename)
            if not os.path.exists(file_path):
                print(f"[WARNING] File '{folder}/{filename}' does not exist on disk.")

            if not isinstance(kw_list, list):
                print(f"[ERROR] Keywords for '{folder}/{filename}' must be a list.")
                return False

            # Check sorting
            expected_sorted = sorted(set(kw_list), key=str.lower)
            if kw_list != expected_sorted:
                print(f"[ERROR] Keywords for '{folder}/{filename}' are not properly deduplicated or case-insensitively sorted.")
                return False

            # Check privacy forbidden terms
            for kw in kw_list:
                if kw.lower() in FORBIDDEN_TERMS:
                    print(f"[ERROR] Privacy violation: '{kw}' is in forbidden terms list.")
                    return False

            total_files += 1
            total_keywords += len(kw_list)

    print(f"[SUCCESS] metadata.json is valid!")
    print(f"Tracks: {len(data)} | Files: {total_files} | Total keywords indexed: {total_keywords}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Resume Keyword Scraper and Metadata Generator")
    parser.add_argument("--sync", action="store_true", help="Scan repository and regenerate metadata.json")
    parser.add_argument("--validate", action="store_true", help="Validate existing metadata.json")
    parser.add_argument("--stats", action="store_true", help="Print summary statistics of indexed keywords")
    args = parser.parse_args()

    if args.validate:
        is_valid = validate_metadata()
        exit(0 if is_valid else 1)

    if args.stats:
        validate_metadata()
        exit(0)

    # Default action: sync
    print(f"Scanning repository at: {REPO_ROOT}")
    meta = scan_and_generate_metadata()
    save_metadata(meta)
    print(f"Updated metadata.json with {len(meta)} track folders.")
    validate_metadata()

if __name__ == "__main__":
    main()
