"""Goal standards for exercise movements based on sex."""
import pandas as pd

POWER_STANDARDS = {
    'male': {
        'Straight Arm Trunk Rotation': 325,
        'Shot Put (Countermovement)': 450,
        'PNF D2 Flexion': 140,
        'PNF D2 Extension': 140,
        'Biceps Curl (One Hand)': 100,
        'Triceps Extension (One Hand)': 100,
        'Horizontal Row (One Hand)': 225,
        'Chest Press (One Hand)': 225,
        'Lateral Bound': 80,
        'Vertical Jump (Countermovement)': 90
    },
    'female': {
        'Straight Arm Trunk Rotation': 225,
        'Shot Put (Countermovement)': 300,
        'PNF D2 Flexion': 100,
        'PNF D2 Extension': 100,
        'Biceps Curl (One Hand)': 70,
        'Triceps Extension (One Hand)': 70,
        'Horizontal Row (One Hand)': 175,
        'Chest Press (One Hand)': 175,
        'Lateral Bound': 80,
        'Vertical Jump (Countermovement)': 80
    }
}

# Add alternate keys for Press/Pull exercises to support various formats
for sex in ['male', 'female']:
    # Ensure variations for Horizontal Row
    if 'Horizontal Row (One Hand)' in POWER_STANDARDS[sex]:
        POWER_STANDARDS[sex]['Horizontal Row'] = POWER_STANDARDS[sex]['Horizontal Row (One Hand)']
    
    # Ensure variations for Chest Press
    if 'Chest Press (One Hand)' in POWER_STANDARDS[sex]:
        POWER_STANDARDS[sex]['Chest Press'] = POWER_STANDARDS[sex]['Chest Press (One Hand)']

ACCELERATION_STANDARDS = {
    'male': {
        'Straight Arm Trunk Rotation': 15,
        'Shot Put (Countermovement)': 25,
        'PNF D2 Flexion': 14,
        'PNF D2 Extension': 14,
        'Biceps Curl (One Hand)': 10,
        'Triceps Extension (One Hand)': 10,
        'Horizontal Row (One Hand)': 25,
        'Chest Press (One Hand)': 25,
        'Lateral Bound': 5,
        'Vertical Jump (Countermovement)': 10
    },
    'female': {
        'Straight Arm Trunk Rotation': 10,
        'Shot Put (Countermovement)': 15,
        'PNF D2 Flexion': 8,
        'PNF D2 Extension': 8,
        'Biceps Curl (One Hand)': 7,
        'Triceps Extension (One Hand)': 7,
        'Horizontal Row (One Hand)': 15,
        'Chest Press (One Hand)': 15,
        'Lateral Bound': 5,
        'Vertical Jump (Countermovement)': 10
    }
}

# Add alternate keys for Press/Pull exercises to support various formats
for sex in ['male', 'female']:
    # Ensure variations for Horizontal Row
    if 'Horizontal Row (One Hand)' in ACCELERATION_STANDARDS[sex]:
        ACCELERATION_STANDARDS[sex]['Horizontal Row'] = ACCELERATION_STANDARDS[sex]['Horizontal Row (One Hand)']
    
    # Ensure variations for Chest Press
    if 'Chest Press (One Hand)' in ACCELERATION_STANDARDS[sex]:
        ACCELERATION_STANDARDS[sex]['Chest Press'] = ACCELERATION_STANDARDS[sex]['Chest Press (One Hand)']

def get_base_exercise_name(full_exercise_name):
    """Extract base exercise name from full name including dominance."""
    # Special case for Vertical Jump
    if 'Vertical Jump (Countermovement)' in full_exercise_name:
        return 'Vertical Jump (Countermovement)'
        
    # Special case for Shot Put
    if 'Shot Put (Countermovement)' in full_exercise_name:
        print(f"DEBUG: Shot Put special case handling for: {full_exercise_name}")
        return 'Shot Put (Countermovement)'
        
    # Handle exercises with "One Hand" in the name differently
    if 'One Hand' in full_exercise_name and '(' in full_exercise_name:
        # For exercises like "Horizontal Row (One Hand) (Dominant)"
        # We want to return "Horizontal Row (One Hand)" as the base name
        if full_exercise_name.count('(') > 1:
            base = full_exercise_name.rsplit('(', 1)[0].strip()
            return base
    
    # Standard case for exercises without "One Hand" in base name
    if '(' in full_exercise_name:
        base = full_exercise_name.split('(')[0].strip()
        return base
        
    # No parens, return as is
    return full_exercise_name

def calculate_development_score(value, exercise_name, sex, metric_type='power'):
    """Calculate development score as percentage of goal standard."""
    if not value or pd.isna(value):
        return None

    base_exercise = get_base_exercise_name(exercise_name)
    standards = POWER_STANDARDS if metric_type == 'power' else ACCELERATION_STANDARDS

    if sex not in standards or base_exercise not in standards[sex]:
        return None

    goal_standard = standards[sex][base_exercise]
    return (value / goal_standard) * 100 if goal_standard else None