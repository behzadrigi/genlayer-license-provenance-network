# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
from dataclasses import dataclass
import json
import hashlib


ALLOWED_LABELS = ["MIT", "APACHE-2.0", "BSD-2-CLAUSE", "BSD-3-CLAUSE", "ISC", "MPL-2.0", "GPL-2.0", "GPL-3.0", "LGPL-3.0", "AGPL-3.0", "UNLICENSE"]
MODEL_LABELS = ALLOWED_LABELS + ["OTHER", "UNCLEAR"]
VERDICTS = ["CONFIRMED", "REFUTED", "INCONCLUSIVE"]


def sha_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sender_hex() -> str:
    s = gl.message.sender_address
    try:
        return str(s.as_hex).lower()
    except Exception:
        return str(s).lower()


def civil_to_epoch(y: int, m: int, d: int, hh: int, mm: int, ss: int) -> int:
    y2 = y - 1 if m <= 2 else y
    era = y2 // 400
    yoe = y2 - era * 400
    mp = (m + 9) % 12
    doy = (153 * mp + 2) // 5 + d - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    days = era * 146097 + doe - 719468
    return days * 86400 + hh * 3600 + mm * 60 + ss


def to_epoch(raw) -> int:
    if isinstance(raw, bool):
        raise Exception("TIME_UNAVAILABLE")
    if isinstance(raw, int) or isinstance(raw, float):
        return int(raw)
    if hasattr(raw, "year") and hasattr(raw, "month") and hasattr(raw, "day"):
        return civil_to_epoch(int(raw.year), int(raw.month), int(raw.day), int(getattr(raw, "hour", 0)), int(getattr(raw, "minute", 0)), int(getattr(raw, "second", 0)))
    s = str(raw).strip()
    if s.isdigit():
        return int(s)
    if len(s) < 19:
        raise Exception("TIME_UNAVAILABLE")
    try:
        y = int(s[0:4])
        m = int(s[5:7])
        d = int(s[8:10])
        hh = int(s[11:13])
        mm = int(s[14:16])
        ss = int(s[17:19])
    except Exception:
        raise Exception("TIME_UNAVAILABLE")
    if m < 1 or m > 12 or d < 1 or d > 31:
        raise Exception("TIME_UNAVAILABLE")
    return civil_to_epoch(y, m, d, hh, mm, ss)


def now_seconds() -> int:
    raw = None
    try:
        raw = gl.message.datetime
    except Exception:
        raw = None
    if raw is None:
        try:
            raw = gl.message_raw["datetime"]
        except Exception:
            raw = None
    if raw is None:
        raise Exception("TIME_UNAVAILABLE")
    return to_epoch(raw)


def parse_obj(raw) -> dict:
    s = str(raw)
    a = s.find("{")
    b = s.rfind("}")
    if a < 0 or b <= a:
        return {}
    try:
        v = json.loads(s[a:b + 1])
    except Exception:
        return {}
    if isinstance(v, dict):
        return v
    return {}


def leader_failed_ok(fn) -> bool:
    try:
        fn()
    except Exception:
        return True
    return False


def url_host(u: str) -> str:
    rest = u[8:]
    for sep in ["/", "?", "#"]:
        i = rest.find(sep)
        if i >= 0:
            rest = rest[:i]
    return rest.lower()


def base_domain(host: str) -> str:
    parts = host.split(":")[0].split(".")
    return ".".join(parts[-2:])


def check_url(u: str, err: str):
    if not isinstance(u, str) or len(u) < 12 or len(u) > 300 or not u.startswith("https://"):
        raise Exception(err)
    for ch in u:
        if ord(ch) <= 32 or ord(ch) >= 127:
            raise Exception(err)
    host = url_host(u)
    if host == "" or "@" in host or "." not in host:
        raise Exception(err)


@allow_storage
@dataclass
class Claim:
    claim_id: str
    attester: str
    package_id: str
    primary_url: str
    secondary_url: str
    claimed_label: str


def check_package_id(p: str):
    if not isinstance(p, str) or len(p) < 1 or len(p) > 80:
        raise Exception("INVALID_PACKAGE_ID")
    for ch in p:
        if ord(ch) <= 32 or ord(ch) >= 127:
            raise Exception("INVALID_PACKAGE_ID")


def check_sources(primary_url: str, secondary_url: str):
    check_url(primary_url, "INVALID_PRIMARY_URL")
    check_url(secondary_url, "INVALID_SECONDARY_URL")
    if primary_url == secondary_url:
        raise Exception("SOURCES_NOT_INDEPENDENT")
    if base_domain(url_host(primary_url)) == base_domain(url_host(secondary_url)):
        raise Exception("SOURCES_NOT_INDEPENDENT")


class LicenseClaimRegistry(gl.Contract):
    claims: TreeMap[str, Claim]
    seen: TreeMap[str, str]
    claim_total: u256

    def __init__(self):
        self.claim_total = u256(0)

    @gl.public.write
    def register_claim(self, package_id: str, primary_url: str, secondary_url: str, claimed_label: str):
        check_package_id(package_id)
        check_sources(primary_url, secondary_url)
        if claimed_label not in ALLOWED_LABELS:
            raise Exception("INVALID_LABEL")
        who = sender_hex()
        key = sha_hex(json.dumps([who, package_id, primary_url, secondary_url, claimed_label]))
        if key in self.seen:
            raise Exception("ALREADY_REGISTERED")
        n = int(self.claim_total) + 1
        cid = str(n)
        self.claims[cid] = Claim(
            claim_id=cid,
            attester=who,
            package_id=package_id,
            primary_url=primary_url,
            secondary_url=secondary_url,
            claimed_label=claimed_label,
        )
        self.seen[key] = cid
        self.claim_total = u256(n)

    @gl.public.view
    def get_claim(self, claim_id: str) -> str:
        if claim_id not in self.claims:
            return json.dumps({"exists": False})
        c = self.claims[claim_id]
        return json.dumps({
            "exists": True,
            "claim_id": c.claim_id,
            "attester": c.attester,
            "package_id": c.package_id,
            "primary_url": c.primary_url,
            "secondary_url": c.secondary_url,
            "claimed_label": c.claimed_label,
        }, sort_keys=True)

    @gl.public.view
    def claim_count(self) -> str:
        return str(int(self.claim_total))

    @gl.public.view
    def allowed_labels(self) -> str:
        return json.dumps(ALLOWED_LABELS)

    @gl.public.view
    def preview_sources(self, primary_url: str, secondary_url: str) -> str:
        try:
            check_sources(primary_url, secondary_url)
        except Exception as e:
            return str(e)
        return "OK"
