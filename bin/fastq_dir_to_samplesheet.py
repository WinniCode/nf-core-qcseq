#!/usr/bin/env python3

import argparse
import csv
import sys
from pathlib import Path
import re

R1_PATTERN = re.compile(r"(.+?)(_R?1)(_001)?\.f(ast)?q\.gz$")
R2_PATTERN = re.compile(r"(.+?)(_R?2)(_001)?\.f(ast)?q\.gz$")

def parse_args():
    parser = argparse.ArgumentParser(
        description="Create nf-core qcseq samplesheet from FASTQ directory"
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Directory containing FASTQ files"
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output samplesheet CSV"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    fastq_dir = Path(args.input)

    if not fastq_dir.exists():
        sys.exit(f"ERROR: Directory not found: {fastq_dir}")

    fastqs = list(fastq_dir.rglob("*.f*q.gz"))

    if not fastqs:
        sys.exit("ERROR: No FASTQ files found")

    samples = {}

    for fq in fastqs:
        name = fq.name

        m1 = R1_PATTERN.match(name)
        m2 = R2_PATTERN.match(name)

        if m1:
            sample = m1.group(1)
            samples.setdefault(sample, {})["fastq_1"] = str(fq.resolve())
        elif m2:
            sample = m2.group(1)
            samples.setdefault(sample, {})["fastq_2"] = str(fq.resolve())
        else:
            print(f"WARNING: Skipping unrecognised file: {name}", file=sys.stderr)

    if not samples:
        sys.exit("ERROR: No valid FASTQ pairs found")

    with open(args.output, "w", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=["sample", "fastq_1", "fastq_2"]
        )
        writer.writeheader()

        for sample, files in sorted(samples.items()):
            if "fastq_1" not in files:
                sys.exit(f"ERROR: Missing R1 for sample {sample}")

            writer.writerow({
                "sample": sample,
                "fastq_1": files["fastq_1"],
                "fastq_2": files.get("fastq_2", "")
            })

    print(f"Samplesheet written to {args.output}")

if __name__ == "__main__":
    main()
