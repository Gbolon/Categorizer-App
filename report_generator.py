"""Report generator module for exercise data visualization."""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import io
from weasyprint import HTML

class ReportGenerator:
    """Generates reports for exercise data analysis."""
    
    def __init__(self):
        """Initialize the report generator with default settings."""
        pass
    
    def generate_distribution_report(self, power_counts, accel_counts):
        """
        Generate a report with distribution tables and a bar chart visualization.
        
        Args:
            power_counts (DataFrame): Power development distribution counts
            accel_counts (DataFrame): Acceleration development distribution counts
            
        Returns:
            bytes: PDF report as bytes
        """
        # Create a report buffer
        report_buffer = io.BytesIO()
        
        # Create an HTML string for the report
        html_content = self._generate_html_report(power_counts, accel_counts)
        
        # Return the HTML content as bytes
        report_buffer.write(html_content.encode())
        report_buffer.seek(0)
        
        return report_buffer.getvalue()
    
    def create_distribution_chart(self, power_counts, accel_counts):
        """
        Create a bar chart visualization for distribution data.
        
        Args:
            power_counts (DataFrame): Power development distribution
            accel_counts (DataFrame): Acceleration development distribution
            
        Returns:
            plotly.graph_objects.Figure: Plotly figure object
        """
        # Extract categories and test values
        categories = power_counts.index.tolist()
        
        # Set up the data for plotting
        test_columns = [col for col in power_counts.columns if 'Test' in col]
        
        # Create a figure with a single subplot for both power and acceleration
        fig = make_subplots(rows=1, cols=1)
        
        # Add bars for power data
        for i, col in enumerate(test_columns):
            fig.add_trace(
                go.Bar(
                    x=categories,
                    y=power_counts[col],
                    name=f"Power {col}",
                    marker_color='blue',
                    opacity=0.7,
                    showlegend=True
                )
            )
        
        # Add bars for acceleration data
        for i, col in enumerate(test_columns):
            fig.add_trace(
                go.Bar(
                    x=categories,
                    y=accel_counts[col],
                    name=f"Acceleration {col}",
                    marker_color='green',
                    opacity=0.7,
                    showlegend=True
                )
            )
        
        # Update layout
        fig.update_layout(
            title="Distribution of Users by Development Category",
            xaxis_title="Development Category",
            yaxis_title="Number of Users",
            barmode='group',
            bargap=0.15,
            bargroupgap=0.1,
            height=500,
            width=800,
            legend=dict(
                x=0.01,
                y=0.99,
                bgcolor='rgba(255, 255, 255, 0.5)',
                bordercolor='rgba(0, 0, 0, 0.1)',
                borderwidth=1
            )
        )
        
        return fig
    
    def _generate_html_report(self, power_counts, accel_counts, power_transitions=None, accel_transitions=None):
        """
        Generate HTML report content.
        
        Args:
            power_counts (DataFrame): Power development distribution
            accel_counts (DataFrame): Acceleration development distribution
            power_transitions (dict): Dictionary of power transition matrices by period
            accel_transitions (dict): Dictionary of acceleration transition matrices by period
            
        Returns:
            str: HTML content
        """
        # No distribution chart visualization
        chart_html = ""  # Empty string since we're not using the chart
        
        # Convert dataframes to HTML tables
        power_table = power_counts.to_html(classes='table table-striped', index=True)
        accel_table = accel_counts.to_html(classes='table table-striped', index=True)
        
        # Generate transition tables HTML if provided
        transitions_html = ""
        if power_transitions is not None and accel_transitions is not None and len(power_transitions) > 0 and len(accel_transitions) > 0:
            transitions_html += """
            <h2>Transition Analysis</h2>
            <p>Reading guide: Rows show starting bracket, columns show ending bracket. Numbers show how many users made each transition.</p>
            """
            
            # Power transitions
            transitions_html += "<h3>Power Transitions</h3>"
            for period, matrix in power_transitions.items():
                transitions_html += f"<h4>Period: {period}</h4>"
                transitions_html += matrix.to_html(classes='table table-striped', index=True)
            
            # Acceleration transitions
            transitions_html += "<h3>Acceleration Transitions</h3>"
            for period, matrix in accel_transitions.items():
                transitions_html += f"<h4>Period: {period}</h4>"
                transitions_html += matrix.to_html(classes='table table-striped', index=True)
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Exercise Development Distribution Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    padding: 0;
                    color: #333;
                }}
                h1, h2, h3, h4 {{
                    color: #2c3e50;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .table {{
                    border-collapse: collapse;
                    margin: 25px 0;
                    font-size: 0.9em;
                    width: 100%;
                    box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
                }}
                .table thead tr {{
                    background-color: #2c3e50;
                    color: #ffffff;
                    text-align: left;
                }}
                .table th,
                .table td {{
                    padding: 12px 15px;
                }}
                .table tbody tr {{
                    border-bottom: 1px solid #dddddd;
                }}
                .table tbody tr:nth-of-type(even) {{
                    background-color: #f3f3f3;
                }}
                .table tbody tr:last-of-type {{
                    border-bottom: 2px solid #2c3e50;
                }}
                .chart-container {{
                    width: 100%;
                    margin: 25px 0;
                }}
                /* Transition table cell colors */
                .diagonal {{
                    background-color: #d4e6f1 !important; /* Pale Blue for no change */
                }}
                .above-diagonal {{
                    background-color: #f5b7b1 !important; /* Pale Red for regression */
                }}
                .below-diagonal {{
                    background-color: #abebc6 !important; /* Pale Green for improvement */
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Exercise Development Distribution Report</h1>
                
                <h2>Power Development Distribution</h2>
                {power_table}
                
                <h2>Acceleration Development Distribution</h2>
                {accel_table}
                
                {transitions_html}
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def generate_downloadable_html(self, power_counts, accel_counts, power_transitions=None, accel_transitions=None):
        """
        Generate downloadable HTML report.
        
        Args:
            power_counts (DataFrame): Power development distribution
            accel_counts (DataFrame): Acceleration development distribution
            power_transitions (dict): Dictionary of power transition matrices by period
            accel_transitions (dict): Dictionary of acceleration transition matrices by period
            
        Returns:
            bytes: HTML report as bytes
        """
        html_content = self._generate_html_report(power_counts, accel_counts, power_transitions, accel_transitions)
        return html_content.encode('utf-8')
        
    def generate_comprehensive_report(self, power_counts, accel_counts, power_transitions, accel_transitions,
                                    body_region_averages, improvement_thresholds, region_metrics, site_name="",
                                    min_days_between_tests=7, original_avg_days=0, constrained_avg_days=0, 
                                    resistance_filtering=True):
        """
        Generate a comprehensive HTML report with separate pages for each section.
        
        Args:
            power_counts (DataFrame): Power development distribution
            accel_counts (DataFrame): Acceleration development distribution
            power_transitions (dict): Dictionary of power transition matrices by period
            accel_transitions (dict): Dictionary of acceleration transition matrices by period
            body_region_averages (dict): Dictionary of body region averages
            improvement_thresholds (dict): Dictionary of improvement thresholds by region
            region_metrics (dict): Dictionary of region metrics including underperformers
            site_name (str, optional): Name of the site/location for the report header
            min_days_between_tests (int, optional): Minimum days required between test instances
            original_avg_days (float, optional): Original average days between tests
            constrained_avg_days (float, optional): Constrained average days between tests after applying min_days filter
            resistance_filtering (bool, optional): Whether resistance standardization was applied
            
        Returns:
            bytes: Comprehensive HTML report as bytes
        """
        # Start building the HTML report
        html_content = self._generate_comprehensive_html(
            power_counts, accel_counts, power_transitions, accel_transitions,
            body_region_averages, improvement_thresholds, region_metrics, site_name,
            min_days_between_tests, original_avg_days, constrained_avg_days,
            resistance_filtering
        )
        
        return html_content.encode('utf-8')
        
    def _generate_comprehensive_html(self, power_counts, accel_counts, power_transitions, accel_transitions,
                                   body_region_averages, improvement_thresholds, region_metrics, site_name="",
                                   min_days_between_tests=7, original_avg_days=0, constrained_avg_days=0,
                                   resistance_filtering=True):
        """
        Generate comprehensive HTML report content with separate pages.
        
        Args:
            power_counts (DataFrame): Power development distribution
            accel_counts (DataFrame): Acceleration development distribution
            power_transitions (dict): Dictionary of power transition matrices by period
            accel_transitions (dict): Dictionary of acceleration transition matrices by period
            body_region_averages (dict): Dictionary of body region averages
            improvement_thresholds (dict): Dictionary of improvement thresholds by region
            region_metrics (dict): Dictionary of region metrics including underperformers
            site_name (str, optional): Name of the site/location for the report header
            min_days_between_tests (int, optional): Minimum days required between test instances
            original_avg_days (float, optional): Original average days between tests
            constrained_avg_days (float, optional): Constrained average days between tests after applying min_days filter
            resistance_filtering (bool, optional): Whether resistance standardization was applied
            
        Returns:
            str: HTML content
        """
        # Set resistance filtering status based on the parameter
        resistance_status = "ENABLED" if resistance_filtering else "DISABLED"
        if resistance_filtering:
            resistance_message = "The data in this report has been filtered to only include exercises performed at the standard resistance values shown below."
        else:
            resistance_message = "The data in this report includes all exercise instances regardless of resistance settings. Exercise comparisons may be less accurate."
        # Create CSS styles
        css_styles = """
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                padding: 0;
                color: #333;
            }
            h1, h2, h3, h4 {
                color: #2c3e50;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .table {
                border-collapse: collapse;
                margin: 25px 0;
                font-size: 0.9em;
                width: 100%;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
            }
            .table thead tr {
                background-color: #2c3e50;
                color: #ffffff;
                text-align: left;
            }
            .table th,
            .table td {
                padding: 12px 15px;
                border: 1px solid #ddd;
            }
            .table tbody tr {
                border-bottom: 1px solid #dddddd;
            }
            .table tbody tr:nth-of-type(even) {
                background-color: #f3f3f3;
            }
            .table tbody tr:last-of-type {
                border-bottom: 2px solid #2c3e50;
            }
            .chart-container {
                width: 100%;
                margin: 25px 0;
            }
            /* Transition table cell colors */
            .diagonal {
                background-color: #d4e6f1 !important; /* Pale Blue for no change */
            }
            .above-diagonal {
                background-color: #f5b7b1 !important; /* Pale Red for regression */
            }
            .below-diagonal {
                background-color: #abebc6 !important; /* Pale Green for improvement */
            }
            /* Page break for printing */
            .page-break {
                page-break-before: always;
            }
            /* Navigation */
            .nav {
                background-color: #2c3e50;
                overflow: hidden;
                position: fixed;
                top: 0;
                width: 100%;
                z-index: 1000;
            }
            .nav a {
                float: left;
                display: block;
                color: #f2f2f2;
                text-align: center;
                padding: 14px 16px;
                text-decoration: none;
            }
            .nav a:hover {
                background-color: #ddd;
                color: black;
            }
            .content {
                margin-top: 60px;
            }
            /* Positive/negative values */
            .positive {
                color: green;
            }
            .negative {
                color: red;
            }
            /* Thresholds */
            .threshold-table {
                width: 80%;
                margin: 20px auto;
            }
            .underperformers-table {
                width: 90%;
                margin: 20px auto;
            }
            .site-name {
                margin: 20px 0;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 5px;
                border-left: 5px solid #2c3e50;
            }
            .site-name h2 {
                margin: 0;
                color: #2c3e50;
                font-size: 1.5em;
            }
        </style>
        """
        
        # No distribution chart visualization
        chart_html = ""  # Empty string since we're not using the chart
        
        # Create HTML content with navigation bar
        # Set document title with site name if provided
        title = f"Exercise Development Report - {site_name}" if site_name else "Comprehensive Exercise Development Report"
        
        html_header = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            {css_styles}
            <script>
                function goToPage(pageId) {{
                    // Hide all pages
                    document.querySelectorAll('.page').forEach(page => {{
                        page.style.display = 'none';
                    }});
                    
                    // Show the requested page
                    const pageElement = document.getElementById(pageId);
                    if (pageElement) {{
                        pageElement.style.display = 'block';
                        console.log('Showing page:', pageId);
                    }} else {{
                        console.error('Page not found:', pageId);
                        // Fallback to overview if requested page doesn't exist
                        const overviewPage = document.getElementById('overview');
                        if (overviewPage) {{
                            overviewPage.style.display = 'block';
                        }}
                    }}
                }}
            </script>
        </head>
        <body>
            <div class="nav">
                <a href="#" onclick="goToPage('info-page'); return false;">Information</a>
                <a href="#" onclick="goToPage('overview'); return false;">Overview</a>
                <a href="#" onclick="goToPage('power-transitions'); return false;">Power Transitions</a>
                <a href="#" onclick="goToPage('accel-transitions'); return false;">Acceleration Transitions</a>
        """
        
        # Add navigation links for each body region
        for region in body_region_averages.keys():
            region_id = region.lower().replace(' ', '-')
            html_header += f'<a href="#" onclick="goToPage(\'{region_id}-region\'); return false;">{region} Region</a>'
            
        html_header += """
            </div>
            <div class="content">
        """
        
        # OVERVIEW PAGE
        # Add site name to the overview if provided
        site_header = f"<div class='site-name'><h2>Site: {site_name}</h2></div>" if site_name else ""
        
        # Format the time constraint information
        time_constraint_info = ""
        if min_days_between_tests > 0:
            time_constraint_info = f"""
            <div class="site-name" style="margin-bottom: 30px;">
                <h3>Time Constraint Settings</h3>
                <table class="table" style="width: 80%; margin: 10px auto;">
                    <tr>
                        <td><strong>Minimum Days Between Tests:</strong></td>
                        <td>{min_days_between_tests} days</td>
                    </tr>
                    <tr>
                        <td><strong>Original Average Days Between Tests:</strong></td>
                        <td>{original_avg_days:.1f} days</td>
                    </tr>
                    <tr>
                        <td><strong>Constrained Average Days Between Tests:</strong></td>
                        <td>{constrained_avg_days:.1f} days</td>
                    </tr>
                </table>
            </div>
            """
            
        # Format the resistance standardization information
        if resistance_filtering is not None:
            check_symbol = '✓' if resistance_filtering else ''
            resistance_info = f"""
            <div class="site-name" style="margin-bottom: 30px;">
                <h3>Resistance Standardization</h3>
                <table class="table" style="width: 80%; margin: 10px auto;">
                    <tr>
                        <td style="width: 60%;"><strong>Status:</strong></td>
                        <td style="width: 40%;">
                            <span style="color: {'green' if resistance_filtering else 'orange'}; font-weight: bold; display: inline-block; margin-right: 10px;">{resistance_status}</span>
                            <span style="display: inline-block; width: 18px; height: 18px; border: 2px solid {'green' if resistance_filtering else 'gray'}; background-color: {'#abebc6' if resistance_filtering else 'white'}; border-radius: 3px; vertical-align: middle; text-align: center;">
                                {check_symbol}
                            </span>
                        </td>
                    </tr>
                    <tr>
                        <td colspan="2">{resistance_message}</td>
                    </tr>
                </table>
            </div>
            """
        else:
            resistance_info = ""
            
        overview_page = f"""
        <div id="overview" class="page container" style="display: none;">
            <h1>Exercise Development Overview</h1>
            {site_header}
            {time_constraint_info}
            {resistance_info}
            
            <h2>Power Development Distribution</h2>
        """
        
        # Add power distribution table
        overview_page += power_counts.to_html(classes='table table-striped', index=True)
        
        # Add acceleration distribution table
        overview_page += """
            <h2>Acceleration Development Distribution</h2>
        """
        overview_page += accel_counts.to_html(classes='table table-striped', index=True)
        
        # Body region averages section
        overview_page += """
            <h2>Body Region Averages Summary</h2>
        """
        
        # Add body region averages tables
        for region, averages in body_region_averages.items():
            overview_page += f"<h3>{region} Region</h3>"
            overview_page += averages.style.format("{:.2f}%").to_html(classes='table', index=True)
            
        overview_page += """
        </div>
        """
        
        # POWER TRANSITIONS PAGE
        power_transitions_page = """
        <div id="power-transitions" class="page container" style="display: none;">
            <h1>Power Transitions Analysis</h1>
            
            <p>Reading guide:</p>
            <ul>
                <li>Rows show starting bracket, columns show ending bracket.</li>
                <li>Numbers show how many users made each transition.</li>
                <li><span style="background-color: #d4e6f1; padding: 2px 5px;">Blue cells</span> show users who remained in the same bracket.</li>
                <li><span style="background-color: #f5b7b1; padding: 2px 5px;">Red cells</span> show regression to lower brackets.</li>
                <li><span style="background-color: #abebc6; padding: 2px 5px;">Green cells</span> show improvement to higher brackets.</li>
            </ul>
        """
        
        # Add all power transition tables on one page
        for period, matrix in power_transitions.items():
            power_transitions_page += f"<h2>Period: {period}</h2>"
            power_transitions_page += matrix.to_html(classes='table', index=True)
            
        power_transitions_page += """
        </div>
        """
        
        # ACCELERATION TRANSITIONS PAGE
        accel_transitions_page = """
        <div id="accel-transitions" class="page container" style="display: none;">
            <h1>Acceleration Transitions Analysis</h1>
            
            <p>Reading guide:</p>
            <ul>
                <li>Rows show starting bracket, columns show ending bracket.</li>
                <li>Numbers show how many users made each transition.</li>
                <li><span style="background-color: #d4e6f1; padding: 2px 5px;">Blue cells</span> show users who remained in the same bracket.</li>
                <li><span style="background-color: #f5b7b1; padding: 2px 5px;">Red cells</span> show regression to lower brackets.</li>
                <li><span style="background-color: #abebc6; padding: 2px 5px;">Green cells</span> show improvement to higher brackets.</li>
            </ul>
        """
        
        # Add all acceleration transition tables on one page
        for period, matrix in accel_transitions.items():
            accel_transitions_page += f"<h2>Period: {period}</h2>"
            accel_transitions_page += matrix.to_html(classes='table', index=True)
            
        accel_transitions_page += """
        </div>
        """
        
        # BODY REGION ANALYSIS PAGES (one page per region)
        region_pages = ""
        
        for region in body_region_averages.keys():
            region_id = region.lower().replace(' ', '-')
            region_page = f"""
            <div id="{region_id}-region" class="page container" style="display: none;">
                <h1>{region} Region Analysis</h1>
            """
            
            # Add improvement thresholds if available
            if region in improvement_thresholds:
                thresholds = improvement_thresholds[region]
                region_page += """
                <h2>Improvement Thresholds</h2>
                <p>These thresholds represent the average improvement across all users for this region. 
                Users below these thresholds may be underperforming relative to the group.</p>
                <table class="table threshold-table">
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>Test 1 → Test 2</th>
                            <th>Test 2 → Test 3</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Power</td>
                """
                
                # Add power thresholds with color coding
                power_1_to_2 = thresholds.get('power_1_to_2', None)
                power_2_to_3 = thresholds.get('power_2_to_3', None)
                
                if power_1_to_2 is not None and not pd.isna(power_1_to_2):
                    color_class = "positive" if power_1_to_2 >= 0 else "negative"
                    region_page += f'<td class="{color_class}">{power_1_to_2:.2f}%</td>'
                else:
                    region_page += '<td>Not enough data</td>'
                    
                if power_2_to_3 is not None and not pd.isna(power_2_to_3):
                    color_class = "positive" if power_2_to_3 >= 0 else "negative"
                    region_page += f'<td class="{color_class}">{power_2_to_3:.2f}%</td>'
                else:
                    region_page += '<td>Not enough data</td>'
                
                region_page += """
                        </tr>
                        <tr>
                            <td>Acceleration</td>
                """
                
                # Add acceleration thresholds with color coding
                accel_1_to_2 = thresholds.get('accel_1_to_2', None)
                accel_2_to_3 = thresholds.get('accel_2_to_3', None)
                
                if accel_1_to_2 is not None and not pd.isna(accel_1_to_2):
                    color_class = "positive" if accel_1_to_2 >= 0 else "negative"
                    region_page += f'<td class="{color_class}">{accel_1_to_2:.2f}%</td>'
                else:
                    region_page += '<td>Not enough data</td>'
                    
                if accel_2_to_3 is not None and not pd.isna(accel_2_to_3):
                    color_class = "positive" if accel_2_to_3 >= 0 else "negative"
                    region_page += f'<td class="{color_class}">{accel_2_to_3:.2f}%</td>'
                else:
                    region_page += '<td>Not enough data</td>'
                
                region_page += """
                        </tr>
                    </tbody>
                </table>
                """
            
            # Add region metrics from region_metrics if available
            if region in region_metrics and isinstance(region_metrics[region], tuple):
                metrics = region_metrics[region]
                
                # Check if we have the region metrics data
                if len(metrics) >= 4 and metrics[0] is not None and metrics[1] is not None:
                    power_df, accel_df = metrics[0], metrics[1]
                    
                    # Power development table
                    region_page += """
                    <h2>Power Development (%)</h2>
                    """
                    # Convert to HTML with formatting directly - using two decimal places
                    power_styled = power_df.style.format("{:.2f}%").to_html(classes='table')
                    region_page += power_styled
                    
                    # Acceleration development table
                    region_page += """
                    <h2>Acceleration Development (%)</h2>
                    """
                    # Convert to HTML with formatting directly - using two decimal places
                    accel_styled = accel_df.style.format("{:.2f}%").to_html(classes='table')
                    region_page += accel_styled
                    
                    # Display lowest change exercises if available
                    if len(metrics) >= 8:
                        lowest_power_exercise = metrics[4]
                        lowest_power_value = metrics[5]
                        lowest_accel_exercise = metrics[6]
                        lowest_accel_value = metrics[7]
                        
                        # Create tables for lowest change exercises
                        region_page += """
                        <h3>Exercises with Lowest Change</h3>
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Metric</th>
                                    <th>Exercise</th>
                                    <th>Change</th>
                                </tr>
                            </thead>
                            <tbody>
                        """
                            
                        if lowest_power_exercise and lowest_power_value is not None:
                            color_class = "positive" if lowest_power_value >= 0 else "negative"
                            region_page += f"""
                                <tr>
                                    <td>Power</td>
                                    <td>{lowest_power_exercise}</td>
                                    <td class="{color_class}">{lowest_power_value:.2f}%</td>
                                </tr>
                            """
                            
                        if lowest_accel_exercise and lowest_accel_value is not None:
                            color_class = "positive" if lowest_accel_value >= 0 else "negative"
                            region_page += f"""
                                <tr>
                                    <td>Acceleration</td>
                                    <td>{lowest_accel_exercise}</td>
                                    <td class="{color_class}">{lowest_accel_value:.2f}%</td>
                                </tr>
                            """
                            
                        region_page += """
                            </tbody>
                        </table>
                        """
                
                # Add underperformers if available
                power_changes = metrics[2] if len(metrics) > 2 else None
                accel_changes = metrics[3] if len(metrics) > 3 else None
                
                if power_changes and accel_changes:
                    # Test 1 to Test 2 underperformers
                    power_underperformers_1_to_2 = power_changes.get('underperformers_1_to_2', [])
                    accel_underperformers_1_to_2 = accel_changes.get('underperformers_1_to_2', [])
                    
                    if power_underperformers_1_to_2 or accel_underperformers_1_to_2:
                        region_page += """
                        <h2>Underperforming Users</h2>
                        <h3>Test 1 → Test 2</h3>
                        <table class="table underperformers-table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Power</th>
                                    <th>Acceleration</th>
                                </tr>
                            </thead>
                            <tbody>
                        """
                        
                        # Convert to dictionaries for easier lookup
                        power_dict = {name: value for name, value in power_underperformers_1_to_2} if power_underperformers_1_to_2 else {}
                        accel_dict = {name: value for name, value in accel_underperformers_1_to_2} if accel_underperformers_1_to_2 else {}
                        
                        # Get all unique users
                        all_users = set(power_dict.keys()).union(set(accel_dict.keys()))
                        
                        # Add rows for each user
                        for user in sorted(all_users):
                            power_value = power_dict.get(user, None)
                            accel_value = accel_dict.get(user, None)
                            
                            region_page += f"<tr><td>{user}</td>"
                            
                            if power_value is not None:
                                region_page += f'<td>✓ ({power_value:.2f}%)</td>'
                            else:
                                region_page += '<td></td>'
                                
                            if accel_value is not None:
                                region_page += f'<td>✓ ({accel_value:.2f}%)</td>'
                            else:
                                region_page += '<td></td>'
                                
                            region_page += "</tr>"
                            
                        region_page += """
                            </tbody>
                        </table>
                        """
                    
                    # Test 2 to Test 3 underperformers
                    power_underperformers_2_to_3 = power_changes.get('underperformers_2_to_3', [])
                    accel_underperformers_2_to_3 = accel_changes.get('underperformers_2_to_3', [])
                    
                    if power_underperformers_2_to_3 or accel_underperformers_2_to_3:
                        region_page += """
                        <h3>Test 2 → Test 3</h3>
                        <table class="table underperformers-table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Power</th>
                                    <th>Acceleration</th>
                                </tr>
                            </thead>
                            <tbody>
                        """
                        
                        # Convert to dictionaries for easier lookup
                        power_dict = {name: value for name, value in power_underperformers_2_to_3} if power_underperformers_2_to_3 else {}
                        accel_dict = {name: value for name, value in accel_underperformers_2_to_3} if accel_underperformers_2_to_3 else {}
                        
                        # Get all unique users
                        all_users = set(power_dict.keys()).union(set(accel_dict.keys()))
                        
                        # Add rows for each user
                        for user in sorted(all_users):
                            power_value = power_dict.get(user, None)
                            accel_value = accel_dict.get(user, None)
                            
                            region_page += f"<tr><td>{user}</td>"
                            
                            if power_value is not None:
                                region_page += f'<td>✓ ({power_value:.2f}%)</td>'
                            else:
                                region_page += '<td></td>'
                                
                            if accel_value is not None:
                                region_page += f'<td>✓ ({accel_value:.2f}%)</td>'
                            else:
                                region_page += '<td></td>'
                                
                            region_page += "</tr>"
                            
                        region_page += """
                            </tbody>
                        </table>
                        """
            
            region_page += """
            </div>
            """
            
            region_pages += region_page
        
        # Combine all pages
        # INFORMATION PAGE
        # Set resistance filtering status based on the parameter right before using it
        resistance_status = "ENABLED" if resistance_filtering else "DISABLED"
        check_symbol = '✓' if resistance_filtering else ''
        if resistance_filtering:
            resistance_message = "The data in this report has been filtered to only include exercises performed at the standard resistance values shown below."
        else:
            resistance_message = "The data in this report includes all exercise instances regardless of resistance settings. Exercise comparisons may be less accurate."
            
        info_page = f"""
        <div id="info-page" class="page container" style="display: none;">
            <h1>Exercise Movements and Assessment Information</h1>
            
            <h2>How Test Instances are Compiled</h2>
            <div class="site-name" style="margin-bottom: 20px;">
                <p>Test instances are chronological compilations of exercise data organized into groups (Test 1, Test 2, etc.) to track performance over time:</p>
                <ol style="margin-left: 20px;">
                    <li>Exercise data is sorted chronologically by Date/Time for each user.</li>
                    <li>The earliest record for each exercise is assigned to the earliest available test instance slot (Test 1).</li>
                    <li>Subsequent records of the same exercise are assigned to the next available test instance (Test 2, Test 3, etc.).</li>
                    <li>Different exercises may be tested on different dates within the same test instance.</li>
                    <li>If the minimum days between tests constraint is enabled, subsequent measurements of the same exercise that don't meet this requirement are skipped.</li>
                </ol>
                <p>This approach allows for proper tracking of individual progress across multiple exercises even when they aren't all measured on the same day.</p>
            </div>
            
            <p>This report analyzes performance data for the following exercise movements, organized by body region. Please review this information before examining the results.</p>
            
            <h2>Torso Region</h2>
            <ul>
                <li>Straight Arm Trunk Rotation (Dominant)</li>
                <li>Straight Arm Trunk Rotation (Non-Dominant)</li>
                <li>Shot Put (Countermovement)</li>
                <li>Shot Put (Countermovement) (Dominant)</li>
                <li>Shot Put (Countermovement) (Non-Dominant)</li>
            </ul>
            
            <h2>Arms Region</h2>
            <ul>
                <li>PNF D2 Flexion (Dominant)</li>
                <li>PNF D2 Flexion (Non-Dominant)</li>
                <li>PNF D2 Extension (Dominant)</li>
                <li>PNF D2 Extension (Non-Dominant)</li>
                <li>Biceps Curl (One Hand) (Dominant)</li>
                <li>Biceps Curl (One Hand) (Non-Dominant)</li>
                <li>Triceps Extension (One Hand) (Dominant)</li>
                <li>Triceps Extension (One Hand) (Non-Dominant)</li>
            </ul>
            
            <h2>Press/Pull Region</h2>
            <ul>
                <li>Horizontal Row (One Hand) (Dominant)</li>
                <li>Horizontal Row (One Hand) (Non-Dominant)</li>
                <li>Chest Press (One Hand) (Dominant)</li>
                <li>Chest Press (One Hand) (Non-Dominant)</li>
            </ul>
            
            <h2>Legs Region</h2>
            <ul>
                <li>Lateral Bound (Dominant)</li>
                <li>Lateral Bound (Non-Dominant)</li>
                <li>Vertical Jump (Countermovement)</li>
            </ul>
            
            <h2>Development Classification</h2>
            <p>Each user's performance is categorized into one of the following development brackets:</p>
            <table class="table">
                <thead>
                    <tr>
                        <th>Classification</th>
                        <th>Development Score Range (%)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Goal Hit</td>
                        <td>≥ 100%</td>
                    </tr>
                    <tr>
                        <td>Elite</td>
                        <td>90% - 99.99%</td>
                    </tr>
                    <tr>
                        <td>Above Average</td>
                        <td>76% - 90%</td>
                    </tr>
                    <tr>
                        <td>Average</td>
                        <td>51% - 75%</td>
                    </tr>
                    <tr>
                        <td>Under Developed</td>
                        <td>26% - 50%</td>
                    </tr>
                    <tr>
                        <td>Severely Under Developed</td>
                        <td>0% - 25%</td>
                    </tr>
                </tbody>
            </table>
            
            <h2>Calculation Method</h2>
            <p>For each exercise movement, we compute a Development Score as follows:</p>
            <div style="text-align: center; margin: 20px 0;">
                <p style="font-size: 1.2em;">Development Score = (User's Recorded Value / Goal Standard) × 100</p>
            </div>
            <p>This calculation is performed separately for both Power and Acceleration metrics.</p>
            
            <h2>Overall Development Score</h2>
            <p>Each test instance has one overall Power Development Score and one overall Acceleration Development Score per user, calculated as the average of all available exercise development scores for that test instance.</p>
            
            <h2>Time Constraint</h2>
            <p>In order to ensure valid analysis of performance changes over time, a minimum time constraint is applied between measurements of the same exercise. This helps ensure that changes in performance reflect true development rather than day-to-day variability.</p>
            <p>Test instances for the same exercise that don't meet the minimum days requirement are skipped in the analysis. This means that if a user has multiple tests for the same exercise within the minimum time window, only the earliest test is included in the analysis.</p>
            <p>The minimum days between tests setting is reflected in the Overview page, along with both the original average days between tests (before filtering) and the constrained average days (after applying the minimum days filter).</p>
            
            <h2>Resistance Standardization</h2>
            <p>To ensure accurate and comparable measurements across users, each exercise should be performed with a standardized resistance value (in pounds).</p>
            
            <table class="table" style="width: 80%; margin: 10px auto;">
                <tr>
                    <td style="width: 60%;"><strong>Status:</strong></td>
                    <td style="width: 40%;">
                        <span style="color: {'green' if resistance_filtering else 'orange'}; font-weight: bold; display: inline-block; margin-right: 10px;">{resistance_status}</span>
                        <span style="display: inline-block; width: 18px; height: 18px; border: 2px solid {'green' if resistance_filtering else 'gray'}; background-color: {'#abebc6' if resistance_filtering else 'white'}; border-radius: 3px; vertical-align: middle; text-align: center;">
                            {check_symbol}
                        </span>
                    </td>
                </tr>
                <tr>
                    <td colspan="2">{resistance_message}</td>
                </tr>
            </table>
            
            <table class="table">
                <thead>
                    <tr>
                        <th>Exercise</th>
                        <th>Required Resistance (lbs)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>Chest Press (One Hand)</td><td>12</td></tr>
                    <tr><td>Horizontal Row (One Hand)</td><td>12</td></tr>
                    <tr><td>Biceps Curl (One Hand)</td><td>6</td></tr>
                    <tr><td>Triceps Extension (One Hand)</td><td>6</td></tr>
                    <tr><td>PNF D2 Flexion</td><td>6</td></tr>
                    <tr><td>PNF D2 Extension</td><td>6</td></tr>
                    <tr><td>Straight Arm Trunk Rotation</td><td>12</td></tr>
                    <tr><td>Lateral Bound</td><td>6</td></tr>
                    <tr><td>Shot Put (Countermovement)</td><td>18</td></tr>
                    <tr><td>Vertical Jump (Countermovement)</td><td>6</td></tr>
                </tbody>
            </table>
            <p>The analysis only includes exercise data performed at these exact resistance values. This standardization ensures that performance comparisons between users and across time are valid and meaningful.</p>
            
            <p style="margin-top: 30px;">Please proceed to the Overview page to view the report results.</p>
        </div>
        """
        
        html_content = html_header + info_page + overview_page + power_transitions_page + accel_transitions_page + region_pages
        
        # Add closing tags
        html_content += """
            </div>
            <script>
                // Set information page as the default page
                document.addEventListener('DOMContentLoaded', function() {
                    // Initially hide all pages
                    document.querySelectorAll('.page').forEach(function(page) {
                        page.style.display = 'none';
                    });
                    
                    // Show the info page
                    var infoPage = document.getElementById('info-page');
                    if (infoPage) {
                        infoPage.style.display = 'block';
                        console.log('Showing info page on load');
                    } else {
                        console.error('Info page not found, showing overview instead');
                        var overviewPage = document.getElementById('overview');
                        if (overviewPage) {
                            overviewPage.style.display = 'block';
                        }
                    }
                });
            </script>
        </body>
        </html>
        """
        
        return html_content
        
    def _apply_transition_styling(self, html_table, df):
        """
        Apply transition styling to an HTML table based on the dataframe values.
        
        Args:
            html_table (str): The HTML table string
            df (DataFrame): The transition matrix dataframe
            
        Returns:
            str: The styled HTML table with appropriate cell classes
        """
        try:
            import re
            from bs4 import BeautifulSoup
            
            # Create a BeautifulSoup object
            soup = BeautifulSoup(html_table, 'html.parser')
            
            # Get all data rows (skip header row)
            rows = soup.find_all('tr')[1:]
            
            # Process each row
            for i, row in enumerate(rows):
                cells = row.find_all('td')[1:]  # Skip the index column
                
                for j, cell in enumerate(cells):
                    if i == j:  # Diagonal - no change
                        cell['style'] = 'background-color: #d4e6f1 !important;'  # Pale Blue
                    elif i < j:  # Above diagonal - regression
                        cell['style'] = 'background-color: #f5b7b1 !important;'  # Pale Red
                    else:  # Below diagonal - improvement
                        cell['style'] = 'background-color: #abebc6 !important;'  # Pale Green
            
            # Return the modified HTML
            return str(soup)
        except Exception as e:
            print(f"Error in _apply_transition_styling: {e}")
            # Fall back to original table if styling fails
            return html_table
    
    def generate_pdf_from_html(self, html_content):
        """
        Convert HTML content to PDF format using WeasyPrint.
        
        Args:
            html_content (str): The HTML content to convert
            
        Returns:
            bytes: PDF document as bytes
        """
        # Create a BytesIO buffer to store the PDF
        pdf_buffer = io.BytesIO()
        
        # Convert HTML to PDF
        HTML(string=html_content).write_pdf(pdf_buffer)
        
        # Reset buffer position to start
        pdf_buffer.seek(0)
        
        # Return PDF as bytes
        return pdf_buffer.getvalue()
        
    def generate_comprehensive_pdf_report(self, power_counts, accel_counts, power_transitions, accel_transitions,
                                        body_region_averages, improvement_thresholds, region_metrics, site_name="",
                                        min_days_between_tests=7, original_avg_days=0, constrained_avg_days=0, 
                                        resistance_filtering=True):
        """
        Generate a comprehensive PDF report with a structured layout and controlled page breaks.
        
        Args:
            power_counts (DataFrame): Power development distribution
            accel_counts (DataFrame): Acceleration development distribution
            power_transitions (dict): Dictionary of power transition matrices by period
            accel_transitions (dict): Dictionary of acceleration transition matrices by period
            body_region_averages (dict): Dictionary of body region averages
            improvement_thresholds (dict): Dictionary of improvement thresholds by region
            region_metrics (dict): Dictionary of region metrics including underperformers
            site_name (str, optional): Name of the site/location for the report header
            min_days_between_tests (int, optional): Minimum days required between test instances
            original_avg_days (float, optional): Original average days between tests
            constrained_avg_days (float, optional): Constrained average days between tests after applying min_days filter
            resistance_filtering (bool, optional): Whether resistance standardization was applied
            
        Returns:
            bytes: PDF report as bytes
        """
        # Set resistance filtering status based on the parameter
        resistance_status = "ENABLED" if resistance_filtering else "DISABLED"
        if resistance_filtering:
            resistance_message = "The data in this report has been filtered to only include exercises performed at the standard resistance values shown below."
        else:
            resistance_message = "The data in this report includes all exercise instances regardless of resistance settings. Exercise comparisons may be less accurate."
            
        # Create CSS styles optimized for PDF output
        css_styles = """
        <style>
            @page {
                size: letter;
                margin: 2cm;
                @top-center {
                    content: "Exercise Performance Analysis";
                    font-size: 10pt;
                }
                @bottom-center {
                    content: "Page " counter(page) " of " counter(pages);
                    font-size: 10pt;
                }
            }
            body {
                font-family: Arial, sans-serif;
                font-size: 12pt;
                color: #333;
                line-height: 1.5;
            }
            h1 {
                font-size: 20pt;
                color: #2c3e50;
                margin-top: 0;
                border-bottom: 1px solid #2c3e50;
                padding-bottom: 10px;
            }
            h2 {
                font-size: 16pt;
                color: #2c3e50;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            h3 {
                font-size: 14pt;
                color: #2c3e50;
                margin-top: 15px;
                margin-bottom: 10px;
            }
            .page-break {
                page-break-before: always;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
                font-size: 10pt;
            }
            th, td {
                padding: 8px;
                border: 1px solid #ddd;
                text-align: left;
            }
            th {
                background-color: #2c3e50;
                color: white;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            .section {
                margin-bottom: 20px;
            }
            /* Transition table cell colors */
            .diagonal {
                background-color: #d4e6f1 !important; /* Pale Blue for no change */
            }
            .above-diagonal {
                background-color: #f5b7b1 !important; /* Pale Red for regression */
            }
            .below-diagonal {
                background-color: #abebc6 !important; /* Pale Green for improvement */
            }
            /* Positive/negative values */
            .positive {
                color: green;
            }
            .negative {
                color: red;
            }
            .info-box {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                padding: 10px;
                margin: 15px 0;
                border-radius: 5px;
                font-size: 10pt;
            }
            .footer {
                text-align: center;
                font-size: 10pt;
                color: #777;
                margin-top: 30px;
            }
        </style>
        """

        # Generate each section of the report with appropriate page breaks
        
        # 1. Title Page and Overview
        title_page = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Exercise Performance Analysis Report</title>
            {css_styles}
        </head>
        <body>
            <div class="section">
                <h1>Exercise Performance Analysis Report</h1>
                <h2>{site_name}</h2>
                <p>Report Date: {pd.Timestamp.now().strftime("%B %d, %Y")}</p>
                
                <div class="info-box">
                    <h3>Analysis Configuration</h3>
                    <p><strong>Resistance Standardization:</strong> {resistance_status}</p>
                    <p>{resistance_message}</p>
                    <p><strong>Time Constraint:</strong> Minimum {min_days_between_tests} days between measurements of the same exercise</p>
                    <p><strong>Original Average Days Between Tests:</strong> {original_avg_days:.2f} days</p>
                    <p><strong>After Time Constraint Average:</strong> {constrained_avg_days:.2f} days</p>
                </div>
                
                <h3>How Test Instances are Compiled</h3>
                <p>Test instances are chronologically ordered collections of exercise data. Each exercise is assigned to the earliest available test instance where:</p>
                <ol>
                    <li>The exercise hasn't been measured in a previous test instance, or</li>
                    <li>Sufficient time ({min_days_between_tests} days) has passed since the last measurement of the same exercise</li>
                </ol>
                <p>This approach ensures that development tracking is based on meaningful changes over time rather than day-to-day fluctuations.</p>
            </div>
            
            <div class="page-break"></div>
        """
        
        # 2. Distribution Overview
        distribution_section = f"""
            <div class="section">
                <h2>Development Distribution Overview</h2>
                
                <h3>Power Development Distribution</h3>
                {power_counts.to_html(classes='table', index=True)}
                
                <h3>Acceleration Development Distribution</h3>
                {accel_counts.to_html(classes='table', index=True)}
            </div>
            
            <div class="page-break"></div>
        """
        
        # 3. Transition Analysis
        transitions_section = """
            <div class="section">
                <h2>Transition Analysis</h2>
                <p>Reading guide: Rows show starting bracket, columns show ending bracket. Numbers show how many users made each transition.</p>
                <p><strong>Color coding:</strong> Blue cells show users who remained in the same bracket, Red cells show regression, Green cells show improvement.</p>
        """
        
        # Check if power_transitions is a valid dictionary with entries
        if isinstance(power_transitions, dict) and len(power_transitions) > 0:
            # Power transitions
            transitions_section += "<h3>Power Transitions</h3>"
            
            for period, matrix in power_transitions.items():
                transitions_section += f"<h4>Period: {period}</h4>"
                
                # Get the actual DataFrame - handle both DataFrame and Styler objects
                df = None
                if isinstance(matrix, pd.DataFrame) and not matrix.empty:
                    df = matrix
                elif hasattr(matrix, 'data') and not matrix.data.empty:
                    # This is a Styler object, get the underlying DataFrame
                    df = matrix.data
                    
                if df is not None:
                    # Create manual table with inline styling
                    transitions_section += "<table class='table transition-table' border='1' cellpadding='5' cellspacing='0'>"
                    
                    # Add header row with column names
                    transitions_section += "<tr><th></th>"
                    for col in df.columns:
                        # Handle MultiIndex columns if present
                        if isinstance(col, tuple):
                            col_name = col[1] if len(col) > 1 else col[0]
                        else:
                            col_name = col
                        transitions_section += f"<th>{col_name}</th>"
                    transitions_section += "</tr>"
                    
                    # Add data rows with styling
                    for i, row_idx in enumerate(df.index):
                        transitions_section += f"<tr><th>{row_idx}</th>"
                        
                        for j in range(len(df.columns)):
                            # Get the value directly using iloc
                            value = df.iloc[i, j]
                            
                            # Determine cell color
                            if i == j:  # Diagonal - no change
                                bg_color = "#d4e6f1"  # Pale Blue
                            elif i < j:  # Above diagonal - regression
                                bg_color = "#f5b7b1"  # Pale Red
                            else:  # Below diagonal - improvement
                                bg_color = "#abebc6"  # Pale Green
                                
                            transitions_section += f"<td style='background-color: {bg_color};'>{value}</td>"
                            
                        transitions_section += "</tr>"
                    
                    transitions_section += "</table>"
                else:
                    # Create a message for no transition data
                    transitions_section += """
                    <div class="info-box">
                        <p>No transition data available for this period. This can occur when:</p>
                        <ul>
                            <li>There are not enough test instances to create transition matrices</li>
                            <li>Users have not progressed between different development brackets</li>
                            <li>Data does not meet the time constraint requirements</li>
                        </ul>
                    </div>
                    """
        
        # Check if accel_transitions is a valid dictionary with entries
        if isinstance(accel_transitions, dict) and len(accel_transitions) > 0:
            # Acceleration transitions
            transitions_section += "<h3>Acceleration Transitions</h3>"
            
            for period, matrix in accel_transitions.items():
                transitions_section += f"<h4>Period: {period}</h4>"
                
                # Get the actual DataFrame - handle both DataFrame and Styler objects
                df = None
                if isinstance(matrix, pd.DataFrame) and not matrix.empty:
                    df = matrix
                elif hasattr(matrix, 'data') and not matrix.data.empty:
                    # This is a Styler object, get the underlying DataFrame
                    df = matrix.data
                    
                if df is not None:
                    # Create manual table with inline styling
                    transitions_section += "<table class='table transition-table' border='1' cellpadding='5' cellspacing='0'>"
                    
                    # Add header row with column names
                    transitions_section += "<tr><th></th>"
                    for col in df.columns:
                        # Handle MultiIndex columns if present
                        if isinstance(col, tuple):
                            col_name = col[1] if len(col) > 1 else col[0]
                        else:
                            col_name = col
                        transitions_section += f"<th>{col_name}</th>"
                    transitions_section += "</tr>"
                    
                    # Add data rows with styling
                    for i, row_idx in enumerate(df.index):
                        transitions_section += f"<tr><th>{row_idx}</th>"
                        
                        for j in range(len(df.columns)):
                            # Get the value directly using iloc
                            value = df.iloc[i, j]
                            
                            # Determine cell color
                            if i == j:  # Diagonal - no change
                                bg_color = "#d4e6f1"  # Pale Blue
                            elif i < j:  # Above diagonal - regression
                                bg_color = "#f5b7b1"  # Pale Red
                            else:  # Below diagonal - improvement
                                bg_color = "#abebc6"  # Pale Green
                                
                            transitions_section += f"<td style='background-color: {bg_color};'>{value}</td>"
                            
                        transitions_section += "</tr>"
                    
                    transitions_section += "</table>"
                else:
                    # Create a message for no transition data
                    transitions_section += """
                    <div class="info-box">
                        <p>No transition data available for this period. This can occur when:</p>
                        <ul>
                            <li>There are not enough test instances to create transition matrices</li>
                            <li>Users have not progressed between different development brackets</li>
                            <li>Data does not meet the time constraint requirements</li>
                        </ul>
                    </div>
                    """
            
        transitions_section += """
            </div>
            
            <div class="page-break"></div>
        """
        
        # 4. Body Region Analysis
        body_region_section = """
            <div class="section">
                <h2>Body Region Analysis</h2>
        """
        
        for region, data in body_region_averages.items():
            body_region_section += f"<h3>{region} Region</h3>"
            
            # Check if power_averages exists and is not empty
            if 'power_averages' in data and isinstance(data['power_averages'], pd.Series) and not data['power_averages'].empty:
                # Format values to 2 decimal places
                formatted_power = data['power_averages'].map(lambda x: f"{x:.2f}%" if not pd.isna(x) else "N/A")
                body_region_section += "<h4>Power Development (% of Goal)</h4>"
                body_region_section += formatted_power.to_frame().to_html(classes='table', index=True)
            
            # Check if accel_averages exists and is not empty
            if 'accel_averages' in data and isinstance(data['accel_averages'], pd.Series) and not data['accel_averages'].empty:
                # Format values to 2 decimal places
                formatted_accel = data['accel_averages'].map(lambda x: f"{x:.2f}%" if not pd.isna(x) else "N/A")
                body_region_section += "<h4>Acceleration Development (% of Goal)</h4>"
                body_region_section += formatted_accel.to_frame().to_html(classes='table', index=True)
                
        body_region_section += """
            </div>
            
            <div class="page-break"></div>
        """
        
        # 5. Improvement Thresholds
        thresholds_section = """
            <div class="section">
                <h2>Improvement Thresholds</h2>
                <p>These threshold values represent the average percentage change between tests for all users. They are used to identify underperforming users relative to the group average.</p>
        """
        
        # Safe iteration through improvement thresholds if it exists and is a dictionary
        if isinstance(improvement_thresholds, dict) and len(improvement_thresholds) > 0:
            for region, thresholds in improvement_thresholds.items():
                thresholds_section += f"<h3>{region} Region</h3>"
                
                # Create a DataFrame for thresholds with safe access
                threshold_values = [
                    f"{thresholds.get('power_1_to_2', 0):.2f}%" if 'power_1_to_2' in thresholds else "0.00%",
                    f"{thresholds.get('power_2_to_3', 0):.2f}%" if 'power_2_to_3' in thresholds else "0.00%",
                    f"{thresholds.get('accel_1_to_2', 0):.2f}%" if 'accel_1_to_2' in thresholds else "0.00%",
                    f"{thresholds.get('accel_2_to_3', 0):.2f}%" if 'accel_2_to_3' in thresholds else "0.00%"
                ]
                
                thresholds_data = pd.DataFrame({
                    'Metric': ['Power (Test 1 to 2)', 'Power (Test 2 to 3)', 'Acceleration (Test 1 to 2)', 'Acceleration (Test 2 to 3)'],
                    'Threshold': threshold_values
                })
                thresholds_section += thresholds_data.to_html(classes='table', index=False)
            
        thresholds_section += """
            </div>
            
            <div class="page-break"></div>
        """
        
        # 6. Underperforming Users
        underperformers_section = """
            <div class="section">
                <h2>Underperforming Users</h2>
                <p>The following users showed below-average improvement compared to the group thresholds.</p>
        """
        
        # Safe iteration through region metrics if it exists and is a dictionary
        if isinstance(region_metrics, dict) and len(region_metrics) > 0:
            for region, metrics in region_metrics.items():
                # Check if we have any underperformers
                has_underperformers = False
                if isinstance(metrics, dict):
                    has_underperformers = (
                        ('power_underperformers_1_to_2' in metrics and len(metrics.get('power_underperformers_1_to_2', [])) > 0) or 
                        ('accel_underperformers_1_to_2' in metrics and len(metrics.get('accel_underperformers_1_to_2', [])) > 0) or
                        ('power_underperformers_2_to_3' in metrics and len(metrics.get('power_underperformers_2_to_3', [])) > 0) or
                        ('accel_underperformers_2_to_3' in metrics and len(metrics.get('accel_underperformers_2_to_3', [])) > 0)
                    )
                
                if has_underperformers:
                    underperformers_section += f"<h3>{region} Region</h3>"
                    
                    # Test 1 to 2 Underperformers
                    if ('power_underperformers_1_to_2' in metrics and len(metrics.get('power_underperformers_1_to_2', [])) > 0) or \
                       ('accel_underperformers_1_to_2' in metrics and len(metrics.get('accel_underperformers_1_to_2', [])) > 0):
                        underperformers_section += "<h4>Test 1 to Test 2</h4>"
                        
                        power_users = metrics.get('power_underperformers_1_to_2', [])
                        accel_users = metrics.get('accel_underperformers_1_to_2', [])
                        
                        # Create a combined list of underperformers
                        all_users = set()
                        for user_tuple in power_users:
                            if isinstance(user_tuple, tuple) and len(user_tuple) >= 1:
                                all_users.add(user_tuple[0])
                        for user_tuple in accel_users:
                            if isinstance(user_tuple, tuple) and len(user_tuple) >= 1:
                                all_users.add(user_tuple[0])
                        
                        # Create a DataFrame for display
                        user_data = []
                        for user in all_users:
                            power_pct = next((f"{pct:.2f}%" for u, pct in power_users if u == user), "")
                            accel_pct = next((f"{pct:.2f}%" for u, pct in accel_users if u == user), "")
                            
                            user_data.append({
                                'Name': user,
                                'Power': power_pct,
                                'Acceleration': accel_pct
                            })
                        
                        if user_data:
                            df_users = pd.DataFrame(user_data)
                            underperformers_section += df_users.to_html(classes='table', index=False)
                        else:
                            underperformers_section += "<p>No underperforming users identified for this period.</p>"
                    
                    # Test 2 to 3 Underperformers
                    if ('power_underperformers_2_to_3' in metrics and len(metrics.get('power_underperformers_2_to_3', [])) > 0) or \
                       ('accel_underperformers_2_to_3' in metrics and len(metrics.get('accel_underperformers_2_to_3', [])) > 0):
                        underperformers_section += "<h4>Test 2 to Test 3</h4>"
                        
                        power_users = metrics.get('power_underperformers_2_to_3', [])
                        accel_users = metrics.get('accel_underperformers_2_to_3', [])
                        
                        # Create a combined list of underperformers
                        all_users = set()
                        for user_tuple in power_users:
                            if isinstance(user_tuple, tuple) and len(user_tuple) >= 1:
                                all_users.add(user_tuple[0])
                        for user_tuple in accel_users:
                            if isinstance(user_tuple, tuple) and len(user_tuple) >= 1:
                                all_users.add(user_tuple[0])
                        
                        # Create a DataFrame for display
                        user_data = []
                        for user in all_users:
                            power_pct = next((f"{pct:.2f}%" for u, pct in power_users if u == user), "")
                            accel_pct = next((f"{pct:.2f}%" for u, pct in accel_users if u == user), "")
                            
                            user_data.append({
                                'Name': user,
                                'Power': power_pct,
                                'Acceleration': accel_pct
                            })
                        
                        if user_data:
                            df_users = pd.DataFrame(user_data)
                            underperformers_section += df_users.to_html(classes='table', index=False)
                        else:
                            underperformers_section += "<p>No underperforming users identified for this period.</p>"
        
        underperformers_section += """
            </div>
            
            <div class="footer">
                <p>Generated on {timestamp} • Exercise Performance Analysis Tool</p>
            </div>
        </body>
        </html>
        """.format(timestamp=pd.Timestamp.now().strftime("%B %d, %Y at %I:%M %p"))
        
        # Debug print statements for sections
        print("\n\nDEBUG PDF GENERATION:")
        print(f"Power transitions type: {type(power_transitions)}")
        if isinstance(power_transitions, dict):
            print(f"Power transitions keys: {power_transitions.keys()}")
            
            # Debug the transition matrices content
            for period, matrix in power_transitions.items():
                if isinstance(matrix, pd.DataFrame):
                    print(f"Matrix for {period} - Shape: {matrix.shape}, Empty: {matrix.empty}")
                    if not matrix.empty:
                        print(f"Sample values: {matrix.iloc[0, 0] if matrix.shape[0] > 0 and matrix.shape[1] > 0 else 'No data'}")
                elif hasattr(matrix, 'data'):  # This is likely a Styler object
                    print(f"Matrix for {period} is a Styler object - Converting to DataFrame")
                    print(f"Styler data shape: {matrix.data.shape}, Empty: {matrix.data.empty if hasattr(matrix.data, 'empty') else 'unknown'}")
                    if hasattr(matrix.data, 'iloc') and matrix.data.shape[0] > 0 and matrix.data.shape[1] > 0:
                        print(f"Sample values: {matrix.data.iloc[0, 0]}")
                else:
                    print(f"Matrix for {period} is not a DataFrame or Styler, type: {type(matrix)}")
        else:
            print("Power transitions is not a dict")
        
        print(f"Transition section length: {len(transitions_section)}")
        
        # Combine all sections
        complete_html = title_page + distribution_section + transitions_section + body_region_section + thresholds_section + underperformers_section
        
        # Debug print for complete HTML
        print(f"Complete HTML length: {len(complete_html)}")
        
        # Convert the HTML to PDF
        pdf_content = self.generate_pdf_from_html(complete_html)
        
        return pdf_content