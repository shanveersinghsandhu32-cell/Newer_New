# blockchain.py
# Simple in-memory blockchain for student certificates.
import hashlib
import json
import time
from typing import List, Dict, Any, Optional

class CertificateBlockchain:
    """A minimal toy blockchain to demonstrate tamper-proof certificate storage.
    NOTE: This is an educational simulation and NOT a production blockchain.
    """
    def __init__(self):
        self.chain: List[Dict[str, Any]] = []
        self.pending_certificates: List[Dict[str, Any]] = []
        # genesis block
        self.new_block(proof=100, previous_hash='1')

    def new_block(self, proof: int, previous_hash: Optional[str] = None) -> Dict[str, Any]:
        """Create a new Block and add pending certificates to it."""
        block_certs = [c.copy() for c in self.pending_certificates]
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'certificates': block_certs,
            'proof': proof,
            'previous_hash': previous_hash or (self.chain[-1]['hash'] if self.chain else '1')
        }
        # compute and assign hash (excluding 'hash' key)
        block['hash'] = self.hash(block)
        # reset pending and append
        self.pending_certificates = []
        self.chain.append(block)
        return block

    def issue_certificate(self, student_name: str, course: str, issuer: str, metadata: str = '') -> str:
        """Create a certificate entry and add to pending list.
        Returns the certificate id (sha256 hex).
        """
        payload = f"{student_name}|{course}|{issuer}|{time.time()}|{metadata}"
        cert_id = hashlib.sha256(payload.encode()).hexdigest()
        cert = {
            'cert_id': cert_id,
            'student_name': student_name,
            'course': course,
            'issuer': issuer,
            'metadata': metadata,
            'issued_at': time.time(),
            'revoked': False
        }
        self.pending_certificates.append(cert)
        return cert_id

    @staticmethod
    def hash(block: Dict[str, Any]) -> str:
        """Hashes a block using SHA-256 (excluding the block's own 'hash')."""
        block_copy = block.copy()
        block_copy.pop('hash', None)
        block_string = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self) -> Dict[str, Any]:
        return self.chain[-1]

    def is_chain_valid(self) -> bool:
        """Simple integrity check over the chain."""
        for i in range(1, len(self.chain)):
            prev = self.chain[i-1]
            curr = self.chain[i]
            if curr['previous_hash'] != prev['hash']:
                return False
            if curr['hash'] != self.hash(curr):
                return False
        return True

    def find_certificate(self, cert_id: str) -> Optional[Dict[str, Any]]:
        """Search for a certificate by cert_id across all blocks."""
        for block in self.chain:
            for cert in block.get('certificates', []):
                if cert.get('cert_id') == cert_id:
                    return cert.copy()
        # also check pending list
        for cert in self.pending_certificates:
            if cert.get('cert_id') == cert_id:
                return cert.copy()
        return None

    def find_by_student(self, student_name: str) -> List[Dict[str, Any]]:
        """Return all certificates matching a student name (case-insensitive)."""
        results = []
        name_low = student_name.strip().lower()
        for block in self.chain:
            for cert in block.get('certificates', []):
                if cert.get('student_name','').strip().lower() == name_low:
                    results.append(cert.copy())
        for cert in self.pending_certificates:
            if cert.get('student_name','').strip().lower() == name_low:
                results.append(cert.copy())
        return results

    def revoke_certificate(self, cert_id: str) -> bool:
        """Mark a certificate as revoked if found in chain (not pending)."""
        for block in self.chain:
            for cert in block.get('certificates', []):
                if cert.get('cert_id') == cert_id:
                    cert['revoked'] = True
                    # update block hash because content changed
                    block['hash'] = self.hash(block)
                    return True
        return False
