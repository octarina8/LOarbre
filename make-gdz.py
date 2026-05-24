#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera un .gdz listo para Topola Viewer a partir de:
  - Un .ged exportado de Gramps
  - Una carpeta con las fotos (puede tener subcarpetas)

Uso:
  1) Edita las tres rutas de la seccion CONFIGURACION mas abajo.
  2) Ejecuta:  python make-gdz.py
  3) Sube el .gdz resultante a tu repo de GitHub.

Solo usa librerias estandar de Python (no hay que instalar nada).
"""

import os
import re
import sys
import zipfile


# ===================== CONFIGURACION =====================
# Ruta al .ged que has exportado de Gramps:
GED_PATH = r"C:\Users\nit\LOClaude\LOarbre\LOArbre.ged"

# Carpeta donde tienes todas las fotos consolidadas
# (la misma que tienes como base path de media en Gramps,
#  o cualquier carpeta donde esten todas):
MEDIA_DIR = r"C:\Users\nit\LOClaude\LOarbre\media"

# Donde guardar el .gdz resultante:
OUTPUT_GDZ = r"C:\Users\nit\LOClaude\LOarbre\LOArbre.gdz"
# =========================================================


def normalize_file_path(raw_path):
    """
    Convierte cualquier path (absoluto Windows, relativo con ..\\, .\\, etc.)
    a un path estandar 'media/<resto>' que apuntara dentro del ZIP.

    - Si el path contiene un segmento 'media', tomamos lo que va detras.
    - Si no, usamos solo el nombre del fichero.
    """
    parts = re.split(r'[/\\]', raw_path)
    parts = [p for p in parts if p not in ('', '.', '..')]
    # Buscar el ULTIMO segmento llamado 'media' (case-insensitive)
    media_idx = None
    for i, seg in enumerate(parts):
        if seg.lower() == 'media':
            media_idx = i
    if media_idx is not None and media_idx < len(parts) - 1:
        return 'media/' + '/'.join(parts[media_idx + 1:])
    return 'media/' + parts[-1]


def detect_encoding(raw_bytes):
    """Gramps suele exportar en UTF-8; algunos .ged antiguos en ANSEL/Latin-1."""
    try:
        raw_bytes.decode('utf-8')
        return 'utf-8'
    except UnicodeDecodeError:
        return 'latin-1'


def main():
    # --- validaciones basicas ---
    if not os.path.isfile(GED_PATH):
        sys.exit(f"ERROR: no encuentro el .ged: {GED_PATH}")
    if not os.path.isdir(MEDIA_DIR):
        sys.exit(f"ERROR: no encuentro la carpeta de fotos: {MEDIA_DIR}")

    print(f"[1/4] Leyendo .ged: {GED_PATH}")
    with open(GED_PATH, 'rb') as f:
        raw = f.read()
    encoding = detect_encoding(raw)
    text = raw.decode(encoding)
    print(f"      Encoding detectado: {encoding}")

    # --- normalizar rutas FILE ---
    print("[2/4] Normalizando rutas FILE...")
    out_lines = []
    refs_found = []
    for line in text.splitlines(keepends=True):
        bare = line.rstrip('\r\n')
        eol = line[len(bare):]
        if bare.startswith('1 FILE '):
            old_path = bare[len('1 FILE '):]
            # Saltar la auto-referencia del header (apunta al propio .ged)
            if old_path.lower().endswith('.ged'):
                out_lines.append(line)
                continue
            new_path = normalize_file_path(old_path)
            refs_found.append(new_path)
            out_lines.append(f'1 FILE {new_path}{eol}')
        else:
            out_lines.append(line)
    new_ged_bytes = ''.join(out_lines).encode(encoding)
    print(f"      {len(refs_found)} referencias normalizadas")

    # --- verificar que las fotos existen en disco ---
    print(f"[3/4] Verificando fotos en {MEDIA_DIR}")
    unique_refs = sorted(set(refs_found))
    files_to_add = {}      # arcname -> disk path
    missing = []
    for ref in unique_refs:
        rel = ref[len('media/'):]                       # ej. 'P39_291_352.jpeg'
        disk = os.path.join(MEDIA_DIR, rel.replace('/', os.sep))
        if os.path.isfile(disk):
            files_to_add[ref] = disk
        else:
            missing.append(ref)
    if missing:
        print(f"      AVISO: {len(missing)} foto(s) NO encontradas en disco:")
        for m in missing[:10]:
            print(f"        - {m}")
        if len(missing) > 10:
            print(f"        ... y {len(missing) - 10} mas")
        print("      (esas referencias quedaran en el .ged pero sin imagen)")
    print(f"      {len(files_to_add)} foto(s) listas para empaquetar")

    # --- empaquetar .gdz ---
    print(f"[4/4] Generando {OUTPUT_GDZ}")
    ged_arcname = os.path.basename(GED_PATH)
    with zipfile.ZipFile(OUTPUT_GDZ, 'w', zipfile.ZIP_STORED) as gdz:
        gdz.writestr(ged_arcname, new_ged_bytes)
        for arcname, disk in sorted(files_to_add.items()):
            gdz.write(disk, arcname)

    size = os.path.getsize(OUTPUT_GDZ)
    print()
    print(f"OK -> {OUTPUT_GDZ}")
    print(f"     {size:,} bytes  ({size/1024/1024:.1f} MB)")
    if size > 100 * 1024 * 1024:
        print("     AVISO: supera 100 MB. GitHub rechazara la subida.")
        print("     Reduce el tamano de las fotos antes de generar el .gdz.")
    elif size > 50 * 1024 * 1024:
        print("     AVISO: supera 50 MB. GitHub te avisara al subirlo, pero lo acepta.")


if __name__ == '__main__':
    main()
