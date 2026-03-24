FROM python:3.11-slim

# Install git package for our ai package, then clear cache to save docker space. 
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Working dir inside the container.
WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

# Copies req.txt from local machine into /app inside container.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of files into /app folder.
COPY . .

# As HF want for backend.
EXPOSE 7860

# Starting the server.  0.0.0.0 accepts connections from anywhere, not just local. 
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]