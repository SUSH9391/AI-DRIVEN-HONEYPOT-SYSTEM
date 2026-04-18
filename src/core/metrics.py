from prometheus_client import Counter

HONEYPOT_ATTACKS_TOTAL = Counter(
    "honeypot_attacks_total",
    "Total number of honeypot traps triggered",
    ["attack_type"]
)

SUSPICIOUS_REQUESTS_TOTAL = Counter(
    "suspicious_requests_total",
    "Total number of suspicious requests",
    ["endpoint"]
)
