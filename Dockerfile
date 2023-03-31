FROM python:3.10.10-slim-bullseye
WORKDIR /app

RUN apt-get update && apt-get install -y apt-utils
RUN apt-get upgrade -y

# Install python packages
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Add the rest of the code
COPY main.py /app/

# Download the data
COPY download.py /app/
RUN python download.py

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
