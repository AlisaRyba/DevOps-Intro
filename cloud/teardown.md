# Lab 10 — Teardown and limits

## Render

The Lab 10 service is **quicknotes-lab10-alisa**, ID `srv-dbg6vh2jnfac73ff55s0`, at https://quicknotes-lab10-alisa.onrender.com. Its plan is Free. Suspend that exact service from its Settings when it is not needed, or delete it after retaining evidence. Deletion is permanent and must be confirmed separately; no deletion is performed automatically.

Choose only **Free**. Check the workspace billing/usage page: free compute still has usage limits, and unrelated paid resources are not made free by this lab. Do not add a payment card or enable paid disks/databases.

The free filesystem is ephemeral. Do not keep important notes there. This handoff retains the existing Free service for review and grading, which the assignment permits. It will spin down automatically when unused. No paid disk/database, additional service or card was added. The assistant has not suspended or deleted it; the owner can do so after grading.

## Deploy hook

The variable remains `RENDER_DEPLOY_ENABLED=true` so future release tags can deploy. To stop CI deployment after grading, the owner can change it to `false` without deleting the release workflow. Revoke/regenerate the service's deploy hook if it was exposed. Do not paste its URL into the submission, terminal logs, PR or screenshots.

## GitHub

Retain the public package, version tags and successful workflow links long enough for grading. Avoid deleting or moving release tags to rerun CI: create a new version instead. Storage and Actions usage are separate from Render's free compute; inspect the account limits.

## Local Docker

Temporary smoke-test containers use the exact names `quicknotes-lab10-arm64` and `quicknotes-lab10-amd64`, label `course.lab=10`, loopback-only host ports 18090/18091 and disposable tmpfs data.

Before stopping/removing one, inspect its name and label. Never use a blanket prune or stop the existing Lab 8/9 services. The local tags `quicknotes:lab10-arm64` and `quicknotes:lab10-amd64` may be retained for review; removing a tag is not necessary to finish.

No Cloudflare tunnel is created during the mandatory local preparation. Do not expose the existing Lab 8 notes volume for a bonus test.
