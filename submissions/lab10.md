# Lab 10 — Cloud Computing: QuickNotes release and Render

## Status and scope

**The mandatory implementation and remote experiments for Tasks 1 and 2 are complete.** The owner committed and pushed `feature/lab10` and signed tags `v0.1.0` and `v0.1.1` at `766885bd0868f29ca45d7bfa1b03cd8834ad60e9`. No assistant commit or push was performed. All three genuine idle/wake cycles, public readiness and note-persistence observations are recorded below. The final evidence update still needs the owner's review, commit/push and PR submission.

Prepared and checked locally on **2026-10-27**:

- New tag-triggered [release workflow](../.github/workflows/release.yml).
- Multi-platform publication configuration: `linux/amd64` for Render and `linux/arm64` for Apple Silicon.
- Least-privilege GHCR login using `GITHUB_TOKEN`; all six action dependencies pinned to verified 40-character commit SHAs.
- Digest-specific Render deploy-hook helper, with offline tests for URL validation, encoding, redirects and secret suppression.
- [Render settings and bootstrap procedure](../cloud/render.md), [teardown guidance](../cloud/teardown.md), and a reusable curl-based latency recorder.
- Actual local builds and HTTP checks on both architectures, plus Go vet/race tests and helper tests.

The checkout began clean on `feature/lab9`, commit `22093dec18aaca8e9d75263f0c58c8c7731785d2`. `feature/lab10` was created from that commit to preserve the completed previous labs. Existing tracked files, the Lab 8 stack, the Lab 9 instance and their data were not changed.

The local assignment and the raw public main-branch assignment had identical SHA-256:

```text
90cc2c40ee9b12398398b8f57ad6792830709fa92ef64a4333c9c2c792b1afbd
```

The GitHub HTML preview returned an older Hugging Face variant. The raw file matches the updated local **Render / Codespaces** assignment, so that is the version followed.

## Acceptance record

