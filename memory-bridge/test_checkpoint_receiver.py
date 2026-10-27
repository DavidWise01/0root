"""Offline independent Hallway pin and checkpoint receipt verification."""
import base64
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
import checkpoint_receiver as recv

def fixture():
    secret=Ed25519PrivateKey.generate()
    pub=secret.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
    kid=hashlib.sha256(pub).hexdigest()
    pin={"witness":"A","github_actor_id":"148925959","key_id":kid,"public_key_b64":base64.b64encode(pub).decode()}
    state={k:{"count":0,"tip":"GENESIS"} for k in recv.STREAMS}
    body={"version":1,"seq":1,"kind":"CHECKPOINT","recorded_at":"2026-10-27",
          "witness":"A","github_actor":"DavidWise01","github_actor_id":"148925959",
          "key_id":kid,"state":state,"prev":"GENESIS",
          "payload_sha256":"","signature_b64":""}
    payload=recv.message(body)
    body["payload_sha256"]=hashlib.sha256(payload).hexdigest()
    body["signature_b64"]=base64.b64encode(secret.sign(payload)).decode()
    body["hash"]=recv.sha(body)
    return secret,pin,body

class IndependentAnchorTests(unittest.TestCase):
    def test_empty_trust_has_no_fake_witnesses(self):
        self.assertEqual(recv.pins(),{})
        self.assertEqual(recv.anchored(),[])

    def test_trusted_ed25519_checkpoint(self):
        _,pin,record=fixture()
        recv.verify_record(record,{pin["key_id"]:pin})

    def test_reject_signature_from_untrusted_key(self):
        _,pin,record=fixture()
        with self.assertRaisesRegex(ValueError,"pinned"):
            recv.verify_record(record,{})
        wrong=dict(record,signature_b64=base64.b64encode(bytes(64)).decode())
        wrong["hash"]=recv.sha({k:v for k,v in wrong.items() if k!="hash"})
        with self.assertRaisesRegex(ValueError,"signature"):
            recv.verify_record(wrong,{pin["key_id"]:pin})

    def test_source_count_rollback_detection(self):
        _,pin,record=fixture()
        streams={k:[] for k in recv.STREAMS}
        recv.validate_checkpoint_chain([record],{pin["key_id"]:pin},streams)
        fake={"seq":1,"prev":"GENESIS","hash":"a"*64}
        streams["CORPUS"]=[fake]
        record["state"]["CORPUS"]={"count":1,"tip":"b"*64}
        with self.assertRaisesRegex(ValueError,"source-prefix"):
            recv.validate_checkpoint_chain([record],{pin["key_id"]:pin},streams)

    def test_filename_must_match_pinned_hash(self):
        _,pin,record=fixture()
        body={"schema":"root0.checkpoint-anchor/1","receiver":"DavidWise01/0root",
              "accepted_at":"2026-10-27","checkpoint":record}
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)
            (path/"not-the-hash.json").write_text(json.dumps(body))
            with self.assertRaisesRegex(ValueError,"filename"):
                recv.anchored(path,{pin["key_id"]:pin})

    def test_pins_reject_duplicate_actor_in_multiple_lanes(self):
        _,pin,_=fixture()
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"pins.json"
            alt={**pin,"witness":"B","key_id":pin["key_id"]}
            path.write_text(json.dumps({"schema":"root0.checkpoint-trust-pins/1",
                "receiver":"DavidWise01/0root","pins":[pin,alt]}))
            with self.assertRaises(ValueError):
                recv.pins(path)

if __name__=="__main__":unittest.main()
