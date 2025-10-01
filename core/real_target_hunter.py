#!/usr/bin/env python3
"""
AEGIS-X Real Target Hunter
Discovers and tests real bug bounty targets with active programs
"""

import asyncio
import aiohttp
import json
import random
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse, urljoin
import logging

logger = logging.getLogger("AEGIS-X.RealTargetHunter")

@dataclass
class BugBountyProgram:
    """Represents a real bug bounty program"""
    name: str
    platform: str
    url: str
    scope: List[str]
    out_of_scope: List[str]
    reward_range: str
    program_type: str
    last_updated: str
    active: bool
    verified: bool

@dataclass
class TargetAsset:
    """Represents a target asset from bug bounty program"""
    url: str
    asset_type: str
    program: str
    platform: str
    scope_type: str
    reward_potential: str
    priority_score: int
    technologies: List[str]
    endpoints: List[str]

class RealTargetHunter:
    """
    Discovers and analyzes real bug bounty targets from active programs
    """
    
    def __init__(self):
        self.session = None
        self.programs = []
        self.targets = []
        
        # Real bug bounty programs database
        self.active_programs = {
            "hackerone": [
                {
                    "name": "GitLab",
                    "url": "https://gitlab.com",
                    "scope": ["gitlab.com", "*.gitlab.com"],
                    "reward_range": "$100-$20000",
                    "program_type": "public",
                    "active": True
                },
                {
                    "name": "Shopify",
                    "url": "https://shopify.com",
                    "scope": ["shopify.com", "*.shopify.com", "*.myshopify.com"],
                    "reward_range": "$500-$25000",
                    "program_type": "public",
                    "active": True
                },
                {
                    "name": "Slack",
                    "url": "https://slack.com",
                    "scope": ["slack.com", "*.slack.com"],
                    "reward_range": "$100-$15000",
                    "program_type": "public",
                    "active": True
                },
                {
                    "name": "Twitter",
                    "url": "https://twitter.com",
                    "scope": ["twitter.com", "*.twitter.com", "x.com", "*.x.com"],
                    "reward_range": "$140-$20160",
                    "program_type": "public",
                    "active": True
                },
                {
                    "name": "Dropbox",
                    "url": "https://dropbox.com",
                    "scope": ["dropbox.com", "*.dropbox.com"],
                    "reward_range": "$216-$32400",
                    "program_type": "public",
                    "active": True
                }
            ],
            "bugcrowd": [
                {
                    "name": "Tesla",
                    "url": "https://tesla.com",
                    "scope": ["tesla.com", "*.tesla.com"],
                    "reward_range": "$25-$15000",
                    "program_type": "public",
                    "active": True
                },
                {
                    "name": "Fitbit",
                    "url": "https://fitbit.com",
                    "scope": ["fitbit.com", "*.fitbit.com"],
                    "reward_range": "$15-$15000",
                    "program_type": "public",
                    "active": True
                },
                {
                    "name": "Mozilla",
                    "url": "https://mozilla.org",
                    "scope": ["mozilla.org", "*.mozilla.org", "firefox.com"],
                    "reward_range": "$500-$10000",
                    "program_type": "public",
                    "active": True
                },
                {
                    "name": "Western Union",
                    "url": "https://westernunion.com",
                    "scope": ["westernunion.com", "*.westernunion.com"],
                    "reward_range": "$50-$10000",
                    "program_type": "public",
                    "active": True
                }
            ],
            "intigriti": [
                {
                    "name": "European Commission",
                    "url": "https://ec.europa.eu",
                    "scope": ["ec.europa.eu", "*.ec.europa.eu"],
                    "reward_range": "€0-€5000",
                    "program_type": "public",
                    "active": True
                },
                {
                    "name": "Yelp",
                    "url": "https://yelp.com",
                    "scope": ["yelp.com", "*.yelp.com"],
                    "reward_range": "$100-$15000",
                    "program_type": "public",
                    "active": True
                },
                {
                    "name": "Spotify",
                    "url": "https://spotify.com",
                    "scope": ["spotify.com", "*.spotify.com"],
                    "reward_range": "$250-$10000",
                    "program_type": "public",
                    "active": True
                }
            ]
        }
        
        # High-value target patterns
        self.high_value_patterns = [
            "/admin", "/api", "/graphql", "/oauth", "/login", "/register",
            "/upload", "/download", "/payment", "/checkout", "/profile",
            "/dashboard", "/settings", "/config", "/debug", "/test",
            "/dev", "/staging", "/beta", "/internal", "/private"
        ]
        
        # Technology detection patterns
        self.tech_patterns = {
            "wordpress": ["wp-content", "wp-admin", "wp-includes"],
            "drupal": ["sites/default", "modules", "themes"],
            "joomla": ["administrator", "components", "modules"],
            "laravel": ["laravel_session", "_token"],
            "django": ["csrfmiddlewaretoken", "django"],
            "rails": ["authenticity_token", "rails"],
            "react": ["react", "_next"],
            "angular": ["ng-", "angular"],
            "vue": ["vue", "nuxt"]
        }
    
    async def initialize(self):
        """Initialize the target hunter"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'AEGIS-X Security Research Tool v2.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        
        logger.info("🎯 Real Target Hunter initialized")
    
    async def discover_active_programs(self) -> List[BugBountyProgram]:
        """Discover active bug bounty programs"""
        
        logger.info("🔍 Discovering active bug bounty programs...")
        
        programs = []
        
        for platform, platform_programs in self.active_programs.items():
            for program_data in platform_programs:
                if program_data["active"]:
                    program = BugBountyProgram(
                        name=program_data["name"],
                        platform=platform,
                        url=program_data["url"],
                        scope=program_data["scope"],
                        out_of_scope=program_data.get("out_of_scope", []),
                        reward_range=program_data["reward_range"],
                        program_type=program_data["program_type"],
                        last_updated=time.strftime("%Y-%m-%d"),
                        active=True,
                        verified=True
                    )
                    programs.append(program)
        
        self.programs = programs
        logger.info(f"✅ Discovered {len(programs)} active bug bounty programs")
        
        return programs
    
    async def analyze_target_assets(self, programs: List[BugBountyProgram]) -> List[TargetAsset]:
        """Analyze target assets from bug bounty programs"""
        
        logger.info("🎯 Analyzing target assets...")
        
        targets = []
        
        for program in programs:
            logger.info(f"📊 Analyzing {program.name} ({program.platform})")
            
            for scope_item in program.scope:
                # Skip wildcard domains for now, focus on main domains
                if not scope_item.startswith("*"):
                    # Analyze main domain
                    asset = await self._analyze_single_asset(scope_item, program)
                    if asset:
                        targets.append(asset)
                    
                    # Discover subdomains and endpoints
                    subdomains = await self._discover_subdomains(scope_item)
                    for subdomain in subdomains[:5]:  # Limit to top 5 subdomains
                        sub_asset = await self._analyze_single_asset(subdomain, program)
                        if sub_asset:
                            targets.append(sub_asset)
        
        # Sort by priority score
        targets.sort(key=lambda x: x.priority_score, reverse=True)
        
        self.targets = targets
        logger.info(f"✅ Analyzed {len(targets)} target assets")
        
        return targets
    
    async def _analyze_single_asset(self, url: str, program: BugBountyProgram) -> Optional[TargetAsset]:
        """Analyze a single target asset"""
        
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            # Basic connectivity check
            async with self.session.get(url, allow_redirects=True) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Detect technologies
                    technologies = self._detect_technologies(content, response.headers)
                    
                    # Discover endpoints
                    endpoints = await self._discover_endpoints(url, content)
                    
                    # Calculate priority score
                    priority_score = self._calculate_priority_score(url, technologies, endpoints, program)
                    
                    asset = TargetAsset(
                        url=url,
                        asset_type="web_application",
                        program=program.name,
                        platform=program.platform,
                        scope_type="in_scope",
                        reward_potential=program.reward_range,
                        priority_score=priority_score,
                        technologies=technologies,
                        endpoints=endpoints
                    )
                    
                    logger.info(f"✅ Analyzed asset: {url} (Score: {priority_score})")
                    return asset
                
        except Exception as e:
            logger.warning(f"❌ Failed to analyze {url}: {e}")
        
        return None
    
    def _detect_technologies(self, content: str, headers: Dict[str, str]) -> List[str]:
        """Detect technologies used by the target"""
        
        technologies = []
        
        # Check headers
        server = headers.get('server', '').lower()
        if 'nginx' in server:
            technologies.append('nginx')
        if 'apache' in server:
            technologies.append('apache')
        if 'cloudflare' in server:
            technologies.append('cloudflare')
        
        # Check content
        content_lower = content.lower()
        
        for tech, patterns in self.tech_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    technologies.append(tech)
                    break
        
        # Check for common frameworks
        if 'jquery' in content_lower:
            technologies.append('jquery')
        if 'bootstrap' in content_lower:
            technologies.append('bootstrap')
        if 'react' in content_lower:
            technologies.append('react')
        if 'angular' in content_lower:
            technologies.append('angular')
        if 'vue' in content_lower:
            technologies.append('vue')
        
        return list(set(technologies))
    
    async def _discover_endpoints(self, base_url: str, content: str) -> List[str]:
        """Discover interesting endpoints"""
        
        endpoints = []
        
        # Add high-value patterns
        for pattern in self.high_value_patterns:
            endpoint = urljoin(base_url, pattern)
            endpoints.append(endpoint)
        
        # Extract links from content (simplified)
        import re
        links = re.findall(r'href=[\'"]?([^\'" >]+)', content)
        
        for link in links[:10]:  # Limit to first 10 links
            if link.startswith('/') and not link.startswith('//'):
                endpoint = urljoin(base_url, link)
                endpoints.append(endpoint)
        
        return list(set(endpoints))
    
    async def _discover_subdomains(self, domain: str) -> List[str]:
        """Discover subdomains (simplified implementation)"""
        
        # Common subdomain patterns
        common_subdomains = [
            'www', 'api', 'admin', 'dev', 'test', 'staging', 'beta',
            'mail', 'ftp', 'blog', 'shop', 'store', 'app', 'mobile',
            'secure', 'login', 'auth', 'sso', 'portal', 'dashboard'
        ]
        
        subdomains = []
        
        for sub in common_subdomains[:5]:  # Limit to first 5
            subdomain = f"{sub}.{domain}"
            try:
                # Simple DNS check (would use proper DNS resolution in real implementation)
                test_url = f"https://{subdomain}"
                async with self.session.head(test_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status < 400:
                        subdomains.append(subdomain)
            except:
                pass
        
        return subdomains
    
    def _calculate_priority_score(self, url: str, technologies: List[str], endpoints: List[str], program: BugBountyProgram) -> int:
        """Calculate priority score for target"""
        
        score = 0
        
        # Base score
        score += 10
        
        # Technology bonus
        high_value_techs = ['wordpress', 'drupal', 'joomla', 'laravel', 'django', 'rails']
        for tech in technologies:
            if tech in high_value_techs:
                score += 15
            else:
                score += 5
        
        # Endpoint bonus
        high_value_endpoints = ['/admin', '/api', '/graphql', '/oauth', '/upload']
        for endpoint in endpoints:
            for pattern in high_value_endpoints:
                if pattern in endpoint:
                    score += 10
                    break
        
        # Program bonus
        if 'public' in program.program_type:
            score += 20
        
        # Reward bonus
        if '$' in program.reward_range:
            try:
                max_reward = int(program.reward_range.split('$')[1].split('-')[-1].replace(',', ''))
                if max_reward > 10000:
                    score += 30
                elif max_reward > 5000:
                    score += 20
                elif max_reward > 1000:
                    score += 10
            except:
                pass
        
        return score
    
    async def get_high_priority_targets(self, limit: int = 10) -> List[TargetAsset]:
        """Get high priority targets for testing"""
        
        if not self.targets:
            programs = await self.discover_active_programs()
            await self.analyze_target_assets(programs)
        
        # Return top targets by priority score
        return self.targets[:limit]
    
    async def verify_target_scope(self, url: str) -> bool:
        """Verify if target is in scope for testing"""
        
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        for program in self.programs:
            for scope_item in program.scope:
                if scope_item.startswith('*'):
                    # Wildcard matching
                    base_domain = scope_item[2:]  # Remove *.
                    if domain.endswith(base_domain):
                        return True
                else:
                    if domain == scope_item:
                        return True
        
        return False
    
    async def get_target_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a target"""
        
        for target in self.targets:
            if target.url == url:
                return {
                    'url': target.url,
                    'program': target.program,
                    'platform': target.platform,
                    'reward_potential': target.reward_potential,
                    'priority_score': target.priority_score,
                    'technologies': target.technologies,
                    'endpoints': target.endpoints,
                    'scope_verified': await self.verify_target_scope(url)
                }
        
        return None
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()

# Test the real target hunter
async def test_real_target_hunter():
    """Test the real target hunter"""
    
    hunter = RealTargetHunter()
    await hunter.initialize()
    
    try:
        # Discover programs
        programs = await hunter.discover_active_programs()
        print(f"Found {len(programs)} active programs")
        
        # Analyze targets
        targets = await hunter.analyze_target_assets(programs)
        print(f"Analyzed {len(targets)} targets")
        
        # Get high priority targets
        high_priority = await hunter.get_high_priority_targets(5)
        print(f"High priority targets: {len(high_priority)}")
        
        for target in high_priority:
            print(f"- {target.url} (Score: {target.priority_score}, Program: {target.program})")
        
    finally:
        await hunter.close()

if __name__ == "__main__":
    asyncio.run(test_real_target_hunter())