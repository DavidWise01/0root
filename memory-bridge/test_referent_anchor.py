"""Gate13 Hallway independent hash watermark receipts (offline, no network)."""
import hashlib
import json
import sys
from pathlib import Path
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import referent_anchor as anchor

def sample():
    url="https://www.scientificamerican.com/article/openai-just-scooped-human-researchers-on-a-million-dollar-quantum-math-problem/"
    row={"version":1,"seq":1,"kind":"REGISTER","recorded_at":"2026-10-27T18:00:00.000Z",
        "witness":"A","github_actor_id":"148925959",
        "referent_id":hashlib.sha256(url.encode()).hexdigest(),"referent_uri":url,
        "basis":"REPORTED","what":"User-supplied public URL","how":"Recorded as reference",
        "why":"Provenance","claimed_author":None,"content_sha256":None,"source_seq":None,
        "sample":None,"prev":"GENESIS"}
    w=anchor.watermark(row)
    return {**row,"watermark":w,"hash":anchor.hashed({**row,"watermark":w})}

class IndependentReferent(unittest.TestCase):
    def test_valid_watermark(self):
        row=sample();anchor.verify_row(row)
        self.assertEqual(len(row["watermark"]),64)

    def test_dlw_v2_attribution_is_independently_verified(self):
        legacy=sample()
        core={k:v for k,v in legacy.items() if k not in ("hash","watermark")}
        core["version"]=2
        core["attribution"]=dict(anchor.ATTRIBUTION)
        mark=anchor.watermark(core)
        e={**core,"watermark":mark,"hash":anchor.hashed({**core,"watermark":mark})}
        self.assertEqual(mark[:5],".dlw:")
        self.assertEqual(len(mark),69)
        anchor.verify_row(e)
        tampered={**e,"attribution":{**e["attribution"],"third_party_ownership_claim":True}}
        with self.assertRaisesRegex(ValueError,"attribution"):
            anchor.verify_row(tampered)

    def test_mutated_claim_is_rejected(self):
        changed={**sample(),"why":"tampered"}
        with self.assertRaisesRegex(ValueError,"watermark"):
            anchor.verify_row(changed)

    def test_receipt_filename_preserves_event(self):
        e=sample()
        receipt={"schema":"root0.referent-anchor/1","receiver":"DavidWise01/0root",
                 "accepted_at":"2026-10-27T20:00:00Z","event":e}
        with tempfile.TemporaryDirectory() as d:
            before=anchor.INBOX
            try:
                anchor.INBOX=Path(d)
                (Path(d)/(e["hash"]+".json")).write_text(json.dumps(receipt))
                self.assertEqual(len(anchor.local()),1)
                (Path(d)/(e["hash"]+".json")).rename(Path(d)/("a"*64+".json"))
                with self.assertRaisesRegex(ValueError,"filename"):
                    anchor.local()
            finally:anchor.INBOX=before

    def test_chain_sha_is_distinct_from_watermark(self):
        e=sample();self.assertNotEqual(e["hash"],e["watermark"])
        self.assertEqual(anchor.hashed({k:v for k,v in e.items() if k!="hash"}),e["hash"])

if __name__=="__main__":unittest.main()
