import re

from dataclasses import dataclass
from enum import Enum
from typing import Any


class RiskMark(str, Enum):
    SENSITIVE_INFO = "sensitive info"
    CRYPTOGRAPHIC_KEYS = "cryptographic keys"
    CREDENTIALS = "credentials"
    API_KEYS = "api keys"
    TOKENS = "tokens"
    CERTIFICATES = "certificates"

    DATABASE = "database"
    BACKUP = "backup"
    PERSONAL_DATA = "personal data"        # PII — emails, phones, паспорта

    ENV_CONFIG = "env config"              # .env, config.local и т.д.
    SECRETS_CONFIG = "secrets config"     # secrets.yaml, vault config

    CACHE = "cache"
    BUILD_ARTIFACTS = "build artifacts"   # dist/, build/, target/
    DEPENDENCIES = "dependencies"         # node_modules/, vendor/
    COMPILED_BINARIES = "compiled binaries"

    LOGS = "logs"
    DEBUG_OUTPUT = "debug output"
    CRASH_REPORTS = "crash reports"

    IDE_FILES = "ide files"               # .idea/, .vscode/settings
    OS_FILES = "os files"                 # .DS_Store, Thumbs.db

    INFRASTRUCTURE_CONFIG = "infrastructure config"  # terraform.tfstate, kubeconfig
    DEPLOYMENT_SECRETS = "deployment secrets"        # ansible vault, helm secrets

@dataclass
class RiskRule:
    pattern: str
    description: str
    examples: list[str]
    mark: RiskMark