| Required evidence | State |
|---|---|
| Workflow triggered by a release tag on origin | Passed: `v0.1.0`, run `40480341684` |
| Public image at GHCR | Passed: version and `latest` published |
| Anonymous pull and resolved digest | Passed with a fresh Docker configuration; evidence below |
| Successful release-run URL | [Bootstrap release run](https://github.com/AlisaRyba/DevOps-Intro/actions/runs/40480341684), success |
| SHA-pinned actions and minimal permissions | Implemented and statically checked |
| Design answers a–c | Below |
| Public Render `/health` and `/notes` | Passed initially, after CI deployment and after all three wakes |
| Matching `PORT` / `ADDR`, health path, region | Applied: 8080, `/health`, Frankfurt, Free |
| Tag-triggered Render redeployment | Passed: v0.1.1 run 40484545201, all three jobs success; Render Live |
| Warm p50 and three cold samples | Passed: warm p50 0.330455 s; cold 12.805613, 14.896333, 13.723240 s |
| Note persistence across Render spin-down | Observed: all three cycles lost their distinctive synthetic note |
| Design answers d–f | Answered below, with actual persistence evidence |

All mandatory technical acceptance checks have evidence. This is not a claim of an assigned grade: the owner still needs to publish the final evidence update and submit the PR for review. The optional bonus was not attempted.

## Task 1 — Release implementation

The workflow triggers on tag pushes matching `v*`, then validates stable `vMAJOR.MINOR.PATCH`. It rejects the old `v1.0` shape and prerelease suffixes instead of silently publishing them as `latest`.

Jobs run in order:

1. **test**: Go 1.27.3, `go vet`, race-enabled Go tests and offline Python helper tests.
2. **publish**: Buildx builds the existing `app/Dockerfile` for AMD64 and ARM64 and pushes both the version and `latest`.
3. **deploy**: once `RENDER_DEPLOY_ENABLED=true`, invoke the Render hook using the **published digest**, not a later lookup of mutable `latest`.

Published registry name:

```text
ghcr.io/alisaryba/devops-intro/quicknotes
```

The initial tag `v0.1.0` now exists on origin and triggered the successful run linked below. Do not recreate or move it. The package page already displayed **Public**, so no package-visibility setting was changed by the assistant.

Workflow-wide permissions are empty. Test and deploy jobs receive `contents: read`; only publish receives `packages: write` as well. Checkout does not persist credentials. No PAT and no `id-token: write` are required for this GHCR use case.

The current checkout has no legacy Lab 3 workflow file. The new release workflow therefore runs its own vet/race checks; it does not assume a missing workflow will gate publication.

The initial release can publish before a Render service exists: the deploy job is skipped while its enable variable is unset. After creating the service and setting its hook secret, publish a new version such as `v0.1.1` to demonstrate the actual CI → Render path. A publication-only run is not counted as completed deployment.

### Action pins

Verified against the official repositories' tag refs on 2026-10-27:

| Action | Version | Commit |
|---|---|---|
| `actions/checkout` | `v7.0.1` | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| `docker/setup-qemu-action` | `v4.4.0` | `99012661954931238ded8c8b007157a8430204e1` |
| `docker/setup-buildx-action` | `v4.4.1` | `f87e5991a6d7451dcb8d9637bfbc97413f497069` |
| `docker/login-action` | `v4.7.0` | `81c6f93d4bc991e510b342a00b419b3bb4efc5c6` |
| `docker/build-push-action` | `v7.4.0` | `c3c9e263c25d99ce0380d002d59b67737d91b0dc` |
| `actions/setup-go` | `v7.0.0` | `b7ad1dad31e06c5925ef5d2fc7ad053ef454303e` |

## Actual GHCR release evidence

The owner-pushed tag triggered [release run 40480341684](https://github.com/AlisaRyba/DevOps-Intro/actions/runs/40480341684) at source commit `766885bd0868f29ca45d7bfa1b03cd8834ad60e9`. Both **Test before publishing** and **Publish multi-platform image** concluded `success`; the deploy job was intentionally `skipped` because Render was not configured yet.

Published version: `ghcr.io/alisaryba/devops-intro/quicknotes:v0.1.0`.

Published OCI index digest:

```text
sha256:487da8b14865453c32e13b1e1b2ef38583af55f929a867eb5d3c0ee01b27a336
```

An actual `docker pull` succeeded with a newly created, empty Docker configuration, without registry login. Its returned digest matches the release log. Some base layers were already cached by the local engine; this is a clean-credentials pull, not a new physical machine.

The [manifest](lab10/manifest-v0.1.0.json) contains Linux AMD64 and ARM64 application manifests plus two provenance-attestation manifests marked `unknown/unknown`. Those attestation entries are not additional runnable architectures.

Raw evidence: [release status and jobs](lab10/release-bootstrap.json), [anonymous pull output](lab10/anonymous-pull-v0.1.0.txt), and [public package](https://github.com/AlisaRyba/DevOps-Intro/pkgs/container/devops-intro%2Fquicknotes).

## Verified CI-triggered deployment

The owner pushed `v0.1.1` without moving `v0.1.0`. [Release run 40484545201](https://github.com/AlisaRyba/DevOps-Intro/actions/runs/40484545201) completed successfully, including the deploy job. The hook returned HTTP 200 and deployment ID `dep-dbg7d3142hec73dqlndg`; its URL/key are not recorded.

The new published index is `sha256:790cab51be256523b45b2248bd91a35ef5674c6cbcd1c56190577bb153699b0c`. Render's event shows **Triggered via Deploy Hook**, the same full index digest and AMD64 manifest prefix `bab3e26`; its deploy page reports **Deploy succeeded | Live**. The actual log includes `2026/10/27 10:01:58 quicknotes listening on :8080 (notes loaded: 4)` and a live message at 13:02:05 GMT+3. The 13.0-second deploy duration is not an idle cold-start sample.

An unauthenticated [post-CI health request](lab10/render-health-after-ci.txt) independently returned HTTP/2 200 and QuickNotes JSON after readiness. [Post-CI notes](lab10/render-notes-after-ci.json) contain only the four seed notes: the initial v0.1.0 probe was lost across redeployment, not yet a spin-down test.

Five consecutive [final warm samples](lab10/warm.json) give p50 **0.330455 seconds**. Each request uses a fresh curl process, including DNS/connect/TLS. The sample is small and is not a latency SLO.

Evidence: [release/jobs](lab10/release-ci-deploy.json), [CI hook and Render log excerpts](lab10/render-ci-deploy-log.txt), [anonymous v0.1.1 pull](lab10/anonymous-pull-v0.1.1.txt), [manifest](lab10/manifest-v0.1.1.json).

The image source setting still names the initial tag v0.1.0. Render's hook override selected the new digest for this deployment without changing that default setting. Manual Deploy of the default image could therefore return to v0.1.0; subsequent CI releases again pass their explicit digest. The platform's auto-deploy-disabled banner does not mean the separate GitHub deploy-hook job was disabled.

## Local verification and evidence

Host: macOS ARM64. Docker client/server: 29.8.2. Tests use the Lab 9 patched `golang:1.27.3-alpine` builder; the unchanged application image remains distroless and non-root.

Build commands:

```bash
BUILDX_CONFIG=/private/tmp/quicknotes-lab10.U0rD0s/buildx \
  docker build --builder desktop-linux --platform linux/arm64 \
  --tag quicknotes:lab10-arm64 app

BUILDX_CONFIG=/private/tmp/quicknotes-lab10.U0rD0s/buildx \
  docker build --builder desktop-linux --platform linux/amd64 \
  --tag quicknotes:lab10-amd64 app
```

The temporary Buildx configuration avoids writing activity metadata into the user's protected Docker configuration. Both builds succeeded. AMD64 was built and run under Docker Desktop emulation; it was not falsely treated as native ARM64.

Actual image inspection:

```text
[quicknotes:lab10-arm64] os=linux arch=arm64 user=nonroot:nonroot id=sha256:0293a572f1ca78b5d0352804a9986764a6e03f84145636737aa6645f3b6d4d69
[quicknotes:lab10-amd64] os=linux arch=amd64 user=nonroot:nonroot id=sha256:a52738c390deeaf587ac6a808649f0fea38c83a13ec3556eb0ab17ceb5304af6
```

These are local Docker image IDs, not published GHCR digests. Local BuildKit attestations can make an image ID refer to an index. The eventual release workflow records its own published index digest.

Isolated instances used loopback-only ports **18090** and **18091**, label `course.lab=10`, the documented environment and disposable `/data` tmpfs. They did not reuse the original notes volume.

Actual checks:

| Check | Observed result |
|---|---|
| ARM64 `GET /health` | HTTP 200, `{"notes":4,"status":"ok"}` |
| AMD64 `GET /health` | HTTP 200, `{"notes":4,"status":"ok"}` |
| AMD64 `GET /notes` | HTTP 200, four repository seed notes |
| ARM64 synthetic `POST /notes` | HTTP 201, returned ID 5 |
| Delete only that synthetic note | HTTP 204 |
| Image healthcheck, both platforms | `healthy` |
| `go vet ./...` | Exit 0 |
| `go test -race -count=1 ./...` | Exit 0 |
| Python helper suite | 12 tests, pass |
| actionlint 1.7.12 | Exit 0; ShellCheck integration disabled because it is not installed |

The actionlint macOS ARM64 download was verified against its official SHA-256 list:
`aba9ced2dee8d27fecca3dc7feb1a7f9a52caefa1eb46f3271ea66b6e0e6953f`.
It was unpacked only in temporary storage; no global package or configuration was changed.

[Local check details](lab10/local-checks.txt) and [raw local timing samples](lab10/latency-local-arm64.json) are included. The local five-request p50 was **0.001137 seconds**. This only validates the measurement helper and the loopback instance. It is **not** Render warm latency, a cold start, a public URL test or a cross-network comparison.

### Reproduce helper and Go tests

```bash
python3 -m unittest discover -s scripts/lab10 -p 'test_*.py' -v

docker run --rm --platform linux/arm64 \
  --mount type=bind,src="$PWD/app",dst=/src,readonly \
  --workdir /src --env GOCACHE=/tmp/go-build \
  golang:1.27.3-alpine sh -ec \
  'apk add --no-cache gcc musl-dev; go vet ./...; go test -race -count=1 ./...'
```

Compilers are installed only inside the disposable test container. The source mount is read-only. The cloud builder retains the Go security fixes from Lab 9; this task did not rerun a vulnerability scan of the new AMD64 image.

## Design answers a–c

### a) GITHUB_TOKEN versus OIDC

For this repository's GHCR publication, the per-job GitHub token with package-write permission is sufficient. Its authority belongs to GitHub resources; it is not a general cloud-provider identity.

OIDC is useful when deploying to a provider such as AWS, Azure, Google Cloud or Vault that can validate GitHub's signed workload identity and exchange it for short-lived provider credentials. A trust policy can restrict the repository, ref, environment and audience. This avoids storing a long-lived cloud access key in GitHub Secrets.

OIDC does not itself grant arbitrary cloud access: the external trust and provider-side permissions must exist. It would require `id-token: write`, which is deliberately not requested here. See [GitHub's OIDC model](https://docs.github.com/en/actions/concepts/security/openid-connect).

### b) Why publish both latest and a version

`latest` is a convenience pointer for local exploration and consumers intentionally following the newest release. A version identifies a specific release in documentation and rollback procedures.

A registry version **tag is technically mutable too** unless separate registry policy enforces immutability. This project treats published version tags as write-once by process, while Render deployment uses the content digest to identify exact bytes. Changing `latest` cannot silently change the digest already passed to the deploy hook.

### c) Why narrow token permissions

This is least privilege: each job receives only the authority required for its function. A compromised publish action should not also receive repository-content write, issue write or unrelated administrative capabilities. In particular, lack of `contents: write` prevents using that token to push arbitrary source changes where such writes would otherwise be allowed.

`packages: write` still permits package damage within its actual scope, so pinning actions and protecting release creation remain important. Narrow permissions reduce blast radius rather than making a malicious step harmless. See [GitHub token permissions](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token).

## Task 2 — Initial Render deployment

Used **Option A, Render**, with the published image instead of introducing a second source-build pipeline. The owner created her Render account interactively; no password or token was passed through the chat. After explicit confirmation of public exposure, the assistant created only the Free ($0/month) service, without entering a card or upgrading the workspace.

Public origin: https://quicknotes-lab10-alisa.onrender.com. Service ID: `srv-dbg6vh2jnfac73ff55s0`. Initial deploy: `dep-dbg6vhqjnfac73ff58n0`, reported Live by Render. The [actual deploy log](lab10/render-initial-deploy-log.txt) shows `quicknotes listening on :8080 (notes loaded: 4)` and the public URL. Render displayed a 10.7-second initial deploy; this is not an idle cold-start measurement.

An unauthenticated [verbose health request](lab10/render-health-initial.txt) verified the TLS certificate and returned HTTP/2 200 with `{"notes":4,"status":"ok"}`. [GET /notes](lab10/render-notes-initial.json) returned the four repository seed notes. No local data volume was uploaded.

Five consecutive successful requests to the initial release gave warm p50 **0.230013 seconds**. [Raw initial samples](lab10/warm-initial.json) include UTC timestamps and curl phase times. They include client DNS/connect/TLS and are not a server-only processing measurement.

The applied settings and public-check commands are in [cloud/render.md](../cloud/render.md). After the owner's explicit approval, the existing deploy hook was transferred directly from its Render settings field into GitHub Actions repository Secret `RENDER_DEPLOY_HOOK_URL`. GitHub confirmed `Repository secret added.` The repository variable `RENDER_DEPLOY_ENABLED` was created and verified as `true`. The hook value was not printed, added to files, or included in screenshots. [Configuration evidence](lab10/render-ci-configuration.json) records names and status only, never the secret value. The actual successful v0.1.1 hook invocation is documented above.

A synthetic initial probe was created at `2026-10-27T09:39:14.576608396Z`, returned ID 5; its [actual response](lab10/render-note-before-idle-initial.json) is saved. It disappeared across the subsequent redeployment. That initial probe is not used to claim a standalone idle persistence result.

## Genuine idle/wake measurements

All final measurements use the CI-deployed v0.1.1 digest. No manual redeploy or restart is used to create a cold sample. Each independent idle interval lasts at least 21 minutes, with no application requests from this experiment. Reading the Render dashboard is a control-plane operation, not an HTTP request to the public application.

| Cycle | Last request completed, UTC | Shutdown log, UTC | Cold request started, UTC | Idle seconds | HTTP | Total seconds |
|---|---|---|---|---:|---:|---:|
| 1 | 10:03:57 | 10:18:57 | 10:27:25 | 1408 | 200 | 12.805613 |
| 2 | 10:28:10 | 10:43:03 | 10:49:20 | 1270 | 200 | 14.896333 |
| 3 | 10:49:57 | 11:04:44 | 11:11:09 | 1272 | 200 | 13.723240 |

The first cold request returned `{"notes":4,"status":"ok"}`, not Render's intermediate loading page. The dashboard logs show instance `bgffq` shutting down at 10:18:57 and a new instance `6vnb8` starting at 10:27:32 with four loaded notes. The [cycle record](lab10/idle-cycle-1.json), [raw curl metadata](lab10/cold-1.json), [response headers](lab10/cold-1-headers.txt) and [body](lab10/cold-1-body.txt) preserve the actual result. TLS verification succeeded; curl did not retry or follow redirects.

Immediately before the first idle interval, POST returned ID 5 for `Lab 10 v0.1.1 idle persistence probe` at `2026-10-27T10:03:57.238288146Z`. After wake, [GET /notes](lab10/notes-after-cold-1.json) returned only the four original seed notes. The [distinctive probe](lab10/note-before-idle.json) is absent. This is an observed loss across automatic spin-down/wake, independent of the earlier redeployment. ID alone is not the identity check: a fresh seed-backed process can reuse ID 5.

The second cycle independently returned HTTP 200 and `{"notes":4,"status":"ok"}` after 14.896333 seconds. Render logs show `6vnb8` stopping at 10:43:03 and `lnz5s` starting at 10:49:26. Its [cycle record](lab10/idle-cycle-2.json), [curl metadata](lab10/cold-2.json), [headers](lab10/cold-2-headers.txt), [body](lab10/cold-2-body.txt), [note before idle](lab10/note-before-idle-2.json) and [notes after wake](lab10/notes-after-cold-2.json) confirm that the second distinctive probe was also lost.

The third cycle returned HTTP 200 and the same valid health JSON after 13.723240 seconds. Render logs show `lnz5s` stopping at 11:04:44 and `5hprt` starting at 11:11:19. Its [cycle record](lab10/idle-cycle-3.json), [curl metadata](lab10/cold-3.json), [headers](lab10/cold-3-headers.txt), [body](lab10/cold-3-body.txt), [note before idle](lab10/note-before-idle-3.json) and [notes after wake](lab10/notes-after-cold-3.json) confirm the third probe was also lost.

The [actual platform log excerpts](lab10/render-idle-wake-log.txt) cover all three shutdown/startup pairs. All table times are UTC on 2026-10-27; the dashboard displays UTC+3. The recorded last-request completion times for cycles 2 and 3 are deliberately taken after their POST response was collected, so they conservatively understate the quiet interval. These were three separate automatic spin-downs, not three requests during the same startup.

Cold-request times include client DNS/connect/TLS and the wait for a ready application. No intermediate page, redirect, retry or failed response is counted as success. Three observations are enough for this assignment's demonstration, not a statistical availability or production-latency guarantee.

## Design answers d–f

### d) Render spin-down versus Cloud Run scale-to-zero

Both can release application capacity when idle, then need capacity again when demand returns. Render documents free-service spin-down as a resource-saving feature, not a low-latency availability guarantee. Cloud Run is designed around request-driven autoscaling with configurable concurrency and minimum instances.

Render's free tier prioritizes resource savings rather than keeping an always-ready instance. Waking it can involve scheduling capacity, preparing the container filesystem and starting the application before proxying a waiting request. Cloud Run is a managed, request-driven execution platform whose autoscaling and startup path target serving traffic; minimum instances can trade idle cost for less startup delay. Neither model guarantees that every cold start has a fixed duration.

Our three Render cold requests took 12.805613, 14.896333 and 13.723240 seconds versus the five-request warm p50 of 0.330455 seconds. This demonstrates the idle penalty in this experiment, not a measured Render-versus-Cloud-Run benchmark: Cloud Run was not deployed. Startup work, scheduling, image transfer and caches can change later results. See [Render's free-service behavior](https://render.com/docs/free) and [Cloud Run autoscaling](https://docs.cloud.google.com/run/docs/about-instance-autoscaling).

### e) PORT versus EXPOSE

`EXPOSE` is image metadata, not a command that opens a socket or forces the application to listen. The runtime platform needs a usable port contract, including for applications not configured by Docker metadata.

QuickNotes reads `ADDR`, not `PORT`. Both are therefore set explicitly: `PORT=8080` and `ADDR=:8080`. The image's existing local healthcheck also expects 8080. This avoids a port-mismatch detection/restart cycle without editing application code.

The assignment describes an extra restart delay; it is not an observed timing in this submission. The initial actual log shows `quicknotes listening on :8080`; no port-mismatch restart appeared in the observed first-deploy log. See [Render port binding](https://render.com/docs/web-services#port-binding).

### f) Existing image versus a Render source build, and note persistence

Using the GHCR artifact separates build from deployment and permits selecting the exact digest. It avoids silently rebuilding different bytes on another host. A Render source build can be convenient for build logs and platform caches, but is another build environment with its own base-image resolution.

The architecture must match, and a new multi-platform build is not automatically identical to the single-platform ARM64 image scanned in Lab 9. The local ARM64 config output retained the patched app, but the AMD64 artifact and future CI digest need their own supply-chain/scanning evidence if that is required.

**Observed result: all three independent idle/wake cycles lost their synthetic note.** QuickNotes writes `/data/notes.json`, not an external database. Its image makes that directory writable, but a directory inside the container is not automatically persistent storage. The free service has no persistent disk; when Render recreated the runtime after idle, QuickNotes loaded the four bundled seed notes instead of the old writable file. The original source image and public URL staying the same did not preserve the previous instance's writes. Durable notes would require an external database or supported persistent storage, with backup and recovery designed separately.

## Bonus

Not attempted. No Cloudflare Tunnel or public exposure of the existing local notes was created. No remote-network verification or 50-run comparison is claimed. Mandatory cloud publication and deployment take priority.

## Next handoff

The owner has already pushed both `v0.1.0` and `v0.1.1`; publication, CI deployment and public readiness succeeded. No more release tag is needed for this implementation. Do not move either existing tag. The owner retains control of the final evidence-only commit and push, followed by the PR from `feature/lab10` to the course repository's `main` and the Moodle submission.

The existing Free Render service is retained for review, as permitted by the assignment. It may be asleep when opened; the next request wakes it. `RENDER_DEPLOY_ENABLED` remains `true`. No paid resource, payment card, persistent disk, Cloudflare tunnel or additional cloud service was added. Suspension/deletion and disabling future deploys are documented in [teardown guidance](../cloud/teardown.md), not performed automatically.

The final after-wake `/notes` response contains only the four synthetic seed notes. Existing local Lab 8/9 containers and data were left alone. Python bytecode remains locally ignored; no generated build cache or temporary executable is included in the intended commit, and `.gitignore` was not changed.


## Final verification and files left for review

All 12 offline helper tests passed again. Actionlint returned exit 0 (ShellCheck is not installed), relative documentation links resolved, and the saved-evidence cross-check verified five warm samples, all three independent 21+ minute idle intervals, successful HTTP/TLS/QuickNotes responses and the absence of each distinctive probe after wake. `git diff --check` returned exit 0. [Actual final check output](lab10/final-checks.txt) is retained.

A SHA-256 comparison against the 109 tracked files recorded after the owner's push found changes only in the four documentation files below. The release workflow, helper source, application, previous labs and `.gitignore` remain unchanged. Nothing is staged. HEAD remains `766885bd0868f29ca45d7bfa1b03cd8834ad60e9`; both existing release tags still point there. Unrelated running Docker containers were not stopped.

Final working-tree file list (`M` = modified documentation, `??` = new evidence intended for the final commit):

```text
M  cloud/render.md
M  cloud/teardown.md
M  submissions/lab10.md
M  submissions/lab10/README.md
?? submissions/lab10/anonymous-pull-v0.1.0.txt
?? submissions/lab10/anonymous-pull-v0.1.1.txt
?? submissions/lab10/cold-1-body.txt
?? submissions/lab10/cold-1-headers.txt
?? submissions/lab10/cold-1.json
?? submissions/lab10/cold-2-body.txt
?? submissions/lab10/cold-2-headers.txt
?? submissions/lab10/cold-2.json
?? submissions/lab10/cold-3-body.txt
?? submissions/lab10/cold-3-headers.txt
?? submissions/lab10/cold-3.json
?? submissions/lab10/final-checks.txt
?? submissions/lab10/idle-cycle-1.json
?? submissions/lab10/idle-cycle-2.json
?? submissions/lab10/idle-cycle-3.json
?? submissions/lab10/manifest-v0.1.0.json
?? submissions/lab10/manifest-v0.1.1.json
?? submissions/lab10/note-before-idle-2.json
?? submissions/lab10/note-before-idle-3.json
?? submissions/lab10/note-before-idle.json
?? submissions/lab10/notes-after-cold-1.json
?? submissions/lab10/notes-after-cold-2.json
?? submissions/lab10/notes-after-cold-3.json
?? submissions/lab10/release-bootstrap.json
?? submissions/lab10/release-ci-deploy.json
?? submissions/lab10/render-ci-configuration.json
?? submissions/lab10/render-ci-deploy-log.txt
?? submissions/lab10/render-health-after-ci.txt
?? submissions/lab10/render-health-initial.txt
?? submissions/lab10/render-idle-wake-log.txt
?? submissions/lab10/render-initial-deploy-log.txt
?? submissions/lab10/render-note-before-idle-initial.json
?? submissions/lab10/render-notes-after-ci.json
?? submissions/lab10/render-notes-initial.json
?? submissions/lab10/warm-initial.json
?? submissions/lab10/warm.json
```

Review and publish manually from the repository root; the following commands have **not** been executed by the assistant:

```bash
git diff --check
git diff -- cloud/render.md cloud/teardown.md submissions/lab10.md submissions/lab10/README.md
git status --short
# Also inspect the new evidence files: unstaged git diff does not show their contents.
git add cloud/render.md cloud/teardown.md submissions/lab10.md submissions/lab10/
git diff --cached --stat
git diff --cached
git commit -m "Lab 10: record Render deployment and cold-start evidence"
git push origin feature/lab10
```

Then create the course PR and submit its URL via Moodle. No extra tag, force push, package deletion or secret disclosure is needed.
