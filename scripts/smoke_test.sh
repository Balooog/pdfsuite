#!/usr/bin/env bash
set -euo pipefail

fixtures="tests/fixtures"
build_dir="${BUILD_DIR:-build}"
mkdir -p "$build_dir/splits"

sample_a="$fixtures/sampleA.pdf"
sample_b="$fixtures/sampleB.pdf"

pdfsuite version
pdfsuite doctor || true

pdfsuite merge "$sample_a" "$sample_b" -o "$build_dir/merged.pdf"
pdfsuite optimize "$build_dir/merged.pdf" -o "$build_dir/optimized.pdf"
pdfsuite stamp "$build_dir/merged.pdf" --bates TEST --start 1 -o "$build_dir/stamped.pdf"
pdfsuite split "$build_dir/merged.pdf" --pages 1,2 -o "$build_dir/splits"
pdfsuite reorder "$build_dir/merged.pdf" --order 2,1 -o "$build_dir/reordered.pdf"
pdfsuite forms flatten "$sample_a" -o "$build_dir/flat.pdf" || true
pdfsuite metadata_scrub "$build_dir/stamped.pdf" -o "$build_dir/clean.pdf"
pdfsuite compare "$sample_a" "$sample_b" --headless -o "$build_dir/diff.pdf" || true
pdfsuite audit "$sample_a" -o "$build_dir/audit.json" || true
