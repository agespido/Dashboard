import streamlit as st
from datetime import datetime, timedelta
from utils.data_processing import get_excel_to_df, get_date_from_slider
from utils.charts import asset_allocation_pie_chart, balance_of_the_month_bar_chart, monthly_evolution_line_chart
from utils.kpis import show_kpis, months_of_fi

def display_main_window(st, df):
	# Create a two-column layout
	col1, col2, col3 = st.columns([2, 3, 2])

	with col1:
		# Get the date from the slider
		date = get_date_from_slider(df)
		mofi = months_of_fi(df, date)
		with st.container(border=True):
			st.metric("Months of FI", '{} ({:.1f} years)'.format(mofi, mofi / 12))

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

	# Create the
	display_main_window(st, df)


if __name__ == '__main__':
	main()
