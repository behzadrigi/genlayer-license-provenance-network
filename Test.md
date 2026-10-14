# Test report

Date of the on-chain runs: 2026-10-14. Networks: GenLayer Studio (Studionet) and Bradbury. Accounts: ACC1 0x6E74BCbC7153892E8602E72182e64D525A0e3Ac7 (attester, deployer, reviewer) and ACC2 0xaB46b4ae332818735fcc1b6C3E37Ec0b33D92757 (challenger).

The suite has 5 contract files. They were deployed as 6 contracts on each network because AttesterStanding was deployed twice, once with start_score 50 and once with start_score 5 (the low instance used for the below 10 tests).

Status legend: RUN means executed and the result below was observed. DEFINED means not executed on chain. Nothing is marked RUN without a recorded result.

## A. Deployments

### Studio

| Contract | Address | Deploy transaction | Constructor |
|----------|---------|--------------------|-------------|
| LicenseClaimRegistry | https://explorer-studio.genlayer.com/address/0xEc5BeE731B34ca02A11277c7dc7A8c0Ae7899fC9 | https://explorer-studio.genlayer.com/tx/0xe36ea99f1b2ebaf8dfa5d4d3e328330600c8d439a3b80abd692a38c634d385f7 | no arguments |
| LicenseSnapshotAnchor | https://explorer-studio.genlayer.com/address/0x47c6370a442cf482F4c9Ade9EBA43F3345558983 | https://explorer-studio.genlayer.com/tx/0xc40893374d54ac0359ddd43a975539b9742edef9f8676d2396beebd1fa65f2f3 | no arguments |
| CorroboratedLicenseReview | https://explorer-studio.genlayer.com/address/0x9Eff22583259E70DfBE819f69Cf68ddc6458EC1A | https://explorer-studio.genlayer.com/tx/0x95830041d85468a29464bde79ea4407c26675a807f67702bc85b634936ad0993 | registry, snapshot, window_seconds=300 |
| LicenseVerdictChallenge | https://explorer-studio.genlayer.com/address/0x5DF48dd48abA1FF6445c3539E8627a86dcee2594 | https://explorer-studio.genlayer.com/tx/0xfc63397d7a7f037751a6e00f2e95150b901b8d2e0e7f2107c065fb45fccd95c5 | review, resolution_seconds=300 |
| AttesterStanding (start_score 50) | https://explorer-studio.genlayer.com/address/0xBB9cd4d6672BD427F477309733c77697376409cf | https://explorer-studio.genlayer.com/tx/0x47ce6a3b7eeac2441c8c2ce69957db74aefbad5efb73c2a68cdd50ff0f7279a6 | review, challenge, start_score=50 |
| AttesterStanding low instance (start_score 5) | https://explorer-studio.genlayer.com/address/0xFDd2Ef0F761734A372434D6D4a0715da13fe7FeE | https://explorer-studio.genlayer.com/tx/0xe2eec59df6e1581a173b0a2092dbf5b71f14e7df7076dec0e2f0f7b63cd31907 | review, challenge, start_score=5 |

### Bradbury

Constructor arguments were not recorded in the report except the 300 second window used on the review contract and the two start scores (50 and 5).

| Contract | Address | Deploy transaction |
|----------|---------|--------------------|
| LicenseClaimRegistry | https://explorer-bradbury.genlayer.com/address/0xaE75774b00FD50265245088C0Eb76f2988c403aB | https://explorer-bradbury.genlayer.com/tx/0x1b039cd5506fbfbaf60d73fbf9e1333358dcb00c7ad21faef38e141149049282 |
| LicenseSnapshotAnchor | https://explorer-bradbury.genlayer.com/address/0xc16Ad93930b58022303419e934dF5b98ba1035BC | https://explorer-bradbury.genlayer.com/tx/0x57618c3709066e206236d392f6b74ee0493b910bf4c51ebc705d9e232f7f093b |
| CorroboratedLicenseReview | https://explorer-bradbury.genlayer.com/address/0x8a7Fc2b6F7BF1F44F6d72778e2878AdDE2c50e1D | https://explorer-bradbury.genlayer.com/tx/0x8c01a05a1af10f6a374347602119cc5d65e2e009ce10a6f2424dcfa03fa5f067 |
| LicenseVerdictChallenge | https://explorer-bradbury.genlayer.com/address/0x8BdF0D7197722360B36af7e29aEC89F3aa5E9F97 | https://explorer-bradbury.genlayer.com/tx/0x67655a62543b4a04f973199b13edba19651b27267c185ff2bb78898edce28fd7 |
| AttesterStanding (start_score 50) | https://explorer-bradbury.genlayer.com/address/0x50B1D98b5c7012661A5B717eF9535bfBeA7F1658 | https://explorer-bradbury.genlayer.com/tx/0xca4619eaf60166438a520e6a1f9c900e951066205c41e7b6738fc33f6d98f4fe |
| AttesterStanding low instance (start_score 5) | https://explorer-bradbury.genlayer.com/address/0x5831eB3E80fb3FB7e2284aF36eF3437B8b3CAE79 | https://explorer-bradbury.genlayer.com/tx/0xe404cb410eb801d7f5b6f7b8c4b16c34b725d82fe5552c2bde039160b440b323 |

