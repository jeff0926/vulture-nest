# discovery_engine.py
"""
The Cynical Scraper - Vulture-Nest Discovery Engine

This module implements autonomous discovery of market gaps through:
1. Community Scraper: Reddit/X/Forums for "Negative Utility Signals"
2. Market-Cap Arbitrage: Legacy software with high traffic, low maintenance

NO FALSE OPTIMISM. Every discovery is treated as suspicious until validated.
"""
import os
import re
import json
import time
import random
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from validator import LeadCandidate


# =============================================================================
# CONSTANTS
# =============================================================================
NEGATIVE_UTILITY_TRIGGERS = [
    '"{incumbent}" how do I export',
    '"{incumbent}" export data',
    '"{incumbent}" alternatives {year}',
    '"{incumbent}" privacy concerns',
    '"{incumbent}" data privacy',
    '"{incumbent}" not working',
    '"{incumbent}" broken',
    '"{incumbent}" frustrating',
    '"{incumbent}" slow',
    '"{incumbent}" switched from',
    '"{incumbent}" moved away from',
    '"{incumbent}" replacement',
]

PAIN_KEYWORDS = [
    "frustrating", "annoying", "broken", "doesn't work", "can't",
    "missing", "lacks", "wish", "hate", "slow", "buggy", "crash",
    "sync", "backup", "lost", "disappeared", "limitation", "expensive",
    "privacy", "security", "export", "import", "lock-in", "abandoned"
]

# Categories to scan for opportunities
DISCOVERY_CATEGORIES = [
    "chrome extension",
    "micro-saas",
    "productivity app",
    "developer tool",
    "mobile app"
]

# Known high-traffic incumbents to scan (the "carcasses")
# PRIORITY: Unbundling targets - cloud subscriptions replaceable by local-first
KNOWN_CARCASSES = [
    # === PRIORITY UNBUNDLING TARGETS (Isenberg Delta) ===
    # High-value cloud subscriptions that can be local-first
    {"name": "Evernote", "category": "chrome extension", "estimated_traffic": 4000000,
     "unbundle_potential": "high", "cloud_dependency": "core", "local_first_viable": True},
    {"name": "LastPass", "category": "chrome extension", "estimated_traffic": 10000000,
     "unbundle_potential": "high", "cloud_dependency": "core", "local_first_viable": True},
    {"name": "Grammarly", "category": "chrome extension", "estimated_traffic": 30000000,
     "unbundle_potential": "medium", "cloud_dependency": "ai_processing", "local_first_viable": "partial"},
    {"name": "1Password", "category": "chrome extension", "estimated_traffic": 5000000,
     "unbundle_potential": "high", "cloud_dependency": "sync", "local_first_viable": True},
    {"name": "Bitwarden", "category": "chrome extension", "estimated_traffic": 3000000,
     "unbundle_potential": "medium", "cloud_dependency": "optional", "local_first_viable": True},
    {"name": "Dashlane", "category": "chrome extension", "estimated_traffic": 2000000,
     "unbundle_potential": "high", "cloud_dependency": "core", "local_first_viable": True},
    {"name": "Roam Research", "category": "micro-saas", "estimated_traffic": 500000,
     "unbundle_potential": "high", "cloud_dependency": "core", "local_first_viable": True},
    {"name": "Todoist", "category": "micro-saas", "estimated_traffic": 8000000,
     "unbundle_potential": "medium", "cloud_dependency": "sync", "local_first_viable": True},
    {"name": "Raindrop.io", "category": "chrome extension", "estimated_traffic": 500000,
     "unbundle_potential": "high", "cloud_dependency": "core", "local_first_viable": True},
    {"name": "Instapaper", "category": "chrome extension", "estimated_traffic": 1000000,
     "unbundle_potential": "high", "cloud_dependency": "core", "local_first_viable": True},

    # === STANDARD CARCASSES ===
    # Chrome Extensions
    {"name": "OneTab", "category": "chrome extension", "estimated_traffic": 2100000},
    {"name": "Evernote Web Clipper", "category": "chrome extension", "estimated_traffic": 4000000},
    {"name": "Honey", "category": "chrome extension", "estimated_traffic": 17000000},
    {"name": "AdBlock", "category": "chrome extension", "estimated_traffic": 65000000},
    {"name": "Momentum", "category": "chrome extension", "estimated_traffic": 3000000},
    {"name": "Web Highlights", "category": "chrome extension", "estimated_traffic": 100000},
    {"name": "Session Buddy", "category": "chrome extension", "estimated_traffic": 1000000},
    {"name": "Tab Manager Plus", "category": "chrome extension", "estimated_traffic": 500000},
    # Micro-SaaS
    {"name": "Calendly", "category": "micro-saas", "estimated_traffic": 8000000},
    {"name": "Loom", "category": "micro-saas", "estimated_traffic": 5000000},
    {"name": "Notion", "category": "micro-saas", "estimated_traffic": 30000000},
    {"name": "Airtable", "category": "micro-saas", "estimated_traffic": 5000000},
    {"name": "Zapier", "category": "micro-saas", "estimated_traffic": 10000000},
    {"name": "Carrd", "category": "micro-saas", "estimated_traffic": 2000000},
    {"name": "Gumroad", "category": "micro-saas", "estimated_traffic": 3000000},
    {"name": "ConvertKit", "category": "micro-saas", "estimated_traffic": 2000000},
    # Developer Tools
    {"name": "Postman", "category": "developer tool", "estimated_traffic": 15000000},
    {"name": "Figma", "category": "developer tool", "estimated_traffic": 20000000},
    {"name": "GitHub Copilot", "category": "developer tool", "estimated_traffic": 5000000},
]

