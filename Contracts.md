# Contracts

Common rules for all files: first line is the py-genlayer dependency comment, pure ASCII, no undecorated instance methods, helpers at module level, views return strings, constructor addresses are strings, cross-contract calls are view reads only.

Shared definitions: labels MIT, APACHE-2.0, BSD-2-CLAUSE, BSD-3-CLAUSE, ISC, MPL-2.0, GPL-2.0, GPL-3.0, LGPL-3.0, AGPL-3.0, UNLICENSE (claimable), plus OTHER and UNCLEAR (model outputs only). Verdicts: CONFIRMED, REFUTED, INCONCLUSIVE.

Fetched text is normalized (lowercase, whitespace collapsed) before hashing. Digest means SHA-256 of that normalized text. Query strings in URLs are never stripped.

## 1. LicenseClaimRegistry (deterministic)

Storage: `claims` (claim_id to Claim: attester, package_id, primary_url, secondary_url, claimed_label), `seen` (dedupe key to claim_id), `claim_total`.

Methods:
- `register_claim(package_id, primary_url, secondary_url, claimed_label)` write
- `get_claim(claim_id)`, `claim_count()`, `allowed_labels()`, `preview_sources(primary_url, secondary_url)` views

Guards and exact errors: `INVALID_PACKAGE_ID` (1 to 80 printable ASCII characters, no spaces), `INVALID_PRIMARY_URL` and `INVALID_SECONDARY_URL` (https only, ASCII, no whitespace, no user info, 300 characters max), `SOURCES_NOT_INDEPENDENT` (identical URLs or same base domain), `INVALID_LABEL`, `ALREADY_REGISTERED` (same sender, package, both URLs and label).

Safety properties: the attester is always the transaction sender. The URLs are stored exactly as given, so two URLs that differ only by query string are different resources. State only grows; no record is edited or deleted.

On chain evidence: R1 to R7 (Studio), R1 (Bradbury).

## 2. LicenseSnapshotAnchor (strict equality)

Storage: `snaps` (sha256 of exact URL to Snapshot: url, content_hash, fingerprint, text_len, version, snapshotter), `snap_total`.

Methods: `snapshot(url)` write; `get_snapshot(url)`, `snapshot_count()`, `fingerprint_of(text)`, `url_key(url)` views.

Consensus: the leader fetches the page with `gl.nondet.web.render(url, mode='text')`, and returns digest, fingerprint and length. A validator fetches again and requires the whole result to be equal. If the leader fails, a validator accepts only if its own fetch fails too.

Guards: `INVALID_URL`, `SOURCE_UNREADABLE` (fetch failed or fewer than 60 characters, fail closed), `BAD_DIGEST`, `BAD_FINGERPRINT`.

Fingerprint: a deterministic detector over the text. It finds the earliest license marker (full title plus version for the Apache, MPL, GPL, LGPL and AGPL families, characteristic grant sentences for MIT, ISC and the Unlicense, and the BSD conditions text). It returns a label, OTHER for the advertising clause variant, or an empty string.

Safety properties: re-snapshotting a URL raises its version and replaces the digest, which can never alter an existing review because reviews store their own digests. Unreadable pages never create a record.

On chain evidence: S1 to S6 (Studio), S1 (Bradbury). The same digests were produced on both networks.

## 3. CorroboratedLicenseReview (custom tolerance band)

Constructor: `(registry_addr, snapshot_addr, window_seconds)`. Error `INVALID_WINDOW` unless 1 to 31536000.

Storage: `reviews` (claim_id to Review: reviewer, attester, claimed_label, both URLs, digest_a, digest_b, label_a, label_b, strength_a, strength_b, verdict, reviewed_at, deadline), `window_seconds`, counters, `last_probe`.

Methods: `time_probe()` and `review_claim(claim_id)` write; `get_review`, `review_count`, `get_last_probe`, `get_config` views.

Flow of `review_claim`: read the claim from the registry, read both snapshots, then inside the nondeterministic block fetch both sources, compute digests and require them to equal the snapshot digests, then classify each source with the model. The prompt wraps the text in BEGIN_DATA and END_DATA and states it is data. The model never sees the claimed license. A label that disagrees with the deterministic fingerprint becomes UNCLEAR. Verdict rule: strength of both sources at least 50 is required for any decisive verdict; CONFIRMED needs both labels equal to the claim; REFUTED needs both sources to agree with each other on a different known license; everything else is INCONCLUSIVE.

Consensus: validators repeat the work and require equal digests, labels and verdict, and strength scores within 15 points for each source.

Guards: `ALREADY_REVIEWED`, `CLAIM_NOT_FOUND`, `SNAPSHOT_REQUIRED_PRIMARY`, `SNAPSHOT_REQUIRED_SECONDARY`, `SOURCE_UNREADABLE`, `SOURCE_CHANGED_SINCE_SNAPSHOT`, `BAD_VERDICT`, `BAD_LABEL`, `BAD_STRENGTH`, `BINDING_MISMATCH`, `TIME_UNAVAILABLE`.

