FROM python::3.10.10-slim-bullseye
WORKDIR /app

RUN apt-get update && apt-get install -y apt-utils
RUN apt-get upgrade -y

# Install python packages
RUN pip install --upgrade pip
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Add the rest of the code
ADD main.py .

# Download the data
ADD download.py .
RUN python download.py

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