# Exclusion list - already analyzed or built
EXCLUSION_FILE = "analyzed_hosts.json"


@dataclass
class DiscoverySignal:
    """A single pain signal discovered from scraping."""
    source: str  # reddit, twitter, forum, review_site
    content: str
    url: Optional[str] = None
    keyword: Optional[str] = None
    sentiment_score: float = 50.0  # 0-100, lower = more negative
    engagement: int = 0  # upvotes, likes, etc.
    timestamp: Optional[str] = None


@dataclass
class CarcassProfile:
    """Profile of an incumbent being analyzed."""
    name: str
    category: str
    traffic_monthly: int = 0
    last_update_months: int = 0
    sentiment_score: float = 50.0
    pain_signals: List[DiscoverySignal] = field(default_factory=list)
    competitors: List[str] = field(default_factory=list)
    weakness: str = ""
    export_format: str = "Unknown"

    def to_lead_candidate(self, growth_proj: float = 20.0, margin_proj: float = 80.0) -> LeadCandidate:
        """Convert to LeadCandidate for validation."""
        return LeadCandidate(
            name=f"{self.name} Alternative",
            incumbent=self.name,
            weakness=self.weakness,
            export_format=self.export_format,
            traffic_monthly=self.traffic_monthly,
            last_update_months=self.last_update_months,
            sentiment_score=self.sentiment_score,
            pain_signals=[s.content for s in self.pain_signals],
            competitors=self.competitors,
            growth_projection=growth_proj,
            margin_projection=margin_proj
        )


class ExclusionList:
    """Manages the list of already-analyzed hosts with time-based exclusions."""

    def __init__(self, filepath: str = EXCLUSION_FILE):
        self.filepath = filepath
        self.data = self._load()
        self.exclusions = self._get_active_exclusions()

    def _load(self) -> Dict:
        """Load exclusions from file."""
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as f:
                return json.load(f)
        return {"exclusions": [], "version": "1.0.0"}

    def _get_active_exclusions(self) -> Set[str]:
        """Get hosts that are still within exclusion period."""
        active = set()
        today = datetime.now().date()

        for exc in self.data.get("exclusions", []):
            exclude_until = exc.get("exclude_until")
            if exclude_until:
                try:
                    until_date = datetime.strptime(exclude_until, "%Y-%m-%d").date()
                    if today < until_date:
                        active.add(exc.get("name", "").lower())
                except ValueError:
                    pass

        # Also support legacy format
        for host in self.data.get("analyzed_hosts", []):
            active.add(host.lower())

        return active

    def save(self):
        """Save exclusions to file."""
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.filepath, 'w') as f:
            json.dump(self.data, f, indent=2)

    def is_excluded(self, host: str) -> bool:
        """Check if host is in exclusion list and still within exclusion period."""
        return host.lower() in self.exclusions

    def add(self, host: str, months: int = 6, reason: str = "ANALYZED"):
        """Add host to exclusion list with expiration."""
        from datetime import timedelta
        exclude_until = (datetime.now() + timedelta(days=months*30)).strftime("%Y-%m-%d")

        # Check if already exists
        for exc in self.data.get("exclusions", []):
            if exc.get("name", "").lower() == host.lower():
                exc["exclude_until"] = exclude_until
                exc["reason"] = reason
                self.save()
                return

        # Add new exclusion
        if "exclusions" not in self.data:
            self.data["exclusions"] = []

        self.data["exclusions"].append({
            "name": host,
            "host": f"{host.lower().replace(' ', '')}.com",
            "analyzed_at": datetime.now().strftime("%Y-%m-%d"),
            "exclude_until": exclude_until,
            "reason": reason
        })
        self.exclusions.add(host.lower())
        self.save()


