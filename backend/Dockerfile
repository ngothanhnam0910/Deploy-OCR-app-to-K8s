FROM python:3.10-slim

# Define label
LABEL maintainer="NamNT"

# the /app folder is the current working directory
WORKDIR /app

COPY . /app/

EXPOSE 5000

# Disable pip cache to shrink the image size a little bit,
# since it does not need to be re-installed
RUN apt-get update -y
RUN pip install -r requirements.txt --no-cache-dir

ENTRYPOINT [ "uvicorn" ]
CMD ["app:app", "--host", "0.0.0.0", "--port", "5000"]