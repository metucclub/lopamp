#!/bin/bash
mkdir -p static && \
sass --update resources:sass_processed && \
pleeease compile sass_processed/style.css -t static/style.css && \
mv sass_processed/content-description.css static/content-description.css && \
mv sass_processed/table.css static/table.css && \
mv sass_processed/ranks.css static/ranks.css && \
find static -name "*.scss" -delete