class CommunityScraper:
    """
    Scrapes communities for Negative Utility Signals.

    Targets:
    - Reddit (via Google site search)
    - Review sites (G2, Capterra, TrustRadius)
    - General web complaints
    """

    def __init__(self, tool_client=None):
        self.tool_client = tool_client
        self._request_count = 0

    def _stealth_pause(self, min_sec: float = 2.0, max_sec: float = 5.0):
        """V-Governor: Random delay to avoid detection."""
        self._request_count += 1
        if self._request_count % 3 == 0:
            min_sec, max_sec = 4.0, 8.0
        pause = random.uniform(min_sec, max_sec)
        print(f"    [V-Governor] Stealth pause: {pause:.1f}s...")
        time.sleep(pause)

    def scan_reddit(self, incumbent: str) -> List[DiscoverySignal]:
        """Scan Reddit for complaints about incumbent."""
        print(f"    [CommunityScraper] Scanning Reddit for '{incumbent}'...")
        signals = []
        year = datetime.now().year

        # Build search queries from triggers
        queries = [
            f'site:reddit.com "{incumbent}" (problem OR frustrating OR broken OR alternative)',
            f'site:reddit.com "{incumbent}" (export OR migrate OR switch OR moved)',
            f'site:reddit.com "{incumbent}" alternatives {year}',
        ]

        if self.tool_client:
            for query in queries:
                self._stealth_pause(1.5, 3.0)
                try:
                    result = self.tool_client.google_web_search(query, max_results=5)
                    output = result.get("output", "")

                    # Extract signals from search results
                    for line in output.split('\n'):
                        line = line.strip()
                        if not line or line.startswith('('):
                            continue

                        # Check for pain keywords
                        for keyword in PAIN_KEYWORDS:
                            if keyword.lower() in line.lower():
                                signals.append(DiscoverySignal(
                                    source="reddit",
                                    content=line[:300],
                                    keyword=keyword,
                                    sentiment_score=self._estimate_sentiment(line)
                                ))
                                break

                except Exception as e:
                    print(f"    [CommunityScraper] Reddit scan error: {e}")

        print(f"    [CommunityScraper] Found {len(signals)} Reddit signals")
        return signals

    def scan_review_sites(self, incumbent: str) -> List[DiscoverySignal]:
        """Scan G2, Capterra, etc. for negative reviews."""
        print(f"    [CommunityScraper] Scanning review sites for '{incumbent}'...")
        signals = []

        review_queries = [
            f'site:g2.com "{incumbent}" reviews cons',
            f'site:capterra.com "{incumbent}" reviews',
            f'site:alternativeto.net "{incumbent}"',
            f'site:trustpilot.com "{incumbent}"',
        ]

        if self.tool_client:
            for query in review_queries:
                self._stealth_pause(2.0, 4.0)
                try:
                    result = self.tool_client.google_web_search(query, max_results=3)
                    output = result.get("output", "")

                    for line in output.split('\n'):
                        line = line.strip()
                        if not line:
                            continue

                        for keyword in PAIN_KEYWORDS:
                            if keyword.lower() in line.lower():
                                signals.append(DiscoverySignal(
                                    source="review_site",
                                    content=line[:300],
                                    keyword=keyword,
                                    sentiment_score=self._estimate_sentiment(line)
                                ))
                                break

                except Exception as e:
                    print(f"    [CommunityScraper] Review site scan error: {e}")

        print(f"    [CommunityScraper] Found {len(signals)} review site signals")
        return signals

    def scan_general_web(self, incumbent: str) -> List[DiscoverySignal]:
        """General web search for frustrations."""
        print(f"    [CommunityScraper] General web scan for '{incumbent}'...")
        signals = []
        year = datetime.now().year

        queries = [
            f'"{incumbent}" frustration OR problem OR "doesn\'t work"',
            f'"{incumbent}" alternative OR replacement {year}',
            f'"{incumbent}" privacy OR security concerns',
        ]

        if self.tool_client:
            for query in queries:
                self._stealth_pause(2.0, 4.0)
                try:
                    result = self.tool_client.google_web_search(query, max_results=5)
                    output = result.get("output", "")

                    for line in output.split('\n'):
                        line = line.strip()
                        if not line:
                            continue

                        for keyword in PAIN_KEYWORDS:
                            if keyword.lower() in line.lower():
                                signals.append(DiscoverySignal(
                                    source="web",
                                    content=line[:300],
                                    keyword=keyword,
                                    sentiment_score=self._estimate_sentiment(line)
                                ))
                                break

                except Exception as e:
                    print(f"    [CommunityScraper] Web scan error: {e}")

        print(f"    [CommunityScraper] Found {len(signals)} web signals")
        return signals

    def _estimate_sentiment(self, text: str) -> float:
        """
        Simple keyword-based sentiment estimation.
        Returns 0-100 where lower = more negative.
        """
        text_lower = text.lower()

        # Strong negative indicators
        strong_negative = ["hate", "terrible", "awful", "worst", "broken", "unusable", "garbage"]
        # Moderate negative
        moderate_negative = ["frustrating", "annoying", "slow", "buggy", "disappointing", "lacks"]
        # Neutral/positive
        positive = ["love", "great", "amazing", "best", "excellent", "perfect"]

        score = 50  # Start neutral

        for word in strong_negative:
            if word in text_lower:
                score -= 20

        for word in moderate_negative:
            if word in text_lower:
                score -= 10

        for word in positive:
            if word in text_lower:
                score += 15

        return max(0, min(100, score))


