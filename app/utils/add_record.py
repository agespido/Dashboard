import json
import streamlit as st
import datetime
import pandas as pd

def get_today_date():
	return datetime.date.today().strftime("%Y-%m-%d")

def load_json(file_path):
	with open(file_path, 'r') as f:
		data = json.load(f)
	return data

def save_to_json(file_path, data):
	try:
		with open(file_path, 'r+') as f:
			existing_data = json.load(f)
			existing_data.append(data)
			f.seek(0)
			json.dump(existing_data, f, ensure_ascii=False, indent=4)
	except json.JSONDecodeError:
		with open(file_path, 'w') as f:
			json.dump([data], f, ensure_ascii=False, indent=4)

def save_to_csv(file_path, data, today):
	# Read the CSV file using pandas
	df = pd.read_csv(file_path)
	new_element_df = df[0:0].copy()
	# Add the new date
	new_element_df.loc[0, 'Date'] = today
	new_element_df.loc[0] = [0 if pd.isna(x) else x for x in new_element_df.loc[0]]

	for account in data:
		new_element_df.loc[0, account['type']] += account['value']
		# TDB: currency exchange ratio
	
	# Save in CSV file
	# Append the new row to the existing DataFrame 
	df = pd.concat([df, new_element_df], ignore_index=True) 
	# Save the updated DataFrame back to the CSV file
	df.to_csv(file_path, index=False)

def display_new_record_window(st):
	# Load JSON
	input_file_path = 'database/account_list.json'
	accounts = load_json(input_file_path)
	# Add a "value" field to each account
	for account in accounts:
		account["value"] = None

	# Dictionary to store input values
	json_out_values = {}
	# Record the date
	today = get_today_date()
	json_out_values["Date"] = today

	# Layout with three columns: two for input and one for displaying values
	col1, col2, col3 = st.columns(3)

	# Record each account in two input columns and display in the third column
	for i, account in enumerate(accounts):
		if i % 2 == 0:
			with col1:
				value = st.number_input(f"{account['name']}", key=account['name'], format="%.02f")
				account['value'] = value
				json_out_values[account['name']] = f"{value:.2f}".replace('.', ',')
		else:
			with col2:
				value = st.number_input(f"{account['name']}", key=account['name'], format="%.02f")
				account['value'] = value
				json_out_values[account['name']] = f"{value:.2f}".replace('.', ',')

	# Button to submit the form
	if st.button('Submit'):
		save_to_json('database/data_record.json', json_out_values)
		save_to_csv('database/data.csv', accounts, today)
		with col3:
			df = pd.DataFrame([json_out_values]).transpose().reset_index() 
			df.columns = ["Item", "Value"]
			st.table(df)

