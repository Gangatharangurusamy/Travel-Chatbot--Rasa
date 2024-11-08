# Travel Assistant Chatbot

### Overview
This chatbot is built with the Rasa framework to assist users with travel-related inquiries. It offers general information on popular destinations, personalized travel recommendations, and booking assistance. Basic multilingual support is available in English.

### Features
1. **Travel Inquiries**: Provides details on destinations, top attractions, weather updates, and travel tips.
2. **Personalized Recommendations**: Suggestions based on user preferences like budget, travel style, and season.
3. **Booking and Activity Assistance**: Facilitates bookings and provides activity suggestions for chosen destinations.
### Folder Structure
```bash
├── .rasa/             # Rasa model files
├── actions/           # Custom action definitions in `actions.py`
├── data/              # Training data for NLU and stories
├── frontend/          # React frontend for the chatbot interface
│   ├── public/        # Static files for the frontend
│   ├── src/           # React component files
│   ├── node_modules/  # Node.js modules for frontend dependencies
│   ├── package.json   # Frontend dependencies and scripts
│   ├── package-lock.json # Lock file for dependencies
│   └── README.md      # README for frontend specifics
├── models/            # Saved Rasa models
├── tests/             # Test cases for chatbot features
├── venv/              # Python virtual environment (not included in repo)
├── .env               # Environment variables for API keys
├── .gitignore         # Files and directories to ignore in Git
├── config.yml         # Rasa pipeline and policies configuration
├── credentials.yml    # Credentials for messaging channels and APIs
├── Dockerfile         # Docker setup for containerization
├── domain.yml         # Defines intents, entities, slots, and responses
├── endpoints.yml      # Endpoints configuration for action server
└── requirements.txt   # Python dependencies for Rasa backend
```
### Technical Stack
- **Frontend**: Built with React and styled using Tailwind CSS.
- **Backend**: Rasa framework for natural language understanding and response generation, with actions defined in `action.py`.
- **APIs Used**:
  - **OpenWeatherMap**: Provides weather data for selected destinations.
  - **Foursquare Places**: Supplies location-based recommendations and places of interest.
  - **Amadeus API**: Used for flight booking information and availability.

### Setup Instructions
#### 1. Prerequisites
- Python 3.7 or higher
- Node.js and npm (for frontend setup)
- API keys for OpenWeatherMap, Foursquare, and Amadeus (add these to a `.env` file as environment variables).

#### 2. Installation Steps
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd travel-assistant-chatbot
   ```
2. **Backend Setup**:
   - Install Rasa:
     ```bash
     pip install rasa
     ```
   - Install additional Python dependencies from `requirements.txt`:
     ```bash
     pip install -r requirements.txt
     ```
   - Set up environment variables in a `.env` file:
     ```
     OPENWEATHER_API_KEY=<your_api_key>
     FOURSQUARE_PLACES_API_KEY=<your_api_key>
     AMADEUS_CLIENT_ID=<your_client_id>
     AMADEUS_CLIENT_SECRET=<your_client_secret>
     ```
3. **Frontend Setup**:
   - Navigate to the `frontend` folder and install dependencies:
     ```bash
     cd frontend
     npm install
     ```

#### 3. Running the Chatbot
- Run the Rasa Server:
  ```bash
  rasa run --enable-api
  ```
- Start the Action Server:
  ```bash
  rasa run actions
  ```
- Start the Frontend Server:
  - In the `frontend` folder, start the frontend app:
    ```bash
    npm start
    ```

## Deployment Options
- For web-based deployment, use cloud services like Heroku, AWS, or GCP.
- Alternatively, the chatbot can be run locally by following the instructions above.

## Future Improvements
1. **Enhanced Multilingual Support**: Extend support to additional languages.
2. **Additional APIs for Travel Recommendations**: Incorporate more APIs to offer enriched travel data.
3. **Advanced Personalization**: Refine recommendations by using machine learning models to better match user preferences.
