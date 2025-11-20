# SPMF and Choco-Mining Libraries

This directory should contain the following JAR files:

## Required
- `spmf.jar` - Download from https://www.philippe-fournier-viger.com/spmf/

## Optional
- `choco-mining.jar` - Choco-based constraint mining library

## Installation Instructions

1. Download SPMF:
   ```bash
   wget https://www.philippe-fournier-viger.com/spmf/download.php
   ```

2. Place the JAR file in this directory

3. Update the path in `.env` file:
   ```
   SPMF_JAR_PATH=./lib/spmf.jar
   ```

## Note
JAR files are not tracked in Git due to their size. Each team member should download them separately.
