# app.py
import streamlit as st
import time
from blockchain import CertificateBlockchain
from utils import pretty

st.set_page_config(page_title='🎓 Student Certificate Blockchain', layout='wide')
st.title('🎓 Blockchain-based Student Certificate Verification (Demo)')

# Initialize blockchain in session state
if 'cert_chain' not in st.session_state:
    st.session_state.cert_chain = CertificateBlockchain()

chain: CertificateBlockchain = st.session_state.cert_chain

# Top metrics
col1, col2, col3 = st.columns(3)
col1.metric('Blocks', len(chain.chain))
col2.metric('Pending certificates', len(chain.pending_certificates))
col3.metric('Chain valid?', '✅' if chain.is_chain_valid() else '❌')

st.markdown('---')

tabs = st.tabs(['Issue Certificate', 'Verify Certificate', 'Revoke (Admin)', 'Explorer'])

# Issue
with tabs[0]:
    st.header('📝 Issue a Certificate')
    with st.form('issue_form', clear_on_submit=True):
        student_name = st.text_input('Student name')
        course = st.text_input('Course / Program')
        issuer = st.text_input('Issuer (university / dept)')
        metadata = st.text_area('Metadata (optional): e.g., grade, remarks, link to IPFS)')
        submit = st.form_submit_button('Issue certificate (adds to pending and mines block)')
        if submit:
            if not (student_name and course and issuer):
                st.error('Provide student name, course and issuer.')
            else:
                cert_id = chain.issue_certificate(student_name, course, issuer, metadata)
                # mine a new block (simple demo: immediate mining)
                block = chain.new_block(proof=123)
                st.success(f'Certificate issued with ID: **{cert_id}**')
                st.info(f'Recorded in Block {block["index"]} at {time.ctime(block["timestamp"]) }')
                st.write('Certificate object:')
                st.code(pretty(chain.find_certificate(cert_id)))

# Verify
with tabs[1]:
    st.header('🔍 Verify a Certificate')
    cert_input = st.text_input('Enter full certificate ID (sha256 hex)')
    name_input = st.text_input('OR search by student name (exact match)')
    if st.button('Verify by ID'):
        if not cert_input:
            st.error('Provide a certificate ID.')
        else:
            cert = chain.find_certificate(cert_input.strip())
            if cert:
                if cert.get('revoked'):
                    st.error('Certificate found BUT it is revoked.')
                else:
                    st.success('Certificate is VALID.')
                st.json(cert)
            else:
                st.error('Certificate ID not found on-chain.')
    if st.button('Search by student name'):
        if not name_input:
            st.error('Provide a student name.')
        else:
            results = chain.find_by_student(name_input.strip())
            if results:
                st.success(f'Found {len(results)} certificate(s) for "{name_input}".')
                st.json(results)
            else:
                st.warning('No certificates found for that student.')

# Revoke (admin)
with tabs[2]:
    st.header('⚠️ Revoke Certificate (Admin Demo)')
    revoke_id = st.text_input('Certificate ID to revoke')
    if st.button('Revoke certificate'):
        if not revoke_id:
            st.error('Provide cert ID to revoke.')
        else:
            ok = chain.revoke_certificate(revoke_id.strip())
            if ok:
                st.success('Certificate revoked. Block hashes updated (simulation).')
            else:
                st.error('Certificate not found in mined blocks.')

# Explorer
with tabs[3]:
    st.header('🔗 Blockchain Explorer (blocks newest → oldest)')
    for block in reversed(chain.chain):
        with st.expander(f"Block {block['index']} — {time.ctime(block['timestamp'])}"):
            st.write('Previous hash:', block.get('previous_hash'))
            st.write('Hash:', block.get('hash'))
            st.write('Proof:', block.get('proof'))
            st.subheader('Certificates in this block')
            st.json(block.get('certificates', []))
