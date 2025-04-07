"""
PDF Report generator for the Site Development Bracketer application.
Generates comprehensive PDF reports with data visualizations and tables.
"""

import io
import base64
from fpdf import FPDF
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go


class PDFReport(FPDF):
    """
    PDF Report generator class that extends FPDF.
    
    Provides methods for adding headers, footers, tables, and visualizations
    to create comprehensive performance reports.
    """
    
    def __init__(self, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)
        self.set_auto_page_break(auto=True, margin=15)
        # Set up basic document properties
        self.set_title("Site Development Bracketer - Performance Report")
        self.set_author("Site Development Bracketer")
        self.set_creator("Site Development Bracketer")
        
        # Initialize counters and properties
        self.page_count = 0
        
        # Add fonts
        self.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
        self.add_font("DejaVu", "B", "DejaVuSans.ttf", uni=True)
        self.add_font("DejaVu", "I", "DejaVuSans.ttf", uni=True)
        
        # Set default font
        self.set_font("DejaVu", "", 10)
        
        # Set colors
        self.primary_color = (31, 120, 180)  # Blue
        self.secondary_color = (51, 160, 44)  # Green
        self.accent_color = (227, 26, 28)     # Red
        self.neutral_color = (100, 100, 100)  # Gray
    
    def header(self):
        """Add header to each page with logo and title."""
        self.page_count += 1
        
        # Set the font for the header
        self.set_font("DejaVu", "B", 12)
        self.set_text_color(*self.primary_color)
        
        # Add title
        self.cell(0, 10, "Site Development Bracketer", 0, 0, "L")
        
        # Add date
        self.set_font("DejaVu", "I", 10)
        self.set_text_color(*self.neutral_color)
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.cell(0, 10, f"Report Date: {current_date}", 0, 0, "R")
        
        # Add line below header
        self.ln(12)
        self.set_draw_color(*self.primary_color)
        self.line(10, self.get_y(), self.w - 10, self.get_y())
        self.ln(5)
    
    def footer(self):
        """Add footer to each page with page number."""
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Set font
        self.set_font("DejaVu", "I", 8)
        # Set text color to gray
        self.set_text_color(*self.neutral_color)
        # Page number
        self.cell(0, 10, f"Page {self.page_count}", 0, 0, "C")
    
    def add_title_page(self):
        """Add a title page to the report."""
        self.add_page()
        
        # Move cursor down to center title vertically
        self.ln(40)
        
        # Add title
        self.set_font("DejaVu", "B", 24)
        self.set_text_color(*self.primary_color)
        self.cell(0, 20, "Performance Analysis Report", 0, 1, "C")
        
        # Add subtitle
        self.set_font("DejaVu", "I", 16)
        self.set_text_color(*self.neutral_color)
        self.cell(0, 15, "Site Development Bracketer", 0, 1, "C")
        
        # Add date
        self.set_font("DejaVu", "", 12)
        current_date = datetime.now().strftime("%B %d, %Y")
        self.cell(0, 10, f"Generated on {current_date}", 0, 1, "C")
    
    def add_section_header(self, title):
        """Add a section header with the given title."""
        self.ln(5)
        self.set_font("DejaVu", "B", 14)
        self.set_text_color(*self.primary_color)
        self.cell(0, 10, title, 0, 1, "L")
        self.set_draw_color(*self.primary_color)
        self.line(10, self.get_y(), self.w - 10, self.get_y())
        self.ln(5)
    
    def add_subsection_header(self, title):
        """Add a subsection header with the given title."""
        self.ln(3)
        self.set_font("DejaVu", "B", 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, title, 0, 1, "L")
        self.ln(2)
    
    def add_paragraph(self, text):
        """Add a paragraph of text."""
        self.set_font("DejaVu", "", 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 5, text)
        self.ln(3)
    
    def add_table(self, df, title=None, format_func=None, col_widths=None, has_header=True):
        """
        Add a DataFrame as a table in the PDF.
        
        Args:
            df: Pandas DataFrame to be added as a table
            title: Optional title for the table
            format_func: Optional function to format cell values (takes value, returns string)
            col_widths: Optional list of column widths (in mm)
            has_header: Whether the DataFrame has a header row to be formatted differently
        """
        if title:
            self.add_subsection_header(title)
        
        # Ensure DataFrame is not empty
        if df is None or df.empty:
            self.set_font("DejaVu", "I", 10)
            self.set_text_color(*self.neutral_color)
            self.cell(0, 10, "No data available for this table.", 0, 1, "L")
            return
        
        # Calculate column widths if not provided
        if col_widths is None:
            available_width = self.w - 20  # Total width minus margins
            col_widths = [available_width / len(df.columns)] * len(df.columns)
        
        # Format function for cell values if not provided
        if format_func is None:
            def format_func(x):
                if pd.isna(x):
                    return ""
                elif isinstance(x, (int, np.integer)):
                    return str(x)
                elif isinstance(x, (float, np.floating)):
                    return f"{x:.1f}"
                else:
                    return str(x)
        
        # Set font for header row
        if has_header:
            self.set_font("DejaVu", "B", 10)
            self.set_fill_color(240, 240, 240)  # Light gray background
            
            # Draw header row
            for i, col in enumerate(df.columns):
                self.cell(col_widths[i], 7, str(col), 1, 0, "C", True)
            self.ln()
        
        # Set font for data rows
        self.set_font("DejaVu", "", 9)
        
        # Draw data rows
        for i, row in df.iterrows():
            # Check if we need a page break
            if self.get_y() + 7 > self.page_break_trigger:
                self.add_page()
                
                # Redraw header if we have one
                if has_header:
                    self.set_font("DejaVu", "B", 10)
                    self.set_fill_color(240, 240, 240)
                    for i, col in enumerate(df.columns):
                        self.cell(col_widths[i], 7, str(col), 1, 0, "C", True)
                    self.ln()
                    self.set_font("DejaVu", "", 9)
            
            # Alternate row colors for better readability
            fill = i % 2 == 0
            if fill:
                self.set_fill_color(255, 255, 255)  # White
            else:
                self.set_fill_color(245, 245, 245)  # Very light gray
            
            # Draw the row
            for j, val in enumerate(row):
                formatted_val = format_func(val)
                self.cell(col_widths[j], 6, formatted_val, 1, 0, "L", fill)
            self.ln()
    
    def add_plotly_figure(self, fig, title=None, width=180, height=120):
        """
        Add a Plotly figure to the PDF.
        
        Args:
            fig: Plotly figure to be added
            title: Optional title for the figure
            width: Width of the figure in mm
            height: Height of the figure in mm
        """
        if title:
            self.add_subsection_header(title)
        
        # Check if we need a page break
        if self.get_y() + height > self.page_break_trigger:
            self.add_page()
            if title:
                self.add_subsection_header(title)
        
        # Convert Plotly figure to PNG image
        img_bytes = fig.to_image(format="png", width=width*12, height=height*12)
        
        # Create a BytesIO object from the image bytes
        img_io = io.BytesIO(img_bytes)
        
        # Add the image to the PDF
        self.image(img_io, x=10, w=width, h=height)
        self.ln(height + 5)
    
    def add_development_distribution(self, power_counts, accel_counts, title="Development Distribution"):
        """
        Add development distribution visualization and table.
        
        Args:
            power_counts: DataFrame with power development counts
            accel_counts: DataFrame with acceleration development counts
            title: Title for the section
        """
        self.add_section_header(title)
        
        # Add paragraph explaining the distribution
        self.add_paragraph(
            "The development distribution shows how users are categorized across "
            "different brackets based on their power and acceleration metrics. "
            "This provides insight into the overall performance distribution "
            "within the group."
        )
        
        # Add tables for power and acceleration counts
        self.add_table(power_counts, "Power Development Distribution")
        self.add_table(accel_counts, "Acceleration Development Distribution")
        
        # Create a bar chart visualization for distribution
        fig = go.Figure()
        
        # Add bar for power counts
        categories = power_counts.columns.tolist()
        power_values = power_counts.values.flatten()
        
        fig.add_trace(go.Bar(
            x=categories,
            y=power_values,
            name="Power",
            marker_color="#1f77b4"  # Blue
        ))
        
        # Add bar for acceleration counts
        accel_values = accel_counts.values.flatten()
        fig.add_trace(go.Bar(
            x=categories,
            y=accel_values,
            name="Acceleration",
            marker_color="#ff7f0e"  # Orange
        ))
        
        # Update layout
        fig.update_layout(
            title="Development Bracket Distribution",
            xaxis_title="Development Bracket",
            yaxis_title="Count",
            barmode="group",
            width=800,
            height=500
        )
        
        # Add the plotly figure to the PDF
        self.add_plotly_figure(fig, "Development Distribution Visualization")
    
    def add_transition_matrices(self, power_transitions, accel_transitions, title="Transition Analysis"):
        """
        Add transition matrices for power and acceleration.
        
        Args:
            power_transitions: Dictionary of power transition matrices by period
            accel_transitions: Dictionary of acceleration transition matrices by period
            title: Title for the section
        """
        self.add_section_header(title)
        
        # Add paragraph explaining the transitions
        self.add_paragraph(
            "Transition matrices show how users move between different development brackets "
            "from one test to another. Diagonal values (blue) represent users who remained "
            "in the same bracket. Values below the diagonal (green) represent improvements, "
            "while values above the diagonal (red) represent regressions."
        )
        
        # Add power transition matrices
        self.add_subsection_header("Power Transitions")
        for period, matrix in power_transitions.items():
            self.add_table(matrix, f"Period: {period}")
        
        # Add acceleration transition matrices
        self.add_subsection_header("Acceleration Transitions")
        for period, matrix in accel_transitions.items():
            self.add_table(matrix, f"Period: {period}")
    
    def add_region_analysis(self, region_data, title="Body Region Analysis"):
        """
        Add body region analysis section.
        
        Args:
            region_data: Dictionary with region data
            title: Title for the section
        """
        self.add_section_header(title)
        
        # Add paragraph explaining the region analysis
        self.add_paragraph(
            "The body region analysis shows performance metrics for different body regions. "
            "This includes average development scores and changes between tests. "
            "Positive changes are shown in green, while negative changes are shown in red."
        )
        
        # Add region data tables
        for region, data in region_data.items():
            self.add_subsection_header(f"{region} Region")
            
            if "power_df" in data and data["power_df"] is not None:
                self.add_table(data["power_df"], f"{region} Region Power Development (%)")
            
            if "accel_df" in data and data["accel_df"] is not None:
                self.add_table(data["accel_df"], f"{region} Region Acceleration Development (%)")
            
            # Add changes if available
            if "power_changes" in data and data["power_changes"] is not None:
                power_changes = data["power_changes"]
                change_text = "Average Changes in Power Development:\n"
                
                if "test1_to_test2_pct" in power_changes and not pd.isna(power_changes["test1_to_test2_pct"]):
                    change = float(power_changes["test1_to_test2_pct"])
                    sign = "+" if change >= 0 else ""
                    color = "green" if change >= 0 else "red"
                    change_text += f"Test 1 → Test 2: {sign}{change:.1f}% ({color})\n"
                
                if "test2_to_test3_pct" in power_changes and not pd.isna(power_changes["test2_to_test3_pct"]):
                    change = float(power_changes["test2_to_test3_pct"])
                    sign = "+" if change >= 0 else ""
                    color = "green" if change >= 0 else "red"
                    change_text += f"Test 2 → Test 3: {sign}{change:.1f}% ({color})\n"
                
                self.add_paragraph(change_text)
            
            # Add similar for acceleration changes
            if "accel_changes" in data and data["accel_changes"] is not None:
                accel_changes = data["accel_changes"]
                change_text = "Average Changes in Acceleration Development:\n"
                
                if "test1_to_test2_pct" in accel_changes and not pd.isna(accel_changes["test1_to_test2_pct"]):
                    change = float(accel_changes["test1_to_test2_pct"])
                    sign = "+" if change >= 0 else ""
                    color = "green" if change >= 0 else "red"
                    change_text += f"Test 1 → Test 2: {sign}{change:.1f}% ({color})\n"
                
                if "test2_to_test3_pct" in accel_changes and not pd.isna(accel_changes["test2_to_test3_pct"]):
                    change = float(accel_changes["test2_to_test3_pct"])
                    sign = "+" if change >= 0 else ""
                    color = "green" if change >= 0 else "red"
                    change_text += f"Test 2 → Test 3: {sign}{change:.1f}% ({color})\n"
                
                self.add_paragraph(change_text)
    
    def add_user_analysis(self, user_data, title="Individual User Analysis"):
        """
        Add individual user analysis section.
        
        Args:
            user_data: Dictionary with user analysis data
            title: Title for the section
        """
        self.add_section_header(title)
        
        # Add paragraph explaining the user analysis
        self.add_paragraph(
            "The individual user analysis shows detailed performance metrics for specific users. "
            "This includes raw values, development scores, and bracket categorizations."
        )
        
        for user_name, data in user_data.items():
            self.add_subsection_header(f"User: {user_name}")
            
            # Add power matrix
            if "power_matrix" in data and data["power_matrix"] is not None:
                self.add_table(data["power_matrix"], "Power Matrix (Raw Values)")
            
            # Add acceleration matrix
            if "accel_matrix" in data and data["accel_matrix"] is not None:
                self.add_table(data["accel_matrix"], "Acceleration Matrix (Raw Values)")
            
            # Add development matrices
            if "power_dev_matrix" in data and data["power_dev_matrix"] is not None:
                self.add_table(data["power_dev_matrix"], "Power Development Matrix (%)")
            
            if "accel_dev_matrix" in data and data["accel_dev_matrix"] is not None:
                self.add_table(data["accel_dev_matrix"], "Acceleration Development Matrix (%)")
            
            # Add overall development categorization
            if "overall_dev_matrix" in data and data["overall_dev_matrix"] is not None:
                self.add_table(data["overall_dev_matrix"], "Overall Development Categorization")
            
            # Add development brackets
            if "power_brackets" in data and data["power_brackets"] is not None:
                self.add_table(data["power_brackets"], "Power Development Brackets")
            
            if "accel_brackets" in data and data["accel_brackets"] is not None:
                self.add_table(data["accel_brackets"], "Acceleration Development Brackets")
    
    def generate_complete_report(self, report_data):
        """
        Generate a complete PDF report with all available data.
        
        Args:
            report_data: Dictionary containing all data to be included in the report
            
        Returns:
            BytesIO object containing the generated PDF
        """
        # Reset page count
        self.page_count = 0
        
        # Add title page
        self.add_title_page()
        
        # Add summary section
        if "summary" in report_data:
            self.add_page()
            self.add_section_header("Summary")
            
            summary = report_data["summary"]
            
            # Add paragraph with summary information
            summary_text = (
                "This report provides a comprehensive analysis of exercise performance data. "
                "It includes group-level analysis, transition patterns, and detailed metrics "
                "for different body regions."
            )
            self.add_paragraph(summary_text)
            
            # Add single test user averages if available
            if "power_average" in summary and "accel_average" in summary:
                self.add_subsection_header("Single Test Users Averages")
                
                avg_data = {
                    "Metric": ["Power Development", "Acceleration Development"],
                    "Average (%)": [float(summary["power_average"]), float(summary["accel_average"])]
                }
                avg_df = pd.DataFrame(avg_data)
                self.add_table(avg_df)
            
            # Add multi-test user averages if available
            if "avg_days_between_tests" in summary:
                self.add_subsection_header("Multi-Test User Averages")
                
                multi_avg_data = {
                    "Metric": [
                        "Days Between Tests",
                        "Power Change (Test 1→2)",
                        "Power Change (Test 2→3)",
                        "Accel Change (Test 1→2)",
                        "Accel Change (Test 2→3)"
                    ],
                    "Value": [
                        str(summary.get("avg_days_between_tests", "N/A")),
                        f"{float(summary.get('avg_power_change_1_2', 0)):.1f}%",
                        f"{float(summary.get('avg_power_change_2_3', 0)):.1f}%",
                        f"{float(summary.get('avg_accel_change_1_2', 0)):.1f}%",
                        f"{float(summary.get('avg_accel_change_2_3', 0)):.1f}%"
                    ]
                }
                multi_avg_df = pd.DataFrame(multi_avg_data)
                self.add_table(multi_avg_df)
        
        # Add development distribution section
        if ("power_counts" in report_data and "accel_counts" in report_data and
            report_data["power_counts"] is not None and report_data["accel_counts"] is not None):
            
            self.add_page()
            self.add_development_distribution(
                report_data["power_counts"],
                report_data["accel_counts"]
            )
        
        # Add transition matrices section
        if ("power_transitions" in report_data and "accel_transitions" in report_data and
            report_data["power_transitions"] is not None and report_data["accel_transitions"] is not None):
            
            self.add_page()
            self.add_transition_matrices(
                report_data["power_transitions"],
                report_data["accel_transitions"]
            )
        
        # Add region analysis section
        if "region_data" in report_data and report_data["region_data"] is not None:
            self.add_page()
            self.add_region_analysis(report_data["region_data"])
        
        # Add user analysis section
        if "user_data" in report_data and report_data["user_data"] is not None:
            self.add_page()
            self.add_user_analysis(report_data["user_data"])
        
        # Return the PDF as BytesIO
        output = io.BytesIO()
        self.output(dest=output)
        output.seek(0)
        return output


