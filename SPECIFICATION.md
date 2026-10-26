# State–Major–Feature–Revision (SMFR) Versioning Specification

**Status:** Draft 0.1 — open for review  
**Specification version:** Draft 0.1 (not a declaration of SMFR 1.0 compatibility)

## 1. Purpose and scope

SMFR is a concise, state-first identifier for software releases. It makes release readiness visible immediately, supports explicitly identified parallel release tracks, and omits zero-valued optional components. SMFR does **not** infer dependency compatibility, support lifetime, or artifact identity from a version string alone.

This document defines syntax, canonical representation, comparison of versions within a release track, and recommended release practices. The terms **MUST**, **MUST NOT**, **SHOULD**, and **MAY** are normative requirements and recommendations.

## 2. Canonical syntax

```text
<STAGE><MAJOR>[FEATURE][.SUBVERSION][REVISION]
```

| Component | Form | Meaning |
| --- | --- | --- |
| Stage | `P`, `B`, or `S` | Prototype, Beta, or Stable |
| Major | Positive decimal integer | Compatibility generation or declared product generation |
| Feature | One uppercase `A`–`Z` (optional) | Independently released track within the major generation |
| Subversion | `.` followed by a positive decimal integer (optional) | Subsequent release increment within a track |
| Revision | One uppercase `A`–`Z` (optional) | Small published revision of a particular subversion |

A version MUST match the following pattern (shown with named groups; engines without named groups can use ordinary capture groups):

```regex
^(?<stage>[PBS])(?<major>[1-9][0-9]*)(?<feature>[A-Z])?(?:\.(?<subversion>[1-9][0-9]*))?(?<revision>[A-Z])?$
```

**Additional semantic constraint:** A Revision MUST be present only when Subversion is present. Thus `S1.2A` is valid, while `S1A` always denotes Feature `A`, never Revision `A`.

An equivalent strictly valid regex is:

```regex
^(?<stage>[PBS])(?<major>[1-9][0-9]*)(?<feature>[A-Z])?(?:\.(?<subversion>[1-9][0-9]*)(?<revision>[A-Z])?)?$
```

Versions MUST use ASCII digits and uppercase letters only. They MUST NOT include leading zeros, spaces, prefixes such as `v`, or `.0` components. `P0`, `S01`, `S1.0`, and `S1.02` are invalid.

### 2.1 Examples

Valid: `P1`, `B1`, `S1`, `S1.1`, `S1.1A`, `S2G`, `B2G.3`, `S2G.12Z`, `S100.1000`.

Invalid: `S1.0`, `S01`, `s1`, `S1A.0`, `S1.2AA`, `S1AB.2`, `S1.1.2`, `S1.1-a`, `S1.1a`.

## 3. Component semantics

### 3.1 Stage

- `P` (Prototype): development or experimental release; compatibility may change freely.
- `B` (Beta): testing release; stabilization is underway, but defects or changes remain possible. Release candidates MAY be designated in external release metadata while using `B`.
- `S` (Stable): a released build subject to the project's published stability and support policies. Stable does not mean bug-free.

A project MAY skip stages. Stage is a readiness classification, **not** a global ranking of all releases.

### 3.2 Major

Major SHOULD advance when the project intentionally crosses a published compatibility or product-generation boundary. A breaking public API change normally calls for a new Major. Internal refactoring alone does not. Elapsed time, number of commits, or a Subversion count of 99 MUST NOT automatically trigger a Major change.

### 3.3 Feature track

A Feature letter identifies an **independently released track**, not every Git branch, ticket, or feature flag. For example `S2G.3` belongs to a different release track from `S2.3`.

The empty Feature is the **standard track**. Projects SHOULD maintain a registry describing each letter. They SHOULD NOT reassign a Feature letter to a different meaning within the same product and Major. A large ecosystem with many independent components SHOULD prefer separate package identifiers rather than force every component into a single-letter Feature namespace.

### 3.4 Subversion

Subversion counts releases within a Major and Feature track. It MAY represent compatible features, maintenance updates, or bundled changes. An omitted Subversion has comparison value zero but MUST NOT be rendered as `.0`.

### 3.5 Revision

`A` through `Z` identify up to 26 successive small published revisions to one Subversion baseline. An omitted Revision has comparison value zero; `A` is the first revision. Revision MUST NOT appear without a Subversion, because a suffix letter directly after Major otherwise identifies a Feature track.

For example, the initial stable `S2` cannot have `S2A` as a revision. Its first maintenance baseline can be `S2.1`, followed by `S2.1A`. When the suffix reaches `Z`, a subsequent release SHOULD use a new Subversion (for example `S2.5Z` to `S2.6`). This is a conscious simplicity tradeoff, not a promise that 26 patches will always suffice.

