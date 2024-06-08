if [ "$1" == "-y" ]; then
	# Remove any previous container called "dashboard" and build a new one
	docker stop dashboard
	docker rm dashboard

	# Build the new container and run it
	docker build -t dashboard .
fi

# Copy the excel file to the app folder
cp /Users/asier/Library/CloudStorage/OneDrive-Personal/Documents/Dinero/My\ Money.xlsx app/My_Money.xlsx


# Run the container
docker run \
	-it \
	--rm \
	--name dashboard \
	-p 8501:8501 \
	-v $(pwd)/app:/app \
	dashboard
exit 0
