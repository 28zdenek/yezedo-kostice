"""Nastaví heslo k ostrému webu www.yezedokostice.cz (přihlašovací stránka login.aspx).

Spuštění:  python3 set_password.py            vygeneruje nové heslo a vypíše ho
           python3 set_password.py 'heslo'     nastaví zadané heslo

Uloží sůl, otisk hesla (PBKDF2) a nový náhodný token do .site-password (není v gitu – repozitář je veřejný).
`python3 build.py prod` je odtud dosadí do dist/web.config. Token dostane prohlížeč po správném heslu jako cookie
a URL Rewrite bez něj nepustí nic kromě přihlášení. Po změně hesla sestavit a nahrát web.config: nový token
zároveň odhlásí všechny dosud přihlášené.
"""
import hashlib
import json
import secrets
import sys

ITERATIONS = 100000  # musí sedět s login.aspx (Rfc2898DeriveBytes, HMAC-SHA1)
WORDS = ('hala', 'jezero', 'park', 'zona', 'cesta', 'strecha', 'kostice', 'louka', 'most', 'sklad', 'vinice', 'pole')

password = sys.argv[1] if len(sys.argv) > 1 else '-'.join(secrets.choice(WORDS) for _ in range(3)) + '-%d' % (secrets.randbelow(90) + 10)
salt = secrets.token_hex(16)
digest = hashlib.pbkdf2_hmac('sha1', password.encode('utf-8'), salt.encode('utf-8'), ITERATIONS, 32).hex()
json.dump({'salt': salt, 'hash': digest, 'token': secrets.token_hex(32)}, open('.site-password', 'w'))
print('Heslo nastaveno:', password)
