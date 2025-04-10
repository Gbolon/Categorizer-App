import streamlit as st
import pandas as pd
import numpy as np
import io
import csv
import hashlib
from data_processor import DataProcessor
from matrix_generator import MatrixGenerator
from report_generator import ReportGenerator
from exercise_constants import VALID_EXERCISES
from goal_standards import POWER_STANDARDS, ACCELERATION_STANDARDS

# Function to check password
def check_password():
    """
    Returns `True` if the user had the correct password and is authenticated.
    """
    # Initialize session state for authentication if not already done
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # If already authenticated, return True
    if st.session_state.authenticated:
        return True
    
    # Set a default password - in a real app, you'd want to store this more securely
    # For this example, we'll use "Scoobysnacks!" as the password
    correct_password_hash = "804ac4c5172928dc02d95b48e207eff5"  # md5 hash of "Scoobysnacks!"
    
    # Display header
    st.markdown("<h1 style='font-size: 3em;'>Pythagoras <span style='font-size: 0.4em;'>By Proteus</span></h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size: 1.5em; font-style: italic; margin-top: -10px;'>For the shortest distance between two goals...</h3>", unsafe_allow_html=True)
    
    # Create password input
    password = st.text_input("Please enter the password to access Pythagoras", type="password")
    
    # Check if password was entered and validate it
    if password:
        # Hash the entered password
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        # Verify the password
        if password_hash == correct_password_hash:
            st.session_state.authenticated = True
            return True
        else:
            st.error("Invalid password. Please try again.")
            return False
    else:
        # No password entered yet
        return False

# Dictionary of standard resistances for each exercise (in pounds)
STANDARD_RESISTANCES = {
    "Chest Press (One Hand)": 12,
    "Horizontal Row (One Hand)": 12,
    "Biceps Curl (One Hand)": 6,
    "Triceps Extension (One Hand)": 6,
    "PNF D2 Flexion": 6,
    "PNF D2 Extension": 6,
    "Straight Arm Trunk Rotation": 12,
    "Lateral Bound": 6,
    "Shot Put (Countermovement)": 18,
    "Vertical Jump (Countermovement)": 6
}

# Configure the page at the very beginning
st.set_page_config(
    page_title="Pythagoras",
    page_icon="📊",
    layout="wide",  # This will make the page wider
    initial_sidebar_state="auto"
)

def generate_underperformers_csv(region, type_metric, period, underperformers):
    """
    Generate a CSV report for underperforming users.
    
    Args:
        region: The body region name
        type_metric: 'Power' or 'Acceleration'
        period: '1_to_2' or '2_to_3'
        underperformers: List of tuples containing (user_name, change_percentage)
        
    Returns:
        Bytes object containing CSV data
    """
    # Create StringIO object to write CSV data
    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer)
    
    # Write header
    period_text = "Test 1 to Test 2" if period == "1_to_2" else "Test 2 to Test 3"
    csv_writer.writerow([f"{region} Region Underperforming Users - {type_metric} ({period_text})"])
    csv_writer.writerow(["User Name", "Change Percentage"])
    
    # Write user data
    for user, change in underperformers:
        csv_writer.writerow([user, f"{change:.1f}%"])
    
    # Return bytes for download
    return csv_buffer.getvalue().encode('utf-8')

def create_underperformers_table(region, period, power_underperformers, accel_underperformers):
    """
    Create a DataFrame containing underperforming users with checkboxes for power and acceleration.
    
    Args:
        region: The body region name
        period: '1_to_2' or '2_to_3'
        power_underperformers: List of tuples containing power underperformers (user_name, change_percentage)
        accel_underperformers: List of tuples containing acceleration underperformers (user_name, change_percentage)
        
    Returns:
        DataFrame with columns 'Name', 'Power', 'Acceleration'
    """
    # Convert underperformers lists to dictionaries for easier lookup
    power_dict = {user: change for user, change in power_underperformers} if power_underperformers else {}
    accel_dict = {user: change for user, change in accel_underperformers} if accel_underperformers else {}
    
    # Get all unique user names
    all_users = set(power_dict.keys()).union(set(accel_dict.keys()))
    
    # Create data for the table
    table_data = []
    for user in all_users:
        # Get change values if they exist
        power_change = power_dict.get(user, None)
        accel_change = accel_dict.get(user, None)
        
        # Create display strings with checkmarks and percentages
        power_display = f"✓ ({power_change:.1f}%)" if power_change is not None else ""
        accel_display = f"✓ ({accel_change:.1f}%)" if accel_change is not None else ""
        
        table_data.append({
            "Name": user,
            "Power": power_display,
            "Acceleration": accel_display
        })
    
    # Sort by name and create DataFrame
    return pd.DataFrame(table_data).sort_values(by="Name").reset_index(drop=True) if table_data else None

def generate_exercise_metrics(df, filtered_df=None):
    """
    Generate exercise metrics including total executions, most common resistances,
    and valid entries count.
    
    Args:
        df: The processed dataframe (original data)
        filtered_df: Optional filtered dataframe for showing filtered valid entry counts
        
    Returns:
        DataFrame with exercise metrics
    """
    # If no filtered_df is provided, use the original df for filtered counts too
    if filtered_df is None:
        filtered_df = df
        
    # Create a list to store exercise metrics
    exercise_metrics = []
    
    # Get all valid exercises from the dataframe
    exercises = df['exercise name'].unique()
    
    for exercise in exercises:
        # Filter data for this exercise from the original data
        exercise_df = df[df['exercise name'] == exercise]
        
        # Get total executions from original data
        total_executions = len(exercise_df)
        
        # Get the top 3 most common resistances - handle empty or all-NaN cases
        if 'resistance' in exercise_df.columns and not exercise_df['resistance'].isna().all():
            # Get resistance value counts, excluding NaN values
            resistance_counts = exercise_df['resistance'].dropna().value_counts()
            
            # Get top 3 most common resistances
            most_common_resistance = "N/A"
            second_most_common = "N/A"
            third_most_common = "N/A"
            
            if len(resistance_counts) >= 1:
                most_common_resistance = f"{resistance_counts.index[0]} ({resistance_counts.iloc[0]})"
            
            if len(resistance_counts) >= 2:
                second_most_common = f"{resistance_counts.index[1]} ({resistance_counts.iloc[1]})"
                
            if len(resistance_counts) >= 3:
                third_most_common = f"{resistance_counts.index[2]} ({resistance_counts.iloc[2]})"
        else:
            most_common_resistance = "N/A"
            second_most_common = "N/A"
            third_most_common = "N/A"
        
        # Get valid entries count from the FILTERED data only
        filtered_exercise_df = filtered_df[filtered_df['exercise name'] == exercise]
        valid_entries = filtered_exercise_df.dropna(subset=['power - high', 'acceleration - high']).shape[0]
        
        # Add to list
        exercise_metrics.append({
            'Exercise Name': exercise,
            'Total Executions': total_executions,
            '1st Most Common Resistance': most_common_resistance,
            '2nd Most Common Resistance': second_most_common,
            '3rd Most Common Resistance': third_most_common,
            'Valid Entries': valid_entries
        })
    
    # Convert to DataFrame and sort by Total Executions (descending)
    return pd.DataFrame(exercise_metrics).sort_values(by='Total Executions', ascending=False).reset_index(drop=True)

def get_athlete_metrics(df):
    """
    Calculate metrics related to athletes in the dataset.
    
    Args:
        df: The processed dataframe
        
    Returns:
        Dictionary with athlete metrics including total counts and most active athlete
    """
    # Total number of unique athletes
    total_athletes = df['user name'].nunique()
    
    # Valid athletes have at least one exercise with both power and acceleration values
    valid_athlete_names = set()
    valid_tests_by_athlete = {}
    
    for name in df['user name'].unique():
        athlete_df = df[df['user name'] == name].copy()
        # Use .shape[0] > 0 instead of direct DataFrame evaluation
        valid_entries = athlete_df.dropna(subset=['power - high', 'acceleration - high'])
        
        if len(valid_entries) > 0:  # Using len() instead of directly evaluating DataFrame
            valid_athlete_names.add(name)
            valid_tests_by_athlete[name] = valid_entries.shape[0]
    
    valid_athletes = len(valid_athlete_names)
    
    # Find the athlete with the most valid test instances
    most_active_athlete = None
    if valid_tests_by_athlete:
        most_active_athlete = max(valid_tests_by_athlete.items(), key=lambda x: x[1])
    
    return {
        'total_athletes': total_athletes,
        'valid_athletes': valid_athletes,
        'most_active_athlete': most_active_athlete  # Tuple (athlete_name, test_count) or None
    }

