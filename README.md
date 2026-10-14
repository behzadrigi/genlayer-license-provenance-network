# GenLayer License Provenance Network

Five standalone GenLayer Intelligent Contracts (deployed as six, with two AttesterStanding instances) that answer one question with consensus instead of trust: "does this open source package really ship under the license its maintainer says it does?"

No contract in this suite handles funds. Every judgment is made from material the contracts fetch themselves, never from free text typed by the caller.

## Why it matters beyond a demo

License claims are made in package pages, README files and LICENSE files that all live on different hosts and change over time. A single page can be edited, mislabeled or poisoned with hidden instructions aimed at a language model. This suite makes an attester put a claim on record with two independent sources, freezes the exact content of both sources, judges the claim from that frozen content, lets any third party challenge the judgment inside a window, produces an independently validated corrected outcome when a challenge succeeds, and only then updates the attester's standing.

## Architecture

```
 attester                         anyone                    any third party
    |                               |                              |
    v                               v                              v
+-----------------+   url->hash  +--------------------+   +----------------------+
| 1 ClaimRegistry |<-----+       | 2 SnapshotAnchor   |   | 4 VerdictChallenge   |
| deterministic   |      |       | strict equality    |   | non-comparative      |
+--------+--------+      |       +---------+----------+   +----------+-----------+
         | claim (view)  |                 | digest (view)           | review (view)
         v               +-----------------+                         |
+---------------------------------------------------+                |
| 3 CorroboratedLicenseReview  (tolerance band)     |<---------------+
| two sources, digest bound to snapshot, verdict    |
| reviewed_at, challenge deadline                   |
+------------------------+--------------------------+
                         | review (view)      challenge (view)
                         v                           v
                  +--------------------------------------+
                  | 5 AttesterStanding  (deterministic)  |
                  | finalize + safe reputation arithmetic|
                  +--------------------------------------+
```

All cross-contract access is view reads. No contract relies on a cross-contract write.

## Contracts and consensus patterns

| # | Contract | Role | Consensus logic |
|---|----------|------|-----------------|
| 1 | LicenseClaimRegistry | Records who claims which license for which package, with two independent sources | Deterministic |
| 2 | LicenseSnapshotAnchor | Freezes the exact normalized content of a URL as a SHA-256 digest plus a deterministic license fingerprint | Strict equality across validators (digest, fingerprint, length) |
| 3 | CorroboratedLicenseReview | Judges the claim from both sources, bound to the snapshot digests | Custom tolerance band: digests, labels and verdict must match exactly, strength scores must agree within 15 points |
| 4 | LicenseVerdictChallenge | Independent corrected outcome after a challenge, blind to the original verdict and to the challenger | Non-comparative: validators verify the leader's quoted evidence against their own fetch instead of repeating the judgment |
| 5 | AttesterStanding | Finalization and reputation | Deterministic, reads review and challenge by view |

## Lifecycle of one claim

```
REGISTERED -> (snapshots exist) -> REVIEWED
REVIEWED:  challengeable while block time < challengeable_until
           (challengeable_until = reviewed_at + window_seconds)
 no challenge -> finalizable once block time >= challengeable_until   (path UNCHALLENGED)
 challenge raised -> CHALLENGE_PENDING
     finalize is blocked while pending
     resolve_challenge -> RESOLVED  (path UPHELD or OVERTURNED, final verdict = independently judged verdict)
     expire_challenge  -> EXPIRED   (only after resolution_deadline, the original verdict stands)
 RESOLVED or EXPIRED -> finalizable (the only place reputation changes)
FINALIZED: result is final, one time, never reopened
```

The view `AttesterStanding.lifecycle(claim_id)` returns the stage, `challengeable_until` and `resolution_deadline` as block-time numbers, so a client can see exactly when a claim is challengeable and when its result becomes final.

## Reputation arithmetic

Score is a plain integer 0 to 100. CONFIRMED adds 10 (capped at 100), REFUTED removes 20 (floored at 0, no subtraction below zero is ever evaluated), INCONCLUSIVE changes nothing. Tiers are plain comparisons: TRUSTED at 70 or more, STANDARD at 30 or more, otherwise PROBATION. The views `preview_score(score, verdict)` and `preview_tier(score)` expose the pure functions so values such as 0, 5, 9, 10, 19 and 20 can be checked on chain without building state.

## Deployed addresses

Both networks were tested on 2026-10-14. Full transaction hashes and explorer links are in TEST.md.

