import unittest
from unittest.mock import Mock, patch

import httpx
from groq import RateLimitError

from utils import _groq_completion


class GroqRetryTests(unittest.TestCase):
    def test_rate_limit_uses_retry_after_header(self):
        request = httpx.Request("POST", "https://api.groq.com/test")
        response = httpx.Response(429, headers={"retry-after": "0.25"}, request=request)
        error = RateLimitError("rate limited", response=response, body=None)
        client = Mock()
        client.chat.completions.create.side_effect = [error, "completed"]

        with patch("utils.time.sleep") as sleep:
            result = _groq_completion(client, model="test")

        self.assertEqual(result, "completed")
        sleep.assert_called_once_with(0.75)


if __name__ == "__main__":
    unittest.main()
