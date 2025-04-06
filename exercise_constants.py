# List of valid exercises and their categories
VALID_EXERCISES = {
    'Torso': [
        'Straight Arm Trunk Rotation',
        'Shot Put (Countermovement)'
    ],
    'Arms': [
        'PNF D2 Flexion',
        'PNF D2 Extension',
        'Biceps Curl (One Hand)',
        'Triceps Extension (One Hand)'
    ],
    'Press/Pull': [
        'Horizontal Row (One Hand)',
        'Chest Press (One Hand)'
    ],
    'Legs': [
        'Lateral Bound',
        'Vertical Jump (Countermovement)'
    ]
}

# Define which exercises require dominance and valid dominance values
EXERCISE_DOMINANCE = {
    'Straight Arm Trunk Rotation': {'required': True, 'values': ['Dominant', 'Non-Dominant']},
    'Shot Put (Countermovement)': {'required': False, 'values': ['neither', None, '', 'Dominant', 'Non-Dominant']},
    'PNF D2 Flexion': {'required': True, 'values': ['Dominant', 'Non-Dominant']},
    'PNF D2 Extension': {'required': True, 'values': ['Dominant', 'Non-Dominant']},
    'Biceps Curl (One Hand)': {'required': True, 'values': ['Dominant', 'Non-Dominant']},
    'Triceps Extension (One Hand)': {'required': True, 'values': ['Dominant', 'Non-Dominant']},
    'Horizontal Row (One Hand)': {'required': True, 'values': ['Dominant', 'Non-Dominant']},
    'Chest Press (One Hand)': {'required': True, 'values': ['Dominant', 'Non-Dominant']},
    'Lateral Bound': {'required': True, 'values': ['Dominant', 'Non-Dominant']},
    'Vertical Jump (Countermovement)': {'required': False, 'values': ['neither', None, '']}
}

def standardize_dominance(dominance):
    """Convert dominance string to standard format."""
    if not dominance:
        return None

    dominance = str(dominance).strip().lower()
    if dominance == 'dominant':
        return 'Dominant'
    elif dominance == 'non-dominant':
        return 'Non-Dominant'
    return dominance

def is_valid_exercise_dominance(exercise_name, dominance):
    """Validate if exercise name and dominance combination is valid."""
    if exercise_name not in EXERCISE_DOMINANCE:
        return False

    exercise_config = EXERCISE_DOMINANCE[exercise_name]
    standardized_dominance = standardize_dominance(dominance)
    
    # Check if dominance is valid for this exercise
    if exercise_config['required']:
        # Strict check for exercises requiring dominance
        return standardized_dominance in exercise_config['values']
    else:
        # For exercises without required dominance, check if explicitly listed or allow any
        if exercise_config['values']:
            # If we have specified allowed values, check against them
            raw_dominance = dominance if dominance is not None else None
            std_dominance = standardized_dominance if standardized_dominance is not None else None
            # Check both raw and standardized dominance
            return raw_dominance in exercise_config['values'] or std_dominance in exercise_config['values']
        else:
            # If no values specified, accept any dominance
            return True

def get_full_exercise_name(exercise_name, dominance=None):
    """Generate full exercise name with dominance if required or specified."""
    if not exercise_name in EXERCISE_DOMINANCE:
        return None

    exercise_config = EXERCISE_DOMINANCE[exercise_name]
    standardized_dominance = standardize_dominance(dominance)
    
    # For exercises that require dominance
    if exercise_config['required']:
        if standardized_dominance:
            return f"{exercise_name} ({standardized_dominance})"
    # Special case for Vertical Jump - include 'neither' dominance if present
    elif exercise_name == 'Vertical Jump (Countermovement)' and dominance in ['neither', 'Neither']:
        return exercise_name  # Return just the base name without dominance
    # Special case for Shot Put with dominance
    elif exercise_name == 'Shot Put (Countermovement)':
        if standardized_dominance in ['Dominant', 'Non-Dominant']:
            return f"{exercise_name} ({standardized_dominance})"
        else:
            return exercise_name  # Return base name for other dominance values
    
    return exercise_name

# Generate list of all possible exercise variations
ALL_EXERCISES = []
for exercises in VALID_EXERCISES.values():
    for exercise in exercises:
        if EXERCISE_DOMINANCE[exercise]['required']:
            # Add dominant and non-dominant variations
            ALL_EXERCISES.extend([
                get_full_exercise_name(exercise, "Dominant"),
                get_full_exercise_name(exercise, "Non-Dominant")
            ])
        else:
            # For exercises that don't require dominance (like Vertical Jump)
            # just add the base name
            ALL_EXERCISES.append(exercise)
            
# Ensure Vertical Jump is explicitly included
if 'Vertical Jump (Countermovement)' not in ALL_EXERCISES:
    print("DEBUG: Explicitly adding Vertical Jump to ALL_EXERCISES list")
    ALL_EXERCISES.append('Vertical Jump (Countermovement)')
    
# Ensure Shot Put variations are included
if 'Shot Put (Countermovement)' not in ALL_EXERCISES:
    print("DEBUG: Explicitly adding Shot Put to ALL_EXERCISES list")
    ALL_EXERCISES.append('Shot Put (Countermovement)')
    
# Add Shot Put with dominance variations
shot_put_dominant = 'Shot Put (Countermovement) (Dominant)'
if shot_put_dominant not in ALL_EXERCISES:
    print(f"DEBUG: Adding {shot_put_dominant} to ALL_EXERCISES list")
    ALL_EXERCISES.append(shot_put_dominant)
    
shot_put_non_dominant = 'Shot Put (Countermovement) (Non-Dominant)'
if shot_put_non_dominant not in ALL_EXERCISES:
    print(f"DEBUG: Adding {shot_put_non_dominant} to ALL_EXERCISES list")
    ALL_EXERCISES.append(shot_put_non_dominant)
    
# Print the exercise list for debugging
print(f"DEBUG: ALL_EXERCISES list generated: {ALL_EXERCISES}")