| Contract | Studio | Bradbury |
|----------|--------|----------|
| LicenseClaimRegistry | [0xEc5BeE731B34ca02A11277c7dc7A8c0Ae7899fC9](https://explorer-studio.genlayer.com/address/0xEc5BeE731B34ca02A11277c7dc7A8c0Ae7899fC9) | [0xaE75774b00FD50265245088C0Eb76f2988c403aB](https://explorer-bradbury.genlayer.com/address/0xaE75774b00FD50265245088C0Eb76f2988c403aB) |
| LicenseSnapshotAnchor | [0x47c6370a442cf482F4c9Ade9EBA43F3345558983](https://explorer-studio.genlayer.com/address/0x47c6370a442cf482F4c9Ade9EBA43F3345558983) | [0xc16Ad93930b58022303419e934dF5b98ba1035BC](https://explorer-bradbury.genlayer.com/address/0xc16Ad93930b58022303419e934dF5b98ba1035BC) |
| CorroboratedLicenseReview | [0x9Eff22583259E70DfBE819f69Cf68ddc6458EC1A](https://explorer-studio.genlayer.com/address/0x9Eff22583259E70DfBE819f69Cf68ddc6458EC1A) | [0x8a7Fc2b6F7BF1F44F6d72778e2878AdDE2c50e1D](https://explorer-bradbury.genlayer.com/address/0x8a7Fc2b6F7BF1F44F6d72778e2878AdDE2c50e1D) |
| LicenseVerdictChallenge | [0x5DF48dd48abA1FF6445c3539E8627a86dcee2594](https://explorer-studio.genlayer.com/address/0x5DF48dd48abA1FF6445c3539E8627a86dcee2594) | [0x8BdF0D7197722360B36af7e29aEC89F3aa5E9F97](https://explorer-bradbury.genlayer.com/address/0x8BdF0D7197722360B36af7e29aEC89F3aa5E9F97) |
| AttesterStanding (start_score 50) | [0xBB9cd4d6672BD427F477309733c77697376409cf](https://explorer-studio.genlayer.com/address/0xBB9cd4d6672BD427F477309733c77697376409cf) | [0x50B1D98b5c7012661A5B717eF9535bfBeA7F1658](https://explorer-bradbury.genlayer.com/address/0x50B1D98b5c7012661A5B717eF9535bfBeA7F1658) |
| AttesterStanding low instance (start_score 5) | [0xFDd2Ef0F761734A372434D6D4a0715da13fe7FeE](https://explorer-studio.genlayer.com/address/0xFDd2Ef0F761734A372434D6D4a0715da13fe7FeE) | [0x5831eB3E80fb3FB7e2284aF36eF3437B8b3CAE79](https://explorer-bradbury.genlayer.com/address/0x5831eB3E80fb3FB7e2284aF36eF3437B8b3CAE79) |

## Test results at a glance

- Studio: every recorded row passed (registry guards, snapshots, reviews with CONFIRMED, REFUTED and INCONCLUSIVE verdicts, challenge raise, resolve and expire, finalization paths, reputation arithmetic, tier thresholds, lifecycle views).
- Bradbury: block time probe, claim registration, two snapshots, a CONFIRMED review with digests identical to Studio, and the preview_score checks.
- Not run on chain: the challenge and finalization path on Bradbury (the 300 second window closed before the transaction landed), a source changed review revert, finalizing inside the window, and an OVERTURNED outcome. These are listed honestly in TEST.md section F.

## Quick start

Deploy in this order. Constructor arguments are strings for addresses and integers for seconds and score.

1. `LicenseClaimRegistry()`
2. `LicenseSnapshotAnchor()`
3. `CorroboratedLicenseReview(registry_addr, snapshot_addr, window_seconds)` use 300 on Studio. On Bradbury transactions take minutes, so use at least 3600. Use a larger value such as 86400 for real use
4. `LicenseVerdictChallenge(review_addr, resolution_seconds)` use 300 for testing on Studio
5. `AttesterStanding(review_addr, challenge_addr, start_score)` use 50, and optionally a second instance with 5 to prove the below 10 behavior

Then: `time_probe()` on the review contract first (proves block time works), `register_claim`, `snapshot` for both URLs, `review_claim`, optionally `raise_challenge` and `resolve_challenge`, and finally `finalize`. The executed test cases are in tests/ and the full report is in TEST.md.

## Source integrity

The files in contracts/ are the exact files deployed. SHA-256 checksums:

```
8c170532a8c5ebcc4ed9c41c62c61b067f279e345472b5509c5373fa43baeb94  license_claim_registry.py
c0e82f1dec01cbfe52d52df0311c09e69daa758ec14528a58c6cc7933e99f883  license_snapshot_anchor.py
4155890767dd1599f091fb3605fc41320ae737296895860c83abe11acf283efe  corroborated_license_review.py
8c18854e13ac869ec2d9a67da5569531165d20b7b1a29da93269dbaac5986370  license_verdict_challenge.py
0e089afb1c9c90c4a0f50e922f90f052ebb068641b1ec585e54c76fc684c0560  attester_standing.py
```

Verify with `sha256sum contracts/*.py`.

## Limits

- The suite judges what a fetched page says, not whether the maintainer has the legal right to use it.
- Pages that change on every load (counters, timestamps, ads) produce unstable digests and fail closed with SOURCE_UNREADABLE or SOURCE_CHANGED_SINCE_SNAPSHOT. Use static pages such as raw LICENSE files.
- The independence check on two sources compares the last two labels of the host names. It is a practical guard, not a proof of independent ownership.
- Eleven license labels are recognized plus OTHER and UNCLEAR. Dual licensed texts are treated as UNCLEAR and never produce a penalty.
- A challenge cannot overturn a result when the source changed after the review. The original verdict stands.
- Anyone may call review, resolve, expire and finalize. Timing is block time of the transaction.
