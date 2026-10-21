#!/usr/bin/env python3
"""Encrypt/decrypt all files under a folder with a passphrase (AES-256-GCM + scrypt).

Usage:
  python file_vault.py ./folder encrypt [--out ./encrypted] [--exclude PATTERN ...] [--exclude-file .vaultignore] [--key PASSPHRASE]
  python file_vault.py ./encrypted decrypt [--out ./restored] [--key PASSPHRASE]

The folder path always comes first, before the encrypt/decrypt action. If
--out is omitted, output goes to "<folder>_encrypted" or "<folder>_decrypted"
next to the input folder.

Encrypted file names keep their original name plus a ".enc" suffix; directory
structure remains visible. File contents are authenticated and encrypted
with AES-256-GCM, keyed via scrypt. Keep the passphrase separate from the
repository (e.g. a password manager or an untracked .env), and prefer the
interactive prompt or FVAULT_KEY env var over --key, since command-line
arguments can end up in shell history and process listings.
"""

from __future__ import annotations

import argparse
import fnmatch
import getpass
import os
from pathlib import Path, PurePosixPath
import secrets
import sys

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

MAGIC = b"FVAULT1\0"
SALT_LEN = 16
NONCE_LEN = 12
KEY_LEN = 32
ENC_SUFFIX = ".enc"

DEFAULT_EXCLUDES = [
    ".git",
    ".git/**",
    "venv",
    "venv/**",
    "__pycache__",
    "**/__pycache__/**",
    "*.pyc",
    "Run_Commands.txt",
    "test_cases.txt",
    "requirements.txt",
    "Git_Repo_Notes.txt",
    "behave.ini",
    "file_vault.py",
    ".gitignore",
    ]

DEFAULT_FOLDER = r""


def derive_key(password: str, salt: bytes) -> bytes:
    return Scrypt(salt=salt, length=KEY_LEN, n=2**15, r=8, p=1).derive(
        password.encode("utf-8")
    )


def resolve_password(key_arg: str | None, confirm: bool = False) -> str:
    password = key_arg or os.environ.get("FVAULT_KEY")
    if not password:
        password = getpass.getpass("Passphrase: ")
        if confirm:
            again = getpass.getpass("Confirm passphrase: ")
            if password != again:
                raise ValueError("Passphrases did not match.")
    if len(password) < 12:
        raise ValueError("Use a passphrase of at least 12 characters.")
    return password


def load_exclude_patterns(patterns: list[str], exclude_file: Path | None) -> list[str]:
    all_patterns = list(DEFAULT_EXCLUDES) + list(patterns)
    if exclude_file is not None:
        exclude_file = exclude_file.expanduser().resolve()
        if not exclude_file.exists():
            raise FileNotFoundError(exclude_file)
        for line in exclude_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                all_patterns.append(line)
    return all_patterns


def is_excluded(relative: Path, patterns: list[str]) -> bool:
    rel_posix = PurePosixPath(relative.as_posix())
    candidates = [rel_posix.as_posix(), rel_posix.name] + [
        PurePosixPath(*rel_posix.parts[: i + 1]).as_posix() for i in range(len(rel_posix.parts))
    ]
    for pattern in patterns:
        pattern = pattern.rstrip("/")
        for candidate in candidates:
            if fnmatch.fnmatch(candidate, pattern):
                return True
    return False


def collect_files(folder: Path, patterns: list[str]) -> list[Path]:
    folder = folder.expanduser().resolve()
    if not folder.exists():
        raise FileNotFoundError(folder)
    if not folder.is_dir():
        raise ValueError(f"Not a folder: {folder}")
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(folder):
        current = Path(dirpath)
        dirnames[:] = [
            d for d in dirnames if not is_excluded((current / d).relative_to(folder), patterns)
        ]
        for name in filenames:
            path = current / name
            if not is_excluded(path.relative_to(folder), patterns):
                files.append(path)
    files = sorted(set(files))
    if not files:
        raise ValueError("No files found (check your --exclude patterns).")
    return files


def encrypt(folder: Path, destination: Path, patterns: list[str], key_arg: str | None) -> None:
    root = folder.expanduser().resolve()
    files = collect_files(root, patterns)
    destination = destination.expanduser().resolve()
    password = resolve_password(key_arg, confirm=True)
    for source in files:
        relative = source.relative_to(root)
        target = destination / relative.parent / (relative.name + ENC_SUFFIX)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise FileExistsError(f"Refusing to overwrite {target}")
        data = source.read_bytes()
        salt, nonce = secrets.token_bytes(SALT_LEN), secrets.token_bytes(NONCE_LEN)
        header = MAGIC + salt + nonce
        encrypted = AESGCM(derive_key(password, salt)).encrypt(nonce, data, header)
        target.write_bytes(header + encrypted)
        print(f"Encrypted: {source} -> {target}")


def decrypt(folder: Path, destination: Path, patterns: list[str], key_arg: str | None) -> None:
    root = folder.expanduser().resolve()
    files = collect_files(root, patterns)
    files = [f for f in files if f.name.endswith(ENC_SUFFIX)]
    if not files:
        raise ValueError("No *.enc files found.")
    password = resolve_password(key_arg)
    destination = destination.expanduser().resolve()
    header_len = len(MAGIC) + SALT_LEN + NONCE_LEN
    for source in files:
        raw = source.read_bytes()
        if len(raw) < header_len + 16 or not raw.startswith(MAGIC):
            raise ValueError(f"Not a supported encrypted file: {source}")
        header = raw[:header_len]
        salt = header[len(MAGIC) : len(MAGIC) + SALT_LEN]
        nonce = header[len(MAGIC) + SALT_LEN :]
        ciphertext = raw[header_len:]
        try:
            data = AESGCM(derive_key(password, salt)).decrypt(nonce, ciphertext, header)
        except Exception as exc:
            raise ValueError(f"Failed to decrypt {source}: wrong passphrase or corrupted file") from exc
        relative = source.relative_to(root)
        target = destination / relative.parent / relative.name[: -len(ENC_SUFFIX)]
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise FileExistsError(f"Refusing to overwrite {target}")
        target.write_bytes(data)
        print(f"Decrypted: {source} -> {target}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "folder",
        nargs="?",
        type=Path,
        default=DEFAULT_FOLDER,
        help=f"Folder to encrypt or decrypt (always comes first; default: {DEFAULT_FOLDER})",
    )
    parser.add_argument("command", choices=["encrypt", "decrypt"], help="Action to perform")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Destination folder (default: <folder>_encrypted or <folder>_decrypted, next to it)",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="PATTERN",
        help="Glob pattern (relative path, dir name, or file name) to exclude; repeatable",
    )
    parser.add_argument(
        "--exclude-file",
        type=Path,
        default=None,
        help="File with one exclude glob pattern per line (# comments allowed)",
    )
    parser.add_argument(
        "--key",
        default=None,
        help="Passphrase (min 12 chars). Prefer FVAULT_KEY env var or the interactive prompt instead.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    patterns = load_exclude_patterns(args.exclude, args.exclude_file)
    folder = args.folder.expanduser().resolve()
    suffix = "_encrypted" if args.command == "encrypt" else "_decrypted"
    destination = args.out if args.out is not None else folder.parent / (folder.name + suffix)
    try:
        if args.command == "encrypt":
            encrypt(folder, destination, patterns, args.key)
        else:
            decrypt(folder, destination, patterns, args.key)
    except (ValueError, FileNotFoundError, FileExistsError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
