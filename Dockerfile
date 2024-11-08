# Use a base Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Install frontend dependencies
WORKDIR /app/frontend
RUN npm install

# Set the command to run the Rasa server, actions server, and frontend
WORKDIR /app
CMD ["sh", "-c", "rasa run --enable-api & rasa run actions & npm start --prefix frontend"]