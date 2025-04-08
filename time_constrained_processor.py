"""
Time-constrained data processor for exercise test instances.
This module adds a time constraint to test instance assembly, 
requiring a minimum number of days between tests for the same exercise.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Constant for minimum days between tests
MIN_DAYS_BETWEEN_TESTS = 45

class TimeConstrainedProcessor:
    def __init__(self):
        """Initialize the time-constrained processor."""
        pass
        
    def assign_time_constrained_test_instances(self, df):
        """
        Assign test instances with a time constraint.
        
        Args:
            df: Preprocessed DataFrame with 'user name', 'full_exercise_name', 'exercise createdAt',
                'power - high', and 'acceleration - high' columns.
                
        Returns:
            Dictionary mapping user names to their processed test matrices.
        """
        # Ensure dates are datetime objects
        df['exercise createdAt'] = pd.to_datetime(df['exercise createdAt'])
        
        # Dictionary to store results
        user_matrices = {}
        
        # Process each user
        for user in df['user name'].unique():
            # Get user data and sort by date
            user_df = df[df['user name'] == user].sort_values('exercise createdAt')
            
            # Get user's sex for development calculations
            if user_df.empty:
                continue
                
            user_sex = user_df['sex'].iloc[0]
            if not isinstance(user_sex, str) or user_sex.lower() not in ['male', 'female']:
                continue
                
            # Initialize matrices for this user
            power_matrix = {}
            accel_matrix = {}
            
            # Track last test date for each exercise
            last_test_dates = {}
            
            # Track which exercises have been tested
            exercise_set = set()
            
            # Process each row for this user
            for _, row in user_df.iterrows():
                exercise = row['full_exercise_name']
                test_date = row['exercise createdAt']
                power_value = row['power - high']
                accel_value = row['acceleration - high']
                
                # Normalize names for special exercises
                if 'Vertical Jump' in exercise:
                    exercise = 'Vertical Jump (Countermovement)'
                elif 'Shot Put' in exercise:
                    exercise = 'Shot Put (Countermovement)'
                
                # Add to the set of exercises for this user
                exercise_set.add(exercise)
                
                # Only process if both power and acceleration are present
                if pd.notna(power_value) and pd.notna(accel_value):
                    # Check if this exercise has been tested before and minimum days have passed
                    last_date = last_test_dates.get(exercise)
                    
                    if last_date is None or (test_date - last_date).days >= MIN_DAYS_BETWEEN_TESTS:
                        # Find earliest available test instance for this exercise
                        target_instance = 1
                        while (target_instance in power_matrix and 
                               exercise in power_matrix[target_instance]):
                            target_instance += 1
                            
                        # Initialize new test instance if needed
                        if target_instance not in power_matrix:
                            power_matrix[target_instance] = {}
                            accel_matrix[target_instance] = {}
                            
                        # Add exercise data to matrices
                        power_matrix[target_instance][exercise] = power_value
                        accel_matrix[target_instance][exercise] = accel_value
                        
                        # Update last test date for this exercise
                        last_test_dates[exercise] = test_date
                    else:
                        # Too soon - skip this test
                        pass
            
            # Store matrices for this user
            user_matrices[user] = (power_matrix, accel_matrix, exercise_set, user_sex)
            
        return user_matrices
    
    def finalize_matrices(self, user_matrices, all_exercises):
        """
        Finalize matrices by filling in missing exercises and converting to DataFrames.
        
        Args:
            user_matrices: Dictionary of user matrices from assign_time_constrained_test_instances
            all_exercises: List of all possible exercises
            
        Returns:
            Dictionary mapping user names to their finalized matrices 
            (power_df, accel_df, user_sex)
        """
        finalized_matrices = {}
        
        for user, (power_matrix, accel_matrix, exercise_set, user_sex) in user_matrices.items():
            # Fill empty cells with NaN
            for instance in power_matrix:
                # Ensure all exercises the user has done appear in all test instances
                for exercise in exercise_set:
                    if exercise not in power_matrix[instance]:
                        power_matrix[instance][exercise] = np.nan
                    if exercise not in accel_matrix[instance]:
                        accel_matrix[instance][exercise] = np.nan
                
                # Fill remaining exercises from the all_exercises list
                for exercise in all_exercises:
                    if exercise not in power_matrix[instance]:
                        power_matrix[instance][exercise] = np.nan
                    if exercise not in accel_matrix[instance]:
                        accel_matrix[instance][exercise] = np.nan
            
            # Convert dictionaries to DataFrames
            test_instances = sorted(power_matrix.keys())
            if not test_instances:
                continue
                
            exercises = sorted(power_matrix[test_instances[0]].keys())
            
            power_df = pd.DataFrame(
                {f"Test {i}": [power_matrix[i].get(ex, np.nan) for ex in exercises] 
                for i in test_instances},
                index=exercises
            )
            
            accel_df = pd.DataFrame(
                {f"Test {i}": [accel_matrix[i].get(ex, np.nan) for ex in exercises] 
                for i in test_instances},
                index=exercises
            )
            
            finalized_matrices[user] = (power_df, accel_df, user_sex)
            
        return finalized_matrices