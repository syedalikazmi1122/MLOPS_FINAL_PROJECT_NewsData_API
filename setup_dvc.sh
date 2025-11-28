#!/bin/bash
# DVC Setup Script for Windows (PowerShell compatible commands)

echo "Setting up DVC for data versioning..."

# Initialize DVC (if not already initialized)
if [ ! -d ".dvc" ]; then
    echo "Initializing DVC..."
    dvc init
    echo "✓ DVC initialized"
else
    echo "DVC already initialized"
fi

# Add processed data to DVC
echo "Adding processed data to DVC..."
dvc add data/processed/earthquakes_processed.parquet

echo "✓ DVC setup complete!"
echo ""
echo "Next steps:"
echo "1. Review the generated .dvc and .gitignore files"
echo "2. Commit DVC metadata to git:"
echo "   git add data/processed/earthquakes_processed.parquet.dvc .gitignore"
echo "   git commit -m 'Add processed data to DVC'"
echo ""
echo "3. To configure remote storage (Dagshub/S3), run:"
echo "   dvc remote add origin <remote-url>"
echo "   dvc push"

