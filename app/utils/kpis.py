import pandas as pd
import streamlit as st
from utils.data_processing import get_assets
import plotly.express as px
import numpy as np
from statsmodels.tsa.arima.model import ARIMA

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

def months_of_fi(df, date, monthly_expenses=0):
	return int(df['Total'].iloc[date] / monthly_expenses)

def asset_value_forecast(df, p=24, d=1, q=6):
	# Preprocessing
	df['Date'] = pd.to_datetime(df['Date'])
	df = df.set_index('Date')
	
	# Eliminate NaN values
	df = df.dropna(subset=['Total'])
	
	# Dependent variable
	y = df['Total']
	
	# ARIMA model
	# Parameters: ARIMA(p, d, q)
	# p: The number of lag observations included in the model
	# d: The number of times that the raw observations are differenced
	# q: The size of the moving average
	model = ARIMA(y, order=(p, d, q))
	model_fit = model.fit()
	
	# Future dates
	future = pd.date_range(start=df.index[-1], periods=13, freq='MS')
	future_df = pd.DataFrame(future, columns=['Date'])
	future_df = future_df.set_index('Date')

	# ARIMA based predictions
	pred = model_fit.forecast(steps=12)  # 12 months
	# Adjust the predictions to the original data
	future_df['predicted_assets'] = np.append([np.nan], pred)
	future_df['predicted_assets'] = future_df['predicted_assets'].shift(-1)

	return pd.concat([df, future_df])[:-1], model_fit.aic, model_fit.bic

