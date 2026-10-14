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


REWARD = 10
PENALTY = 20
SCORE_MAX = 100
TRUSTED_MIN = 70
STANDARD_MIN = 30


def apply_verdict(score: int, verdict: str) -> int:
    s = int(score)
    if verdict == "CONFIRMED":
        t = s + REWARD
        if t > SCORE_MAX:
            return SCORE_MAX
        return t
    if verdict == "REFUTED":
        if s <= PENALTY:
            return 0
        return s - PENALTY
    return s


def tier_of(score: int) -> str:
    s = int(score)
    if s >= TRUSTED_MIN:
        return "TRUSTED"
    if s >= STANDARD_MIN:
        return "STANDARD"
    return "PROBATION"


def points_to_trusted(score: int) -> int:
    s = int(score)
    if s >= TRUSTED_MIN:
        return 0
    return TRUSTED_MIN - s


@allow_storage
@dataclass
class FinalRec:
    claim_id: str
    attester: str
    final_verdict: str
    path: str
    score_before: u256
    score_after: u256
    finalized_at: u256


class AttesterStanding(gl.Contract):
    finals: TreeMap[str, FinalRec]
    scores: TreeMap[str, u256]
    review_addr: str
    challenge_addr: str
    start_score: u256
    final_total: u256
    last_probe: u256

    def __init__(self, review_addr: str, challenge_addr: str, start_score: int):
        if start_score < 0 or start_score > SCORE_MAX:
            raise Exception("INVALID_START_SCORE")
        self.review_addr = review_addr.strip()
        self.challenge_addr = challenge_addr.strip()
        self.start_score = u256(start_score)
        self.final_total = u256(0)
        self.last_probe = u256(0)

    @gl.public.write
    def time_probe(self):
        self.last_probe = u256(now_seconds())

    @gl.public.write
    def finalize(self, claim_id: str):
        if claim_id in self.finals:
            raise Exception("ALREADY_FINALIZED")
        rv = parse_obj(gl.get_contract_at(Address(self.review_addr)).view().get_review(claim_id))
        if rv.get("exists") is not True:
            raise Exception("REVIEW_NOT_FOUND")
        ch = parse_obj(gl.get_contract_at(Address(self.challenge_addr)).view().get_challenge(claim_id))
        now = now_seconds()
        original = str(rv["verdict"])
        if ch.get("exists") is True:
            if str(ch["original_verdict"]) != original:
                raise Exception("CHALLENGE_REVIEW_MISMATCH")
            st = str(ch["status"])
            if st == "PENDING":
                raise Exception("CHALLENGE_UNRESOLVED")
            if st == "RESOLVED":
                path = str(ch["outcome"])
                final = str(ch["final_verdict"])
            elif st == "EXPIRED":
                path = "EXPIRED"
                final = str(ch["final_verdict"])
            else:
                raise Exception("CHALLENGE_STATE_INVALID")
        else:
            if now < int(rv["deadline"]):
                raise Exception("CHALLENGE_WINDOW_OPEN")
            path = "UNCHALLENGED"
            final = original
        if final not in VERDICTS:
            raise Exception("FINAL_VERDICT_INVALID")
        attester = str(rv["attester"]).lower()
        if attester in self.scores:
            before = int(self.scores[attester])
        else:
            before = int(self.start_score)
        after = apply_verdict(before, final)
        self.scores[attester] = u256(after)
        self.finals[claim_id] = FinalRec(
            claim_id=claim_id,
            attester=attester,
            final_verdict=final,
            path=path,
            score_before=u256(before),
            score_after=u256(after),
            finalized_at=u256(now),
        )
        self.final_total = u256(int(self.final_total) + 1)

    @gl.public.view
    def get_final(self, claim_id: str) -> str:
        if claim_id not in self.finals:
            return json.dumps({"exists": False})
        f = self.finals[claim_id]
        return json.dumps({
            "exists": True,
            "claim_id": f.claim_id,
            "attester": f.attester,
            "final_verdict": f.final_verdict,
            "path": f.path,
            "score_before": int(f.score_before),
            "score_after": int(f.score_after),
            "finalized_at": int(f.finalized_at),
        }, sort_keys=True)

    @gl.public.view
    def standing(self, attester: str) -> str:
        a = attester.strip().lower()
        if a in self.scores:
            s = int(self.scores[a])
        else:
            s = int(self.start_score)
        return json.dumps({
            "attester": a,
            "score": s,
            "tier": tier_of(s),
            "points_to_trusted": points_to_trusted(s),
        }, sort_keys=True)

    @gl.public.view
    def lifecycle(self, claim_id: str) -> str:
        if claim_id in self.finals:
            f = self.finals[claim_id]
            return json.dumps({
                "claim_id": claim_id,
                "stage": "FINALIZED",
                "result_final": True,
                "final_verdict": f.final_verdict,
                "path": f.path,
            }, sort_keys=True)
        rv = parse_obj(gl.get_contract_at(Address(self.review_addr)).view().get_review(claim_id))
        if rv.get("exists") is not True:
            return json.dumps({"claim_id": claim_id, "stage": "NOT_REVIEWED", "result_final": False}, sort_keys=True)
        ch = parse_obj(gl.get_contract_at(Address(self.challenge_addr)).view().get_challenge(claim_id))
        out = {
            "claim_id": claim_id,
            "original_verdict": str(rv["verdict"]),
            "challengeable_until": int(rv["deadline"]),
            "result_final": False,
        }
        if ch.get("exists") is not True:
            out["stage"] = "REVIEWED"
            out["rule"] = "challengeable while block time < challengeable_until; finalizable without challenge once block time >= challengeable_until"
        else:
            st = str(ch["status"])
            out["challenge_status"] = st
            out["resolution_deadline"] = int(ch["resolution_deadline"])
            if st == "PENDING":
                out["stage"] = "CHALLENGE_PENDING"
                out["rule"] = "finalize is blocked until the challenge is resolved, or expired after resolution_deadline"
            elif st == "RESOLVED":
                out["stage"] = "CHALLENGE_RESOLVED"
                out["final_verdict"] = str(ch["final_verdict"])
                out["rule"] = "ready to finalize with the independently judged verdict"
            else:
                out["stage"] = "CHALLENGE_EXPIRED"
                out["final_verdict"] = str(ch["final_verdict"])
                out["rule"] = "ready to finalize, the original verdict stands"
        return json.dumps(out, sort_keys=True)

    @gl.public.view
    def preview_score(self, score: int, verdict: str) -> str:
        return str(apply_verdict(score, verdict))

    @gl.public.view
    def preview_tier(self, score: int) -> str:
        return tier_of(score)

    @gl.public.view
    def final_count(self) -> str:
        return str(int(self.final_total))

    @gl.public.view
    def get_last_probe(self) -> str:
        return str(int(self.last_probe))

    @gl.public.view
    def get_config(self) -> str:
        return json.dumps({"review": self.review_addr, "challenge": self.challenge_addr, "start_score": int(self.start_score)}, sort_keys=True)
