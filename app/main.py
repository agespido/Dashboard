import streamlit as st
from datetime import datetime, timedelta
from utils import *

def display_main_window(st, df):
	# Create a two-column layout
	col1, col2, col3 = st.columns([2, 3, 2])

	with col1:
		# Get the date from the slider
		date = get_date_from_slider(df)
		monthly_expenses = get_monthly_expenses_from_slider()
		months_fi = months_of_fi(df, date, monthly_expenses)

		with st.container(border=True):
			st.metric("Months of FI (retiring today)", "{} ({:.1f} years)".format(months_fi, months_fi / 12))
		with st.container(border=True):
			st.metric("FIRE number (applying  the 4\% rule)", "{}".format(format_kpi_value(monthly_expenses * 12 * 25)))

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

def display_forecast_window(st, df):
	# Three sliders for the ARIMA model in 3 columns
	col1, col2, col3 = st.columns(3)
	with col1:
		p = st.slider("Number of AR terms (p)", 0, 5, 1)
	with col2:
		d = st.slider("Number of Differences (d)", 0, 2, 1)
	with col3:
		q = st.slider("Number of MA terms (q)", 0, 5, 1)
	df_forecast, aic, bic = total_asset_forecast_line_chart(df, p, d, q)
	col1, col2, col3 = st.columns(3)
	with col1:
		with st.container(border=True):
			forecast_1y = df_forecast['predicted_assets'].iloc[-1]
			current_nw = df['Total'].iloc[-1]
			diff = forecast_1y - current_nw
			st.metric("In one year you will have", format_kpi_value(forecast_1y), format_kpi_value(diff))
	with col2:
		with st.container(border=True):
			str_value = f"{aic:,.2f}"
			str_value = str_value.replace(".", "|").replace(",", ".").replace("|", ",")
			st.metric("AIC: Akaike Information Criterion", "{}".format(str_value))
	with col3:
		with st.container(border=True):
			str_value = f"{bic:,.2f}"
			str_value = str_value.replace(".", "|").replace(",", ".").replace("|", ",")
			st.metric("BIC: Bayesian Information Criterion", "{}".format(str_value))


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

	# Create the dashboard with two windows
	tab1, tab2, tab3 = st.tabs(["Main", "Forecast", "Add new record"])
	with tab1:
		display_main_window(st, df)	
	with tab2:
		display_forecast_window(st, df)
	with tab3:
		display_new_record_window(st)

if __name__ == '__main__':
	main()