def generate_pdf_report(
    power_counts=None,
    accel_counts=None,
    single_test_distribution=None,
    power_transitions=None,
    accel_transitions=None,
    power_average=None,
    accel_average=None,
    avg_power_change_1_2=None,
    avg_accel_change_1_2=None,
    avg_power_change_2_3=None,
    avg_accel_change_2_3=None,
    avg_days_between_tests=None,
    region_data=None,
    user_data=None
):
    """
    Generate a PDF report with available data.
    
    Args:
        power_counts: Power development distribution counts
        accel_counts: Acceleration development distribution counts
        single_test_distribution: Single test user distribution
        power_transitions: Power transition matrices by period
        accel_transitions: Acceleration transition matrices by period
        power_average: Average power development
        accel_average: Average acceleration development
        avg_power_change_1_2: Average power change from test 1 to 2
        avg_accel_change_1_2: Average acceleration change from test 1 to 2
        avg_power_change_2_3: Average power change from test 2 to 3
        avg_accel_change_2_3: Average acceleration change from test 2 to 3
        avg_days_between_tests: Average days between tests
        region_data: Dictionary with region analysis data
        user_data: Dictionary with user analysis data
        
    Returns:
        BytesIO object containing the generated PDF
    """
    # Create PDF report
    pdf = PDFReport()
    
    # Organize data
    report_data = {
        "summary": {
            "power_average": power_average,
            "accel_average": accel_average,
            "avg_power_change_1_2": avg_power_change_1_2,
            "avg_accel_change_1_2": avg_accel_change_1_2,
            "avg_power_change_2_3": avg_power_change_2_3,
            "avg_accel_change_2_3": avg_accel_change_2_3,
            "avg_days_between_tests": avg_days_between_tests
        },
        "power_counts": power_counts,
        "accel_counts": accel_counts,
        "single_test_distribution": single_test_distribution,
        "power_transitions": power_transitions,
        "accel_transitions": accel_transitions,
        "region_data": region_data,
        "user_data": user_data
    }
    
    # Generate and return the PDF report
    return pdf.generate_complete_report(report_data)