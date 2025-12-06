from pymatgen.core import Structure
from io import StringIO
import random

# Read and sanitize the CIF file to replace unknown attached_hydrogens ('?') with 0
with open('UiO66.cif', 'r') as f:
    lines = f.read().splitlines()

clean_lines = []
in_loop = False
headers = []
for line in lines:
    stripped = line.strip()
    # start of a loop block
    if stripped.lower().startswith('loop_'):
        in_loop = True
        headers = []
        clean_lines.append(line)
        continue

    # collect loop headers that belong to atom_site
    if in_loop and stripped.startswith('_atom_site_'):
        headers.append(stripped) # stripped line that shows atomical positionns
        clean_lines.append(line)
        continue

    # data lines for the current loop (once headers collected)
    if in_loop and headers and stripped and not stripped.startswith('_'):
        # locate _atom_site_attached_hydrogens column (if present) and replace '?' with '0'
        try:
            idx = None
            for i, h in enumerate(headers):
                if h.lower().startswith('_atom_site_attached_hydrogens'):
                    idx = i
                    break
            if idx is not None:
                parts = line.split()
                if len(parts) > idx and parts[idx] == '?':
                    parts[idx] = '0'
                    line = '   '.join(parts)
        except Exception:
            # if something unexpected happens, fall back to original line
            pass
        clean_lines.append(line)
        continue

    # end of loop block when a blank line is encountered
    if in_loop and not stripped:
        in_loop = False
        headers = []

    clean_lines.append(line)

clean_cif = '\n'.join(clean_lines)

# Use from_str with fmt='cif' to parse the cleaned CIF content
structure = Structure.from_str(clean_cif, fmt='cif')

all_zr = [i for i, s in enumerate(structure) if s.species_string == "Zr"]

print(all_zr)
