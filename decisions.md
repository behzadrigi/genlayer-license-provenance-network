# Design decisions

Each entry gives the decision, the reason and the cost.

1. No funds anywhere.
   Reason: removes the whole class of stuck money findings. Cost: no economic stake behind a claim, the only consequence is reputation.

2. The contracts fetch the evidence themselves.
   Reason: a language model never judges a statement typed by the caller. Both the snapshot and the review use `gl.nondet.web.render`. Cost: pages must be fetchable and static.

3. Two independent sources per claim.
   Reason: a single caller-chosen URL is easy to control. The registry rejects identical URLs and sources that share a base domain, and REFUTED needs both sources to agree on another license. Cost: the base domain check is approximate and a claim needs two public pages.

4. Fetched text is treated as untrusted data.
   Reason: the prompts wrap the text in BEGIN_DATA and END_DATA and say it is data. A deterministic fingerprint is an extra guard: when the text contains a recognizable license marker and the model disagrees, the label becomes UNCLEAR. Disagreement is treated as uncertainty, never as evidence against the attester. Cost: unusual layouts end up INCONCLUSIVE.

5. A snapshot contract freezes content, the review binds to it.
   Reason: the check and the later judgment are separate steps, so they are bound by a SHA-256 digest. The review recomputes the digest inside the leader and inside each validator and refuses to judge when it differs (`SOURCE_CHANGED_SINCE_SNAPSHOT`). The digest of each source is stored in the review. Cost: one extra transaction per source before a review.

6. Four different consensus patterns.
   Reason: deterministic registry, strict equality for the snapshot, a tolerance band for the review, non-comparative verification for the challenge judge. Each fits its job: the snapshot has no judgment so it must match exactly, the review score is fuzzy so a band is right, the judge output is checkable evidence so verifying it is cheaper and harder to game than repeating it. Cost: more validator code to reason about.

7. Every number or bucket that changes an outcome is compared by validators.
   Reason: in the review the verdict, both labels and both digests must be equal, and the two strength scores must agree within 15 points. The strength threshold of 50 influences the verdict, and since the verdict is compared exactly, a disagreement near the threshold fails consensus instead of slipping through. Cost: a rare retry when a score sits at the boundary. In the challenge judge the labels are verified one by one and the final verdict is derived by code from them.

8. Infrastructure failures revert.
   Reason: unreadable or changed sources raise an error before any state is written, so the transaction can be retried and nobody gets a permanent bad record. Cost: a permanently dead source leaves a claim unreviewed, the attester can register a new claim with other sources.

9. Review and challenge share one clock rule.
   Reason: the review stores `deadline = reviewed_at + window_seconds`. A challenge needs block time before the deadline, an unchallenged finalization needs block time at or after it. The two ranges never overlap, so finalization can never skip a challenge and a challenge can never arrive after finalization. Cost: depends on block time, which is proven by `time_probe` as the first test.

10. A pending challenge blocks finalization and always has an exit.
    Reason: `finalize` reverts with `CHALLENGE_UNRESOLVED` while the status is PENDING. The exits are `resolve_challenge` (open to anyone) and `expire_challenge` (open to anyone after the resolution deadline). Cost: an expired challenge keeps the original verdict.

11. An overturn is an independently validated correction, never a fixed penalty.
    Reason: the judge sees only the documents, never the original verdict, the claim or the challenger. The corrected verdict is computed by code from the judged labels and replaces the original in either direction: REFUTED to CONFIRMED, CONFIRMED to REFUTED, or either to INCONCLUSIVE. The attester is rewarded or penalized by the corrected verdict, and the challenger is never scored. Cost: the judge uses the same two sources as the review, so it corrects model error, not a wrong choice of sources.

12. If the sources changed after the review, the original verdict stands.
    Reason: otherwise an attester could edit a page after a REFUTED review and have the challenge cancel the penalty, or a colluding challenger could void a correct result. Cost: a genuinely wrong review cannot be fixed after the page changed.

13. The attester cannot challenge their own claim.
    Reason: stops a self-overturn after editing a page. Cost: none, a second wallet could still do it, which is why decision 12 exists.

14. Reputation uses plain integers and no unsigned subtraction.
    Reason: the penalty branch compares `score <= 20` and returns 0, otherwise subtracts, so the result is never negative. Tier checks are direct comparisons. Cost: none. `preview_score` and `preview_tier` expose the same functions so below-margin values can be proven on chain.

15. Reputation is applied only at finalization and only once per claim.
    Reason: one place to audit, no double counting. The record keeps score before and after and the path (UNCHALLENGED, UPHELD, OVERTURNED, EXPIRED).

16. Query strings are never stripped and exact URLs are the keys.
    Reason: distinct resources must not share a record.

17. The challenge carries no free text.
    Reason: there is no argument to leak into the judgment.

18. Time parsing is self-contained.
    Reason: the block time string is parsed with integer arithmetic only (no extra imports), with the `gl.message_raw["datetime"]` fallback and `TIME_UNAVAILABLE` on failure.

19. One `from dataclasses import dataclass` line is added after the genlayer import.
    Reason: makes the dataclass name explicit and independent of what the star import exports. It is a plain import line directly under the dependency header.

20. The test windows are 300 seconds.
    Reason: short windows let the whole lifecycle be exercised in one sitting on Studio. Cost: on Bradbury, where transactions take minutes, the window closed before the challenge transaction landed, so the challenge path was only run on Studio. A real deployment should use hours or days, and a Bradbury re-run should use at least 3600 seconds.

21. Two deployments of AttesterStanding.
    Reason: the start_score is a constructor argument, so a second instance with start_score 5 proves the below 10 behavior without long setup. Cost: one extra deployment per network.

## Known limitations

- Not a legal opinion about licenses.
- Dynamic pages fail closed.
- The base domain independence check is approximate.
- The judge shares sources with the review, so it corrects judgment errors, not source selection.
- A challenge on a claim whose source changed cannot overturn anything.
- Because the original verdict stands on expiry, a challenger who wants a correction must resolve before the resolution deadline.
- A leader that abstains is checked against validators' own abstention, so a borderline page may need a retry.
- Block time was proven on both networks by the time_probe test (V0). The first test in TEST.md proves block time. If block time is not available in a runtime, review, challenge and finalize revert with `TIME_UNAVAILABLE` and nothing is stored.
- No OVERTURNED outcome has been observed on chain, because it needs a wrong first review. The correction logic in all three directions is covered by the local mock run described in TEST.md.
- The challenge, resolve and finalize path was not recorded on Bradbury, see decision 20.
- Finalizing inside the challenge window (CHALLENGE_WINDOW_OPEN) and the source changed revert (SOURCE_CHANGED_SINCE_SNAPSHOT) were not observed on chain.
- Two different pages can have identical normalized text. The Kafka LICENSE file and the apache.org license text produced the same digest. This is expected and does not break the independence rule, which checks hosts.
