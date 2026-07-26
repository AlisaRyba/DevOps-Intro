## 1. CI Platform Choice

**Path picked:** GitHub Actions

**Reason:** The course repository is hosted on GitHub, and GitHub Actions integrates seamlessly with pull requests, branch protection rules, and the overall GitHub ecosystem. It requires no additional setup or external accounts, making it the most straightforward choice for this lab. GitHub Actions also provides excellent visibility into CI status directly on the PR page.

---

## 2. Green CI Run

**Link to a successful CI run:**

[https://github.com/AlisaRyba/DevOps-Intro/actions/runs/30217149695](https://github.com/AlisaRyba/DevOps-Intro/actions/runs/30217149695)

**Screenshot:**

![Green CI Run](./PJgeZhtNPl.png)

All three jobs (`vet`, `test`, `lint`) passed successfully.

## 3. Failed Run (Intentional Breakage)

### 3.1: Breaking the Test

To verify that the CI gate works, I intentionally broke the test in `app/health_test.go`:

**Change made:**

```go
// Before (passing)
if response["status"] != "ok" {
    t.Errorf("expected status 'ok', got '%v'", response["status"])
}

// After (failing)
if response["status"] != "broken" {
    t.Errorf("expected status 'broken', got '%v'", response["status"])
}

```

![Screenshot of failed run](./ciRj7meQdU.png)

--- FAIL: TestHealthHandler (0.00s)
health_test.go:39: expected status 'broken', got 'ok'
FAIL
exit status 1
FAIL quicknotes 2.555s

## Fix Commit

test(lab3): revert broken test to pass
Commit e110f46

## Branch Protection Configuration

![Screenshot1](./chrome_Tf9nq8IDne.png)
![Screenshot2](./uD3wPHcsQy.png)

## Design Questions (1.2)

### Why pin the runner version (ubuntu-24.04) instead of ubuntu-latest?

Pinning the runner version ensures reproducible builds. ubuntu-latest changes over time (e.g., from 22.04 to 24.04), which can introduce breaking changes in system libraries, tools, or Go version behavior. This can cause builds that passed yesterday to fail today without any code change, leading to non-reproducible CI results. Using a fixed version guarantees that the CI environment remains consistent over time.

### Why split vet + test + lint into separate units?

Splitting into separate jobs provides better visibility and faster feedback:

If all three were in one job and vet failed, test and lint wouldn't run, hiding additional failures

With separate jobs, all checks run in parallel, and you can see exactly which check failed

It enables retrying only the failed job instead of the entire pipeline

It makes the PR status page clearer: each job shows its own status independently

### What real attack does SHA pinning prevent? (GitHub path)

SHA pinning prevents supply chain attacks where a malicious actor compromises a GitHub Action repository and pushes a malicious update to a tag (e.g., v4.2.2).

Real incident: In October 2022, the reviewdog/action-... repository was compromised, demonstrating how compromised actions could steal secrets. The attacker injected malicious code into a tag that many projects used, potentially exposing CI/CD secrets.

SHA pinning ensures you run exactly the code you reviewed, not a potentially malicious update pushed to a tag after your review. It provides cryptographic guarantee that the action code hasn't changed.

### What is permissions: and what's the principle behind it?

permissions: defines which GitHub API scopes the workflow is allowed to use. It restricts what the workflow can do on the repository.

The principle is least privilege — grant only the minimum permissions required for the job to function. For a CI pipeline:

contents: read is needed to read the repository code

No write permissions are needed

Why it matters: If the workflow is compromised or a malicious dependency is introduced, limited permissions prevent attackers from accessing repository secrets, modifying code, opening PRs, or pushing changes. This limits the blast radius of potential attacks.

### What's the difference between a stage and a job? (GitLab path — N/A for GitHub)

This question applies to GitLab CI, which I did not use in this lab.
