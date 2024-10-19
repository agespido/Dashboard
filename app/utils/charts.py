import pandas as pd
import streamlit as st
import plotly.express as px
import altair as alt
from utils.data_processing import get_assets
from utils.kpis import asset_value_forecast

color_discrete_map = {
	'Stocks': '#3498db',     # blue
	'Crypto': '#9b59b6',     # purple
	'Cash': '#1abc9c',       # teal
	'Home Equity': '#f1c40f' # yellow
}

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

	# Calculate the mean of the current and previous values at each point (cumulative mean)
	df_balance_month['Mean'] = df_balance_month['Balance of the month'][1:].expanding().mean()

	# Create an Altair bar chart for balance of the month
	bars = alt.Chart(df_balance_month).mark_bar().encode(
		x='Date',
		y='Balance of the month',
		color=alt.condition(
			alt.datum['Balance of the month'] > 0,
			alt.value('#1ABC9C'),  # Green for positive values
			alt.value('#E74C3C')   # Red for negative values
		)
	)

	# Create an Altair line chart for the mean
	line = alt.Chart(df_balance_month).mark_line(color='yellow').encode(
		x='Date',
		y='Mean'
	)

	# Combine both charts and configure the combined chart
	combined_chart = alt.layer(bars, line).properties(
	).configure_axis(
		titleFontSize=0
	).configure_legend(
		title=None  # Remove the legend title
	).interactive()

	# Display the combined chart in Streamlit
	st.write('Balance of the month and its mean')
	st.altair_chart(combined_chart, use_container_width=True)

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

def total_asset_forecast_line_chart(df, p, d, q):
	"""
	Creates a line chart showing the total asset values and the ARIMA forecast based on the given dataframe.

	Args:
		df (pd.DataFrame): The dataframe containing asset data.

	Returns:
		None
	"""
	# Ensure to import the asset_value_forecast from utils.kpis
	df_forecast, aic, bic = asset_value_forecast(df, p, d, q)
	
	# Reset index to make 'Date' a column
	df_forecast = df_forecast.reset_index()

	# Prepare the line chart
	fig = px.line(df_forecast, x='Date', y=['Total', 'predicted_assets'], 
				  labels={'value': 'Assets', 'variable': 'Type'})
	# Adjust the layout to the edge of the chart
	fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
	
	# Update the traces to include lines and markers
	fig.update_traces(mode='lines+markers', marker=dict(size=5))
	fig.data[0].name = 'Real values'
	fig.data[1].name = 'Predicted values'
	fig.data[0].line.color = 'blue'
	fig.data[1].line.color = 'red'
	
	# Display the chart
	st.plotly_chart(fig)

	# Two columns for the AIC and BIC values
	return df_forecast, aic, bic
