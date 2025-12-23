# Security

This document defines the security posture, TLS configuration, and certificate management practices for this MCP server.
It is aligned with MCP security best practices and is intended for both human readers and AI agents. TLS is recommended and should be enforced by a forwarding proxy (Nginx, Cloudflare, Pangolin, ContextForge, etc.) or configured directly on the MCP server when a proxy is not available.

---

## Scope

This document covers:

- HTTPS / TLS requirements
- Certificate management (self-signed and CA-issued)
- Certificate trust models
- Secure defaults
- Common TLS failure modes and troubleshooting

This document **does not** define application-level authentication or authorization logic.

---

## Security Principles

The MCP server follows these core security principles:

- **Encrypted transport is mandatory for exposed endpoints** — use a TLS-terminating forwarding proxy whenever possible. Direct TLS on the MCP server is supported for environments without a proxy, but plaintext should only be used on trusted, internal segments between the proxy and server.
- **TLS 1.2+ required** — TLS 1.3 preferred where available when you terminate TLS (proxy or service).
- **Least privilege** for keys and certificates.
- **Explicit trust** — clients must intentionally trust the server or proxy certificate.
- **Fail closed** — misconfigured TLS must prevent startup for directly terminated TLS; proxies should reject insecure configurations.

---

## TLS Requirements

### Protocol Versions

When terminating TLS on a forwarding proxy, configure the proxy to:

- Enable **TLS 1.2 and TLS 1.3**.
- Disable **TLS 1.0 and TLS 1.1**.

When terminating TLS directly on the MCP server, configure the server to:

- Enable **TLS 1.2 and TLS 1.3**.
- Disable **TLS 1.0 and TLS 1.1**.

### Cipher Suites

The TLS terminator (proxy or server) SHOULD:

- Prefer modern AEAD ciphers (e.g., ECDHE with AES-GCM or CHACHA20-POLY1305).
- Disable weak or legacy ciphers (e.g., RC4, 3DES, EXPORT ciphers).
- Use OS / runtime secure defaults unless there is a strong, documented reason to override them.

---

## Certificate Types

### Self-Signed Certificates

Self-signed certificates are supported for:

- Local development
- Test environments
- Internal or isolated networks where both server and client are under control

Self-signed certificates MUST NOT be used for public internet exposure or untrusted networks. If you use a forwarding proxy, terminate TLS on the proxy with the certificate type appropriate for the environment (self-signed for dev, CA-issued for production) and forward HTTP to the MCP server over a trusted segment.

### CA-Issued Certificates

CA-issued certificates are REQUIRED for:

- Public-facing endpoints
- Third-party clients
- Production environments

Use them on the TLS-terminating proxy or directly on the MCP server if you cannot front it with a proxy.

Supported certificate authorities include:

- Public CAs (e.g., Let’s Encrypt, DigiCert, GlobalSign)
- Internal / enterprise PKI
- Vault-based or similar PKI systems

---

## Implementing Self-Signed Certificates

### 1. Generate a Private Key

Generate a 4096-bit RSA private key:

    openssl genrsa -out server.key 4096

The file `server.key` MUST be kept secret and protected with strict file permissions.

### 2. (Optional) Generate a CSR

You may generate a CSR for consistency, even though it will be self-signed:

    openssl req -new -key server.key -out server.csr

At minimum, set the **Common Name (CN)** to the hostname clients will use (for example, `localhost` for local development).

### 3. Create a Certificate with SAN Support

Modern TLS clients require **Subject Alternative Name (SAN)**. Create a configuration file named `san.cnf` with contents:

    [req]
    distinguished_name=req
    x509_extensions=v3_req
    prompt=no

    [req_distinguished_name]
    CN=localhost

    [v3_req]
    keyUsage=keyEncipherment, dataEncipherment
    extendedKeyUsage=serverAuth
    subjectAltName=@alt_names

    [alt_names]
    DNS.1=localhost
    IP.1=127.0.0.1

Then generate the certificate:

    openssl x509 -req \
      -in server.csr \
      -signkey server.key \
      -out server.crt \
      -days 365 \
      -extensions v3_req \
      -extfile san.cnf

You now have:

- `server.key` — private key  
- `server.crt` — self-signed certificate including SANs

### 4. Client Trust for Self-Signed Certificates

Clients MUST explicitly trust the self-signed certificate. For command-line tools (example with curl):

    curl --cacert server.crt https://localhost:8443

For local development only, you MAY import `server.crt` into the OS trust store so that clients trust it automatically. This MUST NOT be done on production systems for self-signed certs.

---

## Implementing CA-Issued Certificates

### Public CA (Example: Let’s Encrypt)

Requirements:

- Public DNS record pointing to the server
- Valid domain name (e.g., `api.example.com`)
- Port 80 or 443 reachable from the internet

Example using Certbot (standalone mode):

    certbot certonly --standalone -d api.example.com

This typically generates:

- `fullchain.pem` — server certificate plus intermediate certificates
- `privkey.pem` — private key

The server SHOULD use the **full chain** file when configuring TLS.

### Internal / Enterprise PKI

If using an internal PKI (e.g., corporate CA):

1. Generate a private key:

       openssl genrsa -out server.key 4096

