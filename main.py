import sqlite3
import os
import shutil
import argparse

def main():
    parser = argparse.ArgumentParser(description='Restore iOS hashed-name backup files to their original name.')
    parser.add_argument('-i', '--backup-dir', required=True, help='Path to the backup directory containing hash-named subfolders.')
    parser.add_argument('-m', '--manifest-db', required=True, help='Path to the Manifest.db file.')
    parser.add_argument('-o', '--output-dir', default='./result', help='Output directory for restored files (default: ./result).')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output (show missing file warnings)')
    args = parser.parse_args()

    # Connect to the Manifest.db
    conn = sqlite3.connect(args.manifest_db)
    cursor = conn.cursor()

    # Query for fileID and relativePath (adjust table/column names if needed)
    cursor.execute('SELECT fileID, relativePath FROM Files')
    rows = cursor.fetchall()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    for file_id, relative_path in rows:
        if not relative_path:
            continue  # Skip entries with empty paths

        # Construct source path: backup_dir/[first_2_chars]/[file_id]
        source_subdir = os.path.join(args.backup_dir, file_id[:2])
        source_path = os.path.join(source_subdir, file_id)

        if not os.path.exists(source_path):
            if args.verbose:
                print(f"⚠️ File not found: {source_path}")
            continue

        # Normalize target path (remove leading slashes)
        target_path = os.path.join(args.output_dir, relative_path.lstrip('/'))

        # Create parent directories
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        # Copy file
        shutil.copy2(source_path, target_path)
        if args.verbose:
            print(f"✅ Copied {file_id} to {target_path}")

    conn.close()

if __name__ == '__main__':
    main()