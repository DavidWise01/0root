"""Gate16 independently preserved Hallway receipts expose source rollback.

All inputs synthetic in memory; tests never fetch GitHub or create receipts.
"""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import loom_anchor as receiver
from test_loom_anchor import event

def receipt(e):
    return {"schema":"root0.loom-anchor/14","receiver":"DavidWise01/0root",
            "accepted_at":"2026-10-27T23:00:00Z","event":e}

class PrefixAuditTests(unittest.TestCase):
    def setUp(self):
        self.first=event([])

    def test_empty_hallway_does_not_invent_anchors(self):
        status=receiver.verify_anchored_prefix([self.first],[])
        self.assertEqual(status["independent_receipts"],0)
        self.assertTrue(status["no_write"])
        self.assertTrue(status["no_quorum"])

    def test_matching_original_can_be_independently_verified(self):
        status=receiver.verify_anchored_prefix([self.first],[receipt(self.first)])
        self.assertEqual(status["independent_receipts"],1)
        self.assertEqual(status["first_anchored_seq"],1)
        self.assertEqual(status["latest_canonical_tip"],self.first["hash"])

    def test_new_source_events_do_not_invalidate_earlier_anchor(self):
        next_event=event([self.first],kind="WEAVE",text="memory cubit")
        status=receiver.verify_anchored_prefix(
            [self.first,next_event],[receipt(self.first)])
        self.assertEqual(status["canonical_events"],2)
        self.assertEqual(status["independent_receipts"],1)

    def test_source_rollback_below_anchored_sequence_halts(self):
        with self.assertRaisesRegex(ValueError,"SOURCE ROLLBACK"):
            receiver.verify_anchored_prefix([],[receipt(self.first)])

    def test_source_fork_with_recomputed_valid_hash_still_halts(self):
        fork=event([],text="changed observable memory")
        self.assertNotEqual(fork["hash"],self.first["hash"])
        with self.assertRaisesRegex(ValueError,"SOURCE DIVERGENCE"):
            receiver.verify_anchored_prefix([fork],[receipt(self.first)])

    def test_duplicate_receipts_do_not_count_as_two_witnesses(self):
        with self.assertRaisesRegex(ValueError,"Duplicate historical"):
            receiver.verify_anchored_prefix(
                [self.first],[receipt(self.first),receipt(self.first)])

    def test_partial_invalid_source_never_claims_complete_validation(self):
        wrong={**self.first,"what":"changed without watermark"}
        with self.assertRaisesRegex(ValueError,"watermark"):
            receiver.verify_anchored_prefix([wrong],[receipt(self.first)])

    def test_invalid_anchored_sequence_is_rejected(self):
        forged=receipt({**self.first,"seq":0})
        with self.assertRaisesRegex(ValueError,"Malformed historical"):
            receiver.verify_anchored_prefix([self.first],[forged])

if __name__=="__main__":unittest.main()
