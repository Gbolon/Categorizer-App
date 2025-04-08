import streamlit as st
import pandas as pd
import numpy as np
import io
import csv
from data_processor import DataProcessor
from matrix_generator import MatrixGenerator
from report_generator import ReportGenerator
from exercise_constants import VALID_EXERCISES
from goal_standards import POWER_STANDARDS, ACCELERATION_STANDARDS

# Configure the page at the very beginning
st.set_page_config(
    page_title="Site Development Bracketer",
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

def main():
    st.markdown("<h1 style='font-size: 3em;'>Site Development Bracketer</h1>", unsafe_allow_html=True)

    # Initialize processors
    data_processor = DataProcessor()
    matrix_generator = MatrixGenerator()
    report_generator = ReportGenerator()

    # File upload and minimum days configuration
    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader("Upload your exercise data (CSV or Excel)", 
                                          type=['csv', 'xlsx'])
    with col2:
        min_days_between_tests = st.number_input(
            "Minimum Days Between Tests",
            min_value=0,
            max_value=365,
            value=7,
            help="Minimum number of days required between test instances for the same exercise"
        )

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
            
            # Show resistance filtering information
            with st.expander("Data Processing Information", expanded=True):
                st.info("""
                **Resistance Filtering Applied**
                
                This app now automatically filters exercise data to only include movements performed at specific required resistance values:
                - Chest Press (One Hand): 12 lbs
                - Horizontal Row (One Hand): 12 lbs
                - Biceps Curl (One Hand): 6 lbs
                - Triceps Extension (One Hand): 6 lbs
                - PNF D2 Flexion: 6 lbs
                - PNF D2 Extension: 6 lbs
                - Straight Arm Trunk Rotation: 12 lbs
                - Lateral Bound: 6 lbs
                - Shot Put (Countermovement): 18 lbs
                - Vertical Jump (Countermovement): 6 lbs
                
                Only exercise instances performed at these exact resistance values will be included in the analysis.
                If the dataset doesn't include a 'resistance' column, this filtering won't be applied.
                """)

            # Show data preview in collapsed expander
            with st.expander("Data Preview", expanded=False):
                st.dataframe(processed_df.head())

            # Generate group-level analysis
            (power_counts, accel_counts, single_test_distribution,
             power_transitions_detail, accel_transitions_detail,
             power_average, accel_average,
             avg_power_change_1_2, avg_accel_change_1_2,
             avg_power_change_2_3, avg_accel_change_2_3,
             original_avg_days_between_tests, constrained_avg_days_between_tests) = matrix_generator.generate_group_analysis(processed_df, min_days=min_days_between_tests)

            # Display group-level analysis
            st.markdown("<h2 style='font-size: 1.875em;'>Group Development Analysis</h2>", unsafe_allow_html=True)

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
            st.markdown("<h2 style='font-size: 1.875em;'>Multi-Test User Averages</h2>", unsafe_allow_html=True)
            
            # Create two columns for the averages
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Original Average Days Between Tests", f"{original_avg_days_between_tests:.1f}")
            
            with col2:
                st.metric("Constrained Average Days Between Tests", f"{constrained_avg_days_between_tests:.1f}")

            # Display Power development distribution and changes
            st.write("Multi-Test Users Power Development Distribution")
            styled_power_counts = power_counts.style.format("{:.0f}")
            st.dataframe(styled_power_counts, use_container_width=True)

            # Display Power changes directly below power distribution
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Power Change (Test 1→2)", f"{avg_power_change_1_2:+.1f}%",
                         delta_color="normal")
            with col2:
                st.metric("Power Change (Test 2→3)", f"{avg_power_change_2_3:+.1f}%",
                         delta_color="normal")

            # Display Acceleration development distribution
            st.write("Multi-Test Users Acceleration Development Distribution")
            styled_accel_counts = accel_counts.style.format("{:.0f}")
            st.dataframe(styled_accel_counts, use_container_width=True)

            # Display Acceleration changes directly below acceleration distribution
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Acceleration Change (Test 1→2)", f"{avg_accel_change_1_2:+.1f}%",
                         delta_color="normal")
            with col2:
                st.metric("Acceleration Change (Test 2→3)", f"{avg_accel_change_2_3:+.1f}%",
                         delta_color="normal")

            # Display detailed transition analysis
            st.markdown("<h2 style='font-size: 1.875em;'>Detailed Transition Analysis</h2>", unsafe_allow_html=True)

            # Display reading guide once at the top
            st.write("Reading guide: Rows show starting bracket, columns show ending bracket. Numbers show how many users made each transition.")
            st.write("Diagonal values (blue) show users who remained in the same bracket.")
            st.write("Above diagonal (red) shows regression to lower brackets.")
            st.write("Below diagonal (green) shows improvement to higher brackets.")

            # Create tabs for Power and Acceleration transitions
            power_tab, accel_tab = st.tabs(["Power Transitions", "Acceleration Transitions"])

            # Power transitions tab
            with power_tab:
                for period, matrix in power_transitions_detail.items():
                    st.write(f"Period: {period}")
                    st.dataframe(matrix, use_container_width=True)
                    st.write("---")

            # Acceleration transitions tab
            with accel_tab:
                for period, matrix in accel_transitions_detail.items():
                    st.write(f"Period: {period}")
                    st.dataframe(matrix, use_container_width=True)
                    st.write("---")

            # Body Region Meta Analysis
            st.markdown("<h2 style='font-size: 1.875em;'>Body Region Meta Analysis</h2>", unsafe_allow_html=True)
            st.write("Group averages by body region for multi-test users")

            # Calculate body region averages
            body_region_averages = matrix_generator.calculate_body_region_averages(processed_df, min_days=min_days_between_tests)

            # Create columns for each body region
            region_cols = st.columns(len(VALID_EXERCISES))

            # Display each region's data
            for i, (region, averages) in enumerate(body_region_averages.items()):
                with region_cols[i]:
                    st.write(f"**{region}**")
                    styled_averages = averages.style.format("{:.1f}%")
                    st.dataframe(styled_averages)
            
            # Calculate improvement thresholds for all regions
            improvement_thresholds = matrix_generator.calculate_improvement_thresholds(processed_df, min_days=min_days_between_tests)
            
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
                    
                    # Get region metrics only once
                    region_metrics = matrix_generator.get_region_metrics(processed_df, region, min_days=min_days_between_tests)
                    
                    # Extract underperformers for all periods
                    if region_metrics[2]:  # Power metrics
                        if 'underperformers_1_to_2' in region_metrics[2]:
                            power_underperformers_1_to_2 = region_metrics[2]['underperformers_1_to_2']
                        if 'underperformers_2_to_3' in region_metrics[2]:
                            power_underperformers_2_to_3 = region_metrics[2]['underperformers_2_to_3']
                    
                    if region_metrics[3]:  # Acceleration metrics
                        if 'underperformers_1_to_2' in region_metrics[3]:
                            accel_underperformers_1_to_2 = region_metrics[3]['underperformers_1_to_2']
                        if 'underperformers_2_to_3' in region_metrics[3]:
                            accel_underperformers_2_to_3 = region_metrics[3]['underperformers_2_to_3']
                    
                    # Display Improvement Thresholds for this region
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
                                            mime="text/csv"
                                        )
                                with col2:
                                    if accel_underperformers_1_to_2:
                                        csv_data = generate_underperformers_csv(
                                            region, "Acceleration", "1_to_2", accel_underperformers_1_to_2)
                                        st.download_button(
                                            label="Download Acceleration Details",
                                            data=csv_data,
                                            file_name=f"{region}_accel_underperformers_test1to2.csv",
                                            mime="text/csv"
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
                                            mime="text/csv"
                                        )
                                with col2:
                                    if accel_underperformers_2_to_3:
                                        csv_data = generate_underperformers_csv(
                                            region, "Acceleration", "2_to_3", accel_underperformers_2_to_3)
                                        st.download_button(
                                            label="Download Acceleration Details",
                                            data=csv_data,
                                            file_name=f"{region}_accel_underperformers_test2to3.csv",
                                            mime="text/csv"
                                        )
                            else:
                                st.info("No underperforming users")
                                
                        st.markdown("<hr>", unsafe_allow_html=True)
                    
                    # Get detailed region metrics using the generalized function for all regions
                    region_metrics = matrix_generator.get_region_metrics(processed_df, region, min_days=min_days_between_tests)
                    # Unpack the values carefully, handling different return formats
                    if region_metrics[0] is None:
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
            
                    if power_df is not None and accel_df is not None:
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


            # User selection for individual analysis
            st.markdown("<h2 style='font-size: 1.875em;'>Individual User Analysis</h2>", unsafe_allow_html=True)
            users = data_processor.get_user_list(processed_df)
            selected_user = st.selectbox("Select User", users)

            if selected_user:
                # Generate matrices
                matrices = matrix_generator.generate_user_matrices(
                    processed_df, selected_user, min_days=min_days_between_tests)

                # The matrices unpacking needs to handle both old and new return formats
                if len(matrices) == 8:
                    # New format with user_data as first return value
                    user_data, power_matrix, accel_matrix, power_dev_matrix, accel_dev_matrix, overall_dev_matrix, power_brackets, accel_brackets = matrices
                else:
                    # Original format with 7 return values
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
                                mime="text/csv"
                            )
                        
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
                region_metrics[region] = matrix_generator.get_region_metrics(processed_df, region, min_days=min_days_between_tests)
            
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
                    min_days_between_tests=min_days_between_tests,
                    original_avg_days=original_avg_days_between_tests,
                    constrained_avg_days=constrained_avg_days_between_tests
                )
                st.download_button(
                    label="Download Comprehensive Report",
                    data=comprehensive_report,
                    file_name="comprehensive_report.html",
                    mime="text/html",
                )
            else:
                # Display disabled button with message
                st.info("Please enter a site name to enable the report download")
                st.button("Download Comprehensive Report", disabled=True)
            
            # Add an explanation about the report
            st.write("**Comprehensive Report**: Includes all analysis data with interactive navigation between pages, site identification, and detailed region-specific metrics")
            
            # Future features info
            with st.expander("Upcoming Features", expanded=False):
                st.info("Custom report generation will be available in a future update.")

            # Display exercise information with standards
            with st.expander("View Tracked Exercises and Goal Standards"):
                for category, exercises in VALID_EXERCISES.items():
                    st.subheader(category)

                    # Create a DataFrame to display standards
                    standards_data = []
                    for exercise in exercises:
                        male_power = POWER_STANDARDS['male'][exercise]
                        male_accel = ACCELERATION_STANDARDS['male'][exercise]
                        female_power = POWER_STANDARDS['female'][exercise]
                        female_accel = ACCELERATION_STANDARDS['female'][exercise]

                        standards_data.append({
                            'Exercise': exercise,
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

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main()