## 4. Comparison and release selection

Comparison is defined **within the same product and Feature track**. Across different Feature tracks it returns `INCOMPARABLE`; one track's version must not silently replace another's. Cross-product comparison is undefined.

Within a product and Feature track, compare these values from left to right:

1. Major (numeric ascending).
2. Subversion (numeric ascending; absent = `0`).
3. Revision (ordinal ascending; absent = `0`, `A` = `1`, ..., `Z` = `26`).
4. Stage (`P` < `B` < `S`) when all earlier values are equal.

This yields, for example:

```text
S2.4 < P2.5 < B2.5 < B2.5A < S2.5A < P2.6
```

This ordering measures **release precedence**, not suitability for production. A resolver that installs stable versions MUST filter out disallowed stages before choosing the greatest eligible version. A greater Major does not prove backward compatibility.

### 4.1 Important limitations

The compact syntax cannot distinguish separate Beta builds that have the same Major, Feature, Subversion, and Revision except by advancing Revision. Each distinct published artifact therefore needs its own unused version (or an explicitly separate build identity, if it is not a publicly released SMFR artifact).

The model also assumes that revisions represent a sequence in a release line; a team SHOULD document its release policy rather than attempt to encode arbitrary ancestry in the string.

## 5. Release policy and immutability

A **published release identifier** MUST NOT be reused for different released contents within the same product, track, and distribution target. Fixes require a new version. A release MAY be withdrawn or marked unsupported, but its identifier MUST NOT be reassigned.

- Targeted patch of `S2.5`: `S2.5A`.
- Further targeted patch: `S2.5B`.
- Larger compatible update: `S2.6`.
- Breaking public API or declared generation transition: new Major, for example `P3`, then `B3`, then `S3` (stages may be skipped).
- Continued maintenance of old Major: `S1.42A` may be published while `S2.8` remains current.
- Rollback: deploy an older already published release; do not renumber it.
- Internal CI build: use a separate build number, commit hash and artifact digest, without necessarily creating a public SMFR release.

For builds differentiated by OS or CPU architecture, the full artifact key SHOULD also contain package identity and target platform. A checksum SHOULD identify the exact bytes.

## 6. Numeric length recommendations

Major and Subversion values from `1` through `99` are **recommended for visual brevity**, not mandatory. `S2.100`, `S100.1`, and `S1000.12000` remain syntactically valid. No rollover, truncation, or forced Major increase occurs at 99.

Revision is always a single letter `A`–`Z` by design.

An implementation MAY impose a documented input-length limit for resource safety; it MUST NOT claim that numbers greater than 99 are invalid SMFR solely for their size.

## 7. Compatibility and ecosystem adapters

SMFR version order does not guarantee API, data, or dependency compatibility. Projects SHOULD separately publish declared compatibility rules and dependencies. Existing registries (for example those requiring SemVer or PEP 440) MAY require an explicit mapping adapter; their acceptance of native SMFR strings MUST NOT be assumed.

## 8. Conformance checklist

A conforming validator MUST:

1. Accept exactly the canonical grammar, including the requirement that Revision needs Subversion.
2. Reject zero components, leading zeros, whitespace, lowercase letters, and extraneous punctuation.
3. Interpret numeric components numerically, not lexicographically (`.12` > `.9`).
4. Preserve the distinction between `S2A` (Feature A) and `S2.1A` (Revision A).
5. Return `INCOMPARABLE` when comparing different Feature tracks.
6. Distinguish syntactic validity from release-policy warnings, including recommended length warnings.

Suggested test cases:

```text
VALID:   P1 B2 S3 S2G S2.9 S2.12 S2.12A S2G.12Z S100.1000
INVALID: P0 S01 S1.0 S1.01 S1.1AA S1AB.2 s1 S1.2a S1.1.2
COMPARE: S2.9 < S2.12
COMPARE: S2.12 < S2.12A < S2.12B < S2.13
COMPARE: P2.5 < B2.5 < S2.5
COMPARE: S2.4 < P2.5
COMPARE: S2G.1 vs S2N.1 => INCOMPARABLE
```

## 9. Known design tradeoffs and open questions

- Feature letters and Revision letters share an alphabet; their placement disambiguates them, at the cost of forbidding revisions on a base version without Subversion.
- The single-letter Revision limit encourages a new maintenance baseline after 26 published patches.
- The ordering is designed for release precedence, not for encoding branch merges or full development history.
- A future specification revision should define a machine-readable Feature Registry and a standard compatibility manifest after reference implementations and ecosystem testing.

**Status notice:** This is a proposed draft, not an adopted industry standard. Rules can change before its first stable specification release.
