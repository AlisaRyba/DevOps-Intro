#!/usr/bin/env python3
"""Trigger one Render deploy without printing the secret URL."""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request


class NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def build_url(hook, image):
    parsed = urllib.parse.urlsplit(hook)
    if (
        parsed.scheme != "https"
        or parsed.hostname != "api.render.com"
        or parsed.port not in (None, 443)
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or not re.fullmatch(r"/deploy/srv-[A-Za-z0-9]+", parsed.path)
    ):
        raise ValueError("Invalid Render deploy hook; expected the HTTPS api.render.com hook.")
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    if not any(key == "key" and value for key, value in query):
        raise ValueError("Render deploy hook has no key.")
    if not re.fullmatch(
        r"ghcr\.io/[a-z0-9][a-z0-9._/-]*/quicknotes"
        r"(?:@sha256:[0-9a-f]{64}|:v[0-9]+\.[0-9]+\.[0-9]+)",
        image,
    ):
        raise ValueError("Expected a versioned GHCR QuickNotes image or SHA-256 digest.")
    query = [(key, value) for key, value in query if key != "imgURL"]
    query.append(("imgURL", image))
    return urllib.parse.urlunsplit(parsed._replace(query=urllib.parse.urlencode(query)))


def main():
    if len(sys.argv) != 2:
        print("Usage: deploy_render.py IMAGE_URL", file=sys.stderr)
        return 2
    try:
        url = build_url(os.environ.get("RENDER_DEPLOY_HOOK_URL", ""), sys.argv[1])
        opener = urllib.request.build_opener(NoRedirects())
        request = urllib.request.Request(url, data=b"", method="POST")
        with opener.open(request, timeout=30) as response:
            status = response.status
            payload = response.read(65536)
        if status not in (200, 202):
            print("Unexpected Render response status.", file=sys.stderr)
            return 1
    except (ValueError, urllib.error.URLError, TimeoutError, OSError):
        # HTTP errors may contain the secret query; never print the exception.
        print("Render hook failed. Check the secret/service and Render dashboard; URL suppressed.", file=sys.stderr)
        return 1
    print(f"Render accepted the deploy request (HTTP {status}); this is not a readiness check.")
    try:
        deployment_id = json.loads(payload).get("deploy", {}).get("id", "")
        if isinstance(deployment_id, str) and re.fullmatch(r"dep-[A-Za-z0-9]+", deployment_id):
            print(f"Deploy ID: {deployment_id}")
    except (ValueError, AttributeError):
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
