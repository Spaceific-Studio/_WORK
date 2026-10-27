from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


OUTPUT_DIR = Path(r"C:\DmsVenv\cert")
PRIVATE_KEY_FILE = OUTPUT_DIR / "graph-certificate.pem"
PUBLIC_CERTIFICATE_FILE = OUTPUT_DIR / "graph-certificate.cer"


OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

subject = issuer = x509.Name(
    [
        x509.NameAttribute(
            NameOID.COMMON_NAME,
            "PVS HomeOffice Automation",
        ),
        x509.NameAttribute(
            NameOID.ORGANIZATION_NAME,
            "PVS",
        ),
    ]
)

now = datetime.now(timezone.utc)

certificate = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(issuer)
    .public_key(private_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(now - timedelta(minutes=5))
    .not_valid_after(now + timedelta(days=730))
    .add_extension(
        x509.BasicConstraints(ca=False, path_length=None),
        critical=True,
    )
    .sign(private_key, hashes.SHA256())
)

PRIVATE_KEY_FILE.write_bytes(
    private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
)

PUBLIC_CERTIFICATE_FILE.write_bytes(
    certificate.public_bytes(serialization.Encoding.DER)
)

thumbprint = certificate.fingerprint(hashes.SHA1()).hex().upper()

print(f"Privátní klíč: {PRIVATE_KEY_FILE}")
print(f"Veřejný certifikát: {PUBLIC_CERTIFICATE_FILE}")
print(f"Otisk SHA-1: {thumbprint}")