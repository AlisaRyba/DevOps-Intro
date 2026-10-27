# Lab 10 — Render deployment

## Current state

The owner pushed `v0.1.0` and `v0.1.1`. Both release workflows succeeded and anonymous GHCR pulls passed. **The CI-triggered Render deployment is verified** at https://quicknotes-lab10-alisa.onrender.com. HTTP `/health` and `/notes` were verified without authentication. With the owner's explicit approval, GitHub Actions Secret `RENDER_DEPLOY_HOOK_URL` was saved and repository variable `RENDER_DEPLOY_ENABLED=true` verified. Run `40484545201` successfully invoked the hook and Render deployed digest `sha256:790cab51be256523b45b2248bd91a35ef5674c6cbcd1c56190577bb153699b0c` in deploy `dep-dbg7d3142hec73dqlndg`. All three genuine idle/wake experiments are complete: warm p50 **0.330455 s**, cold **12.805613 / 14.896333 / 13.723240 s**. Each cycle lost its synthetic note and returned the four seed notes after wake. Full raw evidence is linked from [the submission](../submissions/lab10.md).

Service ID: `srv-dbg6vh2jnfac73ff55s0`. Initial deploy: `dep-dbg6vhqjnfac73ff58n0`, completed on 2026-10-27. No payment card was entered. The selected instance is Free ($0/month).

The service is left on Free for grading and can spin down when idle. No request should be expected to stay warm indefinitely. The configured default image is the bootstrap v0.1.0 tag; the verified CI deployment used an explicit v0.1.1 digest override. Do not use Manual Deploy of the default image to reproduce the CI result: subsequent release jobs supply their own published digest.

Use the updated [Lab 10](../labs/lab10.md), which specifies Render with Codespaces only if card verification blocks Render. The older Hugging Face instructions are not used.

## Service settings

Create one **Web Service → Existing Image**, not a database or static site.

| Setting | Value |
|---|---|
| Name | `quicknotes-lab10-alisa` |
| Image | `ghcr.io/alisaryba/devops-intro/quicknotes:v0.1.0` |
| Credentials | None; the GHCR package was already Public when inspected |
| Region | Frankfurt |
| Instance type | **Free, $0**; explicitly change any paid default |
| Health check path | `/health` |
| Docker command override | Leave empty; use the existing image entrypoint |
| Persistent disk | None; unavailable for the free instance |

Environment:

| Key | Value | Purpose |
|---|---|---|
| `PORT` | `8080` | Advertise the application's actual listening port to Render |
| `ADDR` | `:8080` | Bind QuickNotes on all container interfaces |
| `DATA_PATH` | `/data/notes.json` | Writable non-root directory already supplied by the image |
| `SEED_PATH` | `/seed.json` | Synthetic example data, not private notes |

The existing image HEALTHCHECK also uses 8080. Matching both port variables avoids a detection/restart cycle without changing QuickNotes. Render terminates public HTTPS; the container listens on HTTP internally.

The CI image index contains **linux/amd64** for Render and **linux/arm64** for Apple Silicon. A locally built ARM64-only image is not suitable for the Render service.

Do not enter a card or choose a paid plan. If Render requires verification, stop and use the assignment's Codespaces fallback; that would need a separate devcontainer configuration and actual start/stop measurements.

## First release and public package

The new workflow only runs on pushed `v*` tags. A branch push alone does not publish an image.

1. Review and commit the Lab 10 files, then push `feature/lab10`.
2. Check that `v0.1.0` does not already exist locally or on origin. Create an annotated signed tag at the reviewed commit and push **that tag only**.
3. Wait for **Test before publishing** and **Publish multi-platform image** to succeed.
4. The package is initially private by default. In GitHub Packages, select the package corresponding to `devops-intro/quicknotes`, open its settings and make it public. The repository's public visibility does not automatically do this.
5. Confirm an unauthenticated pull before asking Render to use the image.
6. Create the free service with the settings above. Only use disposable sample notes: the learning application has no user authentication and publicly exposes creation/deletion routes.

The image-backed Render service and GHCR package are separate resources. No application data is copied from the local Lab 8 volume.

## Anonymous pull without changing the normal Docker login

Run from the repository root after CI has published the public image:

```bash
LAB10_DOCKER_HOST="$(docker context inspect --format '{{.Endpoints.docker.Host}}')"
LAB10_CLEAN_CONFIG="$(mktemp -d)"
docker --config "$LAB10_CLEAN_CONFIG" --host "$LAB10_DOCKER_HOST" pull \
  ghcr.io/alisaryba/devops-intro/quicknotes:v0.1.0
```

