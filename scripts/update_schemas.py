#!/usr/bin/env python3
"""
Update local schema cache from AdCP website.

This script downloads all AdCP JSON schemas from adcontextprotocol.org
and updates the local cache in tests/schemas/v1/.

Usage:
    python scripts/update_schemas.py [--dry-run]
"""

import argparse
import json
import sys
from pathlib import Path

import httpx


def filename_to_ref(filename: str) -> str:
    """Convert our flattened filename format to a $ref path."""
    # _schemas_v1_core_format_json.json -> /schemas/v1/core/format.json
    name = filename.replace(".json", "").replace("_json", ".json").replace("_", "/", 1)
    return name


def ref_to_filename(ref: str) -> str:
    """Convert $ref path to our flattened filename format."""
    # /schemas/v1/core/format.json -> _schemas_v1_core_format_json.json
    return ref.replace("/", "_").replace(".", "_") + ".json"


def download_schema(ref: str, base_url: str = "https://adcontextprotocol.org") -> dict | None:
    """
    Download a schema from AdCP website.

    Returns schema dict if successful, None if not found or error.
    """
    schema_url = f"{base_url}{ref}"

    try:
        print(f"  Fetching: {ref}")
        response = httpx.get(schema_url, timeout=10.0, follow_redirects=True)
        response.raise_for_status()

        # Check if we got JSON (not HTML)
        content_type = response.headers.get("content-type", "")
        if "json" not in content_type.lower():
            print(f"  ⚠️  Skipping {ref}: Got {content_type} instead of JSON")
            return None

        schema = response.json()
        return schema

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print(f"  ⚠️  Not found: {ref}")
        else:
            print(f"  ❌ HTTP {e.response.status_code}: {ref}")
        return None
    except Exception as e:
        print(f"  ❌ Error downloading {ref}: {e}")
        return None


def discover_schemas(schema_dir: Path) -> list[str]:
    """
    Discover all schema $refs from existing cache.

    Returns list of unique $ref paths found in existing schemas.
    """
    refs = set()

    for schema_file in schema_dir.glob("*.json"):
        try:
            with open(schema_file) as f:
                schema = json.load(f)

            # Extract $ref from this schema
            if "$id" in schema:
                refs.add(schema["$id"])

            # Recursively find all $refs in the schema
            refs.update(find_refs_in_schema(schema))

        except Exception as e:
            print(f"  ⚠️  Error reading {schema_file.name}: {e}")

    return sorted(refs)


def find_refs_in_schema(obj: dict | list) -> set[str]:
    """Recursively find all $ref values in a schema."""
    refs = set()

    if isinstance(obj, dict):
        if "$ref" in obj:
            refs.add(obj["$ref"])
        for value in obj.values():
            refs.update(find_refs_in_schema(value))
    elif isinstance(obj, list):
        for item in obj:
            refs.update(find_refs_in_schema(item))

    return refs


def update_schemas(schema_dir: Path, dry_run: bool = False):
    """
    Update all schemas from AdCP website.

    Discovers schema refs from existing cache, downloads latest versions,
    and updates local files.
    """
    print(f"📂 Schema directory: {schema_dir}")

    if not schema_dir.exists():
        print(f"❌ Directory not found: {schema_dir}")
        sys.exit(1)

    # Discover all schema refs
    print("\n🔍 Discovering schemas from existing cache...")
    refs = discover_schemas(schema_dir)
    print(f"   Found {len(refs)} unique schema refs")

    # Download and update each schema
    print("\n📥 Downloading latest schemas...")
    updated = 0
    unchanged = 0
    failed = 0

    for ref in refs:
        # Validate ref
        if not ref.startswith("/schemas/v1/"):
            print(f"  ⚠️  Skipping invalid ref: {ref}")
            continue

        # Download latest version
        latest_schema = download_schema(ref)
        if latest_schema is None:
            failed += 1
            continue

        # Compare with local version
        filename = ref_to_filename(ref)
        local_path = schema_dir / filename

        if local_path.exists():
            with open(local_path) as f:
                local_schema = json.load(f)

            if local_schema == latest_schema:
                print(f"  ✓ No changes: {filename}")
                unchanged += 1
                continue

        # Update local file
        if dry_run:
            print(f"  🔄 Would update: {filename}")
            updated += 1
        else:
            with open(local_path, "w") as f:
                json.dump(latest_schema, f, indent=2)
                f.write("\n")  # Add trailing newline
            print(f"  ✅ Updated: {filename}")
            updated += 1

    # Summary
    print(f"\n📊 Summary:")
    print(f"   Updated: {updated}")
    print(f"   Unchanged: {unchanged}")
    print(f"   Failed: {failed}")

    if dry_run:
        print("\n   (Dry run - no files were modified)")

    if updated > 0 and not dry_run:
        print("\n💡 Next steps:")
        print("   1. Review changes: git diff tests/schemas/v1/")
        print("   2. Regenerate Python models: python scripts/generate_schemas.py")
        print("   3. Run tests: pytest")


def main():
    parser = argparse.ArgumentParser(description="Update AdCP schemas from website")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be updated without making changes")
    parser.add_argument(
        "--schema-dir",
        type=Path,
        default=Path("tests/schemas/v1"),
        help="Directory containing JSON schemas (default: tests/schemas/v1)",
    )
    args = parser.parse_args()

    update_schemas(args.schema_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
