import os

# --- Configuration ---
# Set the name of the LAMMPS data file you want to convert
INPUT_FILENAME = "he_np_random.lmpdat"  
OUTPUT_FILENAME = "converted_structure.xyz"

# Define the mapping from LAMMPS Atom Type ID to Element Symbol
# This mapping includes the original O (Type 1), H (Type 2), and the 5 HE metals.
TYPE_TO_ELEMENT = {
    1: "O",    # Type 1: Oxygen
    2: "H",    # Type 2: Hydrogen
    3: "Zr",   # Type 3: Zirconium (or one of the HE metals)
    4: "Hf",   # Type 4: Hafnium (or one of the HE metals)
    5: "Pd",   # Type 5: Palladium (or one of the HE metals)
    6: "Ru",   # Type 6: Ruthenium (or one of the HE metals)
    7: "Ti",   # Type 7: Titanium (or one of the HE metals)
    # Add any other types if necessary
}
# ---------------------

def convert_lmpdat_to_xyz(input_file, output_file):
    """Converts a LAMMPS data file to XYZ format."""
    
    if not os.path.exists(input_file):
        print(f"ERROR: Input file not found at '{input_file}'")
        return

    with open(input_file, 'r') as f:
        lines = f.readlines()

    xyz_coordinates = []
    total_atoms = 0
    in_atoms_section = False
    
    for line in lines:
        cleaned_line = line.split('#')[0].strip()
        
        if "atoms" in line and not total_atoms:
            try:
                total_atoms = int(line.split()[0])
            except (ValueError, IndexError):
                pass 

        if cleaned_line == "Atoms":
            in_atoms_section = True
            continue
            
        # Stop parsing after the Atoms section
        if in_atoms_section and cleaned_line and not cleaned_line.split()[0].isdigit():
            in_atoms_section = False
            
        # Process lines within the Atoms section
        if in_atoms_section and cleaned_line:
            parts = cleaned_line.split()
            
            # Atom line must have at least ID, Type, x, y, z
            if len(parts) >= 6 and parts[0].isdigit(): 
                try:
                    current_type = int(parts[1])
                    x, y, z = parts[2:5]
                    
                    symbol = TYPE_TO_ELEMENT.get(current_type, f"Type{current_type}")

                    xyz_coordinates.append(f"{symbol: <2}  {x: >10}  {y: >10}  {z: >10}")
                    
                except (ValueError, IndexError) as e:
                    print(f"Skipping line due to parsing error: {cleaned_line} ({e})")
                    continue

    if not xyz_coordinates:
        print("ERROR: Could not parse any atom coordinates. Check your 'Atoms' section.")
        return

    # Write the XYZ file
    with open(output_file, 'w') as f:
        f.write(f"{total_atoms}\n")
        f.write(f"Converted from LAMMPS data file: {input_file}\n")
        f.write("\n".join(xyz_coordinates))

    print(f" Successfully converted '{input_file}' to '{output_file}' with {total_atoms} atoms.")

if __name__ == "__main__":
    convert_lmpdat_to_xyz(INPUT_FILENAME, OUTPUT_FILENAME)