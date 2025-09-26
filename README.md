# Blockchain-based Student Certificate Verification (Demo)

This is a small educational project that simulates a tamper-proof certificate registry using a toy Python blockchain.

## Files
- `blockchain.py` - core in-memory blockchain & certificate logic
- `utils.py` - small helper utilities
- `app.py` - Streamlit app to interact with the chain (issue, verify, revoke, explorer)
- `requirements.txt` - minimal deps

## How to run locally
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Notes
- This is a demo: the blockchain is a simple in-memory Python structure (NOT a real distributed ledger).
- In production you'd replace the storage with a real blockchain (Ethereum/Hyperledger) and use proper private key management.

