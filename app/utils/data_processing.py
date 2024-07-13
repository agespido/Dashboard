import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import warnings


# Suppress all warnings
warnings.filterwarnings("ignore")

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
