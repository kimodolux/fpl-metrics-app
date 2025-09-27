FROM public.ecr.aws/lambda/python:3.11

# Copy requirements and install dependencies
COPY lambda-package/requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt -t /var/task/

# Install cryptography and other binary packages with correct architecture
RUN pip install --platform linux_x86_64 \
    --target /var/task/ \
    --implementation cp \
    --python-version 3.11 \
    --only-binary=:all: \
    --upgrade \
    --force-reinstall \
    cryptography cffi

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