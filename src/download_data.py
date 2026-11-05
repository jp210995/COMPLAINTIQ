from __future__ import annotations

import csv
import io
import re
import zipfile
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import urljoin

import requests

from src.config import ROOT, CFPB_RAW, UA

ARCHIVE_DIR = ROOT / "data" / "raw" / "cfpb_archive"
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

ARCHIVE_PAGE = (
    "https://www.consumerfinance.gov/foia-requests/"
    "foia-electronic-reading-room/"
    "cfpb-consumer-complaint-database-narratives-archive/"
)

EXPORTS = {
    "CCDB Export January 2026 through February 2026":
        "january_february_2026.zip",
    "CCDB Export March 2026":
        "march_2026.zip",
    "CCDB Export April 2026":
        "april_2026.zip",
    "CCDB Export May 2026":
        "may_2026.zip",
    "CCDB Export June 2026":
        "june_2026.zip",
}

START_DATE = datetime(2026, 1, 1).date()
END_DATE = datetime(2026, 6, 30).date()

PRODUCT_OUTPUTS = {
    "Credit card": CFPB_RAW / "credit_card.csv",
    "Checking or savings account":
        CFPB_RAW / "checking_or_savings_account.csv",
}

REQUIRED_COLUMNS = {
    "Date received",
    "Product",
    "Consumer complaint narrative",
}


class ArchiveLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.current_href = None
        self.current_text = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            self.current_href = dict(attrs).get("href")
            self.current_text = []

    def handle_data(self, data):
        if self.current_href is not None:
            self.current_text.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self.current_href is not None:
            text = " ".join(" ".join(self.current_text).split())
            self.links.append((text, self.current_href))
            self.current_href = None
            self.current_text = []


def parse_received_date(value):
    value = (value or "").strip()
    if not value:
        return None

    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass

    return None


def download_archives():
    headers = dict(UA)
    headers.setdefault("User-Agent", "ComplaintIQ-capstone/1.0")

    print("Reading official CFPB narrative archive:")
    print(ARCHIVE_PAGE)

    response = requests.get(
        ARCHIVE_PAGE,
        headers=headers,
        timeout=(20, 120),
    )
    response.raise_for_status()

    parser = ArchiveLinkParser()
    parser.feed(response.text)

    available_links = {
        " ".join(text.split()).casefold(): urljoin(ARCHIVE_PAGE, href)
        for text, href in parser.links
        if href
    }

    for label, filename in EXPORTS.items():
        url = available_links.get(label.casefold())

        if not url:
            raise RuntimeError(
                f"Could not find official archive link: {label}. "
                "Open the CFPB archive page and verify the export label."
            )

        destination = ARCHIVE_DIR / filename

        # Reuse a previously downloaded archive only if it is a valid ZIP.
        if destination.exists() and zipfile.is_zipfile(destination):
            print(f"Archive already present and valid: {destination.name}")
            continue

        print(f"Downloading: {label}")

        download = requests.get(
            url,
            headers=headers,
            timeout=(30, 300),
        )
        download.raise_for_status()

        if not zipfile.is_zipfile(io.BytesIO(download.content)):
            raise RuntimeError(
                f"The CFPB download for '{label}' was not a valid ZIP. "
                f"HTTP status: {download.status_code}; "
                f"content type: {download.headers.get('Content-Type')}"
            )

        temporary = destination.with_suffix(".zip.part")
        temporary.write_bytes(download.content)
        temporary.replace(destination)

        print(
            f"Saved {destination.name}: "
            f"{destination.stat().st_size:,} bytes"
        )


def process_archives():
    for output in PRODUCT_OUTPUTS.values():
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists():
            output.unlink()

    counts = {product: 0 for product in PRODUCT_OUTPUTS}
    monthly_counts = {}

    for label, filename in EXPORTS.items():
        archive_path = ARCHIVE_DIR / filename

        if not archive_path.exists() or not zipfile.is_zipfile(archive_path):
            raise RuntimeError(f"Missing or invalid archive: {archive_path}")

        with zipfile.ZipFile(archive_path) as archive:
            csv_names = [
                name for name in archive.namelist()
                if name.lower().endswith(".csv")
            ]

            if len(csv_names) != 1:
                raise RuntimeError(
                    f"Expected exactly one CSV in {filename}; "
                    f"found: {csv_names}"
                )

            csv_name = csv_names[0]
            print(f"\nProcessing {filename} -> {csv_name}")

            with archive.open(csv_name) as binary_file:
                text_file = io.TextIOWrapper(
                    binary_file,
                    encoding="utf-8-sig",
                    newline="",
                )
                reader = csv.DictReader(text_file)

                if not reader.fieldnames:
                    raise RuntimeError(f"No CSV header in {filename}")

                missing = REQUIRED_COLUMNS - set(reader.fieldnames)
                if missing:
                    raise RuntimeError(
                        f"{filename} is missing required columns: {missing}. "
                        f"Found: {reader.fieldnames}"
                    )

                # Open outputs in append mode; write the header only once.
                with (
                    PRODUCT_OUTPUTS["Credit card"].open(
                        "a", encoding="utf-8-sig", newline=""
                    ) as credit_file,
                    PRODUCT_OUTPUTS["Checking or savings account"].open(
                        "a", encoding="utf-8-sig", newline=""
                    ) as checking_file,
                ):
                    writers = {
                        "Credit card": csv.DictWriter(
                            credit_file, fieldnames=reader.fieldnames
                        ),
                        "Checking or savings account": csv.DictWriter(
                            checking_file, fieldnames=reader.fieldnames
                        ),
                    }

                    for product, writer in writers.items():
                        if counts[product] == 0:
                            writer.writeheader()

                    for row in reader:
                        received = parse_received_date(row.get("Date received"))
                        product = (row.get("Product") or "").strip()
                        narrative = (
                            row.get("Consumer complaint narrative") or ""
                        ).strip()

                        if received is None or not (
                            START_DATE <= received <= END_DATE
                        ):
                            continue

                        if product not in PRODUCT_OUTPUTS:
                            continue

                        if not narrative:
                            continue

                        writers[product].writerow(row)
                        counts[product] += 1
                        month_key = received.strftime("%Y-%m")
                        key = (filename, month_key, product)
                        monthly_counts[key] = monthly_counts.get(key, 0) + 1

    print("\n=== Output summary ===")
    for product, output in PRODUCT_OUTPUTS.items():
        print(f"{product}: {counts[product]:,} rows")
        print(f"  File: {output}")
        if not output.exists() or output.stat().st_size == 0:
            raise RuntimeError(f"Output file is empty or missing: {output}")

    print("\n=== Monthly counts by source archive ===")
    for (archive, month, product), count in sorted(monthly_counts.items()):
        print(f"{archive} | {month} | {product}: {count:,}")

    print("\nPASS: CFPB narrative archive processing completed.")


def main():
    download_archives()
    process_archives()


if __name__ == "__main__":
    main()
