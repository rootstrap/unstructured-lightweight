#!/usr/bin/env bash

set -e

SCRIPT_DIR=$(dirname "$(realpath "$0")")
cd "$SCRIPT_DIR"/.. || exit 1
OUTPUT_FOLDER_NAME=local-ocr-langs
OUTPUT_DIR=$SCRIPT_DIR/structured-output/$OUTPUT_FOLDER_NAME

PYTHONPATH=. ./unstructured/ingest/main.py \
    local \
    --metadata-exclude coordinates,filename,file_directory,metadata.data_source.date_processed,metadata.last_modified \
    --structured-output-dir "$OUTPUT_DIR" \
    --partition-ocr-languages eng+kor \
    --partition-strategy ocr_only \
    --verbose \
    --reprocess \
    --input-path example-docs/english-and-korean.png

PYTHONPATH=. ./unstructured/ingest/main.py \
    local \
    --metadata-exclude coordinates,filename,file_directory,metadata.data_source.date_processed,metadata.last_modified \
    --structured-output-dir "$OUTPUT_DIR" \
    --partition-ocr-languages chi_sim \
    --partition-strategy hi_res \
    --verbose \
    --reprocess \
    --input-path example-docs/simplified_chinese.pdf

set +e

sh "$SCRIPT_DIR"/check-diff-expected-output.sh $OUTPUT_FOLDER_NAME