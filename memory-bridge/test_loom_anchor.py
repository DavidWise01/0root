"""Hallway Gate14: independent causal loom verifier and immutable anchor receipts."""
import json
import sys
import tempfile
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import loom_anchor as loom

TIME="2026-10-27T20:00:00.000Z"
def event(rows,kind="OPEN",thread="cortex",witness="A",phase="PAST_OBSERVES",text="cubit",
          refs=None,event_on="2026-10-27"):
    current=[e for e in rows if e["thread"]==thread]
    mine=[e for e in current if e["witness"]==witness]
    body={"version":14,"seq":len(rows)+1,"kind":kind,"recorded_at":TIME,
          "event_on":event_on,"thread":thread,"witness":witness,"phase":phase,
          "what":"Observed a source","how":"Independent observer","why":"Audit",
          "text":text,"refs":refs or [],"source":None,"corpus_tip":"a"*64,
          "thread_prev":current[-1]["seq"] if current and kind!="OPEN" else None,
          "witness_prev":mine[-1]["seq"] if mine and kind!="OPEN" else None,
          "mode":kind.lower() if kind in ("COPY","DISTILL") else None,
          "prev":rows[-1]["hash"] if rows else "GENESIS"}
    m=loom.mark(body);record={**body,"watermark":m,"hash":loom.digest({**body,"watermark":m})}
    loom.verify([*rows,record])
    return record

class IndependentLoomTests(unittest.TestCase):
    def test_empty_root_means_no_fake_events(self):
        self.assertEqual(loom.verify([]),"GENESIS")
        # This fixture must stay valid after the first real Hallway receipt.
        # Never assume the production receipt directory remains empty.
        previous=loom.INBOX
        with tempfile.TemporaryDirectory() as tmp:
            try:
                loom.INBOX=Path(tmp)
                self.assertEqual(loom.local(),[])
            finally:
                loom.INBOX=previous

    def test_source_hash_and_dlw_replay(self):
        first=event([])
        self.assertEqual(loom.verify([first]),first["hash"])
        self.assertTrue(first["watermark"].startswith(".dlw:"))

    def test_three_witness_lanes_continue_without_quorum(self):
        rows=[event([])]
        rows.append(event(rows,kind="WEAVE",witness="B",text="B observed"))
        rows.append(event(rows,kind="WEAVE",witness="C",text="C observed"))
        self.assertEqual(loom.verify(rows),rows[-1]["hash"])

    def test_link_two_threads_then_distill_exact_cubit(self):
        rows=[event([])]
        rows.append(event(rows,kind="OPEN",thread="tessy",text="cubit cubit"))
        rows.append(event(rows,kind="LINK",thread="cortex",refs=[2],text="thread stitch"))
        rows.append(event(rows,kind="DISTILL",thread="cortex",refs=[1,2],text="cubit"))
        self.assertEqual(loom.verify(rows),rows[-1]["hash"])

    def test_bad_cubit_rewrite_and_mutated_witness_fail(self):
        rows=[event([])]
        with self.assertRaises(ValueError):
            event(rows,kind="DISTILL",refs=[1],text="qubit")
        bad=dict(rows[0],witness="B")
        with self.assertRaisesRegex(ValueError,"watermark"):
            loom.verify([bad])

    def test_closing_A_does_not_close_B(self):
        rows=[event([])]
        rows.append(event(rows,kind="CLOSE",text="closed"))
        rows.append(event(rows,kind="WEAVE",witness="B",text="B active"))
        self.assertEqual(loom.verify(rows),rows[-1]["hash"])
        with self.assertRaisesRegex(ValueError,"closed"):
            event(rows,kind="WEAVE",witness="A",text="forbidden")

    def test_immutable_receipt_filename(self):
        first=event([])
        anchored={"schema":"root0.loom-anchor/14","receiver":"DavidWise01/0root",
                  "accepted_at":TIME,"event":first}
        old=loom.INBOX
        with tempfile.TemporaryDirectory() as tmp:
            try:
                loom.INBOX=Path(tmp)
                file=Path(tmp)/(first["hash"]+".json")
                file.write_text(json.dumps(anchored),encoding="utf-8")
                self.assertEqual(len(loom.local()),1)
                file.rename(Path(tmp)/("f"*64+".json"))
                with self.assertRaisesRegex(ValueError,"filename"):
                    loom.local()
            finally:loom.INBOX=old

if __name__=="__main__":unittest.main()
