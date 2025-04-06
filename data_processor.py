import pandas as pd
import numpy as np
from exercise_constants import (
    VALID_EXERCISES,
    EXERCISE_DOMINANCE,
    is_valid_exercise_dominance,
    get_full_exercise_name,
    standardize_dominance
)

class DataProcessor:
    def __init__(self):
        self.required_columns = [
            'user name', 'exercise name', 'dominance', 'exercise createdAt',
            'power - high', 'acceleration - high', 'sex'
        ]

    def validate_data(self, df):
        """Validate only the required columns and their presence."""
        # Check required columns (except sex which can be empty)
        required_non_empty = [col for col in self.required_columns if col != 'sex']
        missing_cols = [col for col in required_non_empty if col not in df.columns]
        if missing_cols:
            return False, f"Missing required columns: {', '.join(missing_cols)}"

        # Check for empty values in required columns (except sex)
        empty_cols = [col for col in required_non_empty if df[col].isna().any()]
        if empty_cols:
            return False, f"Empty values found in columns: {', '.join(empty_cols)}"

        # Validate power and acceleration columns contain numeric values
        numeric_cols = ['power - high', 'acceleration - high']
        for col in numeric_cols:
            if not pd.to_numeric(df[col], errors='coerce').notnull().all():
                return False, f"Non-numeric values found in {col} column"

        # Validate sex values if present
        valid_sex_values = ['male', 'female', 'Male', 'Female', 'MALE', 'FEMALE']
        non_empty_sex = df['sex'].dropna()
        if len(non_empty_sex) > 0:
            invalid_sex = ~non_empty_sex.str.lower().isin(['male', 'female'])
            if invalid_sex.any():
                return False, "Invalid values in sex column. Must be 'male' or 'female' when specified"

        return True, "Data validation successful"

    def preprocess_data(self, df):
        """Clean and prepare the data for matrix generation."""
        # Create a copy to avoid modifying original data
        processed_df = df.copy()

        # Debug initial counts of Shot Put and Vertical Jump
        shot_put_count = len(processed_df[processed_df['exercise name'].str.contains('Shot Put', na=False)])
        vertical_jump_count = len(processed_df[processed_df['exercise name'].str.contains('Vertical Jump', na=False)])
        print(f"DEBUG: Initial counts - Shot Put: {shot_put_count}, Vertical Jump: {vertical_jump_count}")
        
        # Show examples of these exercises
        if shot_put_count > 0:
            example = processed_df[processed_df['exercise name'].str.contains('Shot Put', na=False)].iloc[0]
            print(f"DEBUG: Example Shot Put - Name: {example['exercise name']}, Dominance: {example['dominance']}")
        if vertical_jump_count > 0:
            example = processed_df[processed_df['exercise name'].str.contains('Vertical Jump', na=False)].iloc[0]
            print(f"DEBUG: Example Vertical Jump - Name: {example['exercise name']}, Dominance: {example['dominance']}")

        # Ensure power and acceleration values are numeric
        processed_df['power - high'] = pd.to_numeric(processed_df['power - high'], errors='coerce')
        processed_df['acceleration - high'] = pd.to_numeric(processed_df['acceleration - high'], errors='coerce')

        # Remove rows where either power or acceleration is NaN
        processed_df = processed_df.dropna(subset=['power - high', 'acceleration - high'])

        # Debug after numeric conversion
        shot_put_count = len(processed_df[processed_df['exercise name'].str.contains('Shot Put', na=False)])
        vertical_jump_count = len(processed_df[processed_df['exercise name'].str.contains('Vertical Jump', na=False)])
        print(f"DEBUG: After numeric conversion - Shot Put: {shot_put_count}, Vertical Jump: {vertical_jump_count}")

        # Fill empty sex values with 'male'
        if 'sex' in processed_df.columns:
            processed_df['sex'] = processed_df['sex'].fillna('male')
        else:
            processed_df['sex'] = 'male'

        # Standardize sex values to lowercase
        processed_df['sex'] = processed_df['sex'].str.lower()

        # Get valid base exercises
        valid_base_exercises = [ex for cat in VALID_EXERCISES.values() for ex in cat]
        print(f"DEBUG: Valid base exercises for Shot Put and Vertical Jump: {[ex for ex in valid_base_exercises if 'Shot Put' in ex or 'Vertical Jump' in ex]}")

        # Filter to keep only the specified exercises
        before_filter = len(processed_df)
        processed_df = processed_df[processed_df['exercise name'].isin(valid_base_exercises)].copy()
        after_filter = len(processed_df)
        
        # Debug after exercise name filtering
        print(f"DEBUG: Rows before/after exercise filtering: {before_filter}/{after_filter}")
        shot_put_count = len(processed_df[processed_df['exercise name'].str.contains('Shot Put', na=False)])
        vertical_jump_count = len(processed_df[processed_df['exercise name'].str.contains('Vertical Jump', na=False)])
        print(f"DEBUG: After exercise filtering - Shot Put: {shot_put_count}, Vertical Jump: {vertical_jump_count}")

        # Standardize dominance values
        processed_df['dominance'] = processed_df['dominance'].apply(standardize_dominance)

        # Debug before dominance validation
        shot_put_rows = processed_df[processed_df['exercise name'].str.contains('Shot Put', na=False)]
        vertical_jump_rows = processed_df[processed_df['exercise name'].str.contains('Vertical Jump', na=False)]
        print(f"DEBUG: Before dominance validation - Shot Put rows: {len(shot_put_rows)}")
        print(f"DEBUG: Before dominance validation - Vertical Jump rows: {len(vertical_jump_rows)}")
        
        if len(shot_put_rows) > 0:
            for _, row in shot_put_rows.iterrows():
                print(f"DEBUG: Shot Put dominance check - Name: {row['exercise name']}, Dominance: {row['dominance']}, Valid: {is_valid_exercise_dominance(row['exercise name'], row['dominance'])}")
        
        if len(vertical_jump_rows) > 0:
            for _, row in vertical_jump_rows.iterrows():
                print(f"DEBUG: Vertical Jump dominance check - Name: {row['exercise name']}, Dominance: {row['dominance']}, Valid: {is_valid_exercise_dominance(row['exercise name'], row['dominance'])}")

        # Filter valid exercises and dominance combinations
        valid_rows = []
        for idx, row in processed_df.iterrows():
            is_valid = is_valid_exercise_dominance(row['exercise name'], row['dominance'])
            if is_valid:
                valid_rows.append(idx)
            elif 'Shot Put' in row['exercise name'] or 'Vertical Jump' in row['exercise name']:
                print(f"DEBUG: Invalid dominance - Exercise: {row['exercise name']}, Dominance: {row['dominance']}")

        processed_df = processed_df.loc[valid_rows].copy()

        # Debug after dominance validation
        shot_put_count = len(processed_df[processed_df['exercise name'].str.contains('Shot Put', na=False)])
        vertical_jump_count = len(processed_df[processed_df['exercise name'].str.contains('Vertical Jump', na=False)])
        print(f"DEBUG: After dominance validation - Shot Put: {shot_put_count}, Vertical Jump: {vertical_jump_count}")

        # Generate full exercise names
        processed_df['full_exercise_name'] = processed_df.apply(
            lambda row: get_full_exercise_name(row['exercise name'], row['dominance']),
            axis=1
        )

        # Convert timestamp
        processed_df['exercise createdAt'] = pd.to_datetime(processed_df['exercise createdAt'])

        # Sort by user and timestamp
        processed_df = processed_df.sort_values(['user name', 'exercise createdAt'])

        return processed_df

    def get_user_list(self, df):
        """Get list of unique users in the dataset."""
        return sorted(df['user name'].unique())