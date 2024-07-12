import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import plotly.express as px
import numpy as np
import altair as alt
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

# Define a cool color scheme
color_discrete_map = {
	'Stocks': '#3498db',     # blue
	'Crypto': '#9b59b6',     # purple
	'Cash': '#1abc9c',       # teal
	'Home Equity': '#f1c40f' # yellow
}

def get_excel_to_df(xls_file):
	"""
	Reads an Excel file and returns a cleaned Pandas DataFrame.

	Args:
		xls_file (str): Path to the Excel file.

	Returns:
		pd.DataFrame: Cleaned DataFrame with modified date format, NaN values replaced by 0,
					  and white spaces removed from column names.
	"""
	try:
		df = pd.read_excel(xls_file)
	except FileNotFoundError:
		print("File does not exist")
		st.error("File does not exist")
		exit(1)

	# Modify date to YYYY-MM-DD format
	df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d', errors='coerce')
	df = df.dropna(subset=['Date'])

	# Replace all the NaN values with 0
	df = df.fillna(0)

	# Remove white spaces from column names
	df.columns = df.columns.str.strip()

	return df

def get_assets(df, asset_type, date=-1):
	"""
	Retrieves asset values from a Pandas DataFrame based on the specified asset types and a given date index.

	Args:
		df (pd.DataFrame): The DataFrame containing asset data.
		asset_type (list of str): A list of asset names (e.g., ['Stocks', 'Crypto', 'Cash']).
		date (int, optional): The row index corresponding to the desired date (default is -1, which represents the latest date).

	Returns:
		dict: A dictionary where keys are asset names and values are their corresponding values for the specified date.
	"""
	assets = {}
	for asset in asset_type:
		assets[asset] = df[asset].iloc[date]
		# If NaN, set it to 0
		if pd.isna(assets[asset]):
			assets[asset] = 0
	return assets

def get_date_from_slider(df):
	"""
	Interacts with a Streamlit slider widget to allow users to select a date within a specified range.

	Args:
		df (pd.DataFrame): The DataFrame containing date information.

	Returns:
		int: The row index corresponding to the selected date.
	"""
	# Dates to list
	dates = df['Date'].tolist()
	min_date = df['Date'].min()
	max_date = df['Date'].max()

	# Create a slider to select the date
	date = st.slider(
		"Select the date",
		value=datetime(datetime.now().year, datetime.now().month, datetime.now().day),
		step=timedelta(days=30),
		min_value=min_date,
		max_value=max_date,
		format="YYYY-MM")

	# Get the row number of the date (or the closest one if it does not exist)
	try:
		date_index = dates.index(date)
	except ValueError:
		date_index = -1

	if date_index == -1:
		# Check the closest index to the given date
		date = min(dates, key=lambda x: abs(x - date))
		date_index = dates.index(date)

	return date_index

def asset_allocation_pie_chart(df, date):
	"""
	Creates a pie chart showing asset allocation based on the given dataframe and date.

	Args:
		df (pd.DataFrame): The dataframe containing asset allocation data.
		date (int): The row number corresponding to the desired date.

	Returns:
		None
	"""
	# Calculate asset allocation
	asset_allocation = get_assets(df, ['Stocks', 'Crypto', 'Cash', 'Home Equity'], date)

	# Create a DataFrame for the pie chart
	pie_df = pd.DataFrame({'Asset': asset_allocation.keys(), 'Allocation': asset_allocation.values()})

	# Create a native Streamlit pie chart using Plotly
	st.write("Asset allocation")
	fig = px.pie(pie_df, values='Allocation', names='Asset', color='Asset', color_discrete_map=color_discrete_map)
	st.plotly_chart(fig)

def format_kpi_value(value):
	"""
	Formats a KPI value as 1.000,00 € or shows '0,00 €' if NaN.

	Args:
		value (float): The KPI value to format.

	Returns:
		str: Formatted KPI value as a string.
	"""
	if value > 1000 or value < -1000:
		str_value = f"{value:,.2f}"
	elif pd.isna(value):
		return "0,00 €"
	else:
		str_value = f"{value:.2f}"
	str_value = str_value.replace(".", "|").replace(",", ".").replace("|", ",")
	return f"{str_value} €"

