import random

# --- User Configuration ---
INPUT_FILENAME = "ii.lmpdat"
OUTPUT_FILENAME = "he_np_random.lmpdat"

# Metal atoms to be swapped (IDs 14, 16, 17, 18, 19, 20 are Type 3 in the original file)
METAL_ATOMS_IDS = [14, 16, 17, 18, 19, 20] 
NUM_METAL_ATOMS = len(METAL_ATOMS_IDS) # Should be 6

# Define the new metal types and their properties
# Note: Type 3 (Zr) is kept, and types 4-7 are added.
# Masses for Hf, Pd, Ru, Ti are based on standard atomic weights.
METAL_PROPERTIES = {
    # Type ID: [Mass, Element Symbol]
    3: [91.224, "Zr"],
    4: [178.49, "Hf"], 
    5: [106.42, "Pd"], 
    6: [101.07, "Ru"], 
    7: [47.867, "Ti"], 
}

# Define the target distribution (approximate equimolar mix for 6 sites)
# This results in: 2 Zr (33.3%), 1 Hf (16.7%), 1 Pd, 1 Ru, 1 Ti.
TARGET_TYPES = [3, 3, 4, 5, 6, 7] 
# ---------------------------

def create_random_he_np(input_file, output_file):
    """Reads LAMMPS data file, randomizes metal types, and writes new data file."""
    
    with open(input_file, 'r') as f:
        lines = f.readlines()

    modified_lines = []
    
    # 1. Randomize the metal atom types
    random.shuffle(TARGET_TYPES)
    
    atom_id_to_new_type = dict(zip(METAL_ATOMS_IDS, TARGET_TYPES))
    
    # Flags to track sections
    in_masses_section = False
    in_atoms_section = False
    
    for line in lines:
        
        # --- Handle Masses Section ---
        if "Masses" in line:
            in_masses_section = True
            modified_lines.append(line)
            # Add placeholders for the new masses (Types 4-7)
            for type_id, prop in METAL_PROPERTIES.items():
                if type_id > 3: # Only add new types
                    modified_lines.append(f"{type_id}   {prop[0]}\n")
            continue
        
        # Exit masses section if the next section starts
        if in_masses_section and line.strip() and not line[0].isdigit():
            in_masses_section = False
        
        if in_masses_section:
            # Modify Type 3 mass line if needed, or keep it as is
            if line.strip().startswith("3"):
                modified_lines.append(f"3   {METAL_PROPERTIES[3][0]}\n")
                continue
            # Skip the original mass lines 1 and 2, which are handled later
            if line.strip().startswith("1") or line.strip().startswith("2"):
                 modified_lines.append(line)
                 continue
            # Skip original Type 3 mass line (already added)
            continue
            
        # --- Handle Atoms Section ---
        if "Atoms" in line:
            in_atoms_section = True
            modified_lines.append(line)
            continue
            
        # Modify atom type if it's one of the metal atoms
        if in_atoms_section and line.strip().isdigit():
            # Atom lines start with ID, Type, Coords...
            parts = line.split()
            if len(parts) >= 2:
                atom_id = int(parts[0])
                
                if atom_id in atom_id_to_new_type:
                    new_type = atom_id_to_new_type[atom_id]
                    
                    # Replace the old type (index 1 in the parts list)
                    parts[1] = str(new_type)
                    
                    # Reconstruct the line
                    modified_line = "  ".join(parts) + "\n"
                    modified_lines.append(modified_line)
                    continue
        
        # Exit atoms section if the next section starts (e.g., Bonds)
        if in_atoms_section and line.strip().startswith("Bonds"):
            in_atoms_section = False
            
        # Append all other lines as-is
        modified_lines.append(line)
        
    # Write the new file
    with open(output_file, 'w') as f:
        f.writelines(modified_lines)

    print(f"Successfully generated randomized HE-NP data file: {output_file}")
    print(f"Metal Type Distribution in {output_file}:")
    for type_id, count in zip(TARGET_TYPES, [TARGET_TYPES.count(t) for t in sorted(list(set(TARGET_TYPES)))]):
        if type_id >= 3:
            print(f"- Type {type_id} ({METAL_PROPERTIES[type_id][1]}): {count} atoms")

if __name__ == "__main__":
    create_random_he_np(INPUT_FILENAME, OUTPUT_FILENAME)