class MarketCapArbitrage:
    """
    Identifies legacy software with high traffic but low maintenance.

    Checks:
    - Traffic > 500k/mo
    - Last Update > 24 months
    - User Sentiment < 40%
    """

    def __init__(self, tool_client=None):
        self.tool_client = tool_client

    def check_stagnation(self, incumbent: str) -> Dict[str, Any]:
        """
        Check if incumbent shows signs of stagnation.
        Returns estimated metrics.
        """
        print(f"    [MarketCapArbitrage] Checking stagnation for '{incumbent}'...")

        # In production, this would call SimilarWeb/Semrush APIs
        # For now, we estimate based on web searches

        stagnation_signals = {
            "last_update_months": 0,
            "maintenance_signals": [],
            "stagnation_score": 0  # 0-100, higher = more stagnant
        }

        if self.tool_client:
            try:
                # Search for update/changelog info
                query = f'"{incumbent}" (changelog OR "last updated" OR "version history")'
                result = self.tool_client.google_web_search(query, max_results=5)
                output = result.get("output", "").lower()

                # Look for date patterns
                year_pattern = r'20[12][0-9]'
                years_found = re.findall(year_pattern, output)

                if years_found:
                    most_recent = max(int(y) for y in years_found)
                    current_year = datetime.now().year
                    years_since = current_year - most_recent
                    stagnation_signals["last_update_months"] = years_since * 12

                    if years_since >= 2:
                        stagnation_signals["stagnation_score"] += 40
                        stagnation_signals["maintenance_signals"].append(
                            f"Last mentioned update from {most_recent}"
                        )

                # Check for abandonment signals
                abandon_query = f'"{incumbent}" (abandoned OR "no longer maintained" OR discontinued)'
                abandon_result = self.tool_client.google_web_search(abandon_query, max_results=3)
                abandon_output = abandon_result.get("output", "").lower()

                if "abandoned" in abandon_output or "discontinued" in abandon_output:
                    stagnation_signals["stagnation_score"] += 30
                    stagnation_signals["maintenance_signals"].append("Abandonment signals detected")

            except Exception as e:
                print(f"    [MarketCapArbitrage] Stagnation check error: {e}")

        return stagnation_signals

    def find_competitors(self, incumbent: str) -> List[str]:
        """Find modern alternatives/competitors."""
        print(f"    [MarketCapArbitrage] Finding competitors for '{incumbent}'...")
        competitors = []
        year = datetime.now().year

        if self.tool_client:
            try:
                query = f'"{incumbent}" alternatives {year} OR "better than {incumbent}"'
                result = self.tool_client.google_web_search(query, max_results=10)
                output = result.get("output", "")

                # Extract product names (bold text in markdown)
                for line in output.split('\n'):
                    if '**' in line:
                        try:
                            name = line.split('**')[1].strip()
                            # Filter out the incumbent itself and common words
                            if (name.lower() != incumbent.lower() and
                                len(name) > 2 and
                                len(name.split()) <= 3 and
                                name.lower() not in ["the", "best", "top", "free", "alternative"]):
                                if name not in competitors:
                                    competitors.append(name)
                        except IndexError:
                            continue

            except Exception as e:
                print(f"    [MarketCapArbitrage] Competitor search error: {e}")

        print(f"    [MarketCapArbitrage] Found {len(competitors)} competitors")
        return competitors[:10]  # Limit to top 10

    def estimate_weakness(self, signals: List[DiscoverySignal]) -> str:
        """Synthesize the main weakness from pain signals."""
        if not signals:
            return "Unknown weakness"

        # Count keyword frequencies
        keyword_counts = {}
        for signal in signals:
            if signal.keyword:
                keyword_counts[signal.keyword] = keyword_counts.get(signal.keyword, 0) + 1

        # Find top keywords
        if keyword_counts:
            sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
            top_keywords = [kw for kw, _ in sorted_keywords[:3]]
            return f"Users frustrated with: {', '.join(top_keywords)}"

        return "General user dissatisfaction"


