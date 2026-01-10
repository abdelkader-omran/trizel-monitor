#!/bin/bash
set -e

echo "=========================================="
echo "TRIZEL End-to-End Test"
echo "=========================================="

echo ""
echo "1. Testing data acquisition (main.py)..."
set +e  # Temporarily allow non-zero exit codes
python src/main.py
exit_code=$?
set -e  # Re-enable exit on error
if [ $exit_code -eq 0 ] || [ $exit_code -eq 2 ]; then
    echo "   ✓ Data acquisition completed (exit code: $exit_code)"
else
    echo "   ✗ Data acquisition failed with unexpected exit code: $exit_code"
    exit 1
fi

echo ""
echo "2. Testing data validation..."
python src/validate_data.py
if [ $? -eq 0 ]; then
    echo "   ✓ All data files validated successfully"
else
    echo "   ✗ Validation failed"
    exit 1
fi

echo ""
echo "3. Checking file structure..."
if [ -f "data/snapshot_3I_ATLAS_latest.json" ]; then
    echo "   ✓ Latest snapshot exists"
else
    echo "   ✗ Latest snapshot missing"
    exit 1
fi

echo ""
echo "4. Checking metadata structure..."
python -c "
import json
with open('data/snapshot_3I_ATLAS_latest.json') as f:
    data = json.load(f)
    
assert 'trizel_metadata' in data, 'Missing trizel_metadata'
assert 'data' in data, 'Missing data block'
assert 'metadata' not in data, 'Legacy metadata block found'
assert 'platforms_registry' not in data, 'Legacy platforms_registry found'

meta = data['trizel_metadata']
assert meta['data_classification'] == 'SNAPSHOT', 'Wrong classification'
assert meta['source_agency'] == 'NASA', 'Wrong agency'
assert meta['checksum']['algorithm'] == 'sha256', 'Wrong checksum algorithm'
assert len(meta['checksum']['value']) == 64, 'Invalid SHA-256 length'

print('   ✓ Metadata structure correct')
print(f'   ✓ Classification: {meta[\"data_classification\"]}')
print(f'   ✓ Agency: {meta[\"source_agency\"]}')
print(f'   ✓ SHA-256: {meta[\"checksum\"][\"value\"][:16]}...')
"

echo ""
echo "5. Checking documentation consistency..."
# Check that all docs reference version 2.0.0 (with word boundaries to avoid false matches)
version_count=0
for file in DATA_CONTRACT.md README.md MANIFEST.md; do
    if grep -E "(^|[^0-9])2\.0\.0([^0-9]|$)" "$file" > /dev/null; then
        version_count=$((version_count + 1))
    fi
done
if [ $version_count -eq 3 ]; then
    echo "   ✓ All documentation references v2.0.0"
else
    echo "   ✗ Documentation version mismatch (found v2.0.0 in $version_count/3 files)"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ All tests passed!"
echo "=========================================="
echo ""
echo "Summary:"
echo "- Data acquisition: Working"
echo "- Validation: Passing (100%)"
echo "- Metadata structure: Compliant"
echo "- Documentation: Consistent"
echo "- Checksums: SHA-256 enforced"
echo "- Classification: Correct (SNAPSHOT)"
echo ""
echo "Framework status: READY"
