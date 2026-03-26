#!/usr/bin/env python3
"""
NuGet Version Resolution for UiPath Projects.

Queries the NuGet API to get the latest compatible versions of UiPath packages.
Never hardcode versions - always use this script to get current versions.

Usage:
    # Get latest versions for common packages
    python resolve_nuget.py

    # Get specific packages
    python resolve_nuget.py UiPath.System.Activities UiPath.Excel.Activities

    # Update project.json with latest versions
    python resolve_nuget.py --update ./MyProject/project.json

    # Output as JSON
    python resolve_nuget.py --json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

NUGET_API_BASE = "https://api.nuget.org/v3-flatcontainer"
NUGET_SEARCH_API = "https://azuresearch-usnc.nuget.org/query"

# Common UiPath packages
COMMON_PACKAGES = [
    "UiPath.System.Activities",
    "UiPath.UIAutomation.Activities",
    "UiPath.Excel.Activities",
    "UiPath.Mail.Activities",
    "UiPath.Credentials.Activities",
    "UiPath.Testing.Activities",
]

# Package to activity mapping (for dependency resolution)
PACKAGE_ACTIVITIES = {
    "UiPath.System.Activities": [
        "InvokeWorkflowFile", "Assign", "If", "ForEach", "While", "TryCatch",
        "LogMessage", "RetryScope", "Throw", "Rethrow", "Delay",
    ],
    "UiPath.UIAutomation.Activities": [
        "Click", "TypeInto", "GetText", "NClick", "NTypeInto", "NGetText",
        "NApplicationCard", "NGoToUrl", "NCheckState", "NSelectItem",
    ],
    "UiPath.Excel.Activities": [
        "ReadRange", "WriteRange", "ExcelApplicationScope", "WriteCell",
        "AppendRange", "ReadCell",
    ],
    "UiPath.Mail.Activities": [
        "GetIMAPMailMessages", "SendSMTPMailMessage", "GetOutlookMailMessages",
        "SaveMailAttachments",
    ],
    "UiPath.Credentials.Activities": [
        "GetCredential", "GetRobotCredential", "GetRobotAsset", "SetCredential",
    ],
    "UiPath.WebAPI.Activities": [
        "HttpClient", "DeserializeJson", "SerializeJson",
    ],
    "UiPath.Database.Activities": [
        "ExecuteQuery", "ExecuteNonQuery", "Connect", "Disconnect",
    ],
    "UiPath.PDF.Activities": [
        "ReadPDFText", "ReadPDFWithOCR", "ExtractPDFPageRange",
    ],
    "UiPath.Persistence.Activities": [
        "CreateFormTask", "WaitForFormTaskAndResume", "ResumeProcess",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# API FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_package_versions(package_name: str) -> List[str]:
    """
    Get all available versions of a NuGet package.

    Args:
        package_name: Package ID (e.g., "UiPath.System.Activities")

    Returns:
        List of version strings, sorted newest first
    """
    url = f"{NUGET_API_BASE}/{package_name.lower()}/index.json"

    try:
        req = Request(url, headers={"User-Agent": "UiPath-ReFramework-Generator/1.0"})
        with urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            versions = data.get("versions", [])
            # Sort by version (newest first)
            return sorted(versions, key=_parse_version, reverse=True)
    except HTTPError as e:
        if e.code == 404:
            print(f"  Warning: Package '{package_name}' not found on NuGet", file=sys.stderr)
            return []
        raise
    except URLError as e:
        print(f"  Error: Could not connect to NuGet API: {e}", file=sys.stderr)
        return []


def get_latest_stable_version(package_name: str) -> Optional[str]:
    """
    Get the latest stable (non-prerelease) version of a package.

    Args:
        package_name: Package ID

    Returns:
        Latest stable version string, or None if not found
    """
    versions = get_package_versions(package_name)

    for version in versions:
        # Skip prerelease versions (contain - or +)
        if "-" not in version and "+" not in version:
            return version

    return versions[0] if versions else None


def get_latest_versions(packages: List[str]) -> Dict[str, str]:
    """
    Get latest stable versions for multiple packages.

    Args:
        packages: List of package names

    Returns:
        Dict of {package_name: version}
    """
    result = {}
    for package in packages:
        version = get_latest_stable_version(package)
        if version:
            result[package] = version
    return result


def _parse_version(version: str) -> Tuple:
    """Parse version string for sorting."""
    # Remove prerelease suffix for sorting
    base = version.split("-")[0].split("+")[0]
    parts = base.split(".")
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        return (0, 0, 0)


# ═══════════════════════════════════════════════════════════════════════════════
# DEPENDENCY DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

def detect_required_packages(xaml_content: str) -> List[str]:
    """
    Detect required NuGet packages based on activities used in XAML.

    Args:
        xaml_content: XAML file content

    Returns:
        List of required package names
    """
    required = set()

    for package, activities in PACKAGE_ACTIVITIES.items():
        for activity in activities:
            # Check for activity usage (various patterns)
            if f"<{activity}" in xaml_content or f":{activity}" in xaml_content:
                required.add(package)
                break

    return sorted(required)


def detect_project_packages(project_dir: str) -> List[str]:
    """
    Detect all required packages for a project by scanning XAML files.

    Args:
        project_dir: Path to project directory

    Returns:
        List of required package names
    """
    project_path = Path(project_dir)
    required = set()

    for xaml_file in project_path.rglob("*.xaml"):
        content = xaml_file.read_text(encoding="utf-8")
        required.update(detect_required_packages(content))

    return sorted(required)


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT.JSON MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

def update_project_json(project_json_path: str, versions: Dict[str, str]) -> bool:
    """
    Update project.json with new package versions.

    Args:
        project_json_path: Path to project.json
        versions: Dict of {package_name: version}

    Returns:
        True if changes were made
    """
    path = Path(project_json_path)
    if not path.exists():
        print(f"Error: {project_json_path} not found", file=sys.stderr)
        return False

    with open(path, "r", encoding="utf-8") as f:
        project = json.load(f)

    deps = project.get("dependencies", {})
    changed = False

    for package, version in versions.items():
        new_constraint = f"[{version}, )"
        if package not in deps or deps[package] != new_constraint:
            deps[package] = new_constraint
            changed = True
            print(f"  Updated: {package} → {version}")

    if changed:
        project["dependencies"] = deps
        with open(path, "w", encoding="utf-8") as f:
            json.dump(project, f, indent=2)
        print(f"\nUpdated {project_json_path}")

    return changed


def generate_dependencies_dict(packages: List[str]) -> Dict[str, str]:
    """
    Generate a dependencies dict for project.json.

    Args:
        packages: List of package names

    Returns:
        Dict of {package_name: version_constraint}
    """
    versions = get_latest_versions(packages)
    return {pkg: f"[{ver}, )" for pkg, ver in versions.items()}


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Resolve NuGet package versions for UiPath projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                  Show latest versions of common packages
  %(prog)s UiPath.Excel.Activities          Get version for specific package
  %(prog)s --update ./project.json          Update project.json with latest versions
  %(prog)s --detect ./MyProject             Detect required packages from XAML
"""
    )

    parser.add_argument("packages", nargs="*",
                       help="Package names to resolve (default: common packages)")
    parser.add_argument("--update", "-u", metavar="PROJECT_JSON",
                       help="Update project.json with latest versions")
    parser.add_argument("--detect", "-d", metavar="PROJECT_DIR",
                       help="Detect required packages from XAML files")
    parser.add_argument("--json", "-j", action="store_true",
                       help="Output as JSON")
    parser.add_argument("--all", "-a", action="store_true",
                       help="Show all common packages")

    args = parser.parse_args()

    # Determine packages to resolve
    if args.detect:
        packages = detect_project_packages(args.detect)
        if not packages:
            print("No UiPath activities detected in project")
            return
        print(f"Detected packages: {', '.join(packages)}\n")
    elif args.packages:
        packages = args.packages
    elif args.all:
        packages = COMMON_PACKAGES
    else:
        packages = COMMON_PACKAGES[:4]  # Just the essentials

    # Get versions
    print("Resolving NuGet package versions...")
    versions = get_latest_versions(packages)

    if not versions:
        print("No versions found. Check network connection.", file=sys.stderr)
        sys.exit(1)

    # Output
    if args.json:
        print(json.dumps(versions, indent=2))
    elif args.update:
        update_project_json(args.update, versions)
    else:
        print("\nLatest stable versions:")
        print("-" * 50)
        for pkg, ver in versions.items():
            print(f"  {pkg}: {ver}")
        print("-" * 50)
        print("\nFor project.json:")
        for pkg, ver in versions.items():
            print(f'    "{pkg}": "[{ver}, )",')


if __name__ == "__main__":
    main()
