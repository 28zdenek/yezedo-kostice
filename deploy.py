"""Nahraje dist/ na ostrý web www.yezedokostice.cz přes FTP (složka wwwroot).

Spuštění:  python3 build.py prod
           YEZEDO_FTP_USER=... YEZEDO_FTP_PASS=... python3 deploy.py [--all] [--skip web.config]

Nahrává jen soubory změněné od posledního nahrání (podle .deploy-manifest.json, není v gitu),
`--all` nahraje vše. Soubory, které z dist/ zmizely, na serveru smaže. Přihlašovací údaje se berou
jen z proměnných prostředí – repozitář je veřejný, nikdy je sem nezapisovat.
"""
import ftplib
import hashlib
import json
import os
import sys

HOST = 'www.yezedokostice.cz'
REMOTE = 'wwwroot'  # relativně k domovské složce FTP účtu; server šifrované FTP (TLS) nepovoluje
LOCAL = 'dist'
MANIFEST = '.deploy-manifest.json'


def local_files():
    out = {}
    for root, _, files in os.walk(LOCAL):
        for f in files:
            if f == '.DS_Store':
                continue
            path = os.path.join(root, f)
            out[os.path.relpath(path, LOCAL)] = hashlib.sha1(open(path, 'rb').read()).hexdigest()
    return out


def ensure_dir(ftp, made, rel):
    parts = rel.split('/')[:-1]
    for i in range(1, len(parts) + 1):
        d = REMOTE + '/' + '/'.join(parts[:i])
        if d not in made:
            try:
                ftp.mkd(d)
            except ftplib.error_perm:
                pass  # už existuje
            made.add(d)


def main():
    args = sys.argv[1:]
    skip = set(args[i + 1] for i, a in enumerate(args) if a == '--skip')
    files = {k: v for k, v in local_files().items() if k not in skip}
    old = {} if '--all' in args or not os.path.exists(MANIFEST) else json.load(open(MANIFEST))
    upload = sorted(k for k, v in files.items() if old.get(k) != v)
    delete = sorted(k for k in old if k not in files and k not in skip)
    print('nahrát: %d, smazat: %d, beze změny: %d' % (len(upload), len(delete), len(files) - len(upload)))
    if not upload and not delete:
        return
    ftp = ftplib.FTP(HOST, timeout=60)
    ftp.login(os.environ['YEZEDO_FTP_USER'], os.environ['YEZEDO_FTP_PASS'])
    global REMOTE
    REMOTE = ftp.pwd().rstrip('/') + '/' + REMOTE
    made = set()
    done = dict(old)
    try:
        for rel in upload:
            ensure_dir(ftp, made, rel)
            with open(os.path.join(LOCAL, rel), 'rb') as fh:
                ftp.storbinary('STOR %s/%s' % (REMOTE, rel), fh)
            done[rel] = files[rel]
            print('↑', rel)
        for rel in delete:
            try:
                ftp.delete('%s/%s' % (REMOTE, rel))
            except ftplib.error_perm:
                pass
            done.pop(rel, None)
            print('✕', rel)
    finally:
        json.dump(done, open(MANIFEST, 'w'), indent=0, sort_keys=True)
        ftp.quit()


if __name__ == '__main__':
    main()
