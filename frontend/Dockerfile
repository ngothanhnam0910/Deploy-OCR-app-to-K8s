FROM python:3.10-slim

# Define label
LABEL maintainer="NamNT"

# Define workdir
WORKDIR /app

COPY . /app/

# Install library
RUN apt-get update -y
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit","run"]

CMD ["streamlit.py"]