class DiscoveryEngine:
    """
    Main discovery orchestrator.

    Combines Community Scraper and Market-Cap Arbitrage to find
    high-potential market gaps.
    """

    def __init__(self, tool_client=None):
        self.tool_client = tool_client
        self.community_scraper = CommunityScraper(tool_client)
        self.arbitrage = MarketCapArbitrage(tool_client)
        self.exclusion_list = ExclusionList()

    def discover_carcasses(self, categories: List[str] = None) -> List[CarcassProfile]:
        """
        Discover potential carcasses to analyze.

        Returns list of CarcassProfile objects for validation.
        """
        print("\n[DiscoveryEngine] Starting carcass discovery...")

        if categories is None:
            categories = DISCOVERY_CATEGORIES

        carcasses = []

        # Filter known carcasses by category and exclusion list
        for carcass in KNOWN_CARCASSES:
            if carcass["category"] in categories:
                if self.exclusion_list.is_excluded(carcass["name"]):
                    print(f"    [DiscoveryEngine] Skipping excluded: {carcass['name']}")
                    continue

                profile = CarcassProfile(
                    name=carcass["name"],
                    category=carcass["category"],
                    traffic_monthly=carcass.get("estimated_traffic", 0)
                )
                carcasses.append(profile)

        print(f"[DiscoveryEngine] Found {len(carcasses)} potential carcasses")
        return carcasses

    def analyze_carcass(self, profile: CarcassProfile) -> CarcassProfile:
        """
        Deep analysis of a single carcass.

        Scrapes communities and checks for arbitrage signals.
        """
        print(f"\n[DiscoveryEngine] Analyzing carcass: {profile.name}")

        # === PHASE 1: Community Scraping ===
        print("[DiscoveryEngine] Phase 1: Community Scraping...")

        reddit_signals = self.community_scraper.scan_reddit(profile.name)
        review_signals = self.community_scraper.scan_review_sites(profile.name)
        web_signals = self.community_scraper.scan_general_web(profile.name)

        all_signals = reddit_signals + review_signals + web_signals
        profile.pain_signals = all_signals

        # Calculate average sentiment
        if all_signals:
            avg_sentiment = sum(s.sentiment_score for s in all_signals) / len(all_signals)
            profile.sentiment_score = avg_sentiment
        else:
            profile.sentiment_score = 60  # Neutral-ish if no signals

        # === PHASE 2: Market-Cap Arbitrage ===
        print("[DiscoveryEngine] Phase 2: Market-Cap Arbitrage...")

        stagnation = self.arbitrage.check_stagnation(profile.name)
        profile.last_update_months = stagnation.get("last_update_months", 0)

        competitors = self.arbitrage.find_competitors(profile.name)
        profile.competitors = competitors

        # === PHASE 3: Weakness Synthesis ===
        print("[DiscoveryEngine] Phase 3: Synthesizing weakness...")
        profile.weakness = self.arbitrage.estimate_weakness(all_signals)

        # Add to exclusion list
        self.exclusion_list.add(profile.name)

        print(f"[DiscoveryEngine] Analysis complete for {profile.name}")
        print(f"    Pain signals: {len(all_signals)}")
        print(f"    Sentiment: {profile.sentiment_score:.1f}")
        print(f"    Stagnation: {profile.last_update_months} months")
        print(f"    Competitors: {len(competitors)}")
        print(f"    Weakness: {profile.weakness}")

        return profile

    def run_discovery_cycle(
        self,
        categories: List[str] = None,
        max_carcasses: int = 5
    ) -> List[CarcassProfile]:
        """
        Run a full discovery cycle.

        Returns analyzed CarcassProfiles ready for validation.
        """
        print("\n" + "=" * 60)
        print("VULTURE-NEST DISCOVERY CYCLE")
        print("=" * 60)

        # Discover potential targets
        carcasses = self.discover_carcasses(categories)

        # Limit to max_carcasses
        carcasses = carcasses[:max_carcasses]

        # Analyze each carcass
        analyzed = []
        for profile in carcasses:
            try:
                analyzed_profile = self.analyze_carcass(profile)
                analyzed.append(analyzed_profile)
            except Exception as e:
                print(f"[DiscoveryEngine] Error analyzing {profile.name}: {e}")
                continue

        print("\n" + "=" * 60)
        print(f"DISCOVERY COMPLETE: {len(analyzed)} carcasses analyzed")
        print("=" * 60)

        return analyzed


