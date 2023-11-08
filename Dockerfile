# start by pulling the python image
FROM python:3.11

# switch working directory
WORKDIR /app
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt


RUN python -m pip install --upgrade pip
# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt


# copy every content from the local file to the image
COPY . /app

EXPOSE 5000
