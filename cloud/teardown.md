# Lab 10 — Teardown and limits

## Render

This repository does not yet identify a deployed service. Once created, suspend the **Lab 10 service** from its Settings when it is not needed, or delete that exact service after retaining evidence. Deletion is permanent and must be confirmed separately.

Choose only **Free**. Check the workspace billing/usage page: free compute still has usage limits, and unrelated paid resources are not made free by this lab. Do not add a payment card or enable paid disks/databases.

The free filesystem is ephemeral. Do not keep important notes there. Suspend/delete after collecting the required cold-start and persistence evidence.

## Deploy hook

After finishing the deployment rehearsal, set the GitHub Actions variable `RENDER_DEPLOY_ENABLED` to `false`. Revoke/regenerate the service's deploy hook if it was exposed. Do not paste its URL into the submission, terminal logs, PR or screenshots.

## GitHub

Retain the public package, version tags and successful workflow links long enough for grading. Avoid deleting or moving release tags to rerun CI: create a new version instead. Storage and Actions usage are separate from Render's free compute; inspect the account limits.

## Local Docker

Temporary smoke-test containers use the exact names `quicknotes-lab10-arm64` and `quicknotes-lab10-amd64`, label `course.lab=10`, loopback-only host ports 18090/18091 and disposable tmpfs data.

Before stopping/removing one, inspect its name and label. Never use a blanket prune or stop the existing Lab 8/9 services. The local tags `quicknotes:lab10-arm64` and `quicknotes:lab10-amd64` may be retained for review; removing a tag is not necessary to finish.

No Cloudflare tunnel is created during the mandatory local preparation. Do not expose the existing Lab 8 notes volume for a bonus test.
