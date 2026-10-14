"""Compactar históricos antigos sem apagar conteúdo; conferir SHA e espaço real."""
import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex-root', type=Path, default=Path.home() / '.codex')
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--min-age-hours', type=float, default=48)
    parser.add_argument('--max-total-gb', type=float, default=20)
    args = parser.parse_args()
    assert os.name == 'nt', 'Requer Windows e compact.exe'
    root = args.codex_root.resolve()
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    get_size = kernel.GetCompressedFileSizeW
    get_size.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(wintypes.DWORD)]
    get_size.restype = wintypes.DWORD
    create = kernel.CreateFileW
    create.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                       ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p]
    create.restype = wintypes.HANDLE
    close = kernel.CloseHandle
    close.argtypes = [wintypes.HANDLE]
    wof = ctypes.WinDLL('Wofutil').WofIsExternalFile
    wof.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(wintypes.BOOL),
                    ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p, ctypes.c_void_p]
    wof.restype = ctypes.c_long

    def physical(path):
        high = wintypes.DWORD()
        ctypes.set_last_error(0)
        low = get_size(str(path), ctypes.byref(high))
        if low == 0xffffffff and ctypes.get_last_error():
            raise ctypes.WinError(ctypes.get_last_error())
        return (high.value << 32) | low

    def sha(path):
        with path.open('rb') as stream:
            return hashlib.file_digest(stream, 'sha256').hexdigest()

    def already_wof(path):
        external, provider = wintypes.BOOL(), wintypes.DWORD()
        status = wof(str(path), ctypes.byref(external), ctypes.byref(provider), None, None)
        return status == 0 and bool(external.value) and provider.value == 2

    def exclusive_available(path):
        handle = create(str(path), 0x80000000, 0, None, 3, 0, None)
        if handle == ctypes.c_void_p(-1).value:
            return False
        close(handle)
        return True

    def compact(path, options):
        return subprocess.run(['compact.exe', *options, str(path)],
                              capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)

    current = os.environ.get('CODEX_THREAD_ID', '')
    cutoff = time.time() - args.min_age_hours * 3600
    files = []
    for folder in ['sessions', 'archived_sessions']:
        base = root / folder
        assert not base.is_symlink() and not base.is_junction()
        for path in base.rglob('*.jsonl'):
            if path.is_symlink() or current and current in path.name:
                continue
            try:
                stat = path.stat()
            except OSError:
                continue
            if stat.st_mtime < cutoff and stat.st_size > 10_000_000:
                assert path.resolve().is_relative_to(base.resolve())
                files.append((stat.st_size, path))
    record = {'schema': 'boas/codex-history-compaction-v1', 'algorithm': 'Windows WOF LZX',
              'deleted_files': 0, 'current_conversation_excluded': True,
              'min_age_hours': args.min_age_hours, 'files': [],
              'free_before_bytes': shutil.disk_usage(root).free}
    if args.report.exists():
        previous = json.loads(args.report.read_text(encoding='utf8'))
        assert previous['schema'] == record['schema'] and previous['min_age_hours'] == args.min_age_hours
        record = previous
    record.setdefault('skipped_files', [])
    record['complete'] = False
    args.report.parent.mkdir(parents=True, exist_ok=True)

    def persist():
        record['free_after_bytes'] = shutil.disk_usage(root).free
        record['reclaimed_bytes'] = sum(f.get('reclaimed_bytes', 0) for f in record['files'])
        record['sha256_verified_files'] = sum(f.get('sha256_same', False) for f in record['files'])
        temporary = args.report.with_suffix('.json.writing')
        temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
        temporary.replace(args.report)

    processed = sum(entry['logical_bytes'] for entry in record['files'])
    for logical, path in sorted(files, reverse=True):
        if processed + logical > args.max_total_gb * 1_000_000_000:
            continue
        try:
            before = physical(path)
            if already_wof(path) or not exclusive_available(path):
                continue
        except OSError:
            record['skipped_files'].append({'file': path.relative_to(root).as_posix(), 'reason': 'unavailable_before_operation'})
            continue
        if shutil.disk_usage(root).free < logical + 700_000_000:
            continue
        try:
            first = sha(path)
            stat = path.stat()
        except OSError:
            record['skipped_files'].append({'file': path.relative_to(root).as_posix(), 'reason': 'unavailable_before_operation'})
            continue
        if stat.st_mtime >= cutoff:
            continue
        if stat.st_file_attributes & 0x800:
            compact(path, ['/U', '/Q'])
        result = compact(path, ['/C', '/EXE:LZX', '/F', '/Q'])
        try:
            second = sha(path)
            after = physical(path)
        except OSError:
            record['skipped_files'].append({'file': path.relative_to(root).as_posix(), 'reason': 'unavailable_after_operation_verification_pending'})
            persist()
            continue
        entry = {'file': path.relative_to(root).as_posix(), 'logical_bytes': logical,
                 'physical_before_bytes': before, 'physical_after_bytes': after,
                 'reclaimed_bytes': before - after, 'sha256': second,
                 'sha256_same': first == second, 'compact_returncode': result.returncode}
        record['files'].append(entry)
        persist()
        assert first == second, 'Conteúdo mudou durante a operação; interrompido'
        processed += logical
        print(json.dumps({'verified': record['sha256_verified_files'],
                          'reclaimed_bytes': record['reclaimed_bytes'],
                          'free_bytes': record['free_after_bytes']}, ensure_ascii=False), flush=True)
    record['complete'] = True
    persist()
    print(json.dumps({'complete': True, 'report': args.report.as_posix(),
                      'verified': record['sha256_verified_files'],
                      'reclaimed_bytes': record['reclaimed_bytes'],
                      'free_bytes': record['free_after_bytes']}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