## B. Content digests (identical on both networks)

```
MIT_A     437ce751072e0d872ca8842e43924224de50236745602b3d209e3825a397d0f6
MIT_B     4d6fd97e6eeb579a12ec32c8ae3b11cb7487d1ae218d14a81bfe5b931800dc14
APACHE_A  948703bcf1cb4a2dafd21676dd01e40a58fe21bd9b425c000b9070eccb441092
APACHE_B  948703bcf1cb4a2dafd21676dd01e40a58fe21bd9b425c000b9070eccb441092
```

APACHE_A and APACHE_B returned the same digest, which means the normalized text of the Kafka LICENSE file and the apache.org license text is identical. The registry accepts them as two sources because their hosts differ. The review digests for MIT_A and MIT_B on Bradbury match Studio.

## C. Studio results

| ID | Contract | Result | Status | Transaction |
|----|----------|--------|--------|-------------|
| V0 | CorroboratedLicenseReview | get_last_probe returned 1791983181 | RUN | 0x986d44142b7599178a500ecfe62e8380680bc0af71ef6cb2a8624b4864d10b6d (https://explorer-studio.genlayer.com/tx/0x986d44142b7599178a500ecfe62e8380680bc0af71ef6cb2a8624b4864d10b6d) |
| R1 | LicenseClaimRegistry | claim_count returned 1 | RUN | 0x0628466064fac7f1b824227ecbfb72d9c4cf1d35c42ff35120588776556fe4a8 (https://explorer-studio.genlayer.com/tx/0x0628466064fac7f1b824227ecbfb72d9c4cf1d35c42ff35120588776556fe4a8) |
| R2 | LicenseClaimRegistry | Reverted with ALREADY_REGISTERED | RUN | 0xd5a273337602920b9a5cbef8180d01289b4321c422ca7ae630abbd58c224cffb (https://explorer-studio.genlayer.com/tx/0xd5a273337602920b9a5cbef8180d01289b4321c422ca7ae630abbd58c224cffb) |
| R3 | LicenseClaimRegistry | Reverted with SOURCES_NOT_INDEPENDENT | RUN | 0x14149b6949cafc59609e57bc95d024120ab475e79ca39d973bf503e8ec3cd1c2 (https://explorer-studio.genlayer.com/tx/0x14149b6949cafc59609e57bc95d024120ab475e79ca39d973bf503e8ec3cd1c2) |
| R4 | LicenseClaimRegistry | Reverted with INVALID_LABEL | RUN | 0x1aad75680c5f87c0ecb88e83c29323b22235deb8681a9a55deb59448aeec1c60 (https://explorer-studio.genlayer.com/tx/0x1aad75680c5f87c0ecb88e83c29323b22235deb8681a9a55deb59448aeec1c60) |
| R5 | LicenseClaimRegistry | Reverted with INVALID_PRIMARY_URL | RUN | 0xe2dadaa2990a5b3f7ba113c4bfa1b1c82522d82a076cad2e96b05d0582f78ea4 (https://explorer-studio.genlayer.com/tx/0xe2dadaa2990a5b3f7ba113c4bfa1b1c82522d82a076cad2e96b05d0582f78ea4) |
| R6 | LicenseClaimRegistry | Returned SOURCES_NOT_INDEPENDENT, then OK | RUN | read only, no transaction |
| R7 | LicenseClaimRegistry | claim_count returned 4 | RUN | claim 2 0xafb53133af91e6cd90d704070bad6cd4fe3f605c39a3b2c22c66b14f39a4b6e2 (https://explorer-studio.genlayer.com/tx/0xafb53133af91e6cd90d704070bad6cd4fe3f605c39a3b2c22c66b14f39a4b6e2); claim 3 0xf71b96e494ef093adddf6a9665eed7c2bc0e33f8e139b48879638b7b7b299eb9 (https://explorer-studio.genlayer.com/tx/0xf71b96e494ef093adddf6a9665eed7c2bc0e33f8e139b48879638b7b7b299eb9); claim 4 0x21fb01f7ffbe6ba70234f0cb75564ea2979d15bf4570a470c576b17cc7d45681 (https://explorer-studio.genlayer.com/tx/0x21fb01f7ffbe6ba70234f0cb75564ea2979d15bf4570a470c576b17cc7d45681) |
| S1 | LicenseSnapshotAnchor | All four succeeded. MIT_A digest 437ce751...d0f6 fp MIT len 1083. MIT_B digest 4d6fd97e...dc14 fp MIT len 2278. APACHE_A and APACHE_B both digest 948703bc...1092 fp APACHE-2.0 len 10221. snapshot_count returned 4 | RUN | MIT_A 0x03edbe134b6810e670bf72690d82a390a5e1dc0094cbc5f9f72ff82276e5091f (https://explorer-studio.genlayer.com/tx/0x03edbe134b6810e670bf72690d82a390a5e1dc0094cbc5f9f72ff82276e5091f); MIT_B 0x127adae92fc2ce4199ef1d998ff5c3149094f68c3b9f432ab65278c16f319662 (https://explorer-studio.genlayer.com/tx/0x127adae92fc2ce4199ef1d998ff5c3149094f68c3b9f432ab65278c16f319662); APACHE_A 0x2de8c57412f0244e7d10b815b41de4f4c418d2638b5445fdbacf12c842d5c94a (https://explorer-studio.genlayer.com/tx/0x2de8c57412f0244e7d10b815b41de4f4c418d2638b5445fdbacf12c842d5c94a); APACHE_B 0x96df896b74ef3dbd0dc5730596db786a7ca95237ae73a705f52d0ca4d1d83d59 (https://explorer-studio.genlayer.com/tx/0x96df896b74ef3dbd0dc5730596db786a7ca95237ae73a705f52d0ca4d1d83d59) |
| S2 | LicenseSnapshotAnchor | exists true, version 1, content_hash 437ce751...d0f6, fingerprint MIT, text_len 1083, snapshotter ACC1 | RUN | read only, no transaction |
| S3 | LicenseSnapshotAnchor | MIT, GPL-3.0, NONE | RUN | read only, no transaction |
| S4 | LicenseSnapshotAnchor | Reverted with SOURCE_UNREADABLE (DNS failure), get_snapshot returned exists false | RUN | 0xe0ca7b0a6a8e17bdc3fcff9ab36180cf6298d45cb6a3cecb0205c890e80d4388 (https://explorer-studio.genlayer.com/tx/0xe0ca7b0a6a8e17bdc3fcff9ab36180cf6298d45cb6a3cecb0205c890e80d4388) |
| S5 | LicenseSnapshotAnchor | exists false, so a query string is a distinct resource | RUN | read only, no transaction |
| S6 | LicenseSnapshotAnchor | version 2, content_hash 437ce751...d0f6 unchanged, fingerprint MIT | RUN | 0x926086a45a8515fbf179b754e483b3c013714840a83c238887c7af8e245ce19e (https://explorer-studio.genlayer.com/tx/0x926086a45a8515fbf179b754e483b3c013714840a83c238887c7af8e245ce19e) |
| V1 | CorroboratedLicenseReview | Reverted with SNAPSHOT_REQUIRED_PRIMARY | RUN | 0xadfcb558c04f8983fe72e2d9cd1b5763f79b7faac0d627c0a6622c3650e6c93d (https://explorer-studio.genlayer.com/tx/0xadfcb558c04f8983fe72e2d9cd1b5763f79b7faac0d627c0a6622c3650e6c93d) |
| V8 | CorroboratedLicenseReview | Reverted with CLAIM_NOT_FOUND | RUN | 0x5e3ed952604385756de7bef95ff9a57c476cc80964c37158d1d7912dc283c270 (https://explorer-studio.genlayer.com/tx/0x5e3ed952604385756de7bef95ff9a57c476cc80964c37158d1d7912dc283c270) |
| V2 | CorroboratedLicenseReview | verdict CONFIRMED, labels MIT and MIT, strengths 99 and 99, digests equal to the snapshots | RUN | 0xa333d164ddc6c6b8b4dcc835f8fd3056b12d635a550307602da30da3d930e820 (https://explorer-studio.genlayer.com/tx/0xa333d164ddc6c6b8b4dcc835f8fd3056b12d635a550307602da30da3d930e820) |
| V3 | CorroboratedLicenseReview | verdict REFUTED, labels APACHE-2.0 and APACHE-2.0, strengths 100 and 100 | RUN | 0x1eec5f04aae87f02f833ea706603e7c406495eada044a018c96c35cd8770aa0d (https://explorer-studio.genlayer.com/tx/0x1eec5f04aae87f02f833ea706603e7c406495eada044a018c96c35cd8770aa0d) |
| V4 | CorroboratedLicenseReview | verdict INCONCLUSIVE, labels MIT and APACHE-2.0, strengths 100 and 100 | RUN | 0xac82ac9ceb379b5083b4080d83b2b697d089f2d51f1f9c5a1c369dccf7b7d899 (https://explorer-studio.genlayer.com/tx/0xac82ac9ceb379b5083b4080d83b2b697d089f2d51f1f9c5a1c369dccf7b7d899) |
| V5 | CorroboratedLicenseReview | Reverted with ALREADY_REVIEWED | RUN | 0x8e59b13345b9dafc4e15d681651137ee3b353f81bf48decc37e6b486b67da500 (https://explorer-studio.genlayer.com/tx/0x8e59b13345b9dafc4e15d681651137ee3b353f81bf48decc37e6b486b67da500) |
| V6 | CorroboratedLicenseReview | verdict CONFIRMED, reviewed_at 1791984523, deadline 1791984823 (difference 300) | RUN | read only, no transaction |
| V7 | CorroboratedLicenseReview | Not run on chain. Covered only by the local mock run | DEFINED | read only, no transaction |
| C1 | LicenseVerdictChallenge | Reverted with ATTESTER_CANNOT_CHALLENGE | RUN | 0xd070d8d2c20c12fce436d8a35cf67dd1b987d317ef0db456beef1a24301cc41b (https://explorer-studio.genlayer.com/tx/0xd070d8d2c20c12fce436d8a35cf67dd1b987d317ef0db456beef1a24301cc41b) |
| C2 | LicenseVerdictChallenge | challenge_status returned PENDING | RUN | 0x5d6ab9e735e6ffe5f5447471014670d52abb0bb8b2d9bf72c58aeae0305beb45 (https://explorer-studio.genlayer.com/tx/0x5d6ab9e735e6ffe5f5447471014670d52abb0bb8b2d9bf72c58aeae0305beb45) |
| C9a | LicenseVerdictChallenge | Accepted | RUN | 0xb0836dfa6343aaa283c6e9a5dac7f4b2c264df6ee9e682b4e3050b576b6ea045 (https://explorer-studio.genlayer.com/tx/0xb0836dfa6343aaa283c6e9a5dac7f4b2c264df6ee9e682b4e3050b576b6ea045) |
| C3 | LicenseVerdictChallenge | Reverted with ALREADY_CHALLENGED | RUN | 0x8ffd1d02d97c0eb45b876e5be7dafcd8a137ac51a83bae85bec42ddeba285544 (https://explorer-studio.genlayer.com/tx/0x8ffd1d02d97c0eb45b876e5be7dafcd8a137ac51a83bae85bec42ddeba285544) |
| C8 | LicenseVerdictChallenge | Reverted with REVIEW_NOT_FOUND | RUN | 0xa27241c3f195394058dd7c1a125f471722721c84d8ab7c92aa0c75d799bbb6b0 (https://explorer-studio.genlayer.com/tx/0xa27241c3f195394058dd7c1a125f471722721c84d8ab7c92aa0c75d799bbb6b0) |
| C4 | LicenseVerdictChallenge | Reverted with RESOLUTION_WINDOW_OPEN | RUN | 0xfde6c143b9afa76175d602feb1626bd02c187ff1bc7af00894c87e6304d5a0c8 (https://explorer-studio.genlayer.com/tx/0xfde6c143b9afa76175d602feb1626bd02c187ff1bc7af00894c87e6304d5a0c8) |
| C5 | LicenseVerdictChallenge | status RESOLVED, reason INDEPENDENT_JUDGMENT, outcome UPHELD, original CONFIRMED, corrected CONFIRMED, final CONFIRMED, labels MIT and MIT | RUN | 0x394f63ca27531480055d0c86a00f822c2223514348812782b5105e1a34b02909 (https://explorer-studio.genlayer.com/tx/0x394f63ca27531480055d0c86a00f822c2223514348812782b5105e1a34b02909) |
| C6a | LicenseVerdictChallenge | Reverted with NOT_PENDING | RUN | 0xe28a0b79e96772e75281f54767d7a19b9b56f5b3e9716216c7486dc0d91c2b0c (https://explorer-studio.genlayer.com/tx/0xe28a0b79e96772e75281f54767d7a19b9b56f5b3e9716216c7486dc0d91c2b0c) |
| C6b | LicenseVerdictChallenge | Reverted with NOT_PENDING | RUN | 0x185cca67b01999dc51b22d5b15b7fb75588c63ef2f35f235219da973bc31db54 (https://explorer-studio.genlayer.com/tx/0x185cca67b01999dc51b22d5b15b7fb75588c63ef2f35f235219da973bc31db54) |
| C7 | LicenseVerdictChallenge | Reverted with CHALLENGE_WINDOW_CLOSED | RUN | 0x9013d10098a483db65f4f9399b5ac1862cf52289eae01a46806391e3c9885363 (https://explorer-studio.genlayer.com/tx/0x9013d10098a483db65f4f9399b5ac1862cf52289eae01a46806391e3c9885363) |
| C9b | LicenseVerdictChallenge | status EXPIRED, reason EXPIRED_ORIGINAL_STANDS, outcome UPHELD, original INCONCLUSIVE, final INCONCLUSIVE | RUN | 0xd733946414eb470a60bc9f64ea4326799726ab7dc3b808e61353b618de300426 (https://explorer-studio.genlayer.com/tx/0xd733946414eb470a60bc9f64ea4326799726ab7dc3b808e61353b618de300426) |
| C10 | LicenseVerdictChallenge | Returned 2 | RUN | read only, no transaction |
| T1 | AttesterStanding | Reverted with CHALLENGE_UNRESOLVED | RUN | 0x50c24a0569740c96725fe8efb406f6ee4977e73b0030b7392de5c0ca47bb6684 (https://explorer-studio.genlayer.com/tx/0x50c24a0569740c96725fe8efb406f6ee4977e73b0030b7392de5c0ca47bb6684) |
| T2a | AttesterStanding | Not run on chain. By the time finalize(2) was sent, the deadline had already passed (see T2b). Covered only by the local mock run | DEFINED | read only, no transaction |
| T2b | AttesterStanding | Succeeded. final REFUTED, path UNCHALLENGED, score_before 50, score_after 30. This is the result the guide expected from T3 | RUN | 0xccf2593a933dabd14d9c2b3385d62e239db09881ebddb687acfa5d332c4940d2 (https://explorer-studio.genlayer.com/tx/0xccf2593a933dabd14d9c2b3385d62e239db09881ebddb687acfa5d332c4940d2) |
| T3 | AttesterStanding | Reverted with ALREADY_FINALIZED (claim 2 was already finalized by T2b) | RUN | 0xee257b78396d8f3375a2b3eba10f1db62043f866fb2f418ea350023a4e64f0c9 (https://explorer-studio.genlayer.com/tx/0xee257b78396d8f3375a2b3eba10f1db62043f866fb2f418ea350023a4e64f0c9) |
| T4 | AttesterStanding | Reverted with ALREADY_FINALIZED | RUN | 0x576b6ade8b2874780bd6a86a344de4cfcf5f24442c06eab949ecb54898a5f004 (https://explorer-studio.genlayer.com/tx/0x576b6ade8b2874780bd6a86a344de4cfcf5f24442c06eab949ecb54898a5f004) |
| T5 | AttesterStanding | final CONFIRMED, path UPHELD, score_before 30, score_after 40 (the instance had already moved from 50 to 30 in T2b) | RUN | 0x3d5ab731d18b3185a59e95d065b9e7fec77cf35183702421f7eafd5772ab4fcf (https://explorer-studio.genlayer.com/tx/0x3d5ab731d18b3185a59e95d065b9e7fec77cf35183702421f7eafd5772ab4fcf) |
| T6 | AttesterStanding | 0, 0, 0, 0, 0, 1, 100, 30 | RUN | read only, no transaction |
| T7 | AttesterStanding | score_before 5, score_after 0, final REFUTED, path UNCHALLENGED, standing score 0, tier PROBATION, points_to_trusted 70 | RUN | 0x64d71bd1ef8bcc34e3e8ba4656633e5745554b9f059773baee8dbf71adbfedd6 (https://explorer-studio.genlayer.com/tx/0x64d71bd1ef8bcc34e3e8ba4656633e5745554b9f059773baee8dbf71adbfedd6) |
| T8 | AttesterStanding | PROBATION, PROBATION, STANDARD, STANDARD, TRUSTED | RUN | read only, no transaction |
| T9a | AttesterStanding | stage CHALLENGE_PENDING, original CONFIRMED, challengeable_until 1791984823, resolution_deadline 1791985096, result_final false | RUN | read only, no transaction |
| T9b | AttesterStanding | stage FINALIZED, result_final true, final REFUTED, path UNCHALLENGED | RUN | read only, no transaction |
| T9c | AttesterStanding | stage FINALIZED, result_final true, final CONFIRMED, path UPHELD | RUN | read only, no transaction |
| T10 | AttesterStanding | final INCONCLUSIVE, path EXPIRED, score_before 40, score_after 40 | RUN | 0x51fc06e5d7b5e391e51e63bbaaa34db4b33f2d0ccb54a9a7024368cc86df24c4 (https://explorer-studio.genlayer.com/tx/0x51fc06e5d7b5e391e51e63bbaaa34db4b33f2d0ccb54a9a7024368cc86df24c4) |

## D. Bradbury results

| ID | Contract | Result | Status | Transaction |
|----|----------|--------|--------|-------------|
| V0 | CorroboratedLicenseReview | get_last_probe returned 1792004665 | RUN | 0x942f40df28e44d436e833d117c67f18f330cdb2ac42d4f4b12f1f8f56f6db53d (https://explorer-bradbury.genlayer.com/tx/0x942f40df28e44d436e833d117c67f18f330cdb2ac42d4f4b12f1f8f56f6db53d) |
| R1 | LicenseClaimRegistry | claim_count returned 1 | RUN | 0x9804c019cd1cf1e63148131c38860ba7bbced21e278288e91d92f16dcf372be0 (https://explorer-bradbury.genlayer.com/tx/0x9804c019cd1cf1e63148131c38860ba7bbced21e278288e91d92f16dcf372be0) |
| S1 | LicenseSnapshotAnchor | Both accepted | RUN | MIT_A 0x7b582cadad5adc43d60f05faf23277f88b05f99e24edd55813a5e2811b4b14d2 (https://explorer-bradbury.genlayer.com/tx/0x7b582cadad5adc43d60f05faf23277f88b05f99e24edd55813a5e2811b4b14d2); MIT_B 0xd540f96104077b0712dfb35dfc806b01ef56e9ad5cac0306ee6cfacd6bba15cc (https://explorer-bradbury.genlayer.com/tx/0xd540f96104077b0712dfb35dfc806b01ef56e9ad5cac0306ee6cfacd6bba15cc) |
| V2 | CorroboratedLicenseReview | verdict CONFIRMED, labels MIT and MIT, reviewed_at 1792006577, deadline 1792006877, digest_a 437ce751...d0f6 and digest_b 4d6fd97e...dc14, both equal to Studio | RUN | 0xadb79feb76e5bff0fd5eaa98f3b5c07130fa20b6de336582059a684263cba61b (https://explorer-bradbury.genlayer.com/tx/0xadb79feb76e5bff0fd5eaa98f3b5c07130fa20b6de336582059a684263cba61b) |
| T6 | AttesterStanding | 0, 0, 100 | RUN | read only, no transaction |
| C2 | LicenseVerdictChallenge | Not recorded. The 300 second window had already closed before the challenge transaction landed, because transactions on Bradbury took minutes | DEFINED | read only, no transaction |
| T1 | AttesterStanding | Not recorded. The 300 second window had already closed before the challenge transaction landed, because transactions on Bradbury took minutes | DEFINED | read only, no transaction |
| C5 | LicenseVerdictChallenge | Not recorded. The 300 second window had already closed before the challenge transaction landed, because transactions on Bradbury took minutes | DEFINED | read only, no transaction |
| T5 | AttesterStanding | Not recorded. The 300 second window had already closed before the challenge transaction landed, because transactions on Bradbury took minutes | DEFINED | read only, no transaction |

## E. Deviations from the test guide

1. T2. The guide expected CHALLENGE_WINDOW_OPEN for finalize(2). By the time the transaction was sent the 300 second deadline of claim 2 had passed, so the contract correctly finalized it as UNCHALLENGED (50 to 30). The guide expectation for T3 was therefore met by T2b. The window open revert was not observed on chain.
2. T3. The guide expected a fresh finalize of claim 2. It was already finalized, so the contract returned ALREADY_FINALIZED, which is the correct behavior.
3. T5. The guide expected 50 to 60. The same instance had already moved to 30 in T2b, so the correct record is 30 to 40.
4. Bradbury challenge path (C2, T1, C5, T5). Not recorded. Transactions on Bradbury took minutes, and the 300 second window closed before the challenge transaction landed. The same source code passed these tests on Studio. A longer window, for example 3600 seconds, is needed for a full run on Bradbury.

## F. Honest gaps

- No OVERTURNED outcome was observed on chain. It needs a first review that is wrong, which cannot be forced. Every on-chain challenge resolved as UPHELD, and the expiry path kept the original verdict. All three overturn directions (REFUTED to CONFIRMED, CONFIRMED to REFUTED, INCONCLUSIVE to CONFIRMED) were exercised only in the local mock run in section G.
- V7 (source changed after snapshot) was not run on chain.
- T2a (finalize inside the window) was not run on chain.
- The challenge, resolve and finalize path was not run on Bradbury.

## G. Local mock run (not chain evidence)

Before deployment the five contract files were loaded in a local harness that replaces the GenLayer runtime with a stub (fake web pages, a scripted language model, a settable block clock). Result: 121 checks, 121 passed. It covers the registry guards, the fingerprint detector, snapshot versioning, review verdict rules including injected text, the strength tolerance band, source changed reverts, challenge guards, blind and untrusted-data prompts, overturn in three directions, source changed after review, infrastructure failure leaving a challenge PENDING, expiry, finalization blocked inside the window and while pending, reputation arithmetic for every score from 0 to 100, constructor guards, and validator checks against a lying leader. This is a logic check of the same files, not a replacement for the chain results above.

## H. How the three steward points map to evidence

1. Finalization must not bypass the challenge process.
   Design: the review stores deadline = reviewed_at + window_seconds. A challenge needs block time before the deadline. A finalize without a challenge needs block time at or after it. A pending challenge blocks finalize.
   Chain evidence: V6 (deadline minus reviewed_at is 300), C7 (late challenge reverts with CHALLENGE_WINDOW_CLOSED), T1 (finalize with a pending challenge reverts with CHALLENGE_UNRESOLVED), T2b (unchallenged claim finalized only after the deadline), T3 and T4 (ALREADY_FINALIZED), T9a, T9b, T9c (lifecycle stages).
   Gap: T2a is covered only locally.

2. An overturned challenge must give an independently validated corrected outcome.
   Design: resolve_challenge runs a blind judge. It reads only the two URLs, the stored digests and the claimed label. The prompt never contains the original verdict, the claim or anything from the challenger. Validators verify the leader's quoted evidence against their own fetch. The corrected verdict is derived by code and replaces the original in either direction. If the source changed, the original stands. After the resolution deadline anyone can expire the challenge and the original stands.
   Chain evidence: C5 (reason INDEPENDENT_JUDGMENT, corrected verdict recorded, outcome UPHELD), C9b (expiry path), T5 (finalize uses the challenge final verdict), T10 (finalize uses the expired path).
   Gap: no OVERTURNED outcome on chain, see section F.

3. The reputation comparison must be safe below 10.
   Design: REFUTED returns 0 when score is 20 or less, otherwise score minus 20. CONFIRMED adds 10 capped at 100. Tiers are plain comparisons.
   Chain evidence: T6 (eight values on Studio, three on Bradbury), T7 (start_score 5 ends at 0), T8 (tier boundaries).