def show_kpis(df, date):
	"""
	Displays key performance indicators (KPIs) based on the given dataframe and date.

	Args:
		df (pd.DataFrame): The dataframe containing KPI data.
		date (int): The row number corresponding to the desired date.

	Returns:
		None
	"""
	# Define the KPIs you want to display
	kpi_names = ['Total', 'MA 12m', 'Debt']

	# Get the KPI values
	kpis = get_assets(df, kpi_names, date)
	kpis_1 = get_assets(df, kpi_names, date - 1) if date > 0 else {'Total': 0, 'MA 12m': 0, 'Debt': 0}

	# Display the KPIs
	for kpi_name in kpi_names:
		kpi_value = kpis.get(kpi_name, None)
		kpi_value_1 = kpis_1.get(kpi_name, None)
		formatted_value = format_kpi_value(kpi_value)
		formatted_diff = format_kpi_value(kpi_value - kpi_value_1)
		with st.container(border=True):
			st.metric(kpi_name, formatted_value, formatted_diff)

def balance_of_the_month_bar_chart(df, date):
	"""
	Creates an Altair bar chart showing the balance of the month based on the given dataframe and date.

	Args:
		df (pd.DataFrame): The dataframe containing balance data.
		date (int): The row number corresponding to the desired date.

	Returns:
		None
	"""
	# Create a dataframe with positive and negative values for the balance of the month
	df_balance_month = df[['Date', 'Balance of the month']][:date + 1]

	# Create an Altair chart
	chart = alt.Chart(df_balance_month).mark_bar().encode(
		x='Date',
		y='Balance of the month',
		color=alt.condition(
			alt.datum['Balance of the month'] > 0,
			alt.value('#1ABC9C'),  # Green for positive values
			alt.value('#E74C3C')   # Red for negative values
		) # Eliminate title and axis labels
	).properties().configure_axis(
		titleFontSize=0
	).configure_legend(
		title=None  # Remove the legend title
	).interactive()
	# Display the customized chart using st.altair_chart
	st.write('Balance of the month')
	st.altair_chart(chart, use_container_width=True)

def monthly_evolution_line_chart(df, date):
	"""
	Creates an Altair line chart showing the €/month evolution of assets based on the given dataframe and date.

	Args:
		df (pd.DataFrame): The dataframe containing asset data.
		date (int): The row number corresponding to the desired date.

	Returns:
		None
	"""
	# Create a new dataframe with relevant columns
	df_selected = df[['Date', 'Stocks', 'Crypto', 'Cash', 'Home Equity']][:date + 1]

	# Melt the dataframe to long format for easier plotting
	df_melted = df_selected.melt(id_vars=['Date'], value_vars=['Stocks', 'Crypto', 'Cash', 'Home Equity'])
	
	# Create an Altair area chart using the color_discrete_map
	chart = alt.Chart(df_melted).mark_area().encode(
		x='Date:T',
		y=alt.Y('value:Q'),
		color=alt.Color('variable:N', 
						scale=alt.Scale(domain=list(color_discrete_map.keys()),
						range=list(color_discrete_map.values())))
	).configure_legend(
		title=None,
		orient='top-left'
	).properties().configure_axis(
		titleFontSize=0
	).interactive()

	st.write("€/month evolution of the assets")
	st.altair_chart(chart, use_container_width=True)

def get_monthly_expenses_from_slider():
	# Slider with values from 0 to 3000 €
	monthly_expenses = st.slider('Monthly expenses', 0, 3000, 1000, step=50)
	return monthly_expenses if monthly_expenses > 0 else 1

def months_of_fi(df, date):
	monthly_expenses = get_monthly_expenses_from_slider()
	return int(df['Total'].iloc[date] / monthly_expenses)

def main():
	"""
	Main function for creating a financial dashboard using Streamlit.

	Returns:
		None
	"""
	# Set the page configuration
	st.set_page_config(layout="wide", page_title="My Money Dashboard", page_icon="💰")

	# Load the data from an Excel file
	xls_file = 'My_Money.xlsx'
	df = get_excel_to_df(xls_file)

	# Add a column for the difference between the house value and the mortgage
	df['Home Equity'] = abs(df['House']) - abs(df['Debt'])

	# Create a two-column layout
	col1, col2, col3 = st.columns([2, 3, 2])

	with col1:
		# Get the date from the slider
		date = get_date_from_slider(df)
		mofi= months_of_fi(df, date)
		with st.container(border=True):
			st.metric("Months of FI", '{} ({:.1f} years)'.format(mofi, mofi/12))

	# Display the asset allocation pie chart in the first column
	with col2:
		asset_allocation_pie_chart(df, date)

	# Display the KPIs in the second column
	with col3:
		show_kpis(df, date)

	col1, col2 = st.columns([1, 1])
	# Container for the line chart
	with col1:
		with st.container(border=True):
			monthly_evolution_line_chart(df, date)

	# Container for the Balance of the month
	with col2:
		with st.container(border=True):
			balance_of_the_month_bar_chart(df, date)

if __name__ == '__main__':
	main()
