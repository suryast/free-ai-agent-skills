#!/usr/bin/env python3
"""Validate Agent Skills frontmatter and repository-local resource references.

Spec: https://agentskills.io/specification
Repository checks additionally reject duplicate YAML keys, require body content,
and resolve relative Markdown links plus literal bundled-resource code spans.
No remote requests or agent commands are executed.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

import yaml

FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


class UniqueSafeLoader(yaml.SafeLoader):
    """Safe YAML loading with deterministic rejection of ambiguous keys."""


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise ValueError("YAML mapping keys must be strings")
        if key in result:
            raise ValueError(f"duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping
)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("SKILL.md must start with a --- line")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("unclosed YAML frontmatter") from exc
    data = yaml.load("\n".join(lines[1:end]), Loader=UniqueSafeLoader)
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a YAML mapping")
    return data, "\n".join(lines[end + 1:])


def prose_only(text: str) -> str:
    """Ignore fenced example/template content, including nested shorter fences."""
    kept = []
    fence = None
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})(.*)$", line)
        if fence is None and match:
            fence = match.group(1)
        elif fence is not None:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence) and not match.group(2).strip():
                fence = None
        else:
            kept.append(line)
    return "\n".join(kept)


def resource_errors(path: Path, root: Path) -> list[str]:
    """Check inline/reference Markdown destinations and literal resource spans.

    This is not a general Markdown parser. Anchors and external URLs are skipped;
    placeholder paths in code spans are examples, not bundled resources.
    """
    text = prose_only(path.read_text(encoding="utf-8"))
    targets = set(re.findall(r"\[[^\]\n]*\]\(\s*<?([^\s)>]+)>?(?:\s+[^)]*)?\)", text))
    targets.update(re.findall(r"^\s{0,3}\[[^\]\n]+\]:\s*<?([^\s>]+)>?", text, re.M))
    for span in re.findall(r"(?<!`)`([^`\n]+)`(?!`)", text):
        if re.fullmatch(r"(?:\./)?(?:scripts|references|assets)/[^\s<>*{}]+", span):
            targets.add(span)
    errors = []
    for target in sorted(targets):
        parts = urlsplit(target)
        if parts.scheme or parts.netloc or not parts.path:
            continue
        local = unquote(parts.path)
        resolved = (path.parent / local).resolve()
        if not resolved.is_relative_to(root.resolve()):
            errors.append(f"{path.relative_to(root)}: resource escapes repository: {target}")
        elif not resolved.exists():
            errors.append(f"{path.relative_to(root)}: missing resource: {target}")
    return errors


def validate_package(package: Path, root: Path) -> list[str]:
    path = package / "SKILL.md"
    if not path.is_file():
        return ["missing exact-case SKILL.md"]
    try:
        data, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    except (ValueError, yaml.YAMLError, UnicodeError) as exc:
        return [f"invalid frontmatter: {exc}"]
    errors = []
    for field in sorted(set(data) - FIELDS):
        errors.append(f"unsupported frontmatter field: {field}; use metadata")
    name = data.get("name")
    if not isinstance(name, str) or not 1 <= len(name) <= 64:
        errors.append("name must be a string of 1-64 characters")
    else:
        if name != name.lower() or not all(c.isalnum() or c == "-" for c in name) or name.startswith("-") or name.endswith("-") or "--" in name:
            errors.append("name must use lowercase alphanumeric characters and single interior hyphens")
        if name != package.name:
            errors.append("name must exactly match parent directory")
    for field, limit in (("description", 1024), ("compatibility", 500)):
        if field == "description" or field in data:
            value = data.get(field)
            if not isinstance(value, str) or not value.strip() or len(value) > limit:
                errors.append(f"{field} must be a non-empty string of at most {limit} characters")
    for field in ("license", "allowed-tools"):
        if field in data and not isinstance(data[field], str):
            errors.append(f"{field} must be a string")
    if "metadata" in data:
        value = data["metadata"]
        if not isinstance(value, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in value.items()):
            errors.append("metadata must map string keys to string values")
    if not body.strip():
        errors.append("repository policy: Markdown instructions must not be empty")
    for doc in sorted(package.rglob("*.md")):
        errors.extend(resource_errors(doc, root))
    return errors


def discover_packages(root: Path) -> list[Path]:
    """Discover top-level packages, including mis-cased entry points."""
    return sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".") and any(f.name.lower() == "skill.md" for f in p.iterdir()))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    if not args.root.is_dir():
        print("ERROR: repository directory does not exist", file=sys.stderr)
        return 1
    packages = discover_packages(args.root)
    if not packages:
        print("ERROR: no skill packages found", file=sys.stderr)
        return 1
    failed = 0
    for package in packages:
        errors = validate_package(package, args.root)
        failed += bool(errors)
        print(f"{'FAIL' if errors else 'PASS'} {package.name}")
        for error in errors:
            print(f"  {error}")
    print(f"Validated {len(packages)} packages; {failed} failed")
    return int(bool(failed))


if __name__ == "__main__":
    sys.exit(main())
