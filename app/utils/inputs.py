import streamlit as st
from datetime import datetime, timedelta

def get_monthly_expenses_from_slider():
	# Slider with values from 0 to 3000 €
	monthly_expenses = st.slider('Monthly expenses', 0, 3000, 1000, step=50)
	return monthly_expenses if monthly_expenses > 0 else 1

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