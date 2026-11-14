#Use offical python image as base image
FROM python:3.12-slim

#Set the working directory in the container to /app
WORKDIR /app
#Copy the contents of the current directory in the container /app directory
COPY . /app
#upgrade pip
RUN pip install --upgrade pip
#install any needed packages
RUN pip install --no-cache-dir -r requirements.txt

#set the default commands to run when starting the container
CMD ["python", "app.py"]
