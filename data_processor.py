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

        # Fill empty sex values with 'male'
        if 'sex' in processed_df.columns:
            processed_df['sex'] = processed_df['sex'].fillna('male')
        else:
            processed_df['sex'] = 'male'

        # Standardize sex values to lowercase
        processed_df['sex'] = processed_df['sex'].str.lower()

        # Get valid base exercises
        valid_base_exercises = [ex for cat in VALID_EXERCISES.values() for ex in cat]

        # Filter to keep only the specified exercises
        processed_df = processed_df[processed_df['exercise name'].isin(valid_base_exercises)].copy()

        # Standardize dominance values
        processed_df['dominance'] = processed_df['dominance'].apply(standardize_dominance)

        # Filter valid exercises and dominance combinations
        valid_rows = []
        for idx, row in processed_df.iterrows():
            if is_valid_exercise_dominance(row['exercise name'], row['dominance']):
                valid_rows.append(idx)

        processed_df = processed_df.loc[valid_rows].copy()

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