Safety properties: an unreadable or changed source reverts and stores nothing, so it can never penalize anyone. REFUTED requires two sources that agree. The record carries `deadline = reviewed_at + window_seconds`, which is the single source of truth for the challenge window.

On chain evidence: V0 to V6 and V8 (Studio), V0 and V2 (Bradbury). The source changed revert (V7) was not run on chain.

## 4. LicenseVerdictChallenge (non-comparative)

Constructor: `(review_addr, resolution_seconds)`. Error `INVALID_RESOLUTION_WINDOW`.

Storage: `challenges` (claim_id to ChallengeRec: challenger, original_verdict, status PENDING or RESOLVED or EXPIRED, raised_at, resolution_deadline, resolved_at, corrected_verdict, final_verdict, outcome UPHELD or OVERTURNED, reason, label_a, label_b).

Methods: `time_probe()`, `raise_challenge(claim_id)`, `resolve_challenge(claim_id)`, `expire_challenge(claim_id)` write; `get_challenge`, `challenge_status`, `challenge_count`, `get_last_probe`, `get_config` views.

`raise_challenge` guards: `ALREADY_CHALLENGED`, `REVIEW_NOT_FOUND`, `ATTESTER_CANNOT_CHALLENGE`, `CHALLENGE_WINDOW_CLOSED` (block time at or after the review deadline). A challenge carries no free text.

`resolve_challenge` is the independent judge. It reads only the two URLs, the two review digests, and the claimed label. Inside the nondeterministic block it fetches both sources, requires equal digests, and asks the model for a label and a short verbatim quote for each source. The prompt contains only the document text. It never contains the original verdict, the claim, or anything from the challenger. After consensus the contract derives the corrected verdict in code from the two labels and compares it with the original verdict. Same verdict means UPHELD, different means OVERTURNED. The corrected verdict, in either direction, becomes the final verdict, so an overturn can help or hurt the attester depending on which way the first review was wrong. If the source changed since the review the original verdict stands with reason `SOURCE_CHANGED_ORIGINAL_STANDS`.

Consensus: validators do not repeat the judgment. They fetch the sources themselves and verify the leader's output: equal digests, the quote occurs in their own copy of the text, the label agrees with the deterministic fingerprint when one exists, or contains a keyword of the label when none exists. A leader abstention (UNCLEAR or OTHER) is accepted only if the validator's own independent classification also abstains.

`expire_challenge` guards: `NOT_PENDING`, `RESOLUTION_WINDOW_OPEN`. After the resolution deadline anyone may expire a pending challenge, the original verdict stands.

Other guards: `CHALLENGE_NOT_FOUND`, `NOT_PENDING`, `SOURCE_UNREADABLE` (reverts, challenge stays PENDING and can be retried), `BAD_LABEL`, `BAD_VERDICT`.

Safety properties: every PENDING challenge has two exits (resolve, or expire after the deadline). An infrastructure failure never changes status. The attester cannot edit a page after a REFUTED review to escape, because a changed source leaves the original verdict standing.

On chain evidence: C1 to C10 (Studio). The Bradbury run of the challenge path was not recorded. An OVERTURNED outcome was not observed on chain.

## 5. AttesterStanding (deterministic)

Constructor: `(review_addr, challenge_addr, start_score)`. Error `INVALID_START_SCORE` unless 0 to 100.

Storage: `finals` (claim_id to FinalRec: attester, final_verdict, path, score_before, score_after, finalized_at), `scores` (attester to score, lazy default is start_score), counters.

Methods: `time_probe()`, `finalize(claim_id)` write; `get_final`, `standing`, `lifecycle`, `preview_score`, `preview_tier`, `final_count`, `get_last_probe`, `get_config` views.

`finalize` rules in order: `ALREADY_FINALIZED`, `REVIEW_NOT_FOUND`. If a challenge exists: `CHALLENGE_REVIEW_MISMATCH` when its original verdict differs from the review, `CHALLENGE_UNRESOLVED` while PENDING, final verdict taken from the resolved challenge (path UPHELD or OVERTURNED) or the expired challenge (path EXPIRED), else `CHALLENGE_STATE_INVALID`. If no challenge exists: `CHALLENGE_WINDOW_OPEN` until block time reaches the review deadline, then path UNCHALLENGED. `FINAL_VERDICT_INVALID` guards the verdict value.

Safety properties: finalization cannot happen inside the challenge window, cannot happen while a challenge is unresolved, and happens once per claim. A challenge cannot be raised once the window has closed, so a late challenge cannot appear after finalization. Reputation changes only here.

On chain evidence: T1 to T10 (Studio), T6 (Bradbury).
