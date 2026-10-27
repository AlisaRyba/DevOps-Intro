# Lab 10 — Cloud Computing: QuickNotes release and Render

## Status and scope

**Local preparation is complete; the cloud acceptance criteria are not complete yet.** The owner chose to perform the commit and push herself. No commit, tag, push, GHCR publication, Render service creation, deploy-hook invocation or Cloudflare tunnel was performed by the assistant.

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
| Workflow triggered by a release tag on origin | Pending owner push |
| Public image at GHCR | Not published yet |
| Anonymous pull and resolved digest | Pending publication and package visibility change |
| Successful release-run URL | Not available yet |
| SHA-pinned actions and minimal permissions | Implemented and statically checked |
| Design answers a–c | Below |
| Public Render `/health` and `/notes` | Pending service creation |
| Matching `PORT` / `ADDR`, health path, region | Documented; not yet applied in Render |
| Tag-triggered Render redeployment | Implemented; pending hook secret and enable variable |
| Warm p50 and three cold samples | Not measured in the cloud yet |
| Note persistence across Render spin-down | Not observed yet |
| Design answers d–f | Mechanisms explained below; observed result remains pending |

This is an honest progress record, not a claim of the full 10 points. Remote evidence must be appended after publication and actual deployment.

## Task 1 — Release implementation

The workflow triggers on tag pushes matching `v*`, then validates stable `vMAJOR.MINOR.PATCH`. It rejects the old `v1.0` shape and prerelease suffixes instead of silently publishing them as `latest`.

Jobs run in order:

1. **test**: Go 1.27.3, `go vet`, race-enabled Go tests and offline Python helper tests.
2. **publish**: Buildx builds the existing `app/Dockerfile` for AMD64 and ARM64 and pushes both the version and `latest`.
3. **deploy**: once `RENDER_DEPLOY_ENABLED=true`, invoke the Render hook using the **published digest**, not a later lookup of mutable `latest`.

Planned registry name:

```text
ghcr.io/alisaryba/devops-intro/quicknotes
```

This is the configured destination, **not evidence that the package currently exists**. The first intended tag is `v0.1.0`; it was absent locally, and the unauthenticated GitHub tag API returned 404 during preparation. Check again before creating it.

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

## Task 2 — Planned Render deployment

Choose **Option A, Render**, using the already tested image instead of introducing a second source-build pipeline. The owner created her Render account interactively; no password or token was passed through the chat. No service has been provisioned yet.

Exact planned settings and public-check commands are in [cloud/render.md](../cloud/render.md). The required hook is stored as `RENDER_DEPLOY_HOOK_URL` in GitHub Actions Secrets, never in a tracked file.

Evidence still to collect:

- The real service URL and verbose `curl` output for `/health`.
- `/notes` response, first deploy log and matching listening-port line.
- A release run with the deploy job enabled, followed by a ready public service.
- Five consecutive warm requests and their p50.
- Three separate idle periods of at least 20 minutes, platform spin-down evidence and one cold wake measurement after each.
- A distinctive synthetic note before idle and its actual presence/absence after wake.

Do not poll the service while waiting for spin-down. Local container restarts and redeploys are not substitutes for the required idle/wake experiment.

## Design answers d–f

### d) Render spin-down versus Cloud Run scale-to-zero

Both can release application capacity when idle, then need capacity again when demand returns. Render documents free-service spin-down as a resource-saving feature, not a low-latency availability guarantee. Cloud Run is designed around request-driven autoscaling with configurable concurrency and minimum instances.

This can lead to different wake behavior, but there is no universal fixed speed ratio: startup work, scheduling, image transfer, caches and application initialization all matter. The lab's actual latency comparison is still unmeasured. See [Render's free-service behavior](https://render.com/docs/free) and [Cloud Run autoscaling](https://docs.cloud.google.com/run/docs/about-instance-autoscaling).

### e) PORT versus EXPOSE

`EXPOSE` is image metadata, not a command that opens a socket or forces the application to listen. The runtime platform needs a usable port contract, including for applications not configured by Docker metadata.

QuickNotes reads `ADDR`, not `PORT`. Both are therefore set explicitly: `PORT=8080` and `ADDR=:8080`. The image's existing local healthcheck also expects 8080. This avoids a port-mismatch detection/restart cycle without editing application code.

The assignment describes an extra restart delay; it is not an observed timing in this submission. Actual port log lines remain pending. See [Render port binding](https://render.com/docs/web-services#port-binding).

### f) Existing image versus a Render source build, and note persistence

Using the GHCR artifact separates build from deployment and permits selecting the exact digest. It avoids silently rebuilding different bytes on another host. A Render source build can be convenient for build logs and platform caches, but is another build environment with its own base-image resolution.

The architecture must match, and a new multi-platform build is not automatically identical to the single-platform ARM64 image scanned in Lab 9. The local ARM64 config output retained the patched app, but the AMD64 artifact and future CI digest need their own supply-chain/scanning evidence if that is required.

**Persistence result is pending.** QuickNotes writes a JSON file, not an external database. Render's free filesystem is ephemeral, so an unbacked new note is expected to be lost when the instance's filesystem is replaced, including the documented idle lifecycle. This is a prediction from the storage model, not an invented test result. The actual before/after ID and response must be recorded after the required experiment.

## Bonus

Not attempted. No Cloudflare Tunnel or public exposure of the existing local notes was created. No remote-network verification or 50-run comparison is claimed. Mandatory cloud publication and deployment take priority.

## Next handoff

The owner will review, commit, push `feature/lab10`, and push a fresh stable release tag. After the image appears in GHCR, make the package public and continue Render setup. Do not submit this report as fully completed until the pending acceptance evidence is filled in.