def get_top_session_types(df):
    """
    Get the top 3 most frequently performed test types from the 'session name' column.
    
    Args:
        df: The processed dataframe
        
    Returns:
        Dictionary with the top 3 most common session names and their counts
    """
    result = {
        'most_common': "No session data available",
        'second_most_common': "No data available",
        'third_most_common': "No data available"
    }
    
    if 'session name' in df.columns and len(df) > 0:
        # Get the session name counts
        session_counts = df['session name'].value_counts()
        
        if len(session_counts) >= 1:
            most_common_session = session_counts.index[0]
            count = session_counts.iloc[0]
            result['most_common'] = f"{most_common_session} ({count} instances)"
        
        if len(session_counts) >= 2:
            second_most_common = session_counts.index[1]
            count = session_counts.iloc[1]
            result['second_most_common'] = f"{second_most_common} ({count} instances)"
            
        if len(session_counts) >= 3:
            third_most_common = session_counts.index[2]
            count = session_counts.iloc[2]
            result['third_most_common'] = f"{third_most_common} ({count} instances)"
    
    return result

def main():
    # Check authentication before proceeding
    if not check_password():
        # If not authenticated, stop here
        return
        
    # If authenticated, show the main application (no need to show the title again as it's in the check_password function)

    # Initialize processors
    data_processor = DataProcessor()
    matrix_generator = MatrixGenerator()
    report_generator = ReportGenerator()
    
    # Initialize variables for metrics
    avg_days_between_tests = 0
    avg_constrained_days = 0
    avg_days_between_tests_original = 0
    avg_constrained_days_original = 0

    # File upload
    uploaded_file = st.file_uploader("Upload your exercise data (CSV or Excel)", 
                                      type=['csv', 'xlsx'])

    # If no file is uploaded, show information content
    if uploaded_file is None:
        st.markdown("<h2 style='font-size: 1.875em;'>Welcome to Pythagoras</h2>", unsafe_allow_html=True)
        st.markdown("Please upload a CSV or Excel file to begin analysis. In the meantime, here's some information about how the application works:")
        
        # Application Overview Section
        with st.expander("Application Overview", expanded=True):
            st.markdown("""
            ### Pythagoras
            
            This application processes exercise data to track athlete development over time. It categorizes performance into brackets based on power and acceleration metrics, and provides detailed analysis at both individual and group levels.
            
            #### Core Functionality
            - Processes CSV or Excel files containing exercise performance data
            - Organizes exercises into chronological "test instances" for each user
            - Categorizes development into 6 brackets ranging from "Goal Hit" to "Severely Under Developed"
            - Tracks progression between brackets over time
            - Identifies underperforming users relative to group averages
            - Generates comprehensive reports with detailed data visualizations
            """)
        
        # Development Score Calculation
        with st.expander("Development Score Calculation", expanded=False):
            st.markdown("""
            ### Development Score Calculation
            
            Development scores are calculated as a percentage of goal standards for each exercise:
            
            ```
            Development Score = (User's value / Goal standard) × 100
            ```
            
            #### Development Brackets
            Development scores are categorized into the following brackets:
            
            | Bracket | Score Range |
            |---------|-------------|
            | Goal Hit | 100% and above |
            | Elite | 90% - 99.99% |
            | Above Average | 76% - 90% |
            | Average | 51% - 75% |
            | Under Developed | 26% - 50% |
            | Severely Under Developed | 0% - 25% |
            
            #### Goal Standards
            Goal standards are sex-specific reference values for each exercise. These values represent optimal performance targets.
            """)
            
            # Create a table of goal standards by exercise
            st.markdown("##### Power Standards (Watts)")
            power_standards_data = []
            for exercise in sorted(POWER_STANDARDS['male'].keys()):
                power_standards_data.append({
                    'Exercise': exercise,
                    'Male': POWER_STANDARDS['male'].get(exercise, '-'),
                    'Female': POWER_STANDARDS['female'].get(exercise, '-')
                })
            
            st.dataframe(pd.DataFrame(power_standards_data), use_container_width=True)
            
            st.markdown("##### Acceleration Standards (m/s²)")
            accel_standards_data = []
            for exercise in sorted(ACCELERATION_STANDARDS['male'].keys()):
                accel_standards_data.append({
                    'Exercise': exercise,
                    'Male': ACCELERATION_STANDARDS['male'].get(exercise, '-'),
                    'Female': ACCELERATION_STANDARDS['female'].get(exercise, '-')
                })
            
            st.dataframe(pd.DataFrame(accel_standards_data), use_container_width=True)
        
        # Exercise Information
        with st.expander("Exercise Information", expanded=False):
            st.markdown("""
            ### Exercise Information
            
            #### Body Regions
            Exercises are categorized into the following body regions:
            """)
            
            for region, exercises in VALID_EXERCISES.items():
                st.markdown(f"**{region}**")
                for exercise in exercises:
                    st.markdown(f"- {exercise}")
            
            st.markdown("#### Standard Resistance Values")
            st.markdown("""
            The application can filter data to include only exercises performed at standard resistance values.
            This helps ensure comparability of results across users and tests.
            """)
            
            resistance_data = []
            for exercise, resistance in STANDARD_RESISTANCES.items():
                resistance_data.append({
                    'Exercise': exercise,
                    'Standard Resistance (lbs)': resistance
                })
            
            st.dataframe(pd.DataFrame(resistance_data), use_container_width=True)
        
        # Data Organization
        with st.expander("Data Organization", expanded=False):
            st.markdown("""
            ### Data Organization
            
            #### Test Instances
            Chronological "test instances" are created for each user by organizing exercises by date:
            - The first chronological exercise becomes part of Test 1
            - The next exercise becomes part of Test 2, and so on
            - If an exercise is repeated, it occupies the next available test instance
            
            This approach allows tracking improvement over time across different exercises.
            
            #### Improvement Threshold
            The improvement threshold is calculated as the average percentage change across all users
            for a specific body region between consecutive tests. This serves as a reference point
            to determine which users are underperforming relative to the group average.
            
            #### Minimum Days Between Tests
            When the minimum days filter is applied:
            1. The first chronological test for each exercise is always included
            2. Subsequent tests are only included if they occur at least the specified number of days after the previous test
            3. This filtering is done at the raw data level before organizing into test instances
            """)
        
        # Tab Explanations
        with st.expander("Tab Explanations", expanded=False):
            st.markdown("""
            ### Tab Explanations
            
            #### 1. Overview
            Provides a high-level summary of the dataset including:
            - Athlete metrics (total athletes, valid athletes, most active)
            - Exercise metrics (execution counts, resistance patterns)
            - Test session analysis (most common session types)
            
            #### 2. Group Development Analysis
            Shows the distribution of users across development brackets:
            - Separate analysis for single-test and multi-test users
            - Power and acceleration distributions
            - Average days between tests metrics
            - Percentage changes between consecutive tests
            
            #### 3. Transition Analysis
            Visualizes how users move between development brackets over time:
            - Color-coded matrices (blue = no change, red = regression, green = improvement)
            - Lists users who regressed between tests
            - Separate analysis for power and acceleration
            
            #### 4. Body Region Analysis
            Analyzes performance by body region:
            - Group averages for multi-test users
            - Detailed exercise metrics for each region
            - Underperforming users tables
            - Allows downloading underperformer lists as CSV
            
            #### 5. Individual Analysis
            Provides detailed analysis for specific users:
            - Test matrices showing all exercise values
            - Development categorization
            - Graph visualizations of progress
            
            #### 6. Report Generator
            Creates comprehensive reports for sharing or documentation:
            - Interactive HTML reports with separate pages for each section
            - Comprehensive data visualizations
            - Optional site name for identification
            
            #### 7. Information
            Provides detailed documentation about the application:
            - Development score calculation and bracket definitions
            - Exercise standards and categorization
            - Data organization and filtering methodologies
            - Detailed explanation of all features and tabs
            """)
        
        # Data Filtering
        with st.expander("Data Filtering", expanded=False):
            st.markdown("""
            ### Data Filtering
            
            The application provides several filtering options to refine analysis:
            
            #### Resistance Standardization
            When enabled, only includes data where exercises were performed at standard resistance values.
            A small tolerance (±0.5 lbs) is allowed to account for minor variations.
            
            #### Evaluation Window
            Filters data to a specific date range, allowing focus on particular testing periods.
            
            #### Minimum Days Between Tests
            Ensures tests for the same exercise are separated by at least the specified number of days.
            This helps prevent including tests that are too close together, which might not reflect
            meaningful physiological changes.
            
            When filters are applied:
            - The original metrics are preserved for reference in the Overview tab
            - All other analyses reflect the filtered dataset
            - Filter settings are noted at the top of each analysis section
            """)
        
        # Data Requirements
        with st.expander("Data Requirements", expanded=False):
            st.markdown("""
            ### Data Requirements
            
            For proper functioning, your CSV or Excel file must include the following columns:
            
            | Column | Description |
            |--------|-------------|
            | `user name` | The name or ID of the user |
            | `sex` | User's sex (male/female) - needed for goal standards |
            | `exercise name` | The name of the exercise performed |
            | `dominance` | Hand/foot dominance for appropriate exercises |
            | `exercise createdAt` | Timestamp when the exercise was performed |
            | `power - high` | Power measurement (in watts) |
            | `acceleration - high` | Acceleration measurement (in m/s²) |
            | `resistance` | Weight/resistance used (optional, for filtering) |
            | `session name` | Test session identifier (optional) |
            
            Missing values for power or acceleration will result in those exercises being excluded from analysis.
            """)
            
    if uploaded_file is not None:
        try:
            # Load and validate data
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # Validate data
            is_valid, message = data_processor.validate_data(df)

            if not is_valid:
                st.error(message)
                return

            # Process data
            processed_df = data_processor.preprocess_data(df)

            # Add checkbox for resistance standardization
            standardize_resistance = st.checkbox(
                "Enable Resistance Standardization", 
                value=True,  # Default to enabled
                help="When enabled, only includes data where exercises were performed at standard resistance values"
            )
            
            # Get earliest and latest dates from the dataset for default values
            min_date = processed_df['exercise createdAt'].dt.tz_localize(None).min().date()
            max_date = processed_df['exercise createdAt'].dt.tz_localize(None).max().date()
            
            # Set the default start date to the first data point date rather than min_date
            default_start_date = min_date
            
            # Add Evaluation Window date range selection
            st.write("### Evaluation Window")
            st.write("Select a date range to filter the data. Only exercises performed between these dates will be included in the analysis.")
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "Start Date",
                    value=default_start_date,
                    min_value=min_date,
                    max_value=max_date
                )
            with col2:
                end_date = st.date_input(
                    "End Date",
                    value=max_date,
                    min_value=min_date,
                    max_value=max_date
                )
                
            # Initialize analysis_df to the processed_df
            analysis_df = processed_df.copy()
            
            # Store the original dataframe in the matrix_generator for metrics calculation
            matrix_generator.original_df = processed_df.copy()
            
            # Add minimum days between tests filter
            min_days_between_tests = st.number_input(
                "Minimum Days Between Tests",
                min_value=0,
                max_value=365,
                value=30,  # Default to 30 days minimum between tests
                step=1,
                help="Set the minimum number of days required between consecutive tests. Tests that occur before this threshold will be skipped."
            )
            
            # Apply date range filtering
            if start_date or end_date:
                # Convert to datetime for comparison - ensure consistent timezone handling
                start_datetime = pd.Timestamp(start_date).tz_localize(None)
                end_datetime = pd.Timestamp(end_date).tz_localize(None) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)  # Set to end of the day
                
                # Apply date filter - remove timezone info for consistent comparison
                date_filtered_df = analysis_df[
                    (analysis_df['exercise createdAt'].dt.tz_localize(None) >= start_datetime) & 
                    (analysis_df['exercise createdAt'].dt.tz_localize(None) <= end_datetime)
                ]
                
                # Show date filtering info if dates are not the min/max values
                if start_date > min_date or end_date < max_date:
                    st.info(f"Date filtering applied: Showing exercises from {start_date} to {end_date}.\n"
                           f"Original data rows: {len(analysis_df)}, Filtered data rows: {len(date_filtered_df)}")
                
                # Update analysis_df with date filtered results
                analysis_df = date_filtered_df
                
            # Apply minimum days between tests filtering
            if min_days_between_tests > 0:
                before_count = len(analysis_df)
                analysis_df = data_processor.filter_by_minimum_days(analysis_df, min_days_between_tests)
                after_count = len(analysis_df)
                
                # Show filtering info
                st.info(f"Minimum days filter applied: Ensuring at least {min_days_between_tests} days between tests.\n"
                       f"Data rows before filtering: {before_count}, After filtering: {after_count}")
            
            # Apply resistance filtering when checkbox is checked
            if standardize_resistance:
                # Create a copy of the DataFrame to avoid modifying the original
                resistance_filtered_df = analysis_df.copy()
                
                # Define a filtering function
                def filter_by_standard_resistance(row):
                    # Extract exercise name
                    exercise_name = row['exercise name']
                    # Find the base exercise name that matches our standards dictionary
                    matching_exercise = None
                    for standard_exercise in STANDARD_RESISTANCES.keys():
                        if standard_exercise in exercise_name:
                            matching_exercise = standard_exercise
                            break
                    
                    # If no matching exercise or no resistance value, keep the row
                    if matching_exercise is None or pd.isna(row['resistance']):
                        return True
                    
                    # Check if resistance matches the standard with a small tolerance
                    standard_resistance = STANDARD_RESISTANCES[matching_exercise]
                    # Allow a small tolerance (e.g., ±0.5 lbs)
                    tolerance = 0.5
                    return abs(float(row['resistance']) - standard_resistance) <= tolerance
                
                # Apply the filter
                resistance_filtered_df = resistance_filtered_df[resistance_filtered_df.apply(filter_by_standard_resistance, axis=1)]
                
                # Show filtering info
                st.info(f"Resistance filtering applied: Only showing data with standard resistance values.\n"
                       f"Data rows before resistance filtering: {len(analysis_df)}, After filtering: {len(resistance_filtered_df)}")
                
                # Update analysis_df with resistance filtered results
                analysis_df = resistance_filtered_df
            
            # Show data preview in collapsed expander
            with st.expander("Data Preview", expanded=False):
                # Check if any filtering is applied
                filtering_applied = standardize_resistance or (start_date > min_date or end_date < max_date) or min_days_between_tests > 0
                
                if filtering_applied:
                    st.write("**Filtered Data Preview**")
                    st.dataframe(analysis_df.head())
                    st.write("**Original Data Preview (All Data)**")
                    st.dataframe(processed_df.head())
                    
                    # Show filtering summary
                    if start_date > min_date or end_date < max_date:
                        st.write(f"**Date filtering:** From {start_date} to {end_date}")
                    if min_days_between_tests > 0:
                        st.write(f"**Minimum days between tests:** {min_days_between_tests} days")
                    if standardize_resistance:
                        st.write("**Resistance filtering:** Using standard resistance values")
                else:
                    st.dataframe(processed_df.head())
                
            # Generate group-level analysis for original data (needed for Overview tab)
            (power_counts_original, accel_counts_original, single_test_distribution_original,
             power_transitions_detail_original, accel_transitions_detail_original,
             power_average_original, accel_average_original,
             avg_power_change_1_2_original, avg_accel_change_1_2_original,
             avg_power_change_2_3_original, avg_accel_change_2_3_original,
             avg_power_change_3_4_original, avg_accel_change_3_4_original,
             avg_days_between_tests_original, avg_constrained_days_original,
             power_regression_users_original, accel_regression_users_original) = matrix_generator.generate_group_analysis(processed_df)
            
            # Check if any filtering is applied
            filtering_applied = standardize_resistance or (start_date > min_date or end_date < max_date) or min_days_between_tests > 0
            
            # If any filtering is enabled, generate analysis with filtered data
            if filtering_applied:
                (power_counts, accel_counts, single_test_distribution,
                 power_transitions_detail, accel_transitions_detail,
                 power_average, accel_average,
                 avg_power_change_1_2, avg_accel_change_1_2,
                 avg_power_change_2_3, avg_accel_change_2_3,
                 avg_power_change_3_4, avg_accel_change_3_4,
                 avg_days_between_tests, avg_constrained_days,
                 power_regression_users, accel_regression_users) = matrix_generator.generate_group_analysis(analysis_df)
                
                # Calculate body region averages with filtered data
                body_region_averages = matrix_generator.calculate_body_region_averages(analysis_df)
                
                # Calculate improvement thresholds with filtered data
                improvement_thresholds = matrix_generator.calculate_improvement_thresholds(analysis_df)
                
                # Add a note about filtering being applied to analysis tabs
                filter_note = "Note: Analysis is based on filtered data. "
                if start_date > min_date or end_date < max_date:
                    filter_note += f"Date range: {start_date} to {end_date}. "
                if min_days_between_tests > 0:
                    filter_note += f"Minimum days between tests: {min_days_between_tests}. "
                if standardize_resistance:
                    filter_note += "Using standard resistance values."
                
                st.info(filter_note)
                
            else:
                # Use original data if no filtering
                power_counts = power_counts_original
                accel_counts = accel_counts_original
                single_test_distribution = single_test_distribution_original
                power_transitions_detail = power_transitions_detail_original
                accel_transitions_detail = accel_transitions_detail_original
                power_average = power_average_original
                accel_average = accel_average_original
                avg_power_change_1_2 = avg_power_change_1_2_original
                avg_accel_change_1_2 = avg_accel_change_1_2_original
                avg_power_change_2_3 = avg_power_change_2_3_original
                avg_accel_change_2_3 = avg_accel_change_2_3_original
                avg_power_change_3_4 = avg_power_change_3_4_original
                avg_accel_change_3_4 = avg_accel_change_3_4_original
                avg_days_between_tests = avg_days_between_tests_original
                avg_constrained_days = avg_constrained_days_original
                power_regression_users = power_regression_users_original
                accel_regression_users = accel_regression_users_original
                
                # Calculate body region averages with original data
                body_region_averages = matrix_generator.calculate_body_region_averages(processed_df)
                
                # Calculate improvement thresholds with original data
                improvement_thresholds = matrix_generator.calculate_improvement_thresholds(processed_df)
            
            # Create main application tabs
            tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                "1. Overview", 
                "2. Group Development Analysis", 
                "3. Transition Analysis",
                "4. Body Region Analysis",
                "5. Individual Analysis",
                "6. Report Generator",
                "7. Information"
            ])
            
            # Add custom CSS for metric font size
            st.markdown("""
            <style>
            [data-testid="stMetricValue"] {
                font-size: 1rem;
            }
            [data-testid="stMetricLabel"] {
                font-size: 0.8rem;
                font-weight: 500;
            }
            </style>
            """, unsafe_allow_html=True)
            
            #############################################
            # TAB 1: OVERVIEW
            #############################################
            with tab1:
                st.markdown("<h2 style='font-size: 1.875em;'>Analysis Overview</h2>", unsafe_allow_html=True)
                
                # Athlete Metrics
                st.markdown("<h3 style='font-size: 1.5em;'>Athlete Metrics</h3>", unsafe_allow_html=True)
                athlete_metrics = get_athlete_metrics(processed_df)
                
                # Create columns for displaying athlete metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Number of Athletes", athlete_metrics['total_athletes'])
                
                with col2:
                    st.metric("Total Valid Athletes", athlete_metrics['valid_athletes'])
                    
                with col3:
                    if athlete_metrics['most_active_athlete']:
                        name, count = athlete_metrics['most_active_athlete']
                        st.metric("Most Active Athlete", f"{name} ({count} tests)")
                    else:
                        st.metric("Most Active Athlete", "No data available")
                
                # Exercise Metrics Table
                st.markdown("<h3 style='font-size: 1.5em;'>Exercise Metrics</h3>", unsafe_allow_html=True)
                # Pass both original and filtered dataframes to show both valid entries counts
                exercise_metrics_df = generate_exercise_metrics(processed_df, analysis_df)
                st.dataframe(exercise_metrics_df, use_container_width=True)
                
                # Test Session Analysis
                st.markdown("<h3 style='font-size: 1.5em;'>Test Session Analysis</h3>", unsafe_allow_html=True)
                session_types = get_top_session_types(processed_df)
                
                # Create columns for displaying session metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("1st Most Common Session", session_types['most_common'])
                
                with col2:
                    st.metric("2nd Most Common Session", session_types['second_most_common'])
                    
                with col3:
                    st.metric("3rd Most Common Session", session_types['third_most_common'])
            
            #############################################
            # TAB 2: GROUP DEVELOPMENT ANALYSIS
            #############################################
            with tab2:
                st.markdown("<h2 style='font-size: 1.875em;'>Group Development Analysis</h2>", unsafe_allow_html=True)
                
                st.markdown("<h3 style='font-size: 1.5em;'>Single Test Users</h3>", unsafe_allow_html=True)
                
                # Create two columns for side-by-side layout
                col1, col2 = st.columns(2)

                # Display Single Test Users Distribution in left column
                with col1:
                    st.write("Single Test Users Distribution")
                    styled_single_test = single_test_distribution.style.format("{:.0f}")
                    st.dataframe(styled_single_test)

                # Display average metrics in right column
                with col2:
                    st.write("Single Test Users Averages")
                    st.metric("Average Overall Power Development", f"{power_average:.1f}%")
                    st.metric("Average Overall Acceleration Development", f"{accel_average:.1f}%")

                # Display Multi-Test User Averages
                st.markdown("<h3 style='font-size: 1.5em;'>Multi-Test Users</h3>", unsafe_allow_html=True)
                
                # Create two columns for the metrics
                day_col1, day_col2 = st.columns(2)
                with day_col1:
                    st.metric("Average Days Between Tests", f"{avg_days_between_tests:.1f}")
                with day_col2:
                    st.metric("Avg Days\nBetween Tests, with Minimum", f"{avg_constrained_days:.1f}", 
                             help="Average number of days between tests after minimum days filtering")

                # Display Power development distribution and changes
                st.write("Multi-Test Users Power Development Distribution")
                styled_power_counts = power_counts.style.format("{:.0f}")
                st.dataframe(styled_power_counts, use_container_width=True)

                # Display Power changes directly below power distribution
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Power Change (Test 1→2)", f"{avg_power_change_1_2:+.1f}%",
                             delta_color="normal")
                with col2:
                    st.metric("Power Change (Test 2→3)", f"{avg_power_change_2_3:+.1f}%",
                             delta_color="normal")
                with col3:
                    st.metric("Power Change (Test 3→4)", f"{avg_power_change_3_4:+.1f}%",
                             delta_color="normal")

                # Display Acceleration development distribution
                st.write("Multi-Test Users Acceleration Development Distribution")
                styled_accel_counts = accel_counts.style.format("{:.0f}")
                st.dataframe(styled_accel_counts, use_container_width=True)

                # Display Acceleration changes directly below acceleration distribution
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Acceleration Change (Test 1→2)", f"{avg_accel_change_1_2:+.1f}%",
                             delta_color="normal")
                with col2:
                    st.metric("Acceleration Change (Test 2→3)", f"{avg_accel_change_2_3:+.1f}%",
                             delta_color="normal")
                with col3:
                    st.metric("Acceleration Change (Test 3→4)", f"{avg_accel_change_3_4:+.1f}%",
                             delta_color="normal")
            
            #############################################
            # TAB 3: TRANSITION ANALYSIS
            #############################################
            with tab3:
                st.markdown("<h2 style='font-size: 1.875em;'>Detailed Transition Analysis</h2>", unsafe_allow_html=True)

                # Display reading guide once at the top
                st.markdown("""
                <div style="background-color: #262730; color: white; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                    <h4 style="margin-top: 0; color: white;">Reading Guide:</h4>
                    <ul>
                        <li>Rows show starting bracket, columns show ending bracket.</li>
                        <li><span style="color: #4da6ff; font-weight: bold;">Diagonal values (blue)</span> show users who remained in the same bracket.</li>
                        <li><span style="color: #ff6b6b; font-weight: bold;">Above diagonal (red)</span> shows regression to lower brackets.</li>
                        <li><span style="color: #4dff4d; font-weight: bold;">Below diagonal (green)</span> shows improvement to higher brackets.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

                # Create tabs for Power and Acceleration transitions
                power_tab, accel_tab = st.tabs(["Power Transitions", "Acceleration Transitions"])

                # Power transitions tab
                with power_tab:
                    for period, matrix in power_transitions_detail.items():
                        st.write(f"Period: {period}")
                        st.dataframe(matrix, use_container_width=True)
                        
                        # Display regression users for this period if they exist
                        if period in power_regression_users and power_regression_users[period]:
                            st.markdown(f"<h4 style='font-size: 1.2em; color: #ff6b6b;'>Users who regressed in {period}:</h4>", unsafe_allow_html=True)
                            for user, from_bracket, to_bracket in power_regression_users[period]:
                                st.write(f"- **{user}**: Moved from {from_bracket} to {to_bracket}")
                        
                        st.write("---")

                # Acceleration transitions tab
                with accel_tab:
                    for period, matrix in accel_transitions_detail.items():
                        st.write(f"Period: {period}")
                        st.dataframe(matrix, use_container_width=True)
                        
                        # Display regression users for this period if they exist
                        if period in accel_regression_users and accel_regression_users[period]:
                            st.markdown(f"<h4 style='font-size: 1.2em; color: #ff6b6b;'>Users who regressed in {period}:</h4>", unsafe_allow_html=True)
                            for user, from_bracket, to_bracket in accel_regression_users[period]:
                                st.write(f"- **{user}**: Moved from {from_bracket} to {to_bracket}")
                        
                        st.write("---")
            
            #############################################
            # TAB 4: BODY REGION ANALYSIS
            #############################################
            with tab4:
                # Body Region Meta Analysis
                st.markdown("<h2 style='font-size: 1.875em;'>Body Region Meta Analysis</h2>", unsafe_allow_html=True)
                st.write("Group averages by body region for multi-test users")

                # Create columns for each body region
                region_cols = st.columns(len(VALID_EXERCISES))

                # Display each region's data
                for i, (region, averages) in enumerate(body_region_averages.items()):
                    with region_cols[i]:
                        st.write(f"**{region}**")
                        styled_averages = averages.style.format("{:.1f}%")
                        st.dataframe(styled_averages)
                
                # Detailed Body Region Analysis
                st.markdown("<h2 style='font-size: 1.875em;'>Detailed Body Region Analysis</h2>", unsafe_allow_html=True)
                st.write("Detailed exercise metrics by body region (multi-test users only)")
                
                # Create tabs for each body region
                region_tabs = st.tabs(list(VALID_EXERCISES.keys()))
                
                # Process each region in its own tab
                for i, region in enumerate(VALID_EXERCISES.keys()):
                    with region_tabs[i]:
                        st.markdown(f"<h3 style='font-size: 1.5em;'>{region} Region Analysis</h3>", unsafe_allow_html=True)
                        st.write(f"Separate power and acceleration metrics for {region.lower()} region movements (multi-test users only)")
                        
                        # Initialize all underperformer variables
                        power_underperformers_1_to_2 = None
                        power_underperformers_2_to_3 = None
                        accel_underperformers_1_to_2 = None
                        accel_underperformers_2_to_3 = None
                        
                        # Get region metrics once, using filtered data if any filtering is enabled
                        if filtering_applied:
                            region_metrics = matrix_generator.get_region_metrics(analysis_df, region)
                            # If filtering enabled, show info message
                            filter_msg = f"Showing {region} region analysis with "
                            if start_date > min_date or end_date < max_date:
                                filter_msg += f"date range: {start_date} to {end_date}"
                                if min_days_between_tests > 0 or standardize_resistance:
                                    filter_msg += " and "
                            if min_days_between_tests > 0:
                                filter_msg += f"minimum {min_days_between_tests} days between tests"
                                if standardize_resistance:
                                    filter_msg += " and "
                            if standardize_resistance:
                                filter_msg += "standard resistance filter"
                            filter_msg += " applied"
                            st.info(filter_msg)
                        else:
                            region_metrics = matrix_generator.get_region_metrics(processed_df, region)
                        
                        # Extract underperformers for all periods
                        if region_metrics[2] is not None and isinstance(region_metrics[2], dict):  # Power metrics
                            if 'underperformers_1_to_2' in region_metrics[2]:
                                power_underperformers_1_to_2 = region_metrics[2]['underperformers_1_to_2']
                            if 'underperformers_2_to_3' in region_metrics[2]:
                                power_underperformers_2_to_3 = region_metrics[2]['underperformers_2_to_3']
                        
                        if region_metrics[3] is not None and isinstance(region_metrics[3], dict):  # Acceleration metrics
                            if 'underperformers_1_to_2' in region_metrics[3]:
                                accel_underperformers_1_to_2 = region_metrics[3]['underperformers_1_to_2']
                            if 'underperformers_2_to_3' in region_metrics[3]:
                                accel_underperformers_2_to_3 = region_metrics[3]['underperformers_2_to_3']
                        
                        # Get data metrics for display
                        # Unpack the values carefully, handling different return formats
                        if region_metrics[0] is None or (isinstance(region_metrics[0], pd.DataFrame) and region_metrics[0].empty):
                            # No metrics available
                            power_df, accel_df, power_changes, accel_changes = None, None, None, None
                            lowest_power_exercise, lowest_power_value = None, None
                            lowest_accel_exercise, lowest_accel_value = None, None
                        else:
                            # Handle either 4 or 8 returned values
                            power_df, accel_df = region_metrics[0], region_metrics[1]
                            power_changes, accel_changes = region_metrics[2], region_metrics[3]
                            
                            # Check if we have the additional values for lowest changes
                            if len(region_metrics) >= 8:
                                lowest_power_exercise = region_metrics[4]
                                lowest_power_value = region_metrics[5]
                                lowest_accel_exercise = region_metrics[6]
                                lowest_accel_value = region_metrics[7]
                            else:
                                lowest_power_exercise, lowest_power_value = None, None
                                lowest_accel_exercise, lowest_accel_value = None, None
                
                        # First display the development tables
                        if (power_df is not None and isinstance(power_df, pd.DataFrame) and not power_df.empty and 
                            accel_df is not None and isinstance(accel_df, pd.DataFrame) and not accel_df.empty):
                            # Create two columns for power and acceleration
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**{region} Region Power Development (%)**")
                                
                                # Apply formatting without highlighting
                                styled_power = power_df.style.format("{:.1f}%")
                                st.dataframe(styled_power)
                                
                                # Display only the lowest change exercise (removing duplicate average changes)
                                if lowest_power_exercise is not None and lowest_power_value is not None:
                                    st.write("**Exercise with Lowest Change:**")
                                    if lowest_power_value < 0:
                                        st.markdown(f"**{lowest_power_exercise}**: <span style='color:red'>{lowest_power_value:.1f}%</span>", unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"**{lowest_power_exercise}**: <span style='color:green'>{lowest_power_value:.1f}%</span>", unsafe_allow_html=True)
                            
                            with col2:
                                st.write(f"**{region} Region Acceleration Development (%)**")
                                
                                # Apply formatting without highlighting
                                styled_accel = accel_df.style.format("{:.1f}%")
                                st.dataframe(styled_accel)
                                
                                # Display only the lowest change exercise (removing duplicate average changes)
                                if lowest_accel_exercise is not None and lowest_accel_value is not None:
                                    st.write("**Exercise with Lowest Change:**")
                                    if lowest_accel_value < 0:
                                        st.markdown(f"**{lowest_accel_exercise}**: <span style='color:red'>{lowest_accel_value:.1f}%</span>", unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"**{lowest_accel_exercise}**: <span style='color:green'>{lowest_accel_value:.1f}%</span>", unsafe_allow_html=True)
                        else:
                            st.info(f"Not enough multi-test user data to display detailed {region.lower()} region analysis.")
                            
                        # Then display Improvement Thresholds for this region
                        if region in improvement_thresholds:
                            region_thresholds = improvement_thresholds[region]
                            st.markdown("<h4 style='font-size: 1.3em;'>Group Improvement Thresholds</h4>", unsafe_allow_html=True)
                            st.write("These thresholds represent the average improvement across all users for this region. Users below these thresholds may be underperforming relative to the group.")
                            
                            # Create columns for power and acceleration thresholds
                            threshold_col1, threshold_col2 = st.columns(2)
                            
                            with threshold_col1:
                                st.markdown("**Power Improvement Thresholds:**")
                                
                                # Test 1 to Test 2 Power Threshold
                                if not pd.isna(region_thresholds['power_1_to_2']):
                                    power_value = region_thresholds['power_1_to_2']
                                    color = "green" if power_value >= 0 else "red"
                                    st.markdown(f"**Test 1 → Test 2:** <span style='color:{color}; font-size:1.1em;'>{power_value:.1f}%</span>", unsafe_allow_html=True)
                                else:
                                    st.markdown("**Test 1 → Test 2:** Not enough data")
                                    
                                # Test 2 to Test 3 Power Threshold
                                if not pd.isna(region_thresholds['power_2_to_3']):
                                    power_value = region_thresholds['power_2_to_3']
                                    color = "green" if power_value >= 0 else "red"
                                    st.markdown(f"**Test 2 → Test 3:** <span style='color:{color}; font-size:1.1em;'>{power_value:.1f}%</span>", unsafe_allow_html=True)
                                else:
                                    st.markdown("**Test 2 → Test 3:** Not enough data")
                            
                            with threshold_col2:
                                st.markdown("**Acceleration Improvement Thresholds:**")
                                
                                # Test 1 to Test 2 Acceleration Threshold
                                if not pd.isna(region_thresholds['accel_1_to_2']):
                                    accel_value = region_thresholds['accel_1_to_2']
                                    color = "green" if accel_value >= 0 else "red"
                                    st.markdown(f"**Test 1 → Test 2:** <span style='color:{color}; font-size:1.1em;'>{accel_value:.1f}%</span>", unsafe_allow_html=True)
                                else:
                                    st.markdown("**Test 1 → Test 2:** Not enough data")
                                    
                                # Test 2 to Test 3 Acceleration Threshold
                                if not pd.isna(region_thresholds['accel_2_to_3']):
                                    accel_value = region_thresholds['accel_2_to_3']
                                    color = "green" if accel_value >= 0 else "red"
                                    st.markdown(f"**Test 2 → Test 3:** <span style='color:{color}; font-size:1.1em;'>{accel_value:.1f}%</span>", unsafe_allow_html=True)
                                else:
                                    st.markdown("**Test 2 → Test 3:** Not enough data")
                                
                            # Create combined underperformers table with checkboxes
                            st.markdown("<h4 style='font-size: 1.3em;'>Underperforming Users</h4>", unsafe_allow_html=True)
                            
                            # Test 1 to Test 2
                            if (not pd.isna(region_thresholds['power_1_to_2']) and not pd.isna(region_thresholds['accel_1_to_2']) and 
                                (power_underperformers_1_to_2 or accel_underperformers_1_to_2)):
                                st.write("**Test 1 → Test 2 Underperformers:**")
                                underperformers_table_1_to_2 = create_underperformers_table(
                                    region, "1_to_2", power_underperformers_1_to_2, accel_underperformers_1_to_2)
                                if underperformers_table_1_to_2 is not None:
                                    st.dataframe(underperformers_table_1_to_2)
                                    
                                    # Add download buttons for detailed CSV data
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        if power_underperformers_1_to_2:
                                            csv_data = generate_underperformers_csv(
                                                region, "Power", "1_to_2", power_underperformers_1_to_2)
                                            st.download_button(
                                                label="Download Power Details",
                                                data=csv_data,
                                                file_name=f"{region}_power_underperformers_test1to2.csv",
                                                mime="text/csv",
                                                key=f"{region}_power_test1to2_download"
                                            )
                                    with col2:
                                        if accel_underperformers_1_to_2:
                                            csv_data = generate_underperformers_csv(
                                                region, "Acceleration", "1_to_2", accel_underperformers_1_to_2)
                                            st.download_button(
                                                label="Download Acceleration Details",
                                                data=csv_data,
                                                file_name=f"{region}_accel_underperformers_test1to2.csv",
                                                mime="text/csv",
                                                key=f"{region}_accel_test1to2_download"
                                            )
                                else:
                                    st.info("No underperforming users")
                            
                            # Test 2 to Test 3
                            if (not pd.isna(region_thresholds['power_2_to_3']) and not pd.isna(region_thresholds['accel_2_to_3']) and 
                                (power_underperformers_2_to_3 or accel_underperformers_2_to_3)):
                                st.write("**Test 2 → Test 3 Underperformers:**")
                                underperformers_table_2_to_3 = create_underperformers_table(
                                    region, "2_to_3", power_underperformers_2_to_3, accel_underperformers_2_to_3)
                                if underperformers_table_2_to_3 is not None:
                                    st.dataframe(underperformers_table_2_to_3)
                                    
                                    # Add download buttons for detailed CSV data
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        if power_underperformers_2_to_3:
                                            csv_data = generate_underperformers_csv(
                                                region, "Power", "2_to_3", power_underperformers_2_to_3)
                                            st.download_button(
                                                label="Download Power Details",
                                                data=csv_data,
                                                file_name=f"{region}_power_underperformers_test2to3.csv",
                                                mime="text/csv",
                                                key=f"{region}_power_test2to3_download"
                                            )
                                    with col2:
                                        if accel_underperformers_2_to_3:
                                            csv_data = generate_underperformers_csv(
                                                region, "Acceleration", "2_to_3", accel_underperformers_2_to_3)
                                            st.download_button(
                                                label="Download Acceleration Details",
                                                data=csv_data,
                                                file_name=f"{region}_accel_underperformers_test2to3.csv",
                                                mime="text/csv",
                                                key=f"{region}_accel_test2to3_download"
                                            )
                                else:
                                    st.info("No underperforming users")
                                    
                            st.markdown("<hr>", unsafe_allow_html=True)

            #############################################
            # TAB 5: INDIVIDUAL ANALYSIS
            #############################################
            with tab5:
                # User selection for individual analysis
                st.markdown("<h2 style='font-size: 1.875em;'>Individual User Analysis</h2>", unsafe_allow_html=True)
                
                # Use filtered user list if any filtering is applied
                if filtering_applied:
                    users = data_processor.get_user_list(analysis_df)
                    
                    # Show filtering info
                    filter_msg = "Showing user analysis with "
                    if start_date > min_date or end_date < max_date:
                        filter_msg += f"date range: {start_date} to {end_date}"
                        if standardize_resistance:
                            filter_msg += " and "
                    if standardize_resistance:
                        filter_msg += "standard resistance filter"
                    filter_msg += " applied"
                    st.info(filter_msg)
                else:
                    users = data_processor.get_user_list(processed_df)
                
                selected_user = st.selectbox("Select User", users)

                if selected_user:
                    # Generate matrices using filtered data if any filtering is applied
                    if filtering_applied:
                        matrices = matrix_generator.generate_user_matrices(
                            analysis_df, selected_user)
                    else:
                        matrices = matrix_generator.generate_user_matrices(
                            processed_df, selected_user)

                    power_matrix, accel_matrix, power_dev_matrix, accel_dev_matrix, overall_dev_matrix, power_brackets, accel_brackets = matrices

                    # Special handling to ensure Vertical Jump is visible
                    if 'Vertical Jump (Countermovement)' not in power_matrix.index:
                        print("DEBUG: Vertical Jump missing from power_matrix index - attempting to add it")
                        # Try to add it if it's missing
                        try:
                            # Create a new row with NaN values for all columns
                            new_row = pd.Series([np.nan] * len(power_matrix.columns), index=power_matrix.columns, name='Vertical Jump (Countermovement)')
                            # Add the row to the DataFrame
                            power_matrix = pd.concat([power_matrix, pd.DataFrame(new_row).T])
                            # Same for acceleration matrix
                            new_row_accel = pd.Series([np.nan] * len(accel_matrix.columns), index=accel_matrix.columns, name='Vertical Jump (Countermovement)')
                            accel_matrix = pd.concat([accel_matrix, pd.DataFrame(new_row_accel).T])
                        except Exception as e:
                            print(f"ERROR: Failed to add Vertical Jump row: {e}")

                    # Ensure Vertical Jump is always shown, even if it has NaN values
                    if 'Vertical Jump (Countermovement)' in power_matrix.index:
                        print(f"DEBUG: Vertical Jump IS in power_matrix index with values: {power_matrix.loc['Vertical Jump (Countermovement)'].values}")
                    else:
                        print("DEBUG: Vertical Jump still missing from power_matrix after attempted fix")

                    # Display raw value matrices in a collapsible section
                    with st.expander("Raw Value Matrices", expanded=False):
                        st.write("Power Matrix (Raw Values)")
                        st.dataframe(power_matrix)

                        st.write("Acceleration Matrix (Raw Values)")
                        st.dataframe(accel_matrix)

                    # Display development matrices if available
                    if power_dev_matrix is not None and accel_dev_matrix is not None:
                        # Special handling to ensure Vertical Jump is visible in development matrices too
                        if 'Vertical Jump (Countermovement)' not in power_dev_matrix.index:
                            print("DEBUG: Vertical Jump missing from power_dev_matrix index - attempting to add it")
                            try:
                                # Create a new row with NaN values for all columns
                                new_row = pd.Series([np.nan] * len(power_dev_matrix.columns), index=power_dev_matrix.columns, name='Vertical Jump (Countermovement)')
                                # Add the row to the DataFrame
                                power_dev_matrix = pd.concat([power_dev_matrix, pd.DataFrame(new_row).T])
                                # Same for acceleration matrix
                                new_row_accel = pd.Series([np.nan] * len(accel_dev_matrix.columns), index=accel_dev_matrix.columns, name='Vertical Jump (Countermovement)')
                                accel_dev_matrix = pd.concat([accel_dev_matrix, pd.DataFrame(new_row_accel).T])
                            except Exception as e:
                                print(f"ERROR: Failed to add Vertical Jump row to dev matrices: {e}")

                        # Display development matrices in a collapsible section
                        with st.expander("Development Score Matrices (%)", expanded=False):
                            st.write("Power Development Matrix")
                            styled_power_dev = power_dev_matrix.style.format("{:.1f}%")
                            st.dataframe(styled_power_dev)

                            st.write("Acceleration Development Matrix")
                            styled_accel_dev = accel_dev_matrix.style.format("{:.1f}%")
                            st.dataframe(styled_accel_dev)

                        # Display overall development categorization
                        if overall_dev_matrix is not None:
                            with st.expander("Overall Development Categorization", expanded=True):
                                styled_overall_dev = overall_dev_matrix.style.format("{:.1f}%")
                                st.dataframe(styled_overall_dev)

                        # Display development brackets
                        if power_brackets is not None and accel_brackets is not None:
                            with st.expander("Development Brackets", expanded=False):
                                col1, col2 = st.columns(2)

                                with col1:
                                    st.write("Power Development Brackets")
                                    st.dataframe(power_brackets)

                                with col2:
                                    st.write("Acceleration Development Brackets")
                                    st.dataframe(accel_brackets)

                    # Export functionality in a collapsible section
                    with st.expander("Export Data", expanded=False):
                        def download_matrix(matrix, name):
                            return matrix.to_csv().encode('utf-8')

                        for matrix, name in [
                            (power_matrix, "power"),
                            (accel_matrix, "acceleration"),
                            (power_dev_matrix, "power_development"),
                            (accel_dev_matrix, "acceleration_development"),
                            (overall_dev_matrix, "overall_development"),
                            (power_brackets, "power_brackets"),
                            (accel_brackets, "acceleration_brackets"),
                            (power_counts, "power_group_analysis"),
                            (accel_counts, "acceleration_group_analysis"),
                            (single_test_distribution, "single_test_distribution")
                        ]:
                            if matrix is not None:
                                st.download_button(
                                    label=f"Download {name.replace('_', ' ').title()} Matrix CSV",
                                    data=download_matrix(matrix, name),
                                    file_name=f"{selected_user}_{name}_matrix.csv",
                                    mime="text/csv",
                                    key=f"individual_{name}_download"
                                )
                        
            #############################################
            # TAB 6: REPORT GENERATOR
            #############################################
            with tab6:
                # Report Generator Section
                st.markdown("<h2 style='font-size: 1.875em;'>Report Generator</h2>", unsafe_allow_html=True)
                st.write("Generate comprehensive reports with interactive analysis")
                
                # Comprehensive report section
                st.subheader("Comprehensive Interactive Report")
                st.write("This report includes detailed analysis with separate pages for each body region and interactive navigation")
                
                # Prompt for site name
                site_name = st.text_input("Site Name", placeholder="Enter site name for report header")
                
                # First collect region metrics for all regions
                region_metrics = {}
                for region in VALID_EXERCISES.keys():
                    # Use filtered or original data based on filtering state
                    if filtering_applied:
                        region_metrics[region] = matrix_generator.get_region_metrics(analysis_df, region)
                    else:
                        region_metrics[region] = matrix_generator.get_region_metrics(processed_df, region)
                
                # Add filtering info for the report
                if filtering_applied:
                    filter_msg = "Report will be generated using filtered data"
                    if start_date > min_date or end_date < max_date:
                        filter_msg += f" (date range: {start_date} to {end_date}"
                        if standardize_resistance:
                            filter_msg += ", with standard resistance values"
                        filter_msg += ")"
                    elif standardize_resistance:
                        filter_msg += " (using standard resistance values)"
                    st.info(filter_msg)
                
                # Only enable the download button if a site name is provided
                if site_name.strip() != "":
                    # Create comprehensive report
                    comprehensive_report = report_generator.generate_comprehensive_report(
                        power_counts,
                        accel_counts,
                        power_transitions_detail,
                        accel_transitions_detail,
                        body_region_averages,
                        improvement_thresholds,
                        region_metrics,
                        site_name=site_name,
                        single_test_distribution=single_test_distribution
                    )
                    st.download_button(
                        label="Download Comprehensive Report (HTML)",
                        data=comprehensive_report,
                        file_name=f"{site_name.strip()}_comprehensive_report.html" if site_name.strip() else "comprehensive_report.html",
                        mime="text/html",
                        key="comprehensive_report_download"
                    )
                    
                    # Generate PDF report
                    comprehensive_pdf_report = report_generator.generate_comprehensive_pdf_report(
                        power_counts,
                        accel_counts,
                        power_transitions_detail,
                        accel_transitions_detail,
                        body_region_averages,
                        improvement_thresholds,
                        region_metrics,
                        site_name=site_name,
                        single_test_distribution=single_test_distribution
                    )
                    
                    # Add a PDF download button
                    st.download_button(
                        label="Download Comprehensive Report (PDF)",
                        data=comprehensive_pdf_report,
                        file_name=f"{site_name.strip()}_comprehensive_report.pdf" if site_name.strip() else "comprehensive_report.pdf",
                        mime="application/pdf",
                        key="comprehensive_pdf_report_download"
                    )
                else:
                    # Display disabled buttons with message
                    st.info("Please enter a site name to enable the report downloads")
                    st.button("Download Comprehensive Report (HTML)", disabled=True, key="disabled_html_download")
                    st.button("Download Comprehensive Report (PDF)", disabled=True, key="disabled_pdf_download")
                
                # Add an explanation about the report
                st.write("**Comprehensive Report**: Includes all analysis data with interactive navigation between pages, site identification, and detailed region-specific metrics")
                
                # Future features info
                with st.expander("Upcoming Features", expanded=False):
                    st.info("Custom report generation will be available in a future update.")

                # Display exercise information with standards
                with st.expander("View Tracked Exercises and Goal Standards"):
                    # First show Standard Resistances Table
                    st.subheader("Standard Resistance Values")
                    st.write("These are the standard resistance values used for filtering when 'Enable Resistance Standardization' is checked:")
                    
                    # Create a DataFrame from the standard resistances
                    resistance_data = []
                    for exercise, resistance in STANDARD_RESISTANCES.items():
                        resistance_data.append({
                            'Exercise': exercise,
                            'Standard Resistance (lbs)': resistance
                        })
                    
                    # Display standard resistances table
                    if resistance_data:
                        df_resistances = pd.DataFrame(resistance_data)
                        st.dataframe(df_resistances, use_container_width=True)
                    
                    # Add a separator
                    st.markdown("---")
                    
                    # Then show Goal Standards by category
                    st.subheader("Goal Standards by Category")
                    for category, exercises in VALID_EXERCISES.items():
                        st.write(f"**{category}**")

                        # Create a DataFrame to display standards
                        standards_data = []
                        for exercise in exercises:
                            male_power = POWER_STANDARDS['male'][exercise]
                            male_accel = ACCELERATION_STANDARDS['male'][exercise]
                            female_power = POWER_STANDARDS['female'][exercise]
                            female_accel = ACCELERATION_STANDARDS['female'][exercise]

                            # Get standard resistance if available
                            std_resistance = "N/A"
                            for std_exercise, resistance in STANDARD_RESISTANCES.items():
                                if std_exercise in exercise:
                                    std_resistance = f"{resistance} lbs"
                                    break

                            standards_data.append({
                                'Exercise': exercise,
                                'Standard Resistance': std_resistance,
                                'Male Power': male_power,
                                'Male Acceleration': male_accel,
                                'Female Power': female_power,
                                'Female Acceleration': female_accel
                            })

                        # Display standards table
                        if standards_data:
                            df_standards = pd.DataFrame(standards_data)
                            styled_standards = df_standards.style.format({
                                'Male Power': '{:.0f}',
                                'Male Acceleration': '{:.0f}',
                                'Female Power': '{:.0f}',
                                'Female Acceleration': '{:.0f}'
                            })
                            st.dataframe(styled_standards, use_container_width=True)
                            
            #############################################
            # TAB 7: INFORMATION
            #############################################
            with tab7:
                st.markdown("<h2 style='font-size: 1.875em;'>Information</h2>", unsafe_allow_html=True)
                
                # Application Overview Section
                with st.expander("Application Overview", expanded=True):
                    st.markdown("""
                    ### Pythagoras
                    
                    This application processes exercise data to track athlete development over time. It categorizes performance into brackets based on power and acceleration metrics, and provides detailed analysis at both individual and group levels.
                    
                    #### Core Functionality
                    - Processes CSV or Excel files containing exercise performance data
                    - Organizes exercises into chronological "test instances" for each user
                    - Categorizes development into 6 brackets ranging from "Goal Hit" to "Severely Under Developed"
                    - Tracks progression between brackets over time
                    - Identifies underperforming users relative to group averages
                    - Generates comprehensive reports with detailed data visualizations
                    """)
                
                # Development Score Calculation
                with st.expander("Development Score Calculation", expanded=False):
                    st.markdown("""
                    ### Development Score Calculation
                    
                    Development scores are calculated as a percentage of goal standards for each exercise:
                    
                    ```
                    Development Score = (User's value / Goal standard) × 100
                    ```
                    
                    #### Development Brackets
                    Development scores are categorized into the following brackets:
                    
                    | Bracket | Score Range |
                    |---------|-------------|
                    | Goal Hit | 100% and above |
                    | Elite | 90% - 99.99% |
                    | Above Average | 76% - 90% |
                    | Average | 51% - 75% |
                    | Under Developed | 26% - 50% |
                    | Severely Under Developed | 0% - 25% |
                    
                    #### Goal Standards
                    Goal standards are sex-specific reference values for each exercise. These values represent optimal performance targets.
                    """)
                    
                    # Create a table of goal standards by exercise
                    st.markdown("##### Power Standards (Watts)")
                    power_standards_data = []
                    for exercise in sorted(POWER_STANDARDS['male'].keys()):
                        power_standards_data.append({
                            'Exercise': exercise,
                            'Male': POWER_STANDARDS['male'].get(exercise, '-'),
                            'Female': POWER_STANDARDS['female'].get(exercise, '-')
                        })
                    
                    st.dataframe(pd.DataFrame(power_standards_data), use_container_width=True)
                    
                    st.markdown("##### Acceleration Standards (m/s²)")
                    accel_standards_data = []
                    for exercise in sorted(ACCELERATION_STANDARDS['male'].keys()):
                        accel_standards_data.append({
                            'Exercise': exercise,
                            'Male': ACCELERATION_STANDARDS['male'].get(exercise, '-'),
                            'Female': ACCELERATION_STANDARDS['female'].get(exercise, '-')
                        })
                    
                    st.dataframe(pd.DataFrame(accel_standards_data), use_container_width=True)
                
                # Exercise Information
                with st.expander("Exercise Information", expanded=False):
                    st.markdown("""
                    ### Exercise Information
                    
                    #### Body Regions
                    Exercises are categorized into the following body regions:
                    """)
                    
                    for region, exercises in VALID_EXERCISES.items():
                        st.markdown(f"**{region}**")
                        for exercise in exercises:
                            st.markdown(f"- {exercise}")
                    
                    st.markdown("#### Standard Resistance Values")
                    st.markdown("""
                    The application can filter data to include only exercises performed at standard resistance values.
                    This helps ensure comparability of results across users and tests.
                    """)
                    
                    resistance_data = []
                    for exercise, resistance in STANDARD_RESISTANCES.items():
                        resistance_data.append({
                            'Exercise': exercise,
                            'Standard Resistance (lbs)': resistance
                        })
                    
                    st.dataframe(pd.DataFrame(resistance_data), use_container_width=True)
                
                # Data Organization
                with st.expander("Data Organization", expanded=False):
                    st.markdown("""
                    ### Data Organization
                    
                    #### Test Instances
                    Chronological "test instances" are created for each user by organizing exercises by date:
                    - The first chronological exercise becomes part of Test 1
                    - The next exercise becomes part of Test 2, and so on
                    - If an exercise is repeated, it occupies the next available test instance
                    
                    This approach allows tracking improvement over time across different exercises.
                    
                    #### Improvement Threshold
                    The improvement threshold is calculated as the average percentage change across all users
                    for a specific body region between consecutive tests. This serves as a reference point
                    to determine which users are underperforming relative to the group average.
                    
                    #### Minimum Days Between Tests
                    When the minimum days filter is applied:
                    1. The first chronological test for each exercise is always included
                    2. Subsequent tests are only included if they occur at least the specified number of days after the previous test
                    3. This filtering is done at the raw data level before organizing into test instances
                    """)
                
                # Tab Explanations
                with st.expander("Tab Explanations", expanded=False):
                    st.markdown("""
                    ### Tab Explanations
                    
                    #### 1. Overview
                    Provides a high-level summary of the dataset including:
                    - Athlete metrics (total athletes, valid athletes, most active)
                    - Exercise metrics (execution counts, resistance patterns)
                    - Test session analysis (most common session types)
                    
                    #### 2. Group Development Analysis
                    Shows the distribution of users across development brackets:
                    - Separate analysis for single-test and multi-test users
                    - Power and acceleration distributions
                    - Average days between tests metrics
                    - Percentage changes between consecutive tests
                    
                    #### 3. Transition Analysis
                    Visualizes how users move between development brackets over time:
                    - Color-coded matrices (blue = no change, red = regression, green = improvement)
                    - Lists users who regressed between tests
                    - Separate analysis for power and acceleration
                    
                    #### 4. Body Region Analysis
                    Analyzes performance by body region:
                    - Group averages for multi-test users
                    - Detailed exercise metrics for each region
                    - Underperforming users tables
                    - Allows downloading underperformer lists as CSV
                    
                    #### 5. Individual Analysis
                    Provides detailed analysis for specific users:
                    - Test matrices showing all exercise values
                    - Development categorization
                    - Graph visualizations of progress
                    
                    #### 6. Report Generator
                    Creates comprehensive reports for sharing or documentation:
                    - Interactive HTML reports with separate pages for each section
                    - Comprehensive data visualizations
                    - Optional site name for identification
                    """)
                
                # Data Filtering
                with st.expander("Data Filtering", expanded=False):
                    st.markdown("""
                    ### Data Filtering
                    
                    The application provides several filtering options to refine analysis:
                    
                    #### Resistance Standardization
                    When enabled, only includes data where exercises were performed at standard resistance values.
                    A small tolerance (±0.5 lbs) is allowed to account for minor variations.
                    
                    #### Evaluation Window
                    Filters data to a specific date range, allowing focus on particular testing periods.
                    
                    #### Minimum Days Between Tests
                    Ensures tests for the same exercise are separated by at least the specified number of days.
                    This helps prevent including tests that are too close together, which might not reflect
                    meaningful physiological changes.
                    
                    When filters are applied:
                    - The original metrics are preserved for reference in the Overview tab
                    - All other analyses reflect the filtered dataset
                    - Filter settings are noted at the top of each analysis section
                    """)
                
                # Data Requirements
                with st.expander("Data Requirements", expanded=False):
                    st.markdown("""
                    ### Data Requirements
                    
                    For proper functioning, your CSV or Excel file must include the following columns:
                    
                    | Column | Description |
                    |--------|-------------|
                    | `user name` | The name or ID of the user |
                    | `sex` | User's sex (male/female) - needed for goal standards |
                    | `exercise name` | The name of the exercise performed |
                    | `dominance` | Hand/foot dominance for appropriate exercises |
                    | `exercise createdAt` | Timestamp when the exercise was performed |
                    | `power - high` | Power measurement (in watts) |
                    | `acceleration - high` | Acceleration measurement (in m/s²) |
                    | `resistance` | Weight/resistance used (optional, for filtering) |
                    | `session name` | Test session identifier (optional) |
                    
                    Missing values for power or acceleration will result in those exercises being excluded from analysis.
                    """)

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main()