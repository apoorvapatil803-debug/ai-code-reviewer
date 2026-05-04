# Use official Python 3.11 image as the base
# slim = smaller size, doesn't include unnecessary system tools
FROM python:3.11-slim

# Set the working directory inside the container
# All subsequent commands run from this folder
WORKDIR /app

# Copy requirements first — before copying the rest of the code
# Docker caches each step — if requirements don't change,
# it won't reinstall packages on every build. Saves huge time.
COPY requirements.txt .

# Install all Python packages
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir langchain-groq

# Now copy the rest of the project into the container
COPY . .

# Tell Docker this container listens on port 8000
EXPOSE 8000

# The command that runs when the container starts
# Same as typing: uvicorn main:app --host 0.0.0.0 --port 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
