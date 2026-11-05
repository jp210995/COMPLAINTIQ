from pathlib import Path

import boto3

# --------------------------------------------------
# AWS configuration
# --------------------------------------------------

REGION = "us-east-1"

_sts = boto3.client("sts", region_name=REGION)
ACCOUNT = _sts.get_caller_identity()["Account"]

BUCKET = f"sagemaker-complaintiq-{ACCOUNT}"

# --------------------------------------------------
# Project paths
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

DATA = ROOT / "data"
RAW = DATA / "raw"
PROC = DATA / "processed"

CFPB_RAW = RAW / "cfpb"
ECFR_RAW = RAW / "ecfr"
PDF_RAW = RAW / "pdf"

INDEX = ROOT / "index"
STATE = ROOT / "state"
REPORTS = ROOT / "reports"
LOGS = ROOT / "logs"

# --------------------------------------------------
# Create required directories
# --------------------------------------------------

for directory in [
    CFPB_RAW,
    ECFR_RAW,
    PDF_RAW,
    PROC,
    INDEX,
    STATE,
    REPORTS,
    LOGS,
]:
    directory.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# HTTP request headers
# --------------------------------------------------

UA = {
    "User-Agent": "ComplaintIQ-capstone/1.0 (joshua.paulv@ltm.com)"
}