# =============================================================================
# TEST HARNESS
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("DISCOVERY ENGINE TEST HARNESS")
    print("=" * 60)

    # Test without actual API calls (dry run)
    engine = DiscoveryEngine(tool_client=None)

    # Test exclusion list
    print("\n--- Testing Exclusion List ---")
    exclusions = ExclusionList()
    print(f"Current exclusions: {exclusions.exclusions}")

    # Test carcass discovery
    print("\n--- Testing Carcass Discovery ---")
    carcasses = engine.discover_carcasses(categories=["chrome extension"])
    for c in carcasses[:3]:
        print(f"  - {c.name} ({c.category}): {c.traffic_monthly:,} monthly traffic")

    # Create a mock profile for testing
    print("\n--- Testing Profile to LeadCandidate ---")
    mock_profile = CarcassProfile(
        name="TestApp",
        category="chrome extension",
        traffic_monthly=1000000,
        last_update_months=30,
        sentiment_score=35,
        pain_signals=[
            DiscoverySignal(source="reddit", content="This app is so frustrating", keyword="frustrating"),
            DiscoverySignal(source="reddit", content="Lost all my data", keyword="lost"),
        ],
        competitors=["Alt1", "Alt2"],
        weakness="Data loss and sync issues"
    )

    lead = mock_profile.to_lead_candidate()
    print(f"  Lead: {lead.name}")
    print(f"  Incumbent: {lead.incumbent}")
    print(f"  Weakness: {lead.weakness}")
    print(f"  Pain signals: {len(lead.pain_signals)}")

    print("\n" + "=" * 60)
    print("TEST HARNESS COMPLETE")
    print("=" * 60)
