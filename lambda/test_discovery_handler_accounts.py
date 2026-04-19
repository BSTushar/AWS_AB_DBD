import os
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import discovery_handler


class DiscoveryAccountResolutionTests(unittest.TestCase):
    @patch("discovery_handler.list_active_org_account_ids", return_value=["111111111111", "222222222222"])
    def test_org_mode_merges_manual_and_org_and_excludes(self, _org_ids):
        with patch.dict(
            os.environ,
            {
                "DISCOVER_ALL_ORG_ACCOUNTS": "true",
                "ORG_EXCLUDE_ACCOUNT_IDS": "222222222222",
                "SPOKE_ACCOUNTS": "333333333333",
            },
            clear=False,
        ):
            discovery_handler.DISCOVER_ALL_ORG_ACCOUNTS = True
            discovery_handler.SPOKE_ACCOUNTS = ["333333333333"]
            result = discovery_handler.resolve_accounts_to_scan()
            self.assertEqual(result, ["111111111111", "333333333333"])

    @patch("discovery_handler.list_active_org_account_ids", return_value=["111111111111"])
    def test_org_mode_falls_back_to_manual_if_org_call_errors(self, _org_ids):
        with patch("discovery_handler.list_active_org_account_ids", side_effect=Exception("org failed")):
            discovery_handler.DISCOVER_ALL_ORG_ACCOUNTS = True
            discovery_handler.SPOKE_ACCOUNTS = ["333333333333"]
            result = discovery_handler.resolve_accounts_to_scan()
            self.assertEqual(result, ["333333333333"])

    def test_manual_mode_exclude_filter(self):
        with patch.dict(
            os.environ,
            {"ORG_EXCLUDE_ACCOUNT_IDS": "222222222222"},
            clear=False,
        ):
            discovery_handler.DISCOVER_ALL_ORG_ACCOUNTS = False
            discovery_handler.SPOKE_ACCOUNTS = ["111111111111", "222222222222"]
            result = discovery_handler.resolve_accounts_to_scan()
            self.assertEqual(result, ["111111111111"])


if __name__ == "__main__":
    unittest.main()
