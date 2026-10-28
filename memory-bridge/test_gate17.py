"""Gate17 independent Hallway Stochieon receiver: no network or fake receipts."""
import copy
import hashlib
import json
import sys
import tempfile
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import stochieon_receiver as r

STAMP="2026-10-27T23:40:00.000Z"
ANCHOR="9368d3921ec95ad4c1ba02ce79f4bdde89516a1449d69a8f81dfbc1fa3e53780"
CORPUS="f3b41c27321a98f5059c1affc846fcb0ff9b7b4acc0c89c437252dacb29aab57"

def manifest():
    return {"schema":"root0.stochieon.kernel/17","name":"stochieon",
            "contract":{"constant":"cubit","watermark":".dlw","quorum":None},
            "endpoints":[{"id":"top","kind":"git_file","expected_git_blob":"a"*40,"required":True}]}

def build(seq,kind,rows,m):
    ob={"result":"MATCH","time_quality":"UNSIGNED_HTTP_DATE_NOT_TRUSTED_TSA",
        "sent_utc":STAMP,"received_utc":STAMP,"content_sha256":"b"*64,
        "git_blob_sha":"a"*40} if kind=="OBSERVE" else None
    coverage=[{"node_id":"top","observation_seq":rows[0]["seq"],
        "observation_hash":rows[0]["hash"]}] if kind=="SEAL" else None
    root=r.digest({"scope":"stochieon-v17","coverage":coverage,"manifest":r.digest(m),
                    "loom_tip":ANCHOR,"corpus_tip":CORPUS}) if kind=="SEAL" else None
    rec={"receiver":"DavidWise01/0root","source_seq":1,
         "source_hash":ANCHOR,"receipt_sha256":"c"*64} if kind=="SEAL" else None
    body={"version":17,"seq":seq,"kind":kind,"recorded_at":STAMP,
          "witness":"A","actor_id":"148925959","node_id":"top" if kind=="OBSERVE" else None,
          "manifest_sha256":r.digest(m),"loom_tip":ANCHOR,"corpus_tip":CORPUS,
          "observation":ob,"coverage":coverage,"seal_root":root,"hallway_receipt":rec,
          "prev":rows[-1]["hash"] if rows else "GENESIS"}
    mark=".dlw:"+hashlib.sha256(r.DOMAIN.encode()+r.canon(body)).hexdigest()
    return {**body,"watermark":mark,"hash":r.digest({**body,"watermark":mark})}

def packet(e,pin):
    body={"schema":"root0.stochieon-receipt/17","receiver":"DavidWise01/0root",
          "accepted_at":STAMP,"manifest_pin":pin,
          "seal":e,"trusted_tsa_timestamp":False}
    return {**body,"receipt_watermark":".dlw:"+hashlib.sha256(
        b"ROOT0-STOCHIEON-RECEIVER-v1\n"+r.canon(body)).hexdigest()}

class IndependentGate17(unittest.TestCase):
    def setUp(self):
        self.m=manifest()
        self.a=build(1,"OBSERVE",[],self.m)
        self.seal=build(2,"SEAL",[self.a],self.m)
        self.trust=r.pinned()

    def test_empty_genesis_no_work_claims(self):
        self.assertEqual(r.verify([],self.m,self.trust),"GENESIS")
        self.assertEqual(r.check_prefix([],[])["independent_seals"],0)

    def test_complete_synthetic_seal_still_not_a_real_timestamp(self):
        self.assertEqual(r.verify([self.a,self.seal],self.m,self.trust),self.seal["hash"])
        self.assertFalse(packet(self.seal,self.trust["source_manifest"]["git_blob_sha"])["trusted_tsa_timestamp"])

    def test_source_rollback_detected(self):
        with self.assertRaisesRegex(ValueError,"SOURCE ROLLBACK"):
            r.check_prefix([], [{"seal":self.seal}])

    def test_source_fork_detected_even_if_sha_changed_validly(self):
        replacement=copy.deepcopy(self.seal)
        replacement["what"]="contradiction"
        with self.assertRaisesRegex(ValueError,"SOURCE DIVERGENCE"):
            r.check_prefix([self.a,replacement],[{"seal":self.seal}])

    def test_duplicate_hallway_seal_never_counts_as_two(self):
        with self.assertRaisesRegex(ValueError,"Duplicate independent"):
            r.check_prefix([self.a,self.seal],[{"seal":self.seal},{"seal":self.seal}])

    def test_missing_required_coverage_halts(self):
        with self.assertRaisesRegex(ValueError,"UNOBSERVED"):
            r.verify([self.seal],self.m,self.trust)

    def test_modified_dlw_digest_refused(self):
        tampered={**self.a,"watermark":".dlw:"+"0"*64}
        with self.assertRaisesRegex(ValueError,"SHA/.dlw"):
            r.verify([tampered],self.m,self.trust)

    def test_local_receipt_filename_and_watermark(self):
        prior=r.RECEIPTS
        with tempfile.TemporaryDirectory() as td:
            try:
                r.RECEIPTS=Path(td)
                p=packet(self.seal,self.trust["source_manifest"]["git_blob_sha"])
                f=Path(td)/(self.seal["hash"]+".json")
                f.write_text(json.dumps(p),encoding="utf-8")
                self.assertEqual(len(r.local()),1)
                f.rename(Path(td)/("f"*64+".json"))
                with self.assertRaisesRegex(ValueError,"receipt file"):
                    r.local()
            finally:r.RECEIPTS=prior

    def test_time_header_never_counted_as_tsa(self):
        altered=copy.deepcopy(self.a)
        altered["observation"]["time_quality"]="SIGNED_TSA"
        with self.assertRaisesRegex(ValueError,"Time evidence"):
            r.verify([altered],self.m,self.trust)

if __name__=="__main__":unittest.main()
