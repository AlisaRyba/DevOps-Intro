"""Offline helper tests. No deployment and no network requests."""
import contextlib
import io
import json
import os
import unittest
import urllib.error
import urllib.parse
from unittest import mock

import deploy_render
import measure


class DeployTests(unittest.TestCase):
    def setUp(self):
        self.hook = "https://api.render.com/deploy/srv-example123?key=DO_NOT_PRINT"
        self.image = "ghcr.io/alisaryba/devops-intro/quicknotes@sha256:" + "a" * 64

    def test_digest_is_encoded_once(self):
        built = deploy_render.build_url(self.hook, self.image)
        parsed = urllib.parse.urlsplit(built)
        query = urllib.parse.parse_qs(parsed.query)
        self.assertEqual(query["imgURL"], [self.image])
        self.assertEqual(query["key"], ["DO_NOT_PRINT"])
        self.assertIn("%2F", parsed.query)
        self.assertIn("%3A", parsed.query)

    def test_replaces_previous_image_parameter(self):
        built = deploy_render.build_url(self.hook + "&imgURL=old", self.image)
        self.assertEqual(urllib.parse.parse_qs(urllib.parse.urlsplit(built).query)["imgURL"], [self.image])

    def test_invalid_destinations_rejected(self):
        for hook in [
            "http://api.render.com/deploy/srv-example?key=secret",
            "https://api.render.com.evil.test/deploy/srv-example?key=secret",
            "https://user:secret@api.render.com/deploy/srv-example?key=secret",
            "https://api.render.com/deploy/srv-example",
            "https://api.render.com/deploy/srv-example?key=secret#fragment",
        ]:
            with self.subTest(hook=hook), self.assertRaises(ValueError):
                deploy_render.build_url(hook, self.image)

    def test_unversioned_image_rejected(self):
        with self.assertRaises(ValueError):
            deploy_render.build_url(self.hook, "ghcr.io/alisaryba/devops-intro/quicknotes:latest")

    def test_redirects_disabled(self):
        self.assertIsNone(deploy_render.NoRedirects().redirect_request(None, None, 302, "", {}, "https://elsewhere.test"))

    def test_error_does_not_reveal_hook(self):
        error = urllib.error.URLError(self.hook)
        buffer = io.StringIO()
        with mock.patch.dict(os.environ, {"RENDER_DEPLOY_HOOK_URL": self.hook}), \
                mock.patch("sys.argv", ["deploy_render.py", self.image]), \
                mock.patch("urllib.request.OpenerDirector.open", side_effect=error), \
                contextlib.redirect_stderr(buffer):
            self.assertEqual(deploy_render.main(), 1)
        self.assertNotIn("DO_NOT_PRINT", buffer.getvalue())
        self.assertNotIn("api.render.com", buffer.getvalue())

    def test_success_means_accepted_not_ready(self):
        response = mock.MagicMock()
        response.__enter__.return_value = response
        response.status = 202
        response.read.return_value = b"{}"
        buffer = io.StringIO()
        with mock.patch.dict(os.environ, {"RENDER_DEPLOY_HOOK_URL": self.hook}), \
                mock.patch("sys.argv", ["deploy_render.py", self.image]), \
                mock.patch("urllib.request.OpenerDirector.open", return_value=response), \
                contextlib.redirect_stdout(buffer):
            self.assertEqual(deploy_render.main(), 0)
        self.assertIn("not a readiness check", buffer.getvalue())


class MeasurementTests(unittest.TestCase):
    def test_percentile(self):
        self.assertEqual(measure.percentile([5, 1, 3, 2, 4], 0.5), 3)
        self.assertAlmostEqual(measure.percentile([1, 2, 3, 4, 5], 0.95), 4.8)
        self.assertEqual(measure.percentile([4], 0.95), 4)

    def test_url_without_secret(self):
        self.assertEqual(measure.validate_base_url("https://app.onrender.com/"), "https://app.onrender.com")
        for url in ["ftp://host.test", "https://host.test?key=secret", "https://user:secret@host.test", "https://host.test/path"]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                measure.validate_base_url(url)

    def test_successful_sample(self):
        metadata = {
            "http_code": 200, "time_total": 1.2, "time_namelookup": 0.1,
            "time_connect": 0.2, "time_appconnect": 0.3,
            "time_starttransfer": 1.1, "remote_ip": "127.0.0.1",
        }
        result = mock.Mock(returncode=0, stdout='{"status":"ok"}\n' + json.dumps(metadata))
        with mock.patch("subprocess.run", return_value=result) as call:
            sample = measure.measure_one("https://app.onrender.com", 180)
        self.assertEqual(sample["time_total_seconds"], 1.2)
        self.assertEqual(call.call_args.args[0][-1], "https://app.onrender.com/health")

    def test_gateway_page_not_counted_as_health(self):
        result = mock.Mock(returncode=0, stdout='Waking up\n{"http_code":200}')
        with mock.patch("subprocess.run", return_value=result), self.assertRaises(RuntimeError):
            measure.measure_one("https://app.onrender.com", 180)

    def test_curl_failure_not_counted(self):
        result = mock.Mock(returncode=28, stdout="")
        with mock.patch("subprocess.run", return_value=result), self.assertRaises(RuntimeError):
            measure.measure_one("https://app.onrender.com", 180)


if __name__ == "__main__":
    unittest.main()
