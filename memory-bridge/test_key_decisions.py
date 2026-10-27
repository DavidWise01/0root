"""Hallway independent key-block decision and historical pin tests."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import key_decisions as d
import checkpoint_receiver as rec

def fixture():
    key="a"*64
    pins={key:{"key_id":key,"witness":"A","github_actor_id":"148925959",
               "public_key_b64":""}}
    return key,pins

class IndependentBlock(unittest.TestCase):
    def test_empty_history_valid(self):
        self.assertEqual(d.replay([],{}),set())
        self.assertEqual(d.read(d.LEDGER,{}),[])

    def test_append_only_irreversible_block(self):
        kid,pins=fixture()
        body={"version":1,"seq":1,"kind":"BLOCK","recorded_at":"2026-10-27",
              "key_id":kid,"witness":"A","github_actor_id":"148925959",
              "reason":"key lost","prev":"GENESIS"}
        e={**body,"hash":rec.sha(body)}
        self.assertEqual(d.replay([e],pins),{kid})
        with self.assertRaisesRegex(ValueError,"already blocked"):
            d.replay([e,{**e,"seq":2,"prev":e["hash"]}],pins)

    def test_tamper_rejected(self):
        kid,pins=fixture()
        body={"version":1,"seq":1,"kind":"BLOCK","recorded_at":"2026-10-27",
              "key_id":kid,"witness":"A","github_actor_id":"148925959",
              "reason":"incident","prev":"GENESIS"}
        e={**body,"hash":rec.sha(body)}
        with self.assertRaisesRegex(ValueError,"SHA mismatch"):
            d.replay([{**e,"reason":"tampered"}],pins)

    def test_unpinned_never_disabled_by_fake_event(self):
        kid,pins=fixture()
        body={"version":1,"seq":1,"kind":"BLOCK","recorded_at":"2026-10-27",
              "key_id":kid,"witness":"A","github_actor_id":"148925959",
              "reason":"incident","prev":"GENESIS"}
        with self.assertRaisesRegex(ValueError,"unpinned"):
            d.replay([{**body,"hash":rec.sha(body)}],{})

if __name__=="__main__":unittest.main()
