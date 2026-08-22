import re


# ==================================================
# PHONE VALIDATION
# ==================================================

def validate_phone(phone):

    if not phone:
        return True

    return bool(
        re.fullmatch(
            r"\d{10}",
            phone.strip()
        )
    )


# ==================================================
# PINCODE VALIDATION
# ==================================================

def validate_pincode(pincode):

    if not pincode:
        return True

    return bool(
        re.fullmatch(
            r"\d{6}",
            pincode.strip()
        )
    )


# ==================================================
# PAN VALIDATION
# ==================================================

def validate_pan(pan):

    if not pan:
        return True

    return bool(
        re.fullmatch(
            r"[A-Z]{5}[0-9]{4}[A-Z]{1}",
            pan.strip().upper()
        )
    )


# ==================================================
# GSTIN VALIDATION
# ==================================================

def validate_gstin(gstin):

    if not gstin:
        return True

    return bool(
        re.fullmatch(
            r"\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z0-9]{3}",
            gstin.strip().upper()
        )
    )