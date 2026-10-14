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


PHRASE_PRINTS = [
    ("permission is hereby granted, free of charge, to any person obtaining a copy", "MIT"),
    ("permission to use, copy, modify, and/or distribute this software for any purpose with or without fee", "ISC"),
    ("this is free and unencumbered software released into the public domain", "UNLICENSE"),
]
TITLE_PRINTS = [
    ("gnu affero general public license", "version 3", "AGPL-3.0"),
    ("gnu lesser general public license", "version 3", "LGPL-3.0"),
    ("gnu general public license", "version 3", "GPL-3.0"),
    ("gnu general public license", "version 2", "GPL-2.0"),
    ("apache license", "version 2.0", "APACHE-2.0"),
    ("mozilla public license", "2.0", "MPL-2.0"),
]
BSD_START = "redistribution and use in source and binary forms"


def normalize_text(t) -> str:
    return " ".join(str(t).lower().split())


def fingerprint_of_text(norm: str) -> str:
    best_i = -1
    best = ""
    for phrase, label in PHRASE_PRINTS:
        i = norm.find(phrase)
        if i >= 0 and (best_i < 0 or i < best_i):
            best_i = i
            best = label
    for title, ver, label in TITLE_PRINTS:
        start = 0
        while True:
            i = norm.find(title, start)
            if i < 0:
                break
            tail = norm[i + len(title): i + len(title) + 40]
            if ver in tail:
                if best_i < 0 or i < best_i:
                    best_i = i
                    best = label
                break
            start = i + 1
    j = norm.find(BSD_START)
    if j >= 0:
        if "all advertising materials" in norm:
            bsd = "OTHER"
        elif "neither the name" in norm:
            bsd = "BSD-3-CLAUSE"
        else:
            bsd = "BSD-2-CLAUSE"
        if best_i < 0 or j < best_i:
            best_i = j
            best = bsd
    return best


def fetch_norm(url: str) -> str:
    try:
        raw = gl.nondet.web.render(url, mode='text')
    except Exception:
        raise Exception("SOURCE_UNREADABLE")
    norm = normalize_text(raw if raw is not None else "")
    if len(norm) < 60:
        raise Exception("SOURCE_UNREADABLE")
    return norm


@allow_storage
@dataclass
class Snapshot:
    url: str
    content_hash: str
    fingerprint: str
    text_len: u256
    version: u256
    snapshotter: str


class LicenseSnapshotAnchor(gl.Contract):
    snaps: TreeMap[str, Snapshot]
    snap_total: u256

    def __init__(self):
        self.snap_total = u256(0)

    @gl.public.write
    def snapshot(self, url: str):
        check_url(url, "INVALID_URL")

        def leader_fn():
            norm = fetch_norm(url)
            return {"digest": sha_hex(norm), "fp": fingerprint_of_text(norm), "len": len(norm)}

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return leader_failed_ok(leader_fn)
            try:
                mine = leader_fn()
            except Exception:
                return False
            return mine == leader_result.calldata

        res = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        digest = str(res["digest"])
        fp = str(res["fp"])
        n = int(res["len"])
        if len(digest) != 64:
            raise Exception("BAD_DIGEST")
        if fp != "" and fp not in MODEL_LABELS:
            raise Exception("BAD_FINGERPRINT")
        key = sha_hex(url)
        who = sender_hex()
        if key in self.snaps:
            rec = self.snaps[key]
            rec.content_hash = digest
            rec.fingerprint = fp
            rec.text_len = u256(n)
            rec.version = u256(int(rec.version) + 1)
            rec.snapshotter = who
        else:
            self.snaps[key] = Snapshot(
                url=url,
                content_hash=digest,
                fingerprint=fp,
                text_len=u256(n),
                version=u256(1),
                snapshotter=who,
            )
            self.snap_total = u256(int(self.snap_total) + 1)

    @gl.public.view
    def get_snapshot(self, url: str) -> str:
        key = sha_hex(url)
        if key not in self.snaps:
            return json.dumps({"exists": False})
        r = self.snaps[key]
        return json.dumps({
            "exists": True,
            "url": r.url,
            "content_hash": r.content_hash,
            "fingerprint": r.fingerprint,
            "text_len": int(r.text_len),
            "version": int(r.version),
            "snapshotter": r.snapshotter,
        }, sort_keys=True)

    @gl.public.view
    def snapshot_count(self) -> str:
        return str(int(self.snap_total))

    @gl.public.view
    def fingerprint_of(self, text: str) -> str:
        fp = fingerprint_of_text(normalize_text(text))
        if fp == "":
            return "NONE"
        return fp

    @gl.public.view
    def url_key(self, url: str) -> str:
        return sha_hex(url)
