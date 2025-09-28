FROM public.ecr.aws/lambda/python:3.11

# First install packages that don't require compilation
COPY lambda-package/requirements.txt /tmp/
RUN pip install --no-cache-dir \
    --target /var/task/ \
    boto3 requests python-dotenv pyarrow==15.0.2

# Install snowflake-connector-python and its dependencies
RUN pip install --no-cache-dir \
    --target /var/task/ \
    snowflake-connector-python==3.7.0

# Install cryptography with specific compatible version for Lambda
RUN pip install --no-cache-dir \
    --target /var/task/ \
    cryptography==3.4.8

# Copy source code
COPY lambda-package/ /var/task/

# Clean up unnecessary files
RUN find /var/task -type f -name "*.pyc" -delete && \
    find /var/task -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find /var/task -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true && \
    find /var/task -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true && \
    find /var/task -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true && \
    rm -f /var/task/requirements.txt

# Create deployment package
WORKDIR /var/task
RUN zip -r /tmp/lambda-deployment.zip . -x "*.git*"

CMD ["echo", "Build complete"]