# Categorizer-App

A specialized Streamlit application for advanced exercise data processing and performance tracking, leveraging interactive visualizations and comprehensive analytics to provide deep insights into athlete development.

## Installation

When running this application externally (outside of Replit), make sure to install the required dependencies:

```bash
pip install streamlit pandas numpy plotly openpyxl trafilatura
```

Or you can create a requirements.txt file with the following content:

```
streamlit>=1.24.0
pandas>=1.5.0
numpy>=1.22.0
plotly>=5.14.0
openpyxl>=3.1.0
trafilatura>=1.5.0
```

And then run:

```bash
pip install -r requirements.txt
```

## Running the App

To run the app:

```bash
streamlit run app.py
```

## Features

- Data validation and preprocessing from CSV/Excel files
- User-specific performance matrices tracking
- Development categorization into brackets (Goal Hit, Elite, Above Average, Average, Under Developed, Severely Under Developed)
- Color-coded transition matrices showing user movements between brackets over time
- Body region meta-analysis with performance metrics
- Separate interfaces for single-test and multi-test users
- Visual performance tracking with interactive graphs
- Comprehensive change metrics between test instances
- Report generation with distribution visualizations and transition tables for easy sharing

## Key Components

- **Data Processing**: Validation, cleaning, and preparation of exercise data
- **Matrix Generation**: Creation of user-specific performance matrices
- **Bracket Visualization**: Visual representation of performance transitions between brackets
- **Statistical Analysis**: Calculation of performance metrics and change indicators
- **Interactive UI**: Streamlit-powered interface with filtering and visualization tools
- **Report Generator**: Creation of downloadable reports with visualizations

## Technologies Used

- Streamlit for the web application framework
- Pandas for data manipulation
- Plotly for interactive visualizations
- NumPy for mathematical operations
