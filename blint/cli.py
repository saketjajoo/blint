#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys

from blint.analysis import report, start

blint_logo = """
██████╗ ██╗     ██╗███╗   ██╗████████╗
██╔══██╗██║     ██║████╗  ██║╚══██╔══╝
██████╔╝██║     ██║██╔██╗ ██║   ██║
██╔══██╗██║     ██║██║╚██╗██║   ██║
██████╔╝███████╗██║██║ ╚████║   ██║
╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝
"""


def build_args():
    """
    Constructs command line arguments for the blint tool
    """
    parser = argparse.ArgumentParser(
        prog="blint",
        description="Linting tool for binary files powered by lief.",
    )
    parser.add_argument(
        "-i",
        "--src",
        dest="src_dir_image",
        action="extend",
        nargs="+",
        help="Source directories, container images or binary files. Defaults to current directory.",
    )
    parser.add_argument(
        "-o",
        "--reports",
        dest="reports_dir",
        help="Reports directory. Defaults to reports.",
    )
    parser.add_argument(
        "--no-error",
        action="store_true",
        default=False,
        dest="noerror",
        help="Continue on error to prevent build from breaking",
    )
    parser.add_argument(
        "--no-banner",
        action="store_true",
        default=False,
        dest="no_banner",
        help="Do not display banner",
    )
    parser.add_argument(
        "--no-reviews",
        action="store_true",
        default=False,
        dest="no_reviews",
        help="Do not perform method reviews",
    )
    parser.add_argument(
        "--suggest-fuzzable",
        action="store_true",
        default=False,
        dest="suggest_fuzzable",
        help="Suggest functions and symbols for fuzzing based on a dictionary",
    )
    return parser.parse_args()


def parse_input(src):
    path = src[0]
    result = path.split("\n")
    result.pop()
    return result


def main():
    args = build_args()
    if not args.no_banner:
        print(blint_logo)
    if not os.getenv("CI"):
        src_dir = args.src_dir_image
    else:
        src_dir = parse_input(args.src_dir_image)
    if not src_dir:
        src_dir = [os.getcwd()]
    if args.reports_dir:
        reports_dir = args.reports_dir
    else:
        reports_dir = os.path.join(os.getcwd(), "reports")
    for src in src_dir:
        if not os.path.exists(src):
            print(f"{src} is an invalid file or directory!")
            return
    # Create reports directory
    if reports_dir and not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    findings, reviews, files, fuzzables = start(args, src_dir, reports_dir)
    report(args, src_dir, reports_dir, findings, reviews, files, fuzzables)

    if os.getenv("CI"):
        for f in findings:
            if f['severity'] == 'critical':
                sys.exit(1)


if __name__ == "__main__":
    main()
