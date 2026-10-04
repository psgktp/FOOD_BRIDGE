import io
import base64
import qrcode

def generate_qr_base64(payload_text: str) -> str:
    """
    Generates a Base64-encoded PNG data URI for embedding directly in HTML <img> tags.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(payload_text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#1e293b", back_color="#ffffff")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    b64_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return f"data:image/png;base64,{b64_str}"


def build_pickup_qr_payload(donation, donor_user) -> str:
    """
    Generates verification payload for Donor -> Volunteer/NGO pickup handshake.
    """
    return f"FOODBRIDGE-PICKUP:DONATION_ID={donation.id}:TOKEN={donation.qr_secret_token}:OTP={donation.donor_pickup_code}"


def build_delivery_qr_payload(allocation, org_user) -> str:
    """
    Generates verification payload for Volunteer -> NGO delivery handshake.
    """
    return f"FOODBRIDGE-DELIVER:ALLOC_ID={allocation.id}:ORG_ID={org_user.id}:OTP={allocation.donation.ngo_delivery_code}"
