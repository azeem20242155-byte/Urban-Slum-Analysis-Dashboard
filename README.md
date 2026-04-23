# Urban Slum Analysis Dashboard
## Live Dashboard
https://urban-slum-analysis-dashboard-lzve7abkdxvbmqtvhexufv.streamlit.app/

This project is developed as part of the Data Science Project Lifecycle coursework.

This Streamlit dashboard visualizes sustainability-related data, focusing on urban population and slum population indicators.

1. Install required libraries:
   pip install streamlit pandas numpy plotly

2. Run the app:
   streamlit run app.py

- app.py → main Streamlit dashboard
- data → dataset files

  ## Objectives

The main objectives of this project are:

- To analyse trends in urban population growth across countries  
- To examine changes in slum population and slum share  
- To identify patterns between urbanisation and housing conditions  
- To classify countries into risk categories based on observed trends  
- To present insights through an interactive dashboard  


## Key Features

The dashboard consists of four main sections:

**Global Overview**  
Provides a high-level summary of urban population trends and slum indicators.

**Urban vs Slums Analysis**  
Explores the relationship between urban growth and changes in slum population.

**Country Explorer**  
Allows detailed analysis of individual countries.

**Risk Classification**  
Groups countries into categories based on:
- Urban population growth  
- Change in slum share  
- Change in estimated slum population  

The categories include:
- Improving urbanisation  
- Growth with pressure  
- Housing deterioration  
- Low growth / mixed outcome  

Interactive features such as filters, sorting options, and hover information are included to improve usability.


## Methodology

The project follows a structured data pipeline approach:

1. Data collection  
   Data was obtained from the World Bank World Development Indicators.

2. Data cleaning and preparation  
   Missing values were handled and datasets were aligned by country and time period.

3. Feature engineering  
   Key variables were created, including:
   - Total urban population growth (%)  
   - Change in slum share (percentage points)  
   - Change in slum population  

4. Risk classification  
   Countries were grouped based on the direction of change in urban growth and slum indicators.  
   A simple scoring approach was also applied to support comparison.

The classification is intended to support interpretation rather than to act as a predictive model.



## Project Structure
Urban-Slum-Analysis Dashboard
── app.py
── requirements.txt
── data_raw
── data_processed
     ── final_dataset.csv
── pages
     1_Global_Overview.py
     2_Urban_vs_Slums.py
     3_Country_Explorer.py
     4_Risk_Classification.py

    


## Installations
To run the application locally:

1. Install the required libraries: pip install -r requirements.txt
2. Run the Streamlit application:


## Technologies Used

- Python  
- Streamlit  
- Pandas  
- Plotly  

## Key Insight

The analysis shows that urban population growth does not produce the same outcomes across countries.  

Some countries appear to manage urbanisation effectively, with declining slum conditions, while others experience increasing housing pressure and expanding slum populations.  

This highlights the importance of urban planning, infrastructure development and housing policy in shaping development outcomes.


## Data Source

- The World Bank – World Development Indicators (WDI)  

