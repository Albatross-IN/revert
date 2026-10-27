"""Check a database's filestore against its attachments: every stored file present, and its bytes
hash (sha1) to the checksum Odoo recorded. Run as the service user on the server:

    sudo -u erp /opt/erp/venv/bin/python check_filestore.py <db> [data_dir=/opt/erp/data]

Exit 1 on any missing or altered file. Files on disk that no attachment points to are only counted.
"""
import hashlib
import os
import sys

import psycopg2

db = sys.argv[1]
root = os.path.join(sys.argv[2] if len(sys.argv) > 2 else '/opt/erp/data', 'filestore', db)
cr = psycopg2.connect(dbname=db).cursor()
cr.execute("SELECT DISTINCT store_fname, checksum FROM ir_attachment WHERE store_fname IS NOT NULL")
rows = cr.fetchall()
missing, altered = [], []
for fname, checksum in rows:
    path = os.path.join(root, fname)
    if not os.path.isfile(path):
        missing.append(fname)
        continue
    with open(path, 'rb') as f:
        if hashlib.sha1(f.read()).hexdigest() != checksum:
            altered.append(fname)
on_disk = {os.path.relpath(os.path.join(dirpath, name), root)
           for dirpath, _subdirs, files in os.walk(root) for name in files}
unreferenced = on_disk - {fname for fname, _checksum in rows}
print(f"{db}: {len(rows)} stored files referenced, {len(rows) - len(missing) - len(altered)} present with the "
      f"right sha1, {len(missing)} missing, {len(altered)} altered; {len(on_disk)} files on disk, "
      f"{len(unreferenced)} not referenced")
for label, names in (('MISSING', missing), ('ALTERED', altered)):
    for name in names[:20]:
        print(f"  {label} {name}")
sys.exit(1 if missing or altered else 0)
