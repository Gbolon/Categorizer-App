"""Report generator module for exercise data visualization."""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import io

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
        # Create a chart and convert to HTML
        fig = self.create_distribution_chart(power_counts, accel_counts)
        chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
        
        # Convert dataframes to HTML tables
        power_table = power_counts.to_html(classes='table table-striped', index=True)
        accel_table = accel_counts.to_html(classes='table table-striped', index=True)
        
        # Generate transition tables HTML if provided
        transitions_html = ""
        if power_transitions and accel_transitions:
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
                
                <h2>Distribution Visualization</h2>
                <div class="chart-container">
                    {chart_html}
                </div>
                
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
                                    body_region_averages, improvement_thresholds, region_metrics, site_name=""):
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
            
        Returns:
            bytes: Comprehensive HTML report as bytes
        """
        # Start building the HTML report
        html_content = self._generate_comprehensive_html(
            power_counts, accel_counts, power_transitions, accel_transitions,
            body_region_averages, improvement_thresholds, region_metrics, site_name
        )
        
        return html_content.encode('utf-8')
        
    def _generate_comprehensive_html(self, power_counts, accel_counts, power_transitions, accel_transitions,
                                   body_region_averages, improvement_thresholds, region_metrics, site_name=""):
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
            
        Returns:
            str: HTML content
        """
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
        
        # Create a chart for distribution visualization
        fig = self.create_distribution_chart(power_counts, accel_counts)
        chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
        
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
                    document.querySelectorAll('.page').forEach(page => {{
                        page.style.display = 'none';
                    }});
                    document.getElementById(pageId).style.display = 'block';
                }}
            </script>
        </head>
        <body>
            <div class="nav">
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
        
        overview_page = f"""
        <div id="overview" class="page container">
            <h1>Exercise Development Overview</h1>
            {site_header}
            
            <h2>Power Development Distribution</h2>
        """
        
        # Add power distribution table
        overview_page += power_counts.to_html(classes='table table-striped', index=True)
        
        # Add acceleration distribution table
        overview_page += """
            <h2>Acceleration Development Distribution</h2>
        """
        overview_page += accel_counts.to_html(classes='table table-striped', index=True)
        
        # Add distribution chart
        overview_page += """
            <h2>Distribution Visualization</h2>
            <div class="chart-container">
        """
        overview_page += chart_html
        overview_page += """
            </div>
            
            <h2>Body Region Averages Summary</h2>
        """
        
        # Add body region averages tables
        for region, averages in body_region_averages.items():
            overview_page += f"<h3>{region} Region</h3>"
            overview_page += averages.to_html(classes='table', index=True)
            
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
                    region_page += f'<td class="{color_class}">{power_1_to_2:.1f}%</td>'
                else:
                    region_page += '<td>Not enough data</td>'
                    
                if power_2_to_3 is not None and not pd.isna(power_2_to_3):
                    color_class = "positive" if power_2_to_3 >= 0 else "negative"
                    region_page += f'<td class="{color_class}">{power_2_to_3:.1f}%</td>'
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
                    region_page += f'<td class="{color_class}">{accel_1_to_2:.1f}%</td>'
                else:
                    region_page += '<td>Not enough data</td>'
                    
                if accel_2_to_3 is not None and not pd.isna(accel_2_to_3):
                    color_class = "positive" if accel_2_to_3 >= 0 else "negative"
                    region_page += f'<td class="{color_class}">{accel_2_to_3:.1f}%</td>'
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
                    # Convert to HTML with formatting directly
                    power_styled = power_df.style.format("{:.1f}%").to_html()
                    region_page += power_styled
                    
                    # Acceleration development table
                    region_page += """
                    <h2>Acceleration Development (%)</h2>
                    """
                    # Convert to HTML with formatting directly
                    accel_styled = accel_df.style.format("{:.1f}%").to_html()
                    region_page += accel_styled
                    
                    # Display lowest change exercises if available
                    if len(metrics) >= 8:
                        lowest_power_exercise = metrics[4]
                        lowest_power_value = metrics[5]
                        lowest_accel_exercise = metrics[6]
                        lowest_accel_value = metrics[7]
                        
                        if lowest_power_exercise and lowest_power_value is not None:
                            color_class = "positive" if lowest_power_value >= 0 else "negative"
                            region_page += f"""
                            <h3>Exercise with Lowest Power Change</h3>
                            <p><strong>{lowest_power_exercise}</strong>: <span class="{color_class}">{lowest_power_value:.1f}%</span></p>
                            """
                            
                        if lowest_accel_exercise and lowest_accel_value is not None:
                            color_class = "positive" if lowest_accel_value >= 0 else "negative"
                            region_page += f"""
                            <h3>Exercise with Lowest Acceleration Change</h3>
                            <p><strong>{lowest_accel_exercise}</strong>: <span class="{color_class}">{lowest_accel_value:.1f}%</span></p>
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
                                region_page += f'<td>✓ ({power_value:.1f}%)</td>'
                            else:
                                region_page += '<td></td>'
                                
                            if accel_value is not None:
                                region_page += f'<td>✓ ({accel_value:.1f}%)</td>'
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
                                region_page += f'<td>✓ ({power_value:.1f}%)</td>'
                            else:
                                region_page += '<td></td>'
                                
                            if accel_value is not None:
                                region_page += f'<td>✓ ({accel_value:.1f}%)</td>'
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
        html_content = html_header + overview_page + power_transitions_page + accel_transitions_page + region_pages
        
        # Add closing tags
        html_content += """
            </div>
            <script>
                // Set overview as the default page
                document.addEventListener('DOMContentLoaded', function() {
                    goToPage('overview');
                });
            </script>
        </body>
        </html>
        """
        
        return html_content