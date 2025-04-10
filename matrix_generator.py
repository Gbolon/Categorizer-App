import pandas as pd
import numpy as np
from exercise_constants import ALL_EXERCISES, VALID_EXERCISES
from goal_standards import calculate_development_score, get_base_exercise_name, POWER_STANDARDS, ACCELERATION_STANDARDS

class MatrixGenerator:
    def __init__(self):
        # Create a modified exercise list that includes proper handling for all exercises
        self.exercises = ALL_EXERCISES.copy()
        
        # Explicitly ensure Vertical Jump is included
        if 'Vertical Jump (Countermovement)' not in self.exercises:
            print("Adding Vertical Jump (Countermovement) to exercises list")
            self.exercises.append('Vertical Jump (Countermovement)')
            
        # Explicitly ensure Shot Put is included
        if 'Shot Put (Countermovement)' not in self.exercises:
            print("DEBUG: Adding Shot Put (Countermovement) to exercises list")
            self.exercises.append('Shot Put (Countermovement)')
            
        self.development_brackets = {
            'Goal Hit': (100, float('inf')),
            'Elite': (90, 99.99),
            'Above Average': (76, 90),
            'Average': (51, 75),
            'Under Developed': (26, 50),
            'Severely Under Developed': (0, 25)
        }
        # Define bracket order for progression analysis
        self.bracket_order = [
            'Goal Hit',
            'Elite',
            'Above Average',
            'Average',
            'Under Developed',
            'Severely Under Developed'
        ]
        
        # Store original dataframe for calculating original metrics
        self.original_df = None

    def generate_group_analysis(self, df, max_tests=4):
        """Generate group-level analysis of development categories."""
        # Initialize count DataFrames for power and acceleration
        categories = list(self.development_brackets.keys()) + ['Total Users', 'Average Development Score (%)']
        power_counts = pd.DataFrame(0, index=categories, columns=[])
        accel_counts = pd.DataFrame(0, index=categories, columns=[])

        # Initialize single test user distribution
        single_test_distribution = pd.DataFrame(0, 
            index=list(self.development_brackets.keys()) + ['Total Users'],
            columns=['Power', 'Acceleration'])

        # Track single test user averages
        single_test_power_scores = []
        single_test_accel_scores = []

        # Track multi-test user changes
        test1_to_2_power = []
        test1_to_2_accel = []
        test2_to_3_power = []
        test2_to_3_accel = []
        test3_to_4_power = []
        test3_to_4_accel = []
        
        # Track all power/acceleration scores for each test to calculate group averages
        test1_power_scores = []
        test2_power_scores = []
        test3_power_scores = []
        test4_power_scores = []
        test1_accel_scores = []
        test2_accel_scores = []
        test3_accel_scores = []
        test4_accel_scores = []

        # Initialize transition tracking for all movements
        power_transitions = {f'Test {i}-{i+1}': [] for i in range(1, max_tests)}
        accel_transitions = {f'Test {i}-{i+1}': [] for i in range(1, max_tests)}


        # Process each user
        for user in df['user name'].unique():
            # Generate matrices for user
            matrices = self.generate_user_matrices(df, user)

            if matrices[2] is not None:  # If development matrices exist
                _, _, power_dev, accel_dev, overall_dev, power_brackets, accel_brackets = matrices

                # Determine if user has multiple tests
                has_multiple_tests = len(power_brackets) >= 2

                # Update columns if needed (limited to max_tests)
                test_columns = [f"Test {i}" for i in range(1, max_tests + 1)]
                for test in test_columns:
                    if test not in power_counts.columns:
                        power_counts[test] = 0
                        accel_counts[test] = 0

                if not has_multiple_tests:
                    # Process single test users
                    if 'Test 1' in power_brackets.index and 'Test 1' in accel_brackets.index:
                        # Get overall scores from overall_dev matrix
                        power_score = overall_dev.loc['Power Average', 'Test 1']
                        accel_score = overall_dev.loc['Acceleration Average', 'Test 1']

                        # Add to single test score lists
                        if pd.notna(power_score):
                            single_test_power_scores.append(power_score)
                        if pd.notna(accel_score):
                            single_test_accel_scores.append(accel_score)

                        # Get categories for both power and acceleration
                        power_category = power_brackets.loc['Test 1', 'Category']
                        accel_category = accel_brackets.loc['Test 1', 'Category']

                        # Only count if both categories are valid
                        if (power_category in self.development_brackets and 
                            accel_category in self.development_brackets):
                            # Increment category counts
                            single_test_distribution.loc[power_category, 'Power'] += 1
                            single_test_distribution.loc[accel_category, 'Acceleration'] += 1
                            # Increment total users (same for both columns)
                            single_test_distribution.loc['Total Users', 'Power'] += 1
                            single_test_distribution.loc['Total Users', 'Acceleration'] += 1

                else:
                    # Process multi-test users
                    for test, row in power_brackets.iterrows():
                        if test in test_columns:
                            category = row['Category']
                            if category in self.development_brackets:
                                power_counts.loc[category, test] += 1

                    for test, row in accel_brackets.iterrows():
                        if test in test_columns:
                            category = row['Category']
                            if category in self.development_brackets:
                                accel_counts.loc[category, test] += 1

                    # Store test scores for calculating averages
                    # Test 1 scores
                    if 'Test 1' in overall_dev.columns:
                        power_1 = overall_dev.loc['Power Average', 'Test 1']
                        accel_1 = overall_dev.loc['Acceleration Average', 'Test 1']
                        
                        if pd.notna(power_1):
                            test1_power_scores.append(power_1)
                        if pd.notna(accel_1):
                            test1_accel_scores.append(accel_1)
                    
                    # Test 2 scores
                    if 'Test 2' in overall_dev.columns:
                        power_2 = overall_dev.loc['Power Average', 'Test 2']
                        accel_2 = overall_dev.loc['Acceleration Average', 'Test 2']
                        
                        if pd.notna(power_2):
                            test2_power_scores.append(power_2)
                        if pd.notna(accel_2):
                            test2_accel_scores.append(accel_2)
                    
                    # Test 3 scores
                    if 'Test 3' in overall_dev.columns:
                        power_3 = overall_dev.loc['Power Average', 'Test 3']
                        accel_3 = overall_dev.loc['Acceleration Average', 'Test 3']
                        
                        if pd.notna(power_3):
                            test3_power_scores.append(power_3)
                        if pd.notna(accel_3):
                            test3_accel_scores.append(accel_3)
                    
                    # Test 4 scores
                    if 'Test 4' in overall_dev.columns:
                        power_4 = overall_dev.loc['Power Average', 'Test 4']
                        accel_4 = overall_dev.loc['Acceleration Average', 'Test 4']
                        
                        if pd.notna(power_4):
                            test4_power_scores.append(power_4)
                        if pd.notna(accel_4):
                            test4_accel_scores.append(accel_4)
                    
                    # Calculate changes between tests for Test 1-2
                    if 'Test 1' in overall_dev.columns and 'Test 2' in overall_dev.columns:
                        power_1 = overall_dev.loc['Power Average', 'Test 1']
                        power_2 = overall_dev.loc['Power Average', 'Test 2']
                        accel_1 = overall_dev.loc['Acceleration Average', 'Test 1']
                        accel_2 = overall_dev.loc['Acceleration Average', 'Test 2']

                        if pd.notna(power_1) and pd.notna(power_2):
                            power_change_1_2 = power_2 - power_1
                            test1_to_2_power.append(power_change_1_2)

                        if pd.notna(accel_1) and pd.notna(accel_2):
                            accel_change_1_2 = accel_2 - accel_1
                            test1_to_2_accel.append(accel_change_1_2)

                    # Calculate changes between tests for Test 2-3
                    if 'Test 2' in overall_dev.columns and 'Test 3' in overall_dev.columns:
                        power_2 = overall_dev.loc['Power Average', 'Test 2']
                        power_3 = overall_dev.loc['Power Average', 'Test 3']
                        accel_2 = overall_dev.loc['Acceleration Average', 'Test 2']
                        accel_3 = overall_dev.loc['Acceleration Average', 'Test 3']

                        if pd.notna(power_2) and pd.notna(power_3):
                            power_change_2_3 = power_3 - power_2
                            test2_to_3_power.append(power_change_2_3)

                        if pd.notna(accel_2) and pd.notna(accel_3):
                            accel_change_2_3 = accel_3 - accel_2
                            test2_to_3_accel.append(accel_change_2_3)
                            
                    # Calculate changes between tests for Test 3-4
                    if 'Test 3' in overall_dev.columns and 'Test 4' in overall_dev.columns:
                        power_3 = overall_dev.loc['Power Average', 'Test 3']
                        power_4 = overall_dev.loc['Power Average', 'Test 4']
                        accel_3 = overall_dev.loc['Acceleration Average', 'Test 3']
                        accel_4 = overall_dev.loc['Acceleration Average', 'Test 4']

                        if pd.notna(power_3) and pd.notna(power_4):
                            power_change_3_4 = power_4 - power_3
                            test3_to_4_power.append(power_change_3_4)

                        if pd.notna(accel_3) and pd.notna(accel_4):
                            accel_change_3_4 = accel_4 - accel_3
                            test3_to_4_accel.append(accel_change_3_4)

                    # Increment total users once for all test columns
                    for test in test_columns:
                        if test in power_brackets.index:
                            power_counts.loc['Total Users', test] += 1
                        if test in accel_brackets.index:
                            accel_counts.loc['Total Users', test] += 1

                    # Process transitions for multi-test users
                    # Store current user name for regression tracking
                    current_user = user
                    for i in range(len(test_columns)-1):
                        current_test = test_columns[i]
                        next_test = test_columns[i+1]
                        transition_col = f'Test {i+1}-{i+2}'

                        # Power transitions
                        if current_test in power_brackets.index and next_test in power_brackets.index:
                            current_cat = power_brackets.loc[current_test, 'Category']
                            next_cat = power_brackets.loc[next_test, 'Category']
                            self._update_progression_counts(
                                current_cat, next_cat,
                                transition_col,
                                power_transitions[transition_col],
                                current_user
                            )

                        # Acceleration transitions
                        if current_test in accel_brackets.index and next_test in accel_brackets.index:
                            current_cat = accel_brackets.loc[current_test, 'Category']
                            next_cat = accel_brackets.loc[next_test, 'Category']
                            self._update_progression_counts(
                                current_cat, next_cat,
                                transition_col,
                                accel_transitions[transition_col],
                                current_user
                            )

        # Calculate actual averages for single test users
        power_average = np.mean(single_test_power_scores) if single_test_power_scores else 0
        accel_average = np.mean(single_test_accel_scores) if single_test_accel_scores else 0

        # Generate detailed transition matrices and track regression users
        power_transitions_detail, power_regression_users = self._analyze_detailed_transitions(power_transitions)
        accel_transitions_detail, accel_regression_users = self._analyze_detailed_transitions(accel_transitions)

        # Calculate time differences between tests for the same movement
        # For filtered dataframe, only calculate constrained days (since it's already filtered)
        constrained_time_differences = []
        for user in df['user name'].unique():
            user_data = df[df['user name'] == user].copy()
            if len(user_data) > 1:
                # Group by exercise and calculate time differences within each exercise
                for exercise in user_data['full_exercise_name'].unique():
                    exercise_data = user_data[user_data['full_exercise_name'] == exercise]
                    if len(exercise_data) > 1:
                        # Sort by timestamp
                        exercise_data = exercise_data.sort_values('exercise createdAt')
                        # Calculate differences in days
                        time_diffs = exercise_data['exercise createdAt'].diff().dropna().dt.days
                        constrained_time_differences.extend(time_diffs.tolist())
        
        # If min_days filter was applied, this will naturally be higher or equal to the overall average
        avg_constrained_days = np.mean(constrained_time_differences) if constrained_time_differences else 0
        
        # Get original dataset from the class instance to calculate original average days
        if hasattr(self, 'original_df') and self.original_df is not None:
            # Calculate the original time differences (from unfiltered data)
            time_differences = []
            for user in self.original_df['user name'].unique():
                user_data = self.original_df[self.original_df['user name'] == user].copy()
                if len(user_data) > 1:
                    # Group by exercise and calculate time differences within each exercise
                    for exercise in user_data['full_exercise_name'].unique():
                        exercise_data = user_data[user_data['full_exercise_name'] == exercise]
                        if len(exercise_data) > 1:
                            # Sort by timestamp
                            exercise_data = exercise_data.sort_values('exercise createdAt')
                            # Calculate differences in days
                            time_diffs = exercise_data['exercise createdAt'].diff().dropna().dt.days
                            time_differences.extend(time_diffs.tolist())
            
            avg_days_between_tests = np.mean(time_differences) if time_differences else 0
        else:
            # If no original data stored, use the current dataframe (happens on first run)
            avg_days_between_tests = avg_constrained_days

        # Calculate average changes
        avg_power_change_1_2 = np.mean(test1_to_2_power) if test1_to_2_power else 0
        avg_accel_change_1_2 = np.mean(test1_to_2_accel) if test1_to_2_accel else 0
        avg_power_change_2_3 = np.mean(test2_to_3_power) if test2_to_3_power else 0
        avg_accel_change_2_3 = np.mean(test2_to_3_accel) if test2_to_3_accel else 0
        avg_power_change_3_4 = np.mean(test3_to_4_power) if test3_to_4_power else 0
        avg_accel_change_3_4 = np.mean(test3_to_4_accel) if test3_to_4_accel else 0
        
        # Calculate average scores for each test and update the distribution tables
        avg_power_test1 = np.mean(test1_power_scores) if test1_power_scores else 0
        avg_power_test2 = np.mean(test2_power_scores) if test2_power_scores else 0
        avg_power_test3 = np.mean(test3_power_scores) if test3_power_scores else 0
        avg_power_test4 = np.mean(test4_power_scores) if test4_power_scores else 0
        
        avg_accel_test1 = np.mean(test1_accel_scores) if test1_accel_scores else 0
        avg_accel_test2 = np.mean(test2_accel_scores) if test2_accel_scores else 0
        avg_accel_test3 = np.mean(test3_accel_scores) if test3_accel_scores else 0
        avg_accel_test4 = np.mean(test4_accel_scores) if test4_accel_scores else 0
        
        # Update the Average Development Score row in each distribution table
        if 'Test 1' in power_counts.columns:
            power_counts.loc['Average Development Score (%)', 'Test 1'] = avg_power_test1
        if 'Test 2' in power_counts.columns:
            power_counts.loc['Average Development Score (%)', 'Test 2'] = avg_power_test2
        if 'Test 3' in power_counts.columns:
            power_counts.loc['Average Development Score (%)', 'Test 3'] = avg_power_test3
        if 'Test 4' in power_counts.columns:
            power_counts.loc['Average Development Score (%)', 'Test 4'] = avg_power_test4
            
        if 'Test 1' in accel_counts.columns:
            accel_counts.loc['Average Development Score (%)', 'Test 1'] = avg_accel_test1
        if 'Test 2' in accel_counts.columns:
            accel_counts.loc['Average Development Score (%)', 'Test 2'] = avg_accel_test2
        if 'Test 3' in accel_counts.columns:
            accel_counts.loc['Average Development Score (%)', 'Test 3'] = avg_accel_test3
        if 'Test 4' in accel_counts.columns:
            accel_counts.loc['Average Development Score (%)', 'Test 4'] = avg_accel_test4

        return (power_counts, accel_counts, single_test_distribution,
                power_transitions_detail, accel_transitions_detail,
                power_average, accel_average,
                avg_power_change_1_2, avg_accel_change_1_2,
                avg_power_change_2_3, avg_accel_change_2_3,
                avg_power_change_3_4, avg_accel_change_3_4,
                avg_days_between_tests, avg_constrained_days,
                power_regression_users, accel_regression_users)

    def _update_progression_counts(self, current_cat, next_cat, col, transitions_list, user_name=None):
        """Update progression counts based on category changes."""
        if current_cat and next_cat and pd.notna(current_cat) and pd.notna(next_cat):
            try:
                # Record the transition for detailed analysis with user name if provided
                if user_name:
                    transitions_list.append((current_cat, next_cat, user_name))
                else:
                    transitions_list.append((current_cat, next_cat))

            except ValueError:
                # Skip if category is not in bracket_order
                pass

    def _analyze_detailed_transitions(self, transitions_dict):
        """
        Create a transition matrix where:
        - Diagonal cells (no change) are Pale Blue
        - Above the diagonal (regression) is Pale Red
        - Below the diagonal (improvement) is Pale Green
        """
        transition_matrices = {}
        regression_users_dict = {}

        for period, transitions in transitions_dict.items():
            # Create an empty transition matrix
            matrix = pd.DataFrame(0, 
                index=self.bracket_order,
                columns=self.bracket_order)
                
            # Track users who regressed
            regression_users = []

            # Count transitions from each bracket to another and track regressions
            for transition in transitions:
                if len(transition) == 3:
                    from_bracket, to_bracket, user_name = transition
                    
                    # Check if this is a regression (moving from better to worse category)
                    if (from_bracket in self.bracket_order and to_bracket in self.bracket_order and
                        self.bracket_order.index(from_bracket) < self.bracket_order.index(to_bracket)):
                        regression_users.append((user_name, from_bracket, to_bracket))
                    
                    # Update the matrix count
                    if from_bracket in self.bracket_order and to_bracket in self.bracket_order:
                        matrix.loc[from_bracket, to_bracket] += 1
                else:
                    # Handle old format data without user names
                    from_bracket, to_bracket = transition
                    if from_bracket in self.bracket_order and to_bracket in self.bracket_order:
                        matrix.loc[from_bracket, to_bracket] += 1
            
            # Store regression users for this period
            regression_users_dict[period] = regression_users

            # Function to apply background color based on cell position
            def highlight_cells(dataframe):
                styles = pd.DataFrame("", index=dataframe.index, columns=dataframe.columns)

                for i in range(len(dataframe)):  # Row index
                    for j in range(len(dataframe.columns)):  # Column index
                        base_style = "color: black; font-weight: bold; "
                        if i == j:  # Diagonal (No movement)
                            styles.iloc[i, j] = base_style + "background-color: lightblue;"
                        elif i < j:  # Above diagonal (Regression)
                            styles.iloc[i, j] = base_style + "background-color: lightcoral;"  # Pale Red
                        else:  # Below diagonal (Improvement)
                            styles.iloc[i, j] = base_style + "background-color: lightgreen;"  # Pale Green

                return styles

            # Create a new MultiIndex for the columns with centered text
            col_index = pd.MultiIndex.from_tuples([
                ('Ending Bracket', col) for col in matrix.columns
            ])
            matrix.columns = col_index

            # Apply static color formatting, number formatting, and header styling to the DataFrame
            styled_matrix = (matrix.style
                           .format("{:.0f}")
                           .apply(highlight_cells, axis=None)
                           .set_table_styles([
                               {
                                   'selector': 'th.col_heading.level0',
                                   'props': [('text-align', 'center'), 
                                            ('font-weight', 'bold'),
                                            ('background-color', '#f0f0f0'),
                                            ('color', '#333333')]
                               },
                               {
                                   'selector': 'th.col_heading.level1',
                                   'props': [('text-align', 'center')]
                               }
                           ]))

            transition_matrices[period] = styled_matrix

        return transition_matrices, regression_users_dict

    def _analyze_transition_patterns(self, transitions_dict):
        """Analyze common transition patterns for level ups."""
        patterns_df = pd.DataFrame(columns=['Most Common From', 'Most Common To', 'Count'])

        for period, transitions in transitions_dict.items():
            if transitions:
                # Count frequency of each transition pattern
                transition_counts = {}
                for transition in transitions:
                    # Handle transitions with or without user name
                    if len(transition) == 3:
                        from_bracket, to_bracket, _ = transition
                    else:
                        from_bracket, to_bracket = transition
                        
                    key = (from_bracket, to_bracket)
                    transition_counts[key] = transition_counts.get(key, 0) + 1

                # Find most common transition
                if transition_counts:
                    most_common = max(transition_counts.items(), key=lambda x: x[1])
                    patterns_df.loc[period] = [
                        most_common[0][0],  # From bracket
                        most_common[0][1],  # To bracket
                        most_common[1]      # Count
                    ]
                else:
                    patterns_df.loc[period] = ['No level ups', 'No level ups', 0]
            else:
                patterns_df.loc[period] = ['No level ups', 'No level ups', 0]

        return patterns_df

    def generate_user_matrices(self, df, user_name):
        """Generate test instance matrices for a specific user."""
        user_data = df[df['user name'] == user_name].copy()

        # Initialize matrices
        power_matrix = {}
        accel_matrix = {}
        test_instances = {}
        
        # Explicitly track if Vertical Jump is present for this user
        has_vertical_jump = False

        # Get user's sex for development calculations
        if user_data.empty:
            return power_matrix, accel_matrix, None, None, None, None, None

        user_sex = user_data['sex'].iloc[0]
        if not isinstance(user_sex, str) or user_sex.lower() not in ['male', 'female']:
            return power_matrix, accel_matrix, None, None, None, None, None

        # Debug for Shot Put and Vertical Jump exercises
        shot_put_exercises = user_data[user_data['full_exercise_name'].str.contains('Shot Put', na=False)]
        if not shot_put_exercises.empty:
            print(f"Debug: User '{user_name}' has {len(shot_put_exercises)} Shot Put exercises")
            for _, row in shot_put_exercises.iterrows():
                print(f"Debug: Shot Put Exercise: {row['full_exercise_name']}, Power: {row['power - high']}, Accel: {row['acceleration - high']}")
                
        vertical_jump_exercises = user_data[user_data['full_exercise_name'].str.contains('Vertical Jump', na=False)]
        if not vertical_jump_exercises.empty:
            print(f"Debug: User '{user_name}' has {len(vertical_jump_exercises)} Vertical Jump exercises")
            has_vertical_jump = True  # Mark that user has Vertical Jump exercises
            for _, row in vertical_jump_exercises.iterrows():
                print(f"Debug: Vertical Jump Exercise: {row['full_exercise_name']}, Power: {row['power - high']}, Accel: {row['acceleration - high']}")

        # Debug for Press/Pull exercises
        press_pull_exercises = user_data[user_data['full_exercise_name'].str.contains('Horizontal Row|Chest Press', na=False)]
        if not press_pull_exercises.empty:
            print(f"Debug: User '{user_name}' has {len(press_pull_exercises)} Press/Pull exercises")
            for _, row in press_pull_exercises.iterrows():
                print(f"Debug: Exercise: {row['full_exercise_name']}, Power: {row['power - high']}, Accel: {row['acceleration - high']}")

        # Process each exercise chronologically and keep power/acceleration paired
        for _, row in user_data.iterrows():
            exercise = row['full_exercise_name']
            power_value = row['power - high']
            accel_value = row['acceleration - high']
            
            # For Vertical Jump, ensure we use the standard name without dominance
            if 'Vertical Jump' in exercise:
                # Normalize to use just the base name for Vertical Jump
                exercise = 'Vertical Jump (Countermovement)'
                has_vertical_jump = True  # Mark that user has Vertical Jump exercises
                print(f"Debug: Standardizing Vertical Jump name to: {exercise}")
                
            # For Shot Put, ensure we use the standard name
            if 'Shot Put' in exercise:
                # Normalize to use just the base name for Shot Put
                exercise = 'Shot Put (Countermovement)'
                print(f"DEBUG: Standardizing Shot Put name to: {exercise}")
            
            # Debug Shot Put and Vertical Jump exercises
            if 'Shot Put' in exercise:
                print(f"DEBUG: Processing Shot Put for {user_name} - Exercise: {exercise}, Power: {power_value}, Accel: {accel_value}")
            elif 'Vertical Jump' in exercise:
                print(f"Debug: Processing Vertical Jump for {user_name} - Exercise: {exercise}, Power: {power_value}, Accel: {accel_value}")
            # Debug Press/Pull exercises
            elif 'Horizontal Row' in exercise or 'Chest Press' in exercise:
                print(f"Debug: Processing Press/Pull for {user_name} - Exercise: {exercise}, Power: {power_value}, Accel: {accel_value}")

            # Only process if both power and acceleration are present
            if pd.notna(power_value) and pd.notna(accel_value):
                # Find earliest available test instance for this exercise
                target_instance = 1
                while target_instance in test_instances and exercise in test_instances[target_instance]:
                    target_instance += 1

                # Initialize new test instance if needed
                if target_instance not in power_matrix:
                    power_matrix[target_instance] = {}
                    accel_matrix[target_instance] = {}
                    test_instances[target_instance] = set()

                # Add exercise data to matrices as a pair
                power_matrix[target_instance][exercise] = power_value
                accel_matrix[target_instance][exercise] = accel_value
                test_instances[target_instance].add(exercise)
                
                # Debug Shot Put and Vertical Jump exercises
                if 'Shot Put' in exercise:
                    print(f"Debug: Added Shot Put to matrices - Test {target_instance}, Exercise: {exercise}, Power: {power_value}, Accel: {accel_value}")
                elif 'Vertical Jump' in exercise:
                    print(f"Debug: Added Vertical Jump to matrices - Test {target_instance}, Exercise: {exercise}, Power: {power_value}, Accel: {accel_value}")
                # Debug Press/Pull exercises
                elif 'Horizontal Row' in exercise or 'Chest Press' in exercise:
                    print(f"Debug: Added to matrices - Test {target_instance}, Exercise: {exercise}, Power: {power_value}, Accel: {accel_value}")

        # Check for Vertical Jump in the matrices
        has_vertical_jump = False
        for instance in power_matrix:
            if 'Vertical Jump (Countermovement)' in power_matrix[instance]:
                has_vertical_jump = True
                break
        
        # Check for Shot Put in the matrices
        has_shot_put = False
        for instance in power_matrix:
            if 'Shot Put (Countermovement)' in power_matrix[instance]:
                has_shot_put = True
                print(f"DEBUG: Shot Put found in power_matrix[{instance}] with value: {power_matrix[instance]['Shot Put (Countermovement)']}")
                break
        
        # Fill empty cells with NaN
        for instance in power_matrix:
            # Ensure Vertical Jump is added if it exists for this user
            if has_vertical_jump and 'Vertical Jump (Countermovement)' not in power_matrix[instance]:
                power_matrix[instance]['Vertical Jump (Countermovement)'] = np.nan
                accel_matrix[instance]['Vertical Jump (Countermovement)'] = np.nan
                
            # Ensure Shot Put is added if it exists for this user
            if has_shot_put and 'Shot Put (Countermovement)' not in power_matrix[instance]:
                print(f"DEBUG: Adding Shot Put placeholder to instance {instance}")
                power_matrix[instance]['Shot Put (Countermovement)'] = np.nan
                accel_matrix[instance]['Shot Put (Countermovement)'] = np.nan
                
            # Fill remaining exercises from the exercises list
            for exercise in self.exercises:
                if exercise not in power_matrix[instance]:
                    power_matrix[instance][exercise] = np.nan
                if exercise not in accel_matrix[instance]:
                    accel_matrix[instance][exercise] = np.nan

        # Convert to DataFrames
        result = self._convert_to_dataframes(power_matrix, accel_matrix)
        power_df, accel_df = result

        # Generate development matrices if sex is available
        power_dev_df = self._calculate_development_matrix(power_df, user_sex, 'power')
        accel_dev_df = self._calculate_development_matrix(accel_df, user_sex, 'acceleration')

        # Calculate overall development categorization
        overall_dev_df = self._calculate_overall_development(power_dev_df, accel_dev_df)

        # Add bracketing information
        power_brackets = self._categorize_development(power_dev_df)
        accel_brackets = self._categorize_development(accel_dev_df)

        return power_df, accel_df, power_dev_df, accel_dev_df, overall_dev_df, power_brackets, accel_brackets

    def _convert_to_dataframes(self, power_matrix, accel_matrix):
        """Convert dictionary matrices to pandas DataFrames."""
        # Get all exercises present in the matrices
        all_matrix_exercises = set()
        for instance in power_matrix:
            all_matrix_exercises.update(power_matrix[instance].keys())
        for instance in accel_matrix:
            all_matrix_exercises.update(accel_matrix[instance].keys())
            
        # Create a combined exercise list that includes both the predefined list and anything in the matrices
        combined_exercises = list(self.exercises)
        for exercise in all_matrix_exercises:
            if exercise not in combined_exercises:
                print(f"DEBUG: Adding matrix exercise to combined list: {exercise}")
                combined_exercises.append(exercise)
                
        # Explicitly ensure Vertical Jump is in the combined list
        if 'Vertical Jump (Countermovement)' not in combined_exercises:
            print(f"DEBUG: Explicitly adding Vertical Jump to combined exercises list")
            combined_exercises.append('Vertical Jump (Countermovement)')
            
        # Explicitly ensure Shot Put is in the combined list
        if 'Shot Put (Countermovement)' not in combined_exercises:
            print(f"DEBUG: Explicitly adding Shot Put to combined exercises list")
            combined_exercises.append('Shot Put (Countermovement)')
            
        # Debug what's in the matrices for Vertical Jump
        for instance in power_matrix:
            if 'Vertical Jump (Countermovement)' in power_matrix[instance]:
                print(f"DEBUG: Vertical Jump found in power_matrix[{instance}] with value: {power_matrix[instance]['Vertical Jump (Countermovement)']}")
                
        # Debug what's in the matrices for Shot Put
        for instance in power_matrix:
            if 'Shot Put (Countermovement)' in power_matrix[instance]:
                print(f"DEBUG: Shot Put found in power_matrix[{instance}] with value: {power_matrix[instance]['Shot Put (Countermovement)']}")
        
        # Create DataFrame for power with the combined exercise list
        power_df = pd.DataFrame(power_matrix)
        power_df = power_df.reindex(combined_exercises)
        power_df.columns = [f"Test {i}" for i in range(1, len(power_df.columns) + 1)]

        # Create DataFrame for acceleration with the combined exercise list
        accel_df = pd.DataFrame(accel_matrix)
        accel_df = accel_df.reindex(combined_exercises)
        accel_df.columns = [f"Test {i}" for i in range(1, len(accel_df.columns) + 1)]
        
        return power_df, accel_df

    def _calculate_development_matrix(self, metric_df, sex, metric_type):
        """Calculate development scores for each value in the matrix."""
        dev_matrix = metric_df.copy()
        
        # Special debugging for development matrix calculation
        print(f"DEBUG: Calculating {metric_type} development matrix with sex={sex}")
        print(f"DEBUG: Input matrix has shape {metric_df.shape} with columns {metric_df.columns.tolist()}")
        print(f"DEBUG: Input matrix index/exercises: {metric_df.index.tolist()}")
        
        # Check for Vertical Jump
        if 'Vertical Jump (Countermovement)' in metric_df.index:
            print(f"DEBUG: Vertical Jump IS in input matrix with values: {metric_df.loc['Vertical Jump (Countermovement)'].values}")
        else:
            print(f"DEBUG: Vertical Jump NOT found in input matrix!")
            
        # Check for Shot Put
        if 'Shot Put (Countermovement)' in metric_df.index:
            print(f"DEBUG: Shot Put IS in input matrix with values: {metric_df.loc['Shot Put (Countermovement)'].values}")
        else:
            print(f"DEBUG: Shot Put NOT found in input matrix!")

        # Calculate development scores
        for col in dev_matrix.columns:
            for idx in dev_matrix.index:
                value = metric_df.loc[idx, col]
                base_exercise = get_base_exercise_name(idx)
                dev_score = calculate_development_score(value, idx, sex, metric_type)
                
                # Debug specific exercises
                if 'Vertical Jump' in idx:
                    print(f"DEBUG: Calculating development score for {idx}, value={value}, base={base_exercise}")
                    print(f"DEBUG: Development score result: {dev_score}")
                    
                    # Add extra check for standards lookup
                    standards = POWER_STANDARDS if metric_type == 'power' else ACCELERATION_STANDARDS
                    if sex in standards and base_exercise in standards[sex]:
                        goal_std = standards[sex][base_exercise]
                        print(f"DEBUG: Found goal standard: {goal_std}")
                    else:
                        print(f"DEBUG: No goal standard found for {base_exercise} in {sex} {metric_type} standards")
                
                # Debug Shot Put specifically
                if 'Shot Put' in idx:
                    print(f"DEBUG: Calculating development score for {idx}, value={value}, base={base_exercise}")
                    print(f"DEBUG: Development score result: {dev_score}")
                    
                    # Add extra check for standards lookup
                    standards = POWER_STANDARDS if metric_type == 'power' else ACCELERATION_STANDARDS
                    if sex in standards and base_exercise in standards[sex]:
                        goal_std = standards[sex][base_exercise]
                        print(f"DEBUG: Found goal standard for Shot Put: {goal_std}")
                    else:
                        print(f"DEBUG: No goal standard found for Shot Put {base_exercise} in {sex} {metric_type} standards")
                
                dev_matrix.loc[idx, col] = dev_score

        # Check for Vertical Jump in output
        if 'Vertical Jump (Countermovement)' in dev_matrix.index:
            print(f"DEBUG: Vertical Jump IS in development matrix with values: {dev_matrix.loc['Vertical Jump (Countermovement)'].values}")
        else:
            print(f"DEBUG: Vertical Jump STILL NOT in development matrix after calculation!")
            
        # Check for Shot Put in output
        if 'Shot Put (Countermovement)' in dev_matrix.index:
            print(f"DEBUG: Shot Put IS in development matrix with values: {dev_matrix.loc['Shot Put (Countermovement)'].values}")
        else:
            print(f"DEBUG: Shot Put NOT in development matrix after calculation!")

        return dev_matrix

    def _calculate_overall_development(self, power_dev_df, accel_dev_df):
        """Calculate overall development categorization for each test instance."""
        # Create data structure to store calculated values
        overall_data = {}

        # Calculate averages for each test instance
        for col in power_dev_df.columns:
            # Calculate power average (excluding NaN values)
            power_avg = power_dev_df[col].apply(lambda x: min(x, 100) if pd.notnull(x) else x).mean(skipna=True)

            # Calculate acceleration average (excluding NaN values)
            accel_avg = accel_dev_df[col].apply(lambda x: min(x, 100) if pd.notnull(x) else x).mean(skipna=True)

            # Calculate overall average
            overall_avg = np.mean([power_avg, accel_avg])

            # Store values in dictionary
            overall_data[col] = [power_avg, accel_avg, overall_avg]

        # Create the DataFrame all at once to avoid fragmentation
        overall_dev = pd.DataFrame(
            overall_data,
            index=['Power Average', 'Acceleration Average', 'Overall Average']
        )

        return overall_dev

    def _categorize_development(self, dev_matrix):
        """Categorize development scores into brackets."""
        # Initialize DataFrame for bracketing
        brackets_df = pd.DataFrame(index=dev_matrix.columns, columns=['Category', 'Score'])

        # Calculate overall average for each test instance (capped at 100%)
        test_averages = dev_matrix.apply(
            lambda x: x.apply(lambda y: min(y, 100) if pd.notnull(y) else y).mean(skipna=True)
        )

        # Categorize each test instance
        for test in test_averages.index:
            score = test_averages[test]
            if pd.isna(score):
                brackets_df.loc[test, 'Category'] = None
                brackets_df.loc[test, 'Score'] = 'N/A'
                continue

            for category, (min_val, max_val) in self.development_brackets.items():
                if min_val <= score <= max_val:
                    brackets_df.loc[test, 'Category'] = category
                    brackets_df.loc[test, 'Score'] = f"{score:.1f}%"
                    break

        return brackets_df

    def calculate_body_region_averages(self, df, max_tests=4):
        """Calculate average development scores by body region for multi-test users."""
        from exercise_constants import VALID_EXERCISES

        # Initialize results dictionary
        body_region_averages = {
            region: pd.DataFrame(
                0.0,  # Initialize with float instead of int
                index=['Power Average', 'Acceleration Average'],
                columns=[f'Test {i}' for i in range(1, max_tests + 1)]
            ) for region in VALID_EXERCISES.keys()
        }

        # Track number of users per test for each region
        users_per_test = {
            region: {f'Test {i}': 0 for i in range(1, max_tests + 1)}
            for region in VALID_EXERCISES.keys()
        }

        # Process each user
        for user in df['user name'].unique():
            # Generate matrices for user
            matrices = self.generate_user_matrices(df, user)
            if matrices[2] is not None:  # If development matrices exist
                power_dev, accel_dev = matrices[2], matrices[3]  # Get development matrices

                # Only process multi-test users
                if len(power_dev.columns) >= 2:
                    # Process each body region
                    for region, exercises in VALID_EXERCISES.items():
                        # Only process up to max_tests columns
                        test_cols = [col for col in power_dev.columns if int(col.split()[-1]) <= max_tests]

                        for test_col in test_cols:
                            # Get relevant exercises for this region (including dominance variations)
                            region_exercises = []
                            for exercise in exercises:
                                matching_exercises = [ex for ex in power_dev.index if exercise in ex]
                                region_exercises.extend(matching_exercises)

                            # Calculate averages for this region if data exists
                            power_scores = power_dev.loc[region_exercises, test_col].dropna()
                            accel_scores = accel_dev.loc[region_exercises, test_col].dropna()

                            if not power_scores.empty or not accel_scores.empty:
                                # Calculate means only if we have valid scores
                                if not power_scores.empty:
                                    power_mean = power_scores.mean()
                                    if pd.notna(power_mean):
                                        body_region_averages[region].loc['Power Average', test_col] += power_mean
                                if not accel_scores.empty:
                                    accel_mean = accel_scores.mean()
                                    if pd.notna(accel_mean):
                                        body_region_averages[region].loc['Acceleration Average', test_col] += accel_mean
                                users_per_test[region][test_col] += 1

        # Calculate final averages
        for region in VALID_EXERCISES.keys():
            for test in body_region_averages[region].columns:
                n_users = users_per_test[region][test]
                if n_users > 0:
                    body_region_averages[region][test] = body_region_averages[region][test] / n_users
                else:
                    body_region_averages[region][test] = np.nan

        return body_region_averages
        
    def calculate_test_changes(self, data_df, include_users=False):
        """
        Calculate average changes between tests for the provided DataFrame.
        
        Args:
            data_df: DataFrame containing test values
            include_users: Whether to include user-specific data for identifying underperformers
            
        Returns:
            Dictionary with change metrics and lists of underperforming users if requested
        """
        changes = {}
        
        # Calculate Test 1 to Test 2 changes
        if 'Test 1' in data_df.columns and 'Test 2' in data_df.columns:
            # Get valid rows (non-NaN in both columns)
            valid_rows = data_df[data_df['Test 1'].notna() & data_df['Test 2'].notna()]
            if not valid_rows.empty:
                # Calculate changes
                changes['test1_to_test2'] = (valid_rows['Test 2'] - valid_rows['Test 1']).mean()
                changes['test1_to_test2_pct'] = ((valid_rows['Test 2'] - valid_rows['Test 1']) / valid_rows['Test 1'] * 100).mean()
                # Store individual user changes for improvement threshold
                changes['test1_to_test2_individual'] = (valid_rows['Test 2'] - valid_rows['Test 1']) / valid_rows['Test 1'] * 100
                
                # If requested, track underperforming users
                if include_users and 'User' in valid_rows.index.names:
                    threshold = changes['test1_to_test2_pct']
                    underperformers = []
                    for user in valid_rows.index.get_level_values('User').unique():
                        user_rows = valid_rows.xs(user, level='User', drop_level=False)
                        if not user_rows.empty:
                            user_change_pct = ((user_rows['Test 2'] - user_rows['Test 1']) / user_rows['Test 1'] * 100).mean()
                            if user_change_pct < threshold:
                                underperformers.append((user, user_change_pct))
                    changes['underperformers_1_to_2'] = sorted(underperformers, key=lambda x: x[1])
            else:
                changes['test1_to_test2'] = np.nan
                changes['test1_to_test2_pct'] = np.nan
                changes['test1_to_test2_individual'] = pd.Series()
                if include_users:
                    changes['underperformers_1_to_2'] = []
        
        # Calculate Test 2 to Test 3 changes
        if 'Test 2' in data_df.columns and 'Test 3' in data_df.columns:
            # Get valid rows (non-NaN in both columns)
            valid_rows = data_df[data_df['Test 2'].notna() & data_df['Test 3'].notna()]
            if not valid_rows.empty:
                # Calculate changes
                changes['test2_to_test3'] = (valid_rows['Test 3'] - valid_rows['Test 2']).mean()
                changes['test2_to_test3_pct'] = ((valid_rows['Test 3'] - valid_rows['Test 2']) / valid_rows['Test 2'] * 100).mean()
                # Store individual user changes for improvement threshold
                changes['test2_to_test3_individual'] = (valid_rows['Test 3'] - valid_rows['Test 2']) / valid_rows['Test 2'] * 100
                
                # If requested, track underperforming users
                if include_users and 'User' in valid_rows.index.names:
                    threshold = changes['test2_to_test3_pct']
                    underperformers = []
                    for user in valid_rows.index.get_level_values('User').unique():
                        user_rows = valid_rows.xs(user, level='User', drop_level=False)
                        if not user_rows.empty:
                            user_change_pct = ((user_rows['Test 3'] - user_rows['Test 2']) / user_rows['Test 2'] * 100).mean()
                            if user_change_pct < threshold:
                                underperformers.append((user, user_change_pct))
                    changes['underperformers_2_to_3'] = sorted(underperformers, key=lambda x: x[1])
            else:
                changes['test2_to_test3'] = np.nan
                changes['test2_to_test3_pct'] = np.nan
                changes['test2_to_test3_individual'] = pd.Series()
                if include_users:
                    changes['underperformers_2_to_3'] = []
        
        return changes
            
    def get_region_metrics(self, df, region_name, max_tests=4):
        """
        Calculate detailed power and acceleration metrics for the specified body region exercises.
        Only includes multi-test users with separate metrics for power and acceleration.
        
        Args:
            df: The processed dataframe
            region_name: The name of the body region (e.g., 'Torso', 'Arms', etc.)
            max_tests: Maximum number of tests to include
            
        Returns:
            Tuple containing:
            - power_df: DataFrame with power development values
            - accel_df: DataFrame with acceleration development values
            - power_changes: Dictionary with power change metrics
            - accel_changes: Dictionary with acceleration change metrics
            - lowest_power_change_exercise: Exercise name with lowest power change
            - lowest_power_change_value: Value of the lowest power change
            - lowest_accel_change_exercise: Exercise name with lowest acceleration change
            - lowest_accel_change_value: Value of the lowest acceleration change
        """
        # Import constants
        from exercise_constants import VALID_EXERCISES
        
        # Get region exercises
        region_exercises = VALID_EXERCISES.get(region_name, [])
        
        if not region_exercises:
            # Return None values for all 8 return values
            return None, None, None, None, None, None, None, None  # Return None if region not found
        
        # Always include Vertical Jump in correct region
        vertical_jump_name = 'Vertical Jump (Countermovement)'
        if region_name == 'Legs' and vertical_jump_name not in region_exercises:
            print(f"Debug: Explicitly adding Vertical Jump to region_exercises for Legs region")
            region_exercises.append(vertical_jump_name)
            
        # Always include Shot Put in Torso region
        shot_put_name = 'Shot Put (Countermovement)'
        if region_name == 'Torso' and shot_put_name not in region_exercises:
            print(f"DEBUG: Explicitly adding Shot Put to region_exercises for Torso region")
            region_exercises.append(shot_put_name)
        
        # Get all exercise variations including dominance
        variations = []
        for exercise in region_exercises:
            print(f"DEBUG: Finding variations for '{exercise}' in region {region_name}")
            # Include base exercises
            if exercise == vertical_jump_name:
                # For Vertical Jump, just add the exercise itself without looking for variations
                if exercise not in variations:
                    variations.append(exercise)
                    print(f"DEBUG: Added '{exercise}' directly to variations list")
            elif exercise == shot_put_name:
                # For Shot Put, just add the exercise itself without looking for variations
                if exercise not in variations:
                    variations.append(exercise)
                    print(f"DEBUG: Added '{exercise}' directly to variations list")
            else:
                # For other exercises, look for variations with dominance
                matching = [ex for ex in self.exercises if exercise in ex]
                print(f"DEBUG: Found {len(matching)} matching variations: {matching}")
                variations.extend(matching)
        
        # Special handling for Press/Pull exercises - make sure all variants are included
        if region_name == 'Press/Pull':
            press_pull_exercises = [
                'Horizontal Row (One Hand) (Dominant)', 
                'Horizontal Row (One Hand) (Non-Dominant)',
                'Chest Press (One Hand) (Dominant)',
                'Chest Press (One Hand) (Non-Dominant)'
            ]
            
            # Ensure all Press/Pull exercises are in the variations list
            for ex in press_pull_exercises:
                if ex not in variations and ex in self.exercises:
                    variations.append(ex)
        
        # Special handling for Legs - ALWAYS ensure Vertical Jump is included regardless
        if region_name == 'Legs' and vertical_jump_name not in variations:
            print(f"Debug: FORCING Vertical Jump into Legs region variations")
            variations.append(vertical_jump_name)
            
        # Special handling for Torso - ALWAYS ensure Shot Put is included regardless
        if region_name == 'Torso' and shot_put_name not in variations:
            print(f"DEBUG: FORCING Shot Put into Torso region variations")
            variations.append(shot_put_name)
            
        print(f"DEBUG: Final variations list for {region_name}: {variations}")
        
        # Get users with multiple tests
        multi_test_users = []
        for user in df['user name'].unique():
            # Generate matrices for user
            matrices = self.generate_user_matrices(df, user)
            if matrices[2] is not None:  # If development matrices exist
                power_dev = matrices[2]  # Get power development matrix
                
                # Check if user has multiple tests
                if len(power_dev.columns) >= 2:
                    multi_test_users.append(user)
                
        if not multi_test_users:
            # Return None values for all 8 return values
            return None, None, None, None, None, None, None, None  # Return None if no multi-test users

        # Initialize DataFrames for power and acceleration
        power_df = pd.DataFrame(
            0.0,
            index=variations,
            columns=['Test 1', 'Test 2', 'Test 3', 'Test 4'][:max_tests]
        )
        
        accel_df = pd.DataFrame(
            0.0,
            index=variations,
            columns=['Test 1', 'Test 2', 'Test 3', 'Test 4'][:max_tests]
        )

        # Track user counts for each cell
        power_count_df = pd.DataFrame(
            0,
            index=variations,
            columns=['Test 1', 'Test 2', 'Test 3', 'Test 4'][:max_tests]
        )
        
        accel_count_df = pd.DataFrame(
            0,
            index=variations,
            columns=['Test 1', 'Test 2', 'Test 3', 'Test 4'][:max_tests]
        )

        # Process each user
        for user in multi_test_users:
            # Generate matrices for user
            matrices = self.generate_user_matrices(df, user)
            if matrices[2] is not None:  # If development matrices exist
                power_dev, accel_dev = matrices[2], matrices[3]  # Get development matrices
                
                # Only process multi-test users
                if len(power_dev.columns) >= 2:
                    # Only process up to max_tests columns
                    test_cols = [col for col in power_dev.columns if int(col.split()[-1]) <= max_tests]
                    
                    for test_col in test_cols:
                        # Get power and acceleration values for region exercises
                        for exercise in variations:
                            if exercise in power_dev.index:
                                # Get power development score
                                power_value = power_dev.loc[exercise, test_col]
                                if pd.notna(power_value):
                                    power_df.loc[exercise, test_col] += power_value
                                    power_count_df.loc[exercise, test_col] += 1
                                
                                # Get acceleration development score
                                accel_value = accel_dev.loc[exercise, test_col]
                                if pd.notna(accel_value):
                                    accel_df.loc[exercise, test_col] += accel_value
                                    accel_count_df.loc[exercise, test_col] += 1

        # Calculate averages for each cell
        for col in power_df.columns:
            for idx in power_df.index:
                # Power averages
                count = power_count_df.loc[idx, col]
                if count > 0:
                    power_df.loc[idx, col] = power_df.loc[idx, col] / count
                else:
                    power_df.loc[idx, col] = np.nan
                    
                # Acceleration averages
                count = accel_count_df.loc[idx, col]
                if count > 0:
                    accel_df.loc[idx, col] = accel_df.loc[idx, col] / count
                else:
                    accel_df.loc[idx, col] = np.nan

        # Calculate change metrics with user tracking
        power_changes = self.calculate_test_changes(power_df, include_users=True)
        accel_changes = self.calculate_test_changes(accel_df, include_users=True)
        
        # Track user-specific data to identify underperformers
        power_user_data = pd.DataFrame(index=multi_test_users, columns=['Test 1', 'Test 2', 'Test 3', 'Test 4'][:max_tests])
        accel_user_data = pd.DataFrame(index=multi_test_users, columns=['Test 1', 'Test 2', 'Test 3', 'Test 4'][:max_tests])
        
        # Calculate average development per user across all exercises in this region
        for user in multi_test_users:
            # Generate matrices for user
            matrices = self.generate_user_matrices(df, user)
            if matrices[2] is not None:  # If development matrices exist
                power_dev, accel_dev = matrices[2], matrices[3]  # Get development matrices
                
                # For each test, calculate the average development across all region exercises
                for test_col in power_dev.columns:
                    if test_col in power_user_data.columns:
                        # Get power values for region exercises
                        power_values = []
                        for exercise in variations:
                            if exercise in power_dev.index and pd.notna(power_dev.loc[exercise, test_col]):
                                power_values.append(power_dev.loc[exercise, test_col])
                        
                        # Calculate average if there are values
                        if power_values:
                            power_user_data.loc[user, test_col] = sum(power_values) / len(power_values)
                
                # Do the same for acceleration
                for test_col in accel_dev.columns:
                    if test_col in accel_user_data.columns:
                        # Get acceleration values for region exercises
                        accel_values = []
                        for exercise in variations:
                            if exercise in accel_dev.index and pd.notna(accel_dev.loc[exercise, test_col]):
                                accel_values.append(accel_dev.loc[exercise, test_col])
                        
                        # Calculate average if there are values
                        if accel_values:
                            accel_user_data.loc[user, test_col] = sum(accel_values) / len(accel_values)
        
        # Find underperforming users (below average improvement)
        power_underperformers_1_to_2 = []
        power_underperformers_2_to_3 = []
        accel_underperformers_1_to_2 = []
        accel_underperformers_2_to_3 = []
        
        # For power
        if not pd.isna(power_changes.get('test1_to_test2_pct')):
            threshold = power_changes['test1_to_test2_pct']
            for user in power_user_data.index:
                if pd.notna(power_user_data.loc[user, 'Test 1']) and pd.notna(power_user_data.loc[user, 'Test 2']):
                    change = ((power_user_data.loc[user, 'Test 2'] - power_user_data.loc[user, 'Test 1']) / 
                              power_user_data.loc[user, 'Test 1'] * 100)
                    if change < threshold:
                        power_underperformers_1_to_2.append((user, change))
        
        if not pd.isna(power_changes.get('test2_to_test3_pct')):
            threshold = power_changes['test2_to_test3_pct']
            for user in power_user_data.index:
                if pd.notna(power_user_data.loc[user, 'Test 2']) and pd.notna(power_user_data.loc[user, 'Test 3']):
                    change = ((power_user_data.loc[user, 'Test 3'] - power_user_data.loc[user, 'Test 2']) / 
                              power_user_data.loc[user, 'Test 2'] * 100)
                    if change < threshold:
                        power_underperformers_2_to_3.append((user, change))
        
        # For acceleration
        if not pd.isna(accel_changes.get('test1_to_test2_pct')):
            threshold = accel_changes['test1_to_test2_pct']
            for user in accel_user_data.index:
                if pd.notna(accel_user_data.loc[user, 'Test 1']) and pd.notna(accel_user_data.loc[user, 'Test 2']):
                    change = ((accel_user_data.loc[user, 'Test 2'] - accel_user_data.loc[user, 'Test 1']) / 
                              accel_user_data.loc[user, 'Test 1'] * 100)
                    if change < threshold:
                        accel_underperformers_1_to_2.append((user, change))
        
        if not pd.isna(accel_changes.get('test2_to_test3_pct')):
            threshold = accel_changes['test2_to_test3_pct']
            for user in accel_user_data.index:
                if pd.notna(accel_user_data.loc[user, 'Test 2']) and pd.notna(accel_user_data.loc[user, 'Test 3']):
                    change = ((accel_user_data.loc[user, 'Test 3'] - accel_user_data.loc[user, 'Test 2']) / 
                              accel_user_data.loc[user, 'Test 2'] * 100)
                    if change < threshold:
                        accel_underperformers_2_to_3.append((user, change))
        
        # Sort underperformers by change value (lowest first)
        power_changes['underperformers_1_to_2'] = sorted(power_underperformers_1_to_2, key=lambda x: x[1])
        power_changes['underperformers_2_to_3'] = sorted(power_underperformers_2_to_3, key=lambda x: x[1])
        accel_changes['underperformers_1_to_2'] = sorted(accel_underperformers_1_to_2, key=lambda x: x[1])
        accel_changes['underperformers_2_to_3'] = sorted(accel_underperformers_2_to_3, key=lambda x: x[1])
        
        # Find exercise with lowest change for Test 1 to Test 2
        # We want to prioritize negative changes, then smallest positive changes
        lowest_power_change_exercise = None
        lowest_power_change_value = None
        has_negative_power = False
        
        lowest_accel_change_exercise = None
        lowest_accel_change_value = None
        has_negative_accel = False

        # Find exercise with lowest change from Test 1 to Test 2 for power
        if 'Test 1' in power_df.columns and 'Test 2' in power_df.columns:
            for exercise in variations:
                if exercise in power_df.index:
                    test1_value = power_df.loc[exercise, 'Test 1']
                    test2_value = power_df.loc[exercise, 'Test 2']
                    
                    if pd.notna(test1_value) and pd.notna(test2_value) and test1_value > 0:
                        change_pct = ((test2_value - test1_value) / test1_value) * 100
                        
                        # If this is a negative change and we haven't found one yet, or
                        # if we already have negative changes and this one is more negative
                        if change_pct < 0:
                            if not has_negative_power or change_pct < lowest_power_change_value:
                                has_negative_power = True
                                lowest_power_change_value = change_pct
                                lowest_power_change_exercise = exercise
                        # If we don't have any negative changes yet and this is a smaller positive
                        # change than we've seen so far (or we haven't seen any yet)
                        elif not has_negative_power and (lowest_power_change_value is None or change_pct < lowest_power_change_value):
                            lowest_power_change_value = change_pct
                            lowest_power_change_exercise = exercise

        # Do similar calculation for acceleration
        if 'Test 1' in accel_df.columns and 'Test 2' in accel_df.columns:
            for exercise in variations:
                if exercise in accel_df.index:
                    test1_value = accel_df.loc[exercise, 'Test 1']
                    test2_value = accel_df.loc[exercise, 'Test 2']
                    
                    if pd.notna(test1_value) and pd.notna(test2_value) and test1_value > 0:
                        change_pct = ((test2_value - test1_value) / test1_value) * 100
                        
                        # Prioritize negative changes
                        if change_pct < 0:
                            if not has_negative_accel or change_pct < lowest_accel_change_value:
                                has_negative_accel = True
                                lowest_accel_change_value = change_pct
                                lowest_accel_change_exercise = exercise
                        # Then consider smallest positive changes
                        elif not has_negative_accel and (lowest_accel_change_value is None or change_pct < lowest_accel_change_value):
                            lowest_accel_change_value = change_pct
                            lowest_accel_change_exercise = exercise
        
        # We already initialized values to None, so no further handling needed
        
        return power_df, accel_df, power_changes, accel_changes, lowest_power_change_exercise, lowest_power_change_value, lowest_accel_change_exercise, lowest_accel_change_value
            
    def get_torso_region_metrics(self, df, max_tests=4):
        """
        Calculate detailed power and acceleration metrics for the Torso region exercises.
        Only includes multi-test users with separate metrics for power and acceleration.
        
        Returns:
            Same as get_region_metrics - a tuple with 8 elements containing power and 
            acceleration metrics, changes, and lowest change information.
        """
        return self.get_region_metrics(df, 'Torso', max_tests)
        
    def calculate_improvement_thresholds(self, df):
        """
        Calculate the improvement thresholds for each body region.
        
        The improvement threshold is the average percentage change across all users
        for a specific body region between consecutive tests. This serves as a
        reference point to determine which users are underperforming relative to
        the group average.
        
        Args:
            df: The processed dataframe
            
        Returns:
            Dictionary containing improvement thresholds for each region:
            {
                'region_name': {
                    'power_1_to_2': threshold value,
                    'power_2_to_3': threshold value,
                    'accel_1_to_2': threshold value,
                    'accel_2_to_3': threshold value
                }
            }
        """
        from exercise_constants import VALID_EXERCISES
        
        # Initialize thresholds dictionary
        thresholds = {}
        
        # Process each region
        for region in VALID_EXERCISES.keys():
            print(f"Calculating improvement thresholds for {region} region")
            region_metrics = self.get_region_metrics(df, region)
            
            # Skip if no metrics available
            if region_metrics[0] is None:
                thresholds[region] = {
                    'power_1_to_2': np.nan,
                    'power_2_to_3': np.nan,
                    'accel_1_to_2': np.nan,
                    'accel_2_to_3': np.nan
                }
                continue
                
            # Extract changes
            power_changes = region_metrics[2]
            accel_changes = region_metrics[3]
            
            # Initialize region thresholds
            region_thresholds = {
                'power_1_to_2': np.nan,
                'power_2_to_3': np.nan,
                'accel_1_to_2': np.nan,
                'accel_2_to_3': np.nan
            }
            
            # Process power thresholds
            if power_changes and 'test1_to_test2_individual' in power_changes:
                individual_changes = power_changes['test1_to_test2_individual']
                if not individual_changes.empty:
                    region_thresholds['power_1_to_2'] = individual_changes.mean()
                    
            if power_changes and 'test2_to_test3_individual' in power_changes:
                individual_changes = power_changes['test2_to_test3_individual']
                if not individual_changes.empty:
                    region_thresholds['power_2_to_3'] = individual_changes.mean()
            
            # Process acceleration thresholds
            if accel_changes and 'test1_to_test2_individual' in accel_changes:
                individual_changes = accel_changes['test1_to_test2_individual']
                if not individual_changes.empty:
                    region_thresholds['accel_1_to_2'] = individual_changes.mean()
                    
            if accel_changes and 'test2_to_test3_individual' in accel_changes:
                individual_changes = accel_changes['test2_to_test3_individual']
                if not individual_changes.empty:
                    region_thresholds['accel_2_to_3'] = individual_changes.mean()
            
            # Store in thresholds dictionary
            thresholds[region] = region_thresholds
        
        return thresholds