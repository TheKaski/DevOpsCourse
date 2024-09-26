# USe python 3 according to Docker.com instructions
FROM python:3

# Set the working directory in the container:
WORKDIR /usr/src/app

# Import the dependencies using pip
RUN pip install psutil

# Copy the project files
COPY . .

# Expose the API port to the HOST
EXPOSE 8000

# Run the python script
CMD [ "python", "./service1.py"]