2. Generate a CSR:

       openssl req -new -key server.key -out server.csr

3. Submit `server.csr` to the internal CA following organizational procedures.
4. Receive:
   - `server.crt` — server certificate
   - One or more intermediate CA certificates

Concatenate the full chain:

    cat server.crt intermediate.crt > fullchain.crt

The server MUST present a full chain to clients to avoid trust errors.

---

## Server TLS Configuration

The server MUST load:

- A private key file
- A full certificate chain (leaf + intermediates)

Conceptual example in pseudocode:

    ssl_context = create_ssl_context()
    ssl_context.set_minimum_version(TLS_1_2)
    ssl_context.load_cert_chain(
        certfile="fullchain.crt",
        keyfile="server.key"
    )

The server MUST fail startup if:

- The private key file is missing or unreadable.
- The certificate file is missing or unreadable.
- The certificate and key do not match.
- The certificate chain is obviously invalid (parse errors, etc.).

Failing fast is preferred to running with an insecure or partial configuration.

---

## Key Management

- Private keys MUST NOT be committed to source control or shared over unsecured channels.
- Private key files MUST be protected with strict permissions, for example:

      chmod 600 server.key

- Keys and certificates SHOULD be rotated before expiration according to organizational policies.
- Expired certificates MUST NOT be used; the server SHOULD refuse to start with an expired certificate.

For highly sensitive environments, additional protections (e.g., hardware security modules, encrypted key stores) MAY be used.

---

## Certificate Validation Rules

Certificates used by this server MUST:

- Include **Subject Alternative Names (SAN)** for all expected hostnames and/or IPs.
- Have a **Common Name (CN)** and SAN values that match the hostname clients use.
- Present a **valid, complete chain** to a trusted root CA.

Hostname mismatches (for example, certificate issued for `api.example.com` but client connects to `server.example.com`) MUST be treated as fatal.

---

## Troubleshooting TLS and Certificate Issues

### Common Error: “certificate verify failed”

Typical causes:

- The client does not trust the issuing CA (missing root or intermediate).
- The server is not presenting the full certificate chain.
- A self-signed certificate is being used and not added to the client trust set.

Mitigations:

- Ensure the client’s trust store includes the relevant root and intermediate CAs.
- Ensure the server is configured with the full chain (leaf + intermediate certificates).
- For self-signed certs, explicitly provide the certificate to the client as a CA file.

---

### Common Error: “hostname mismatch”

Typical cause:

- The hostname in the URL does not match any CN or SAN entries in the certificate.

Mitigations:

- Regenerate the certificate with correct SAN values matching the hostname(s) actually used.
- Ensure the client uses the same hostname that the certificate was issued for.

---

### Common Error: “unable to get local issuer certificate”

Typical cause:

- The server is not sending intermediate CA certificates.

Mitigations:

- Use `fullchain.crt` (leaf + intermediates) rather than just the leaf certificate.
- Verify the chain with `openssl verify` (see below).

---

### Common Error: Permission or File Access Issues

Typical cause:

- The server process does not have read permission on the key or certificate files.

Mitigations:

- Apply strict but correct permissions, such as:

      chmod 600 server.key
      chown <server-user>:<server-group> server.key

- Ensure the files are located where the server expects them.

---

## Debugging Tools

### Inspect a Certificate

To inspect the contents of a certificate (issuer, subject, SANs, validity dates):

    openssl x509 -in server.crt -text -noout

### Verify a Certificate Chain

To verify a certificate chain against a CA bundle:

    openssl verify -CAfile ca.pem fullchain.crt

### Test a TLS Handshake

To test a handshake and see the certificate chain presented by the server:

    openssl s_client -connect localhost:8443 -servername localhost

Review:

- The protocol and cipher negotiated.
- The certificate chain as seen by the client.
- Any reported verification errors.

---

## MCP-Specific Considerations

- HTTPS is REQUIRED for any client-facing endpoint. You can satisfy this by terminating TLS on a forwarding proxy or by enabling TLS directly on the MCP server; plaintext should only be used on the trusted hop between proxy and server.
- TLS misconfiguration MUST prevent successful startup rather than allowing a downgraded or insecure mode when you terminate TLS directly on the service; proxies should likewise reject invalid TLS settings.
- The server does not make **implicit trust** assumptions; the client is responsible for deciding which CAs and certificates to trust.
- All MCP communication over the network that leaves the trusted segment is expected to occur over a secure TLS channel.

---

## Summary

- Use **self-signed certificates** only for local development and tightly controlled internal environments, and only when clients explicitly trust the certificate.
- Use **CA-issued certificates** (public or internal PKI) for all production and public-facing deployments.
- Always present a **full certificate chain**, not just the leaf certificate.
- Enforce **TLS 1.2+**, prefer TLS 1.3, and avoid weak ciphers.
- Treat TLS and certificate misconfiguration as **fatal**; fail closed rather than fallback.

---

## Non-Goals

This document does **not** cover:

- Authentication strategies (OAuth, API tokens, etc.).
- Authorization models or role-based access control.
- Rate limiting, auditing, or logging policies.
- Network-level firewall or micro-segmentation rules.

Those topics are addressed in separate documentation.
