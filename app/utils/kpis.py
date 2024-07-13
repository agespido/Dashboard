import pandas as pd
import streamlit as st
from utils.data_processing import get_assets

def format_kpi_value(value):
	"""
	Formats a KPI value as 1.000,00 � or shows '0,00 �' if NaN.

	Args:
		value (float): The KPI value to format.

	Returns:
		str: Formatted KPI value as a string.
	"""
	if value > 1000 or value < -1000:
		str_value = f"{value:,.2f}"
	elif pd.isna(value):
		return "0,00 �"
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

def get_monthly_expenses_from_slider():
	# Slider with values from 0 to 3000 €
	monthly_expenses = st.slider('Monthly expenses', 0, 3000, 1000, step=50)
	return monthly_expenses if monthly_expenses > 0 else 1

def months_of_fi(df, date):
	monthly_expenses = get_monthly_expenses_from_slider()
	return int(df['Total'].iloc[date] / monthly_expenses)
