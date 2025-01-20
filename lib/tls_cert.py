import trustme

def generate_tls_certificate(addr:str, name:str)->None:
    ca = trustme.CA()

    # And now you issued a cert signed by this fake CA
    # https://en.wikipedia.org/wiki/Example.org
    server_cert = ca.issue_cert(addr)

    # Save the PEM-encoded data to a file to use in non-Python test
    # suites:
    ca.cert_pem.write_to_path(f"lib/cert/{name}_ca.pem")
    
    #server_cert.private_key_and_cert_chain_pem.write_to_path(f"lib/cert/{name}_cert.pem")
    server_cert.cert_chain_pems[0].write_to_path(f"lib/cert/{name}_cert.pem")
    server_cert.private_key_pem.write_to_path(f"lib/cert/{name}_key.pem")