The temporary configuration starts without registry credentials. Shared engine layers can still be cached: record this as an anonymous pull, not as an entirely new physical machine. Capture the resolved digest and output. Do not remove unrelated images or run `docker system prune`.

## Enable deployment from subsequent release tags

The first tag bootstraps GHCR before a Render service exists. With `RENDER_DEPLOY_ENABLED` unset, the deploy job is explicitly skipped. That first run proves image publication only, not continuous deployment.

After creating the service:

1. In Render service **Settings**, locate its **Deploy Hook**.
2. In the GitHub fork, **Settings → Secrets and variables → Actions → Secrets**, create `RENDER_DEPLOY_HOOK_URL` with the full hook URL.
3. Under **Variables**, create `RENDER_DEPLOY_ENABLED` with value `true`.
4. Publish a new unused stable tag, for example `v0.1.1`, after the first deployment. The workflow then publishes that version and invokes the hook with the **newly built index digest** as `imgURL`.

The helper [deploy_render.py](../scripts/lab10/deploy_render.py) URL-encodes the image, sends one POST, refuses redirects and suppresses secret URLs in errors. It does not automatically retry an uncertain timeout, because that can queue duplicate deployments. The image name must match the service's configured image; only the tag or digest changes.

The deploy job has only `contents: read`; `packages: write` exists only in the publish job. No PAT or cloud API key is committed.

A hook response 200/202 means **accepted/queued**, not ready. Check Render's deploy log and then verify public `/health` and `/notes`.

## Public checks and genuine spin-down measurements

Replace the example origin with the service's actual URL:

```bash
curl --verbose --fail --max-time 180 https://YOUR-SERVICE.onrender.com/health
curl --fail --show-error --max-time 30 https://YOUR-SERVICE.onrender.com/notes
python3 scripts/lab10/measure.py https://YOUR-SERVICE.onrender.com \
  --count 5 --label warm --output submissions/lab10/warm.json
```

Only measure warm requests after the service is ready. The helper validates HTTP 200 **and** QuickNotes JSON, records UTC and curl's phase/total times, and calculates p50. It creates a new output file rather than overwriting earlier evidence.

For each of three cold samples: stop manual requests, external uptime checks and open auto-refreshing pages; allow **at least 20 minutes without traffic**; verify spin-down in the platform logs, then issue exactly one request. Our experiment uses a conservative 21-minute deadline after the last request's completion. Reading dashboard logs does not make an application request.

For a new experiment, choose a fresh output directory first. This raw curl form preserves an intermediate/error response as evidence instead of discarding it:

```bash
LAB10_TIMING_DIR="$(mktemp -d)"
curl --disable --silent --show-error --connect-timeout 10 --max-time 180 \
  --dump-header "$LAB10_TIMING_DIR/cold-1-headers.txt" \
  --output "$LAB10_TIMING_DIR/cold-1-body.txt" \
  --write-out '%{json}\n' https://YOUR-SERVICE.onrender.com/health \
  > "$LAB10_TIMING_DIR/cold-1.json"
```

Record the wall-clock start immediately before the request, and retain curl's exit code. Check the actual status and application JSON before accepting its total time:

```bash
jq '{http_code, time_total, time_starttransfer, ssl_verify_result, exitcode}' \
  "$LAB10_TIMING_DIR/cold-1.json"
jq -e '.status == "ok"' "$LAB10_TIMING_DIR/cold-1-body.txt"
```

Require HTTP 200, curl exit 0 and successful TLS verification too. Repeat a fresh idle period for `cold-2.json` and `cold-3.json`, changing all three output filenames. Our saved cold files use raw curl metadata, whereas `warm.json` uses the measurement helper's report format. Neither command sleeps or polls automatically: polling can keep the service warm. A redeploy/restart is not evidence of automatic idle spin-down. If the waking proxy returns an intermediate page instead of QuickNotes, retain the failure context and measure time to actual readiness separately; do not count that page as successful application latency.

Create a distinctive, synthetic note before an idle period, record its returned ID/title/creation time, and retrieve `/notes` after wake. A fresh instance can reuse a numeric ID, so match the distinctive note rather than the ID alone. Do not confuse the local container restart result with Render's ephemeral-filesystem behavior.

The actual deploy URL, run links, log lines and measurements must be added to [submissions/lab10.md](../submissions/lab10.md) after deployment.

## Official references

- [Render image-backed services](https://render.com/docs/deploying-an-image)
- [Render deploy hooks](https://render.com/docs/deploy-hooks)
- [Render free-instance limits and ephemeral storage](https://render.com/docs/free)
- [GHCR authentication and package visibility](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
