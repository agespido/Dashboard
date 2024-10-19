# Use the official image as a parent image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip3 install altair
RUN pip3 install matplotlib
RUN pip3 install numpy
RUN pip3 install pandas
RUN pip3 install plotly
RUN pip3 install streamlit
RUN pip3 install openpyxl
RUN pip3 install scikit-learn
RUN pip3 install statsmodels

# Make port 8501 available to the world outside this container
EXPOSE 8051
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run main.py when the container launches
ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]


