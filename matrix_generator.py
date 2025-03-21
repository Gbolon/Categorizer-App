import pandas as pd
import numpy as np
from exercise_constants import ALL_EXERCISES
from goal_standards import calculate_development_score

class MatrixGenerator:
    def __init__(self):
        self.exercises = ALL_EXERCISES
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

    def generate_group_analysis(self, df, max_tests=4):
        """Generate group-level analysis of development categories."""
        # Initialize count DataFrames for power and acceleration
        categories = list(self.development_brackets.keys()) + ['Total Users']
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

                    # Increment total users once for all test columns
                    for test in test_columns:
                        if test in power_brackets.index:
                            power_counts.loc['Total Users', test] += 1
                        if test in accel_brackets.index:
                            accel_counts.loc['Total Users', test] += 1

                    # Process transitions for multi-test users
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
                                power_transitions[transition_col]
                            )

                        # Acceleration transitions
                        if current_test in accel_brackets.index and next_test in accel_brackets.index:
                            current_cat = accel_brackets.loc[current_test, 'Category']
                            next_cat = accel_brackets.loc[next_test, 'Category']
                            self._update_progression_counts(
                                current_cat, next_cat,
                                transition_col,
                                accel_transitions[transition_col]
                            )

        # Calculate actual averages for single test users
        power_average = np.mean(single_test_power_scores) if single_test_power_scores else 0
        accel_average = np.mean(single_test_accel_scores) if single_test_accel_scores else 0

        # Generate detailed transition matrices
        power_transitions_detail = self._analyze_detailed_transitions(power_transitions)
        accel_transitions_detail = self._analyze_detailed_transitions(accel_transitions)

        # Calculate average changes
        avg_power_change_1_2 = np.mean(test1_to_2_power) if test1_to_2_power else 0
        avg_accel_change_1_2 = np.mean(test1_to_2_accel) if test1_to_2_accel else 0
        avg_power_change_2_3 = np.mean(test2_to_3_power) if test2_to_3_power else 0
        avg_accel_change_2_3 = np.mean(test2_to_3_accel) if test2_to_3_accel else 0

        return (power_counts, accel_counts, single_test_distribution,
                power_transitions_detail, accel_transitions_detail,
                power_average, accel_average,
                avg_power_change_1_2, avg_accel_change_1_2,
                avg_power_change_2_3, avg_accel_change_2_3)

    def _update_progression_counts(self, current_cat, next_cat, col, transitions_list):
        """Update progression counts based on category changes."""
        if current_cat and next_cat and pd.notna(current_cat) and pd.notna(next_cat):
            try:
                # Record the transition for detailed analysis
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

        for period, transitions in transitions_dict.items():
            # Create an empty transition matrix
            matrix = pd.DataFrame(0, 
                index=self.bracket_order,
                columns=self.bracket_order)

            # Count transitions from each bracket to another
            for from_bracket, to_bracket in transitions:
                if from_bracket in self.bracket_order and to_bracket in self.bracket_order:
                    matrix.loc[from_bracket, to_bracket] += 1

            # Add "Starting Bracket" column
            matrix.insert(0, "Starting Bracket", matrix.index)

            # Create MultiIndex for columns with "Ending Bracket" header
            matrix.columns = pd.MultiIndex.from_tuples([
                ("Ending Bracket", col) if col != "Starting Bracket" else ("Starting Bracket", col)
                for col in matrix.columns
            ])

            # Function to apply background color and text rotation
            def highlight_cells(dataframe):
                styles = pd.DataFrame("", index=dataframe.index, columns=dataframe.columns)

                # Skip the "Starting Bracket" column when applying colors
                data_cols = [col for col in dataframe.columns if col[1] != "Starting Bracket"]

                for i in range(len(dataframe)):  # Row index
                    for col in data_cols:  # Column index
                        j = self.bracket_order.index(col[1])  # Get position in bracket_order
                        base_style = "color: black; font-weight: bold; "
                        if i == j:  # Diagonal (No movement)
                            styles.loc[dataframe.index[i], col] = base_style + "background-color: lightblue;"
                        elif i < j:  # Above diagonal (Regression)
                            styles.loc[dataframe.index[i], col] = base_style + "background-color: lightcoral;"
                        else:  # Below diagonal (Improvement)
                            styles.loc[dataframe.index[i], col] = base_style + "background-color: lightgreen;"

                # Style for Starting Bracket column
                styles[("Starting Bracket", "Starting Bracket")] = "color: black; font-weight: bold;"

                return styles

            # Apply formatting and styling
            styled_matrix = matrix.style.format(lambda x: f"{x:.0f}" if isinstance(x, (int, float)) else x)
            styled_matrix = styled_matrix.apply(highlight_cells, axis=None)

            transition_matrices[period] = styled_matrix

        return transition_matrices

    def _analyze_transition_patterns(self, transitions_dict):
        """Analyze common transition patterns for level ups."""
        patterns_df = pd.DataFrame(columns=['Most Common From', 'Most Common To', 'Count'])

        for period, transitions in transitions_dict.items():
            if transitions:
                # Count frequency of each transition pattern
                transition_counts = {}
                for from_bracket, to_bracket in transitions:
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

        # Get user's sex for development calculations
        if user_data.empty:
            return power_matrix, accel_matrix, None, None, None, None, None

        user_sex = user_data['sex'].iloc[0]
        if not isinstance(user_sex, str) or user_sex.lower() not in ['male', 'female']:
            return power_matrix, accel_matrix, None, None, None, None, None

        # Process each exercise chronologically and keep power/acceleration paired
        for _, row in user_data.iterrows():
            exercise = row['full_exercise_name']
            power_value = row['power - high']
            accel_value = row['acceleration - high']

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

        # Fill empty cells with NaN
        for instance in power_matrix:
            for exercise in self.exercises:
                if exercise not in power_matrix[instance]:
                    power_matrix[instance][exercise] = np.nan
                if exercise not in accel_matrix[instance]:
                    accel_matrix[instance][exercise] = np.nan

        # Convert to DataFrames
        power_df, accel_df = self._convert_to_dataframes(power_matrix, accel_matrix)

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
        # Create DataFrame for power
        power_df = pd.DataFrame(power_matrix)
        power_df = power_df.reindex(self.exercises)
        power_df.columns = [f"Test {i}" for i in range(1, len(power_df.columns) + 1)]

        # Create DataFrame for acceleration
        accel_df = pd.DataFrame(accel_matrix)
        accel_df = accel_df.reindex(self.exercises)
        accel_df.columns = [f"Test {i}" for i in range(1, len(accel_df.columns) + 1)]

        return power_df, accel_df

    def _calculate_development_matrix(self, metric_df, sex, metric_type):
        """Calculate development scores for each value in the matrix."""
        dev_matrix = metric_df.copy()

        for col in dev_matrix.columns:
            for idx in dev_matrix.index:
                value = metric_df.loc[idx, col]
                dev_matrix.loc[idx, col] = calculate_development_score(
                    value, idx, sex, metric_type
                )

        return dev_matrix

    def _calculate_overall_development(self, power_dev_df, accel_dev_df):
        """Calculate overall development categorization for each test instance."""
        # Initialize a new DataFrame for overall development
        overall_dev = pd.DataFrame(index=['Power Average', 'Acceleration Average', 'Overall Average'])

        # Calculate averages for each test instance
        for col in power_dev_df.columns:
            # Calculate power average (excluding NaN values)
            power_avg = power_dev_df[col].apply(lambda x: min(x, 100) if pd.notnull(x) else x).mean(skipna=True)

            # Calculate acceleration average (excluding NaN values)
            accel_avg = accel_dev_df[col].apply(lambda x: min(x, 100) if pd.notnull(x) else x).mean(skipna=True)

            # Calculate overall average
            overall_avg = np.mean([power_avg, accel_avg])

            # Add to overall development DataFrame
            overall_dev[col] = [power_avg, accel_avg, overall_avg]

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