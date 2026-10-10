---
name: static-site-release-verification
description: Verifies source, build artifacts, deployed revision, and clean-URL asset parity. Use when releasing a static site, checking CDN freshness, or investigating a successful upload with stale production content.
license: MIT
compatibility: Runtime-neutral workflow. Optional read-only checker requires Python 3.11+ and HTTP access to explicitly authorized targets; no hosting credentials or deployment tools required.
---

# Static-site release verification

## Establish the release contract

1. Identify the repository, source revision, actual build command, output directory, deployment target, and authorized scope. Read the host's deployment provenance without changing it. Keep expected source revision and observed deployed revision separate; an upload receipt or branch tip is not deployment evidence.
2. Build the reviewed revision in an isolated directory. Record dirty/untracked inputs and build tool versions. Select changed routes plus representative template routes (all routes for site-wide changes). Record exact expected content needles, canonical URLs, and referenced CSS/JS/data files from that artifact.
3. Verify source-to-build content and links before deployment. Do not claim a committed artifact was tested if inputs changed after the build. Preserve raw artifacts; normalize only explicitly documented host injections, never arbitrary differences.
4. If deployment is separately approved, execute it through the documented interface. This skill's checker never deploys or purges. Read back the host's exact deployed revision or immutable release ID and tie it to the tested artifact. If provenance is absent, mark revision verification unavailable; do not infer it from matching text.
5. Check immutable preview and ordinary canonical production URLs separately. Use clean URLs without cache-busting queries. Compare HTML content/canonical and every selected CSS/JS/data file against local build bytes. Fresh HTML can reference stale unversioned assets. Record status, redirects, hashes, cache headers, timestamp, and tested vantage point.
6. A stale edge is a release hold, not permission to purge. Request a scoped purge only if authorized; recheck the same clean URLs afterward. A passing single-edge probe is not proof of global CDN propagation. Keep content success distinct from provenance success and optional visual/accessibility checks.

## Optional read-only checker

Use [check_release.py](scripts/check_release.py) with a reviewed manifest modelled on [example.json](assets/example.json). Paths are relative to `--build-dir`; routes and asset URLs are same-origin clean paths. List assets explicitly, including data and nonstandard HTML references: the checker does not crawl the whole site or discover dependencies. HTML verification uses UTF-8 needles and exactly one canonical; assets require exact byte equality. HTML byte parity is not required because hosts may inject markup.

```bash
python3 static-site-release-verification/scripts/check_release.py \
  --manifest release.json --build-dir dist --base-url https://example.com \
  --observed-revision "$HOST_REPORTED_REVISION" > release-evidence.json
```

Obtain `HOST_REPORTED_REVISION` from independent hosting provenance, not by copying the expected value. The sample's revision is synthetic. A missing/mismatched revision or failed check exits nonzero. The checker rejects redirects rather than silently verifying another host, bounds response size and request count, and sends no authorization headers. It may expose manifest routes to the named server; inspect scope before running. It does not execute downloaded code.

## Handoff

Report expected/observed revision and provenance source, build evidence, tested URLs/assets and vantage point, failed assertions, remaining route/edge coverage, and exact next approved operation. Keep uploads, deployments, and verified releases distinct. Never turn an approval timeout into alternate-tool deployment or repeated purge attempts.
