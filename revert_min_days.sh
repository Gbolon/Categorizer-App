#!/bin/bash

# Remove min_days parameter from generate_group_analysis function in matrix_generator.py
sed -i 's/def generate_group_analysis(self, df, max_tests=4, min_days=0):/def generate_group_analysis(self, df, max_tests=4):/' matrix_generator.py

# Remove min_days parameter from generate_user_matrices function in matrix_generator.py
sed -i 's/, min_days=min_days)/)/g' matrix_generator.py

# Remove min_days parameter filtering logic from generate_user_matrices
sed -i '/# Apply minimum days filter if specified/,/print(f"DEBUG: Applied min_days={min_days} filter, keeping {len(user_data)} instances out of original set")/d' matrix_generator.py

# Remove min_days parameter from calculate_body_region_averages function
sed -i 's/def calculate_body_region_averages(self, df, max_tests=4, min_days=0):/def calculate_body_region_averages(self, df, max_tests=4):/' matrix_generator.py

# Remove min_days parameter from get_region_metrics function
sed -i 's/def get_region_metrics(self, df, region_name, max_tests=4, min_days=0):/def get_region_metrics(self, df, region_name, max_tests=4):/' matrix_generator.py

# Remove min_days parameter from get_torso_region_metrics function
sed -i 's/def get_torso_region_metrics(self, df, max_tests=4, min_days=0):/def get_torso_region_metrics(self, df, max_tests=4):/' matrix_generator.py

# Remove min_days parameter from calculate_improvement_thresholds function
sed -i 's/def calculate_improvement_thresholds(self, df, min_days=0):/def calculate_improvement_thresholds(self, df):/' matrix_generator.py

# Remove min_days parameter from app.py call to generate_group_analysis
sed -i 's/matrix_generator.generate_group_analysis(processed_df, min_days=min_days_between_tests)/matrix_generator.generate_group_analysis(processed_df)/g' app.py

# Remove min_days parameter from app.py call to calculate_body_region_averages
sed -i 's/matrix_generator.calculate_body_region_averages(processed_df, min_days=min_days_between_tests)/matrix_generator.calculate_body_region_averages(processed_df)/g' app.py

# Remove min_days parameter from app.py call to calculate_improvement_thresholds
sed -i 's/matrix_generator.calculate_improvement_thresholds(processed_df, min_days=min_days_between_tests)/matrix_generator.calculate_improvement_thresholds(processed_df)/g' app.py

# Remove min_days parameter from app.py call to get_region_metrics
sed -i 's/matrix_generator.get_region_metrics(processed_df, region, min_days=min_days_between_tests)/matrix_generator.get_region_metrics(processed_df, region)/g' app.py

# Remove min_days parameter from app.py call to generate_user_matrices
sed -i 's/processed_df, selected_user, min_days=min_days_between_tests)/processed_df, selected_user)/g' app.py

# Remove min_days parameter UI element from app.py
sed -i '/min_days_between_tests = st.number_input(/,/)/d' app.py