RISK_RULES = (
    # CRYPTOGRAPHIC_KEYS
    RiskRule(
        pattern=r"(?i)\.(pem|key|p12|pfx|ppk|asc|gpg|pgp|der)$",
        description="Cryptographic key file extensions",
        examples=["id_rsa.pem", "server.key", "keystore.p12", "backup.gpg"],
        mark=RiskMark.CRYPTOGRAPHIC_KEYS,
    ),
    RiskRule(
        pattern=r"(?i)(private[_\-]?key|rsa[_\-]?key|dsa[_\-]?key|ecdsa[_\-]?key|ssh[_\-]?key)",
        description="Private/asymmetric key filename patterns",
        examples=["private_key.pem", "rsa_key.pem", "ssh_key"],
        mark=RiskMark.CRYPTOGRAPHIC_KEYS,
    ),

    # CREDENTIALS
    RiskRule(
        pattern=r"(?i)(^|[\\/])(credentials|passwd|shadow|htpasswd|netrc|\.pgpass)$",
        description="Well-known credential store filenames",
        examples=["credentials", "htpasswd", ".pgpass", "shadow"],
        mark=RiskMark.CREDENTIALS,
    ),
    RiskRule(
        pattern=r"(?i)service[_\-]?account.*\.(json|yaml|yml)$",
        description="Service account credential files",
        examples=["service_account.json", "gcp-service-account.json"],
        mark=RiskMark.CREDENTIALS,
    ),

    # API_KEYS
    RiskRule(
        pattern=r"(?i)api[_\-]?keys?\.(json|yaml|yml|env|txt)$",
        description="Files explicitly named as API key stores",
        examples=["api_keys.json", "api-keys.yml"],
        mark=RiskMark.API_KEYS,
    ),

    # TOKENS
    RiskRule(
        pattern=r"(?i)(access|auth|bearer|refresh)[_\-]?token(s)?\.(json|yaml|yml|txt)$",
        description="Token store filenames",
        examples=["access_token.json", "auth-tokens.yml"],
        mark=RiskMark.TOKENS,
    ),

    # CERTIFICATES
    RiskRule(
        pattern=r"(?i)\.(crt|cer|der|p7b|p7c)$",
        description="X.509 certificate file extensions",
        examples=["server.crt", "ca-bundle.cer", "cert.der"],
        mark=RiskMark.CERTIFICATES,
    ),

    # DATABASE
    RiskRule(
        pattern=r"(?i)\.(sql|sqlite|sqlite3|db|mdb|accdb|dump)$",
        description="Database dump and local DB file extensions",
        examples=["backup.sql", "app.sqlite3", "data.db", "export.dump"],
        mark=RiskMark.DATABASE,
    ),

    # BACKUP
    RiskRule(
        pattern=r"(?i)\.(bak|backup|old|orig|save)$",
        description="Backup file extensions",
        examples=["db.bak", "config.old", "settings.orig"],
        mark=RiskMark.BACKUP,
    ),
    RiskRule(
        pattern=r"(?i)(backup|snapshot|dump)[_\-]?\d{4}[_\-]?\d{2}[_\-]?\d{2}\.",
        description="Date-stamped backup filenames",
        examples=["backup_2024_01_15.sql", "snapshot-2024-03-01.tar.gz"],
        mark=RiskMark.BACKUP,
    ),

    # PERSONAL_DATA
    RiskRule(
        pattern=r"(?i)(pii|gdpr|personal[_\-]?data|user[_\-]?data|customer[_\-]?data)\.(csv|json|xml|xlsx|sql)$",
        description="Files explicitly labeled as containing personal or regulated data",
        examples=["pii_export.csv", "gdpr_users.json", "customer_data.xlsx"],
        mark=RiskMark.PERSONAL_DATA,
    ),
    RiskRule(
        pattern=r"(?i)(email|phone|passport|ssn|national[_\-]?id)[_\-]?(list|export|dump)\.(csv|json|txt)$",
        description="Bulk exports of PII fields",
        examples=["email_list.csv", "phone_dump.txt", "passport_export.json"],
        mark=RiskMark.PERSONAL_DATA,
    ),

    # ENV_CONFIG
    RiskRule(
        pattern=r"(?i)^\.env(\.(local|production|staging|development|test))?$",
        description="Dotenv configuration files",
        examples=[".env", ".env.local", ".env.production"],
        mark=RiskMark.ENV_CONFIG,
    ),
    RiskRule(
        pattern=r"(?i)config\.(local|private)\.(py|js|ts|php|rb|yaml|yml|json)$",
        description="Local override configuration files",
        examples=["config.local.js", "config.private.py"],
        mark=RiskMark.ENV_CONFIG,
    ),

    # SECRETS_CONFIG
    RiskRule(
        pattern=r"(?i)^secrets?\.(yaml|yml|json|toml|ini|cfg)$",
        description="Files explicitly named as secrets configuration",
        examples=["secrets.yaml", "secret.toml"],
        mark=RiskMark.SECRETS_CONFIG,
    ),
    RiskRule(
        pattern=r"(?i)^\.vault[_\-]?pass(word)?$",
        description="Ansible Vault password files",
        examples=[".vault_pass", ".vault_password"],
        mark=RiskMark.SECRETS_CONFIG,
    ),
    RiskRule(
        pattern=r"(?i)^sops\.(yaml|yml|json)$",
        description="SOPS-encrypted secrets file",
        examples=["sops.yaml", "sops.json"],
        mark=RiskMark.SECRETS_CONFIG,
    ),

    # CACHE
    RiskRule(
        pattern=r"(?i)^(__pycache__|\.pytest_cache|\.mypy_cache|\.ruff_cache|\.eslintcache|\.parcel-cache)$",
        description="Common language and tool cache directory names",
        examples=["__pycache__", ".pytest_cache", ".eslintcache"],
        mark=RiskMark.CACHE,
    ),

    # BUILD_ARTIFACTS
    RiskRule(
        pattern=r"(?i)^(dist|build|out|output|\.next|\.nuxt|\.svelte-kit)$",
        description="Common build output directory names",
        examples=["dist", "build", ".next", ".nuxt"],
        mark=RiskMark.BUILD_ARTIFACTS,
    ),
    RiskRule(
        pattern=r"(?i)\.(class|pyc|pyo|wasm)$",
        description="Compiled intermediate artifact file extensions",
        examples=["Main.class", "utils.pyc", "module.wasm"],
        mark=RiskMark.BUILD_ARTIFACTS,
    ),

    # DEPENDENCIES
    RiskRule(
        pattern=r"(?i)^(node_modules|vendor|\.venv|venv|bower_components)$",
        description="Dependency installation directory names",
        examples=["node_modules", "vendor", ".venv", "bower_components"],
        mark=RiskMark.DEPENDENCIES,
    ),

    # COMPILED_BINARIES
    RiskRule(
        pattern=r"(?i)\.(exe|bin|elf|run|msi|pkg|deb|rpm|apk|ipa)$",
        description="Executable and installable binary file extensions",
        examples=["app.exe", "server.elf", "installer.msi", "release.apk"],
        mark=RiskMark.COMPILED_BINARIES,
    ),

    # LOGS
    RiskRule(
        pattern=r"(?i)\.(log|logs?)$",
        description="Log file extensions",
        examples=["app.log", "error.log", "access.log"],
        mark=RiskMark.LOGS,
    ),
    RiskRule(
        pattern=r"(?i)^logs?$",
        description="Log directory names",
        examples=["log", "logs"],
        mark=RiskMark.LOGS,
    ),

    # DEBUG_OUTPUT
    RiskRule(
        pattern=r"(?i)^debug[_\-]?(output|log|dump|trace)\.(txt|log|json)$",
        description="Debug output and trace log filenames",
        examples=["debug_output.txt", "debug_log.json", "debug-trace.log"],
        mark=RiskMark.DEBUG_OUTPUT,
    ),
    RiskRule(
        pattern=r"(?i)\.(hprof|jfr|prof)$",
        description="JVM heap dump and profiling file extensions",
        examples=["java.hprof", "recording.jfr"],
        mark=RiskMark.DEBUG_OUTPUT,
    ),

    # CRASH_REPORTS
    RiskRule(
        pattern=r"(?i)\.(dmp|mdmp|core|crash)$",
        description="Core dump and crash dump file extensions",
        examples=["core.dmp", "app.mdmp", "app.crash"],
        mark=RiskMark.CRASH_REPORTS,
    ),
    RiskRule(
        pattern=r"(?i)^crash[_\-]?report(s)?\.(txt|log|json)$",
        description="Application crash report filenames",
        examples=["crash_report.txt", "crash-reports.json"],
        mark=RiskMark.CRASH_REPORTS,
    ),

    # IDE_FILES
    RiskRule(
        pattern=r"(?i)^(\.idea|\.vscode|\.vs|\.fleet|\.eclipse)$",
        description="IDE workspace and settings directory names",
        examples=[".idea", ".vscode", ".vs", ".fleet"],
        mark=RiskMark.IDE_FILES,
    ),
    RiskRule(
        pattern=r"(?i)\.(iml|iws|ipr|suo|code-workspace|sublime-project|sublime-workspace)$",
        description="IDE project and workspace file extensions",
        examples=["project.iml", "app.suo", "workspace.code-workspace"],
        mark=RiskMark.IDE_FILES,
    ),

    # OS_FILES
    RiskRule(
        pattern=r"(?i)^(\.DS_Store|Thumbs\.db|desktop\.ini|ehthumbs\.db)$",
        description="macOS and Windows OS metadata filenames",
        examples=[".DS_Store", "Thumbs.db", "desktop.ini"],
        mark=RiskMark.OS_FILES,
    ),

    # INFRASTRUCTURE_CONFIG
    RiskRule(
        pattern=r"(?i)^terraform\.tfstate(\.backup)?$",
        description="Terraform state files",
        examples=["terraform.tfstate", "terraform.tfstate.backup"],
        mark=RiskMark.INFRASTRUCTURE_CONFIG,
    ),
    RiskRule(
        pattern=r"(?i)^(kubeconfig|config)$",
        description="Kubernetes kubeconfig filenames",
        examples=["kubeconfig", "config"],
        mark=RiskMark.INFRASTRUCTURE_CONFIG,
    ),
    RiskRule(
        pattern=r"(?i)^(inventory|hosts)\.(ini|yaml|yml)$",
        description="Ansible inventory filenames",
        examples=["inventory.ini", "hosts.yml"],
        mark=RiskMark.INFRASTRUCTURE_CONFIG,
    ),

    # DEPLOYMENT_SECRETS
    RiskRule(
        pattern=r"(?i)^(vault|secrets?)\.(yaml|yml)$",
        description="Ansible vault and secrets variable files",
        examples=["vault.yml", "secrets.yaml"],
        mark=RiskMark.DEPLOYMENT_SECRETS,
    ),
    RiskRule(
        pattern=r"(?i)^values[_\-]secrets?\.(yaml|yml)$",
        description="Helm chart secret value override files",
        examples=["values-secrets.yml", "values_secret.yaml"],
        mark=RiskMark.DEPLOYMENT_SECRETS,
    ),
    RiskRule(
        pattern=r"(?i)^(credentials|accessTokens|application_default_credentials)\.(json|cfg)$",
        description="Cloud provider CLI credential filenames",
        examples=["credentials.json", "accessTokens.json", "application_default_credentials.json"],
        mark=RiskMark.DEPLOYMENT_SECRETS,
    ),

    # SENSITIVE_INFO
    RiskRule(
        pattern=r"(?i)(secret|private|confidential|internal[_\-]only)",
        description="Generic sensitive information markers in filenames",
        examples=["secret_notes.txt", "confidential_report.pdf", "private_data.csv"],
        mark=RiskMark.SENSITIVE_INFO,
    ),
)

def analyze_file(path: str, rules) -> list[dict[str, Any]]:
    matches = []

    for rule in rules:
        if re.search(rule.pattern, path):
            matches.append({
                "file": path,
                "mark": rule.mark,
                "description": rule.description,
                "pattern": rule.pattern,
            })

    return matches


def analyze_repo(files: list[str], rules) -> list:
    report = []

    for _file in files:
        result = analyze_file(_file, rules)

        if result:
            report.extend(result)

    return report


if __name__ == "__main__":
    files = [
        ".env",
        "config.json",
        "src/main.py",
        "id_rsa",
        "logs/app.log",
        "package-lock.json"
    ]

    report = analyze_repo(files, RISK_RULES)
    
    print(render_file_analyze(report))
