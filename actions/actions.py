# from typing import Text, Dict, Any, List
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
# from rasa_sdk.types import DomainDict
# from rasa_sdk.events import SlotSet
# import requests
# import os
# from dotenv import load_dotenv
# from datetime import datetime

# # Load environment variables
# load_dotenv()

# # API keys
# OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
# FOURSQUARE_PLACES_API_KEY = os.getenv("FOURSQUARE_PLACES_API_KEY")

# class ActionGreet(Action):
#     def name(self) -> Text:
#         return "action_greet"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Dict[Text, Any]]:
#         dispatcher.utter_message(response="utter_greet")
#         return []

# class ActionGetDestinationInfo(Action):
#     def name(self) -> Text:
#         return "action_get_destination_info"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Dict[Text, Any]]:
#         location = next(tracker.get_latest_entity_values("location"), None)
#         if not location:
#             dispatcher.utter_message(response="utter_ask_location")
#             return []

#         try:
#             # Get location details using Nominatim (OpenStreetMap)
#             location_info = self._get_location_details(location)
#             if not location_info:
#                 dispatcher.utter_message(text=f"I couldn't find information about {location}. Could you please check the spelling or try another destination?")
#                 return []

#             # Get weather data
#             weather_info = self._get_weather_data(location_info['lat'], location_info['lng'])

#             # Get places data using OpenTripMap
#             places_info = self._get_places_data(location_info['lat'], location_info['lng'])

#             # Get country info
#             country_info = self._get_country_info(location_info['country_code'])

#             # Construct comprehensive response
#             response = f"📍 Information about {location}, {location_info['country']}:\n\n"

#             # Weather section
#             response += "🌤️ Current Weather:\n"
#             response += f"• Condition: {weather_info['description'].capitalize()}\n"
#             response += f"• Temperature: {weather_info['temperature']}°C\n"
#             response += f"• Humidity: {weather_info['humidity']}%\n\n"

#             # Country information
#             response += "🗺️ Country Information:\n"
#             response += f"• Currency: {country_info['currency']}\n"
#             response += f"• Language: {country_info['language']}\n"
#             if country_info.get('timezone'):
#                 response += f"• Timezone: {country_info['timezone']}\n"

#             # Attractions
#             response += "\n🎯 Popular Places to Visit:\n"
#             for place in places_info[:5]:
#                 response += f"• {place['name']}"
#                 if place.get('type'):
#                     response += f" ({place['type']})"
#                 response += "\n"

#             # Travel tips
#             response += f"\n✨ Travel Tips:\n"
#             response += f"• Best time to visit: {self._get_best_time_to_visit(location_info['lat'])}\n"
#             if weather_info.get('recommendation'):
#                 response += f"• Weather recommendation: {weather_info['recommendation']}\n"

#             dispatcher.utter_message(text=response)
#             return [SlotSet("location", location)]

#         except Exception as e:
#             dispatcher.utter_message(text=f"I'm having trouble getting complete information about {location}. Please try again later.")
#             return []

#     def _get_location_details(self, location: Text) -> Dict[Text, Any]:
#         headers = {'User-Agent': 'TravelAssistantBot/1.0'}
#         url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=1"
#         response = requests.get(url, headers=headers)

#         if response.status_code == 200:
#             data = response.json()
#             if data:
#                 location_data = data[0]
#                 country_url = f"https://nominatim.openstreetmap.org/reverse?lat={location_data['lat']}&lon={location_data['lon']}&format=json"
#                 country_response = requests.get(country_url, headers=headers)
#                 country_data = country_response.json()

#                 return {
#                     'lat': float(location_data['lat']),
#                     'lng': float(location_data['lon']),
#                     'country': country_data['address'].get('country', 'Unknown'),
#                     'country_code': country_data['address'].get('country_code', '').upper(),
#                     'timezone': self._get_timezone(float(location_data['lat']), float(location_data['lon']))
#                 }
#         return None

#     def _get_weather_data(self, lat: float, lon: float) -> Dict[Text, Any]:
#         url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
#         response = requests.get(url)
#         if response.status_code == 200:
#             data = response.json()
#             temp = round(data["main"]["temp"])
#             recommendation = self._get_weather_recommendation(temp, data["weather"][0]["main"])
#             return {
#                 "description": data["weather"][0]["description"],
#                 "temperature": temp,
#                 "humidity": data["main"]["humidity"],
#                 "recommendation": recommendation
#             }
#         raise Exception("Weather API error")

#     def _get_places_data(self, lat: float, lon: float) -> List[Dict[Text, Any]]:
#         url = "https://api.foursquare.com/v3/places/search"
#         headers = {
#             "Accept": "application/json",
#             "Authorization": FOURSQUARE_PLACES_API_KEY
#         }
#         params = {
#             "ll": f"{lat},{lon}",
#             "radius": 5000,
#             "limit": 5,
#             "categories": "16000,10000,13000,12000",  # tourist attractions, arts & entertainment, food, shopping
#             "sort": "RATING"
#         }
#         try:
#             response = requests.get(url, headers=headers, params=params)
#             if response.status_code == 200:
#                 data = response.json()
#                 return [{
#                     "name": place["name"],
#                     "type": place.get("categories", [{}])[0].get("name", "Attraction")
#                 } for place in data.get("results", [])]
#         except:
#             pass
#         return [
#             {"name": "Historical Center", "type": "Sightseeing"},
#             {"name": "Local Museums", "type": "Culture"},
#             {"name": "Public Parks", "type": "Nature"},
#             {"name": "Local Markets", "type": "Shopping"},
#             {"name": "Restaurant District", "type": "Dining"}
#         ]

#     def _get_country_info(self, country_code: Text) -> Dict[Text, Any]:
#         url = f"https://restcountries.com/v3.1/alpha/{country_code}"
#         try:
#             response = requests.get(url)
#             if response.status_code == 200:
#                 data = response.json()[0]
#                 currencies = next(iter(data.get('currencies', {}).values()), {})
#                 languages = list(data.get('languages', {}).values())
#                 timezones = data.get('timezones', ['Unknown'])[0]

#                 return {
#                     "currency": f"{currencies.get('name', 'Unknown')} ({currencies.get('symbol', '')})",
#                     "language": ', '.join(languages) if languages else 'Unknown',
#                     "timezone": timezones
#                 }
#         except:
#             pass
#         return {
#             "currency": "Information not available",
#             "language": "Information not available",
#             "timezone": "Information not available"
#         }

#     def _get_timezone(self, lat: float, lon: float) -> Text:
#         try:
#             hour_offset = round(lon / 15)
#             if hour_offset > 0:
#                 return f"UTC+{hour_offset}"
#             elif hour_offset < 0:
#                 return f"UTC{hour_offset}"
#             return "UTC"
#         except:
#             return "UTC"

#     def _get_weather_recommendation(self, temp: int, condition: Text) -> Text:
#         if temp > 30:
#             return "Pack light clothes and sun protection"
#         elif temp < 10:
#             return "Pack warm clothes and layers"
#         elif condition.lower() in ['rain', 'drizzle']:
#             return "Don't forget your umbrella"
#         return "Weather is pleasant for sightseeing"

#     def _get_best_time_to_visit(self, lat: float) -> Text:
#         if lat > 0:
#             return "Spring (March-May) and Fall (September-November)"
#         else:
#             return "Spring (September-November) and Fall (March-May)"

# class ActionProvideRecommendations(Action):
#     def name(self) -> Text:
#         return "action_provide_recommendations"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Dict[Text, Any]]:
#         budget = next(tracker.get_latest_entity_values("budget"), None)
#         preferences = next(tracker.get_latest_entity_values("traveler_preferences"), None)
        
#         if not budget and not preferences:
#             dispatcher.utter_message(text="To provide better recommendations, could you tell me:\n1. Your budget range (e.g., budget, moderate, luxury)\n2. Your travel preferences (e.g., culture, nature, adventure, relaxation)")
#             return []

#         recommendations = self._get_recommendations(budget, preferences)
        
#         response = "Based on your preferences, here are some destinations you might enjoy:\n\n"
#         for rec in recommendations:
#             response += f"🌟 {rec['name']}\n"
#             response += f"• Perfect for: {rec['suitable_for']}\n"
#             response += f"• Highlights: {rec['highlights']}\n"
#             response += f"• Budget range: {rec['budget_range']}\n\n"

#         dispatcher.utter_message(text=response)
#         return []

#     def _get_recommendations(self, budget: str, preferences: str) -> List[Dict[Text, Any]]:
#         recommendations = []
        
#         if not budget:
#             budget = "moderate"
#         if not preferences:
#             preferences = "general"
            
#         if "nature" in str(preferences).lower():
#             recommendations.append({
#                 "name": "Costa Rica",
#                 "suitable_for": "Nature lovers and adventure seekers",
#                 "highlights": "Rainforests, beaches, wildlife",
#                 "budget_range": "Moderate"
#             })
        
#         if "culture" in str(preferences).lower():
#             recommendations.append({
#                 "name": "Kyoto, Japan",
#                 "suitable_for": "Cultural enthusiasts",
#                 "highlights": "Temples, traditional gardens, tea ceremonies",
#                 "budget_range": "Moderate to Luxury"
#             })
            
#         if "budget" in str(budget).lower():
#             recommendations.append({
#                 "name": "Bangkok, Thailand",
#                 "suitable_for": "Budget travelers who love culture and food",
#                 "highlights": "Temples, street food, markets",
#                 "budget_range": "Budget"
#             })
            
#         if "luxury" in str(budget).lower():
#             recommendations.append({
#                 "name": "Maldives",
#                 "suitable_for": "Luxury travelers seeking relaxation",
#                 "highlights": "Overwater villas, pristine beaches, spa retreats",
#                 "budget_range": "Luxury"
#             })

#         if not recommendations:
#             recommendations = [
#                 {
#                     "name": "Barcelona, Spain",
#                     "suitable_for": "All types of travelers",
#                     "highlights": "Architecture, beaches, cuisine",
#                     "budget_range": "Moderate"
#                 },
#                 {
#                     "name": "Bali, Indonesia",
#                     "suitable_for": "Culture and nature lovers",
#                     "highlights": "Temples, beaches, rice terraces",
#                     "budget_range": "Budget to Moderate"
#                 }
#             ]

#         return recommendations

# class ActionDefaultFallback(Action):
#     def name(self) -> str:
#         return "action_default_fallback"

#     def run(self, dispatcher, tracker, domain):
#         dispatcher.utter_message(text="I'm sorry, I didn't understand that.")
#         return []

# class ActionFacilitateBooking(Action):
#     def name(self) -> Text:
#         return "action_facilitate_booking"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Dict[Text, Any]]:
#         location = next(tracker.get_latest_entity_values("location"), None)
#         travel_season = next(tracker.get_latest_entity_values("travel_season"), None)
#         budget = next(tracker.get_latest_entity_values("budget"), None)

#         response = "I'll help you plan your trip."
#         slots_to_set = []

#         if location:
#             response += f"\n📍 Destination: {location}"
#             slots_to_set.append(SlotSet("location", location))
#         else:
#             response += "\nWhere would you like to travel to?"

#         if travel_season:
#             response += f"\n📅 Travel period: {travel_season}"
#             slots_to_set.append(SlotSet("travel_season", travel_season))
#         else:
#             response += "\nWhen would you like to travel?"

#         if budget:
#             response += f"\n💰 Budget: {budget}"
#             slots_to_set.append(SlotSet("budget", budget))
#         else:
#             response += "\nWhat's your budget for this trip?"

#         response += "\n\nI can help you with:"
#         response += "\n• Destination information and weather"
#         response += "\n• Hotel recommendations"
#         response += "\n• Activity suggestions"
#         response += "\n• Travel tips and requirements"
        
#         dispatcher.utter_message(text=response)
#         return slots_to_set

# class ActionHandleTravelDate(Action):
#     def name(self) -> Text:
#         return "action_handle_travel_date"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Dict[Text, Any]]:
#         travel_season = next(tracker.get_latest_entity_values("travel_season"), None)
#         location = tracker.get_slot("location")

#         if travel_season:
#             try:
#                 travel_date = datetime.strptime(travel_season, "%B %d").replace(year=datetime.now().year)
#                 formatted_date = travel_date.strftime("%B %d, %Y")
#                 season = self._get_season(travel_date)
#             except ValueError:
#                 formatted_date = travel_season
#                 season = travel_season

#             if location:
#                 response = f"Great! Let's plan your trip to {location} for {formatted_date}.\n"
#                 response += f"The ideal season for this location is {season}."
#                 dispatcher.utter_message(text=response)
#             else:
#                 dispatcher.utter_message(text="Please specify the location for your travel.")
#         else:
#             dispatcher.utter_message(text="Please provide your preferred travel dates.")
#         return []

#     def _get_season(self, travel_date: datetime) -> Text:
#         month = travel_date.month
#         if month in [12, 1, 2]:
#             return "Winter"
#         elif month in [3, 4, 5]:
#             return "Spring"
#         elif month in [6, 7, 8]:
#             return "Summer"
        # elif month in [9, 10, 11]:
        #     return "Autumn"
        # return "Unknown season"
# from typing import Text, Dict, Any, List
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
# from rasa_sdk.types import DomainDict
# from rasa_sdk.events import SlotSet
# import requests
# import os
# from dotenv import load_dotenv
# from datetime import datetime

# # Load environment variables
# load_dotenv()

# # API keys
# OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
# FOURSQUARE_PLACES_API_KEY = os.getenv("FOURSQUARE_PLACES_API_KEY")

# class ActionGreet(Action):
#     def name(self) -> Text:
#         return "action_greet"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Dict[Text, Any]]:
#         dispatcher.utter_message(response="utter_greet")
#         return []

# class ActionGetDestinationInfo(Action):
#     def name(self) -> Text:
#         return "action_get_destination_info"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Dict[Text, Any]]:
#         location = next(tracker.get_latest_entity_values("location"), None)
#         if not location:
#             dispatcher.utter_message(response="utter_ask_location")
#             return []

#         try:
#             # Get location details using Nominatim (OpenStreetMap)
#             location_info = self._get_location_details(location)
#             if not location_info:
#                 dispatcher.utter_message(text=f"I couldn't find information about {location}. Could you please check the spelling or try another destination?")
#                 return []

#             # Get weather data
#             weather_info = self._get_weather_data(location_info['lat'], location_info['lng'])

#             # Get places data using OpenTripMap
#             places_info = self._get_places_data(location_info['lat'], location_info['lng'])

#             # Get country info
#             country_info = self._get_country_info(location_info['country_code'])

#             # Construct comprehensive response
#             response = f"📍 Information about {location}, {location_info['country']}:\n\n"

#             # Weather section
#             response += "🌤️ Current Weather:\n"
#             response += f"• Condition: {weather_info['description'].capitalize()}\n"
#             response += f"• Temperature: {weather_info['temperature']}°C\n"
#             response += f"• Humidity: {weather_info['humidity']}%\n\n"

#             # Country information
#             response += "🗺️ Country Information:\n"
#             response += f"• Currency: {country_info['currency']}\n"
#             response += f"• Language: {country_info['language']}\n"
#             if country_info.get('timezone'):
#                 response += f"• Timezone: {country_info['timezone']}\n"

#             # Attractions
#             response += "\n🎯 Popular Places to Visit:\n"
#             for place in places_info[:5]:
#                 response += f"• {place['name']}"
#                 if place.get('type'):
#                     response += f" ({place['type']})"
#                 response += "\n"

#             # Travel tips
#             response += f"\n✨ Travel Tips:\n"
#             response += f"• Best time to visit: {self._get_best_time_to_visit(location_info['lat'])}\n"
#             if weather_info.get('recommendation'):
#                 response += f"• Weather recommendation: {weather_info['recommendation']}\n"

#             dispatcher.utter_message(text=response)
#             return [SlotSet("location", location)]

#         except Exception as e:
#             dispatcher.utter_message(text=f"I'm having trouble getting complete information about {location}. Please try again later.")
#             return []

#     def _get_location_details(self, location: Text) -> Dict[Text, Any]:
#         headers = {'User-Agent': 'TravelAssistantBot/1.0'}
#         url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=1"
#         response = requests.get(url, headers=headers)

#         if response.status_code == 200:
#             data = response.json()
#             if data:
#                 location_data = data[0]
#                 country_url = f"https://nominatim.openstreetmap.org/reverse?lat={location_data['lat']}&lon={location_data['lon']}&format=json"
#                 country_response = requests.get(country_url, headers=headers)
#                 country_data = country_response.json()

#                 return {
#                     'lat': float(location_data['lat']),
#                     'lng': float(location_data['lon']),
#                     'country': country_data['address'].get('country', 'Unknown'),
#                     'country_code': country_data['address'].get('country_code', '').upper(),
#                     'timezone': self._get_timezone(float(location_data['lat']), float(location_data['lon']))
#                 }
#         return None

#     def _get_weather_data(self, lat: float, lon: float) -> Dict[Text, Any]:
#         url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
#         response = requests.get(url)
#         if response.status_code == 200:
#             data = response.json()
#             temp = round(data["main"]["temp"])
#             recommendation = self._get_weather_recommendation(temp, data["weather"][0]["main"])
#             return {
#                 "description": data["weather"][0]["description"],
#                 "temperature": temp,
#                 "humidity": data["main"]["humidity"],
#                 "recommendation": recommendation
#             }
#         raise Exception("Weather API error")

#     def _get_places_data(self, lat: float, lon: float) -> List[Dict[Text, Any]]:
#         url = "https://api.foursquare.com/v3/places/search"
#         headers = {
#             "Accept": "application/json",
#             "Authorization": FOURSQUARE_PLACES_API_KEY
#         }
#         params = {
#             "ll": f"{lat},{lon}",
#             "radius": 5000,
#             "limit": 5,
#             "categories": "16000,10000,13000,12000",  # tourist attractions, arts & entertainment, food, shopping
#             "sort": "RATING"
#         }
#         try:
#             response = requests.get(url, headers=headers, params=params)
#             if response.status_code == 200:
#                 data = response.json()
#                 return [{
#                     "name": place["name"],
#                     "type": place.get("categories", [{}])[0].get("name", "Attraction")
#                 } for place in data.get("results", [])]
#         except:
#             pass
#         return [
#             {"name": "Historical Center", "type": "Sightseeing"},
#             {"name": "Local Museums", "type": "Culture"},
#             {"name": "Public Parks", "type": "Nature"},
#             {"name": "Local Markets", "type": "Shopping"},
#             {"name": "Restaurant District", "type": "Dining"}
#         ]

#     def _get_country_info(self, country_code: Text) -> Dict[Text, Any]:
#         url = f"https://restcountries.com/v3.1/alpha/{country_code}"
#         try:
#             response = requests.get(url)
#             if response.status_code == 200:
#                 data = response.json()[0]
#                 currencies = next(iter(data.get('currencies', {}).values()), {})
#                 languages = list(data.get('languages', {}).values())
#                 timezones = data.get('timezones', ['Unknown'])[0]

#                 return {
#                     "currency": f"{currencies.get('name', 'Unknown')} ({currencies.get('symbol', '')})",
#                     "language": ', '.join(languages) if languages else 'Unknown',
#                     "timezone": timezones
#                 }
#         except:
#             pass
#         return {
#             "currency": "Information not available",
#             "language": "Information not available",
#             "timezone": "Information not available"
#         }

#     def _get_timezone(self, lat: float, lon: float) -> Text:
#         try:
#             hour_offset = round(lon / 15)
#             if hour_offset > 0:
#                 return f"UTC+{hour_offset}"
#             elif hour_offset < 0:
#                 return f"UTC{hour_offset}"
#             return "UTC"
#         except:
#             return "UTC"

#     def _get_weather_recommendation(self, temp: int, condition: Text) -> Text:
#         if temp > 30:
#             return "Pack light clothes and sun protection"
#         elif temp < 10:
#             return "Pack warm clothes and layers"
#         elif condition.lower() in ['rain', 'drizzle']:
#             return "Don't forget your umbrella"
#         return "Weather is pleasant for sightseeing"

#     def _get_best_time_to_visit(self, lat: float) -> Text:
#         if lat > 0:
#             return "Spring (March-May) and Fall (September-November)"
#         else:
#             return "Spring (September-November) and Fall (March-May)"

# class ActionProvideRecommendations(Action):
#     def name(self) -> Text:
#         return "action_provide_recommendations"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Dict[Text, Any]]:
#         budget = next(tracker.get_latest_entity_values("budget"), None)
#         preferences = next(tracker.get_latest_entity_values("traveler_preferences"), None)
        
#         if not budget and not preferences:
#             dispatcher.utter_message(text="To provide better recommendations, could you tell me:\n1. Your budget range (e.g., budget, moderate, luxury)\n2. Your travel preferences (e.g., culture, nature, adventure, relaxation)")
#             return []

#         recommendations = self._get_recommendations(budget, preferences)
        
#         response = "Based on your preferences, here are some destinations you might enjoy:\n\n"
#         for rec in recommendations:
#             response += f"🌟 {rec['name']}\n"
#             response += f"• Perfect for: {rec['suitable_for']}\n"
#             response += f"• Highlights: {rec['highlights']}\n"
#             response += f"• Budget range: {rec['budget_range']}\n\n"

#         dispatcher.utter_message(text=response)
#         return []

#     def _get_recommendations(self, budget: str, preferences: str) -> List[Dict[Text, Any]]:
#         recommendations = []
        
#         if not budget:
#             budget = "moderate"
#         if not preferences:
#             preferences = "general"
            
#         if "nature" in str(preferences).lower():
#             recommendations.append({
#                 "name": "Costa Rica",
#                 "suitable_for": "Nature lovers and adventure seekers",
#                 "highlights": "Rainforests, beaches, wildlife",
#                 "budget_range": "Moderate"
#             })
        
#         if "culture" in str(preferences).lower():
#             recommendations.append({
#                 "name": "Kyoto, Japan",
#                 "suitable_for": "Cultural enthusiasts",
#                 "highlights": "Temples, traditional gardens, tea ceremonies",
#                 "budget_range": "Moderate to Luxury"
#             })
            
#         if "budget" in str(budget).lower():
#             recommendations.append({
#                 "name": "Bangkok, Thailand",
#                 "suitable_for": "Budget travelers who love culture and food",
#                 "highlights": "Temples, street food, markets",
#                 "budget_range": "Budget"
#             })
            
#         if "luxury" in str(budget).lower():
#             recommendations.append({
#                 "name": "Maldives",
#                 "suitable_for": "Luxury travelers seeking relaxation",
#                 "highlights": "Overwater villas, pristine beaches, spa retreats",
#                 "budget_range": "Luxury"
#             })

#         if not recommendations:
#             recommendations = [
#                 {
#                     "name": "Barcelona, Spain",
#                     "suitable_for": "All types of travelers",
#                     "highlights": "Architecture, beaches, cuisine",
#                     "budget_range": "Moderate"
#                 },
#                 {
#                     "name": "Bali, Indonesia",
#                     "suitable_for": "Culture and nature lovers",
#                     "highlights": "Temples, beaches, rice terraces",
#                     "budget_range": "Budget to Moderate"
#                 }
#             ]

#         return recommendations

# class ActionDefaultFallback(Action):
#     def name(self) -> str:
#         return "action_default_fallback"

#     def run(self, dispatcher, tracker, domain):
#         dispatcher.utter_message(text="I'm sorry, I didn't understand that.")
#         return []

# class ActionFacilitateBooking(Action):
#     def name(self) -> Text:
#         return "action_facilitate_booking"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Dict[Text, Any]]:
#         location = next(tracker.get_latest_entity_values("location"), None)
#         travel_season = next(tracker.get_latest_entity_values("travel_season"), None)
#         budget = next(tracker.get_latest_entity_values("budget"), None)

#         response = "I'll help you plan your trip."
#         slots_to_set = []

#         if location:
#             response += f"\n📍 Destination: {location}"
#             slots_to_set.append(SlotSet("location", location))
#         else:
#             response += "\nWhere would you like to travel to?"

#         if travel_season:
#             response += f"\n📅 Travel period: {travel_season}"
#             slots_to_set.append(SlotSet("travel_season", travel_season))
#         else:
#             response += "\nWhen would you like to travel?"

#         if budget:
#             response += f"\n💰 Budget: {budget}"
#             slots_to_set.append(SlotSet("budget", budget))
#         else:
#             response += "\nWhat's your budget for this trip?"

#         response += "\n\nI can help you with:"
#         response += "\n• Destination information and weather"
#         response += "\n• Hotel recommendations"
#         response += "\n• Activity suggestions"
#         response += "\n• Travel tips and requirements"
        
#         dispatcher.utter_message(text=response)
#         return slots_to_set

# class ActionHandleTravelDate(Action):
#     def name(self) -> Text:
#         return "action_handle_travel_date"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Dict[Text, Any]]:
#         travel_season = next(tracker.get_latest_entity_values("travel_season"), None)
#         location = tracker.get_slot("location")

#         if travel_season:
#             try:
#                 travel_date = datetime.strptime(travel_season, "%B %d").replace(year=datetime.now().year)
#                 formatted_date = travel_date.strftime("%B %d, %Y")
#                 season = self._get_season(travel_date)
#             except ValueError:
#                 formatted_date = travel_season
#                 season = travel_season

#             if location:
#                 response = f"Great! Let's plan your trip to {location} for {formatted_date}.\n"
#                 response += f"The ideal season for this location is {season}."
#                 dispatcher.utter_message(text=response)
#             else:
#                 dispatcher.utter_message(text="Please specify the location for your travel.")
#         else:
#             dispatcher.utter_message(text="Please provide your preferred travel dates.")
#         return []

#     def _get_season(self, travel_date: datetime) -> Text:
#         month = travel_date.month
#         if month in [12, 1, 2]:
#             return "Winter"
#         elif month in [3, 4, 5]:
#             return "Spring"
#         elif month in [6, 7, 8]:
#             return "Summer"
#         elif month in [9, 10, 11]:
#             return "Autumn"
#         return "Unknown season"
from typing import Text, Dict, Any, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# API keys
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
FOURSQUARE_PLACES_API_KEY = os.getenv("FOURSQUARE_PLACES_API_KEY")
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")

class ActionGreet(Action):
    def name(self) -> Text:
        return "action_greet"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_greet")
        return []


class ActionGetDestinationInfo(Action):
    def name(self) -> Text:
        return "action_get_destination_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot('location')
        if not location:
            dispatcher.utter_message(response="utter_ask_location")
            return []

        try:
            # Get location details using Nominatim (OpenStreetMap)
            location_info = self._get_location_details(location)
            if not location_info:
                dispatcher.utter_message(text=f"I couldn't find information about {location}. Could you please check the spelling or try another destination?")
                return []

            # Get weather data
            weather_info = self._get_weather_data(location_info['lat'], location_info['lng'])

            # Get places data using OpenTripMap
            places_info = self._get_places_data(location_info['lat'], location_info['lng'])

            # Get country info
            country_info = self._get_country_info(location_info['country_code'])

            # Construct comprehensive response
            response = f"📍 Information about {location}, {location_info['country']}:\n\n"

            # Weather section
            response += "🌤️ Current Weather:\n"
            response += f"• Condition: {weather_info['description'].capitalize()}\n"
            response += f"• Temperature: {weather_info['temperature']}°C\n"
            response += f"• Humidity: {weather_info['humidity']}%\n\n"

            # Country information
            response += "🗺️ Country Information:\n"
            response += f"• Currency: {country_info['currency']}\n"
            response += f"• Language: {country_info['language']}\n"
            if country_info.get('timezone'):
                response += f"• Timezone: {country_info['timezone']}\n"

            # Attractions
            response += "\n🎯 Popular Places to Visit:\n"
            for place in places_info[:5]:
                response += f"• {place['name']}"
                if place.get('type'):
                    response += f" ({place['type']})"
                response += "\n"

            # Travel tips
            response += f"\n✨ Travel Tips:\n"
            response += f"• Best time to visit: {self._get_best_time_to_visit(location_info['lat'])}\n"
            if weather_info.get('recommendation'):
                response += f"• Weather recommendation: {weather_info['recommendation']}\n"

            dispatcher.utter_message(text=response)
            return [SlotSet("location", location)]

        except Exception as e:
            dispatcher.utter_message(text=f"I'm having trouble getting complete information about {location}. Please try again later.")
            return []

    def _get_location_details(self, location: Text) -> Dict[Text, Any]:
        headers = {'User-Agent': 'TravelAssistantBot/1.0'}
        url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=1"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if data:
                location_data = data[0]
                country_url = f"https://nominatim.openstreetmap.org/reverse?lat={location_data['lat']}&lon={location_data['lon']}&format=json"
                country_response = requests.get(country_url, headers=headers)
                country_data = country_response.json()

                return {
                    'lat': float(location_data['lat']),
                    'lng': float(location_data['lon']),
                    'country': country_data['address'].get('country', 'Unknown'),
                    'country_code': country_data['address'].get('country_code', '').upper(),
                    'timezone': self._get_timezone(float(location_data['lat']), float(location_data['lon']))
                }
        return None

    def _get_weather_data(self, lat: float, lon: float) -> Dict[Text, Any]:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            temp = round(data["main"]["temp"])
            recommendation = self._get_weather_recommendation(temp, data["weather"][0]["main"])
            return {
                "description": data["weather"][0]["description"],
                "temperature": temp,
                "humidity": data["main"]["humidity"],
                "recommendation": recommendation
            }
        raise Exception("Weather API error")

    def _get_places_data(self, lat: float, lon: float) -> List[Dict[Text, Any]]:
        url = "https://api.foursquare.com/v3/places/search"
        headers = {
            "Accept": "application/json",
            "Authorization": FOURSQUARE_PLACES_API_KEY
        }
        params = {
            "ll": f"{lat},{lon}",
            "radius": 5000,
            "limit": 5,
            "categories": "16000,10000,13000,12000",  # tourist attractions, arts & entertainment, food, shopping
            "sort": "RATING"
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                return [{
                    "name": place["name"],
                    "type": place.get("categories", [{}])[0].get("name", "Attraction")
                } for place in data.get("results", [])]
        except:
            pass
        return [
            {"name": "Historical Center", "type": "Sightseeing"},
            {"name": "Local Museums", "type": "Culture"},
            {"name": "Public Parks", "type": "Nature"},
            {"name": "Local Markets", "type": "Shopping"},
            {"name": "Restaurant District", "type": "Dining"}
        ]

    def _get_country_info(self, country_code: Text) -> Dict[Text, Any]:
        url = f"https://restcountries.com/v3.1/alpha/{country_code}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()[0]
                currencies = next(iter(data.get('currencies', {}).values()), {})
                languages = list(data.get('languages', {}).values())
                timezones = data.get('timezones', ['Unknown'])[0]

                return {
                    "currency": f"{currencies.get('name', 'Unknown')} ({currencies.get('symbol', '')})",
                    "language": ', '.join(languages) if languages else 'Unknown',
                    "timezone": timezones
                }
        except:
            pass
        return {
            "currency": "Information not available",
            "language": "Information not available",
            "timezone": "Information not available"
        }

    def _get_timezone(self, lat: float, lon: float) -> Text:
        try:
            hour_offset = round(lon / 15)
            if hour_offset > 0:
                return f"UTC+{hour_offset}"
            elif hour_offset < 0:
                return f"UTC{hour_offset}"
            return "UTC"
        except:
            return "UTC"

    def _get_weather_recommendation(self, temp: int, condition: Text) -> Text:
        if temp > 30:
            return "Pack light clothes and sun protection"
        elif temp < 10:
            return "Pack warm clothes and layers"
        elif condition.lower() in ['rain', 'drizzle']:
            return "Don't forget your umbrella"
        return "Weather is pleasant for sightseeing"

    def _get_best_time_to_visit(self, lat: float) -> Text:
        if lat > 0:
            return "Spring (March-May) and Fall (September-November)"
        else:
            return "Spring (September-November) and Fall (March-May)"

class ActionProvideRecommendations(Action):
    def name(self) -> Text:
        return "action_provide_recommendations"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        budget = tracker.get_slot('budget')
        travel_style = tracker.get_slot('travel_style')
        
        if not budget and not travel_style:
            dispatcher.utter_message(response="utter_ask_preferences")
            dispatcher.utter_message(response="utter_ask_budget")
            return []

        recommendations = self._get_recommendations(budget, travel_style)
        
        response = "Based on your preferences, here are some destinations you might enjoy:\n\n"
        for rec in recommendations:
            response += f"🌟 {rec['name']}\n"
            response += f"• Perfect for: {rec['suitable_for']}\n"
            response += f"• Highlights: {rec['highlights']}\n"
            response += f"• Budget range: {rec['budget_range']}\n\n"

        dispatcher.utter_message(text=response)
        return []

    def _get_recommendations(self, budget: Text, travel_style: Text) -> List[Dict[Text, Any]]:
        # Add your recommendation logic here
        return [
            {
                'name': 'Paris',
                'suitable_for': 'Culture, Romance',
                'highlights': 'Eiffel Tower, Louvre, Seine River Cruise',
                'budget_range': 'Moderate to Luxury'
            },
            {
                'name': 'Bali',
                'suitable_for': 'Relaxation, Adventure',
                'highlights': 'Beaches, Temples, Rice Terraces',
                'budget_range': 'Budget to Moderate'
            },
            {
                'name': 'New York City',
                'suitable_for': 'Culture, Food, Shopping',
                'highlights': 'Times Square, Central Park, Broadway',
                'budget_range': 'Moderate to Luxury'
            }
        ]


class ActionFacilitateBooking(Action):
    def name(self) -> Text:
        return "action_facilitate_booking"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        origin = tracker.get_slot("origin")
        destination = tracker.get_slot("destination")
        travel_date = tracker.get_slot("travel_date")

        if not origin or not destination or not travel_date:
            dispatcher.utter_message(response="utter_ask_origin")
            dispatcher.utter_message(response="utter_ask_destination")
            dispatcher.utter_message(response="utter_ask_travel_date")
            return []

        flights = search_flights(origin, destination, travel_date)
        display_flights(dispatcher, flights)

        # Add additional booking logic here
        dispatcher.utter_message(text="Okay, let's proceed with booking your flight.")
        return [SlotSet("origin", origin), SlotSet("destination", destination), SlotSet("travel_date", travel_date)]

def search_flights(origin: str, destination: str, travel_date: str) -> List[Dict[str, str]]:
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {
        "Authorization": f"Bearer {get_amadeus_access_token()}"
    }
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": travel_date,
        "currency": "GBP",
        "adults": 1,
        "max": 10
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    flights = []
    for offer in data["data"]:
        for itinerary in offer["itineraries"]:
            flight = {
                "airline": itinerary["segments"][0]["operating"]["carrierCode"],
                "departure": itinerary["segments"][0]["departure"]["iataCode"],
                "arrival": itinerary["segments"][-1]["arrival"]["iataCode"],
                "departure_time": itinerary["segments"][0]["departure"]["at"],
                "arrival_time": itinerary["segments"][-1]["arrival"]["at"],
                "price": offer["price"]["total"]
            }
            flights.append(flight)

    return flights

def get_amadeus_access_token() -> str:
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_CLIENT_ID,
        "client_secret": AMADEUS_CLIENT_SECRET
    }
    response = requests.post(url, data=payload)
    data = response.json()
    return data["access_token"]

def display_flights(dispatcher: CollectingDispatcher, flights: List[Dict[str, str]]):
    if not flights:
        dispatcher.utter_message(text="No flights found.")
        return

    for flight in flights:
        dispatcher.utter_message(text=f"Airline: {flight['airline']}")
        dispatcher.utter_message(text=f"Departure: {flight['departure']} ({flight['departure_time']})")
        dispatcher.utter_message(text=f"Arrival: {flight['arrival']} ({flight['arrival_time']})")
        dispatcher.utter_message(text=f"Price: {flight['price']} GBP")
        dispatcher.utter_message(text="")


class ActionHandleTravelDate(Action):
    def name(self) -> Text:
        return "action_handle_travel_date"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        travel_season = tracker.get_slot('travel_season')
        if not travel_season:
            dispatcher.utter_message(response="utter_ask_dates")
            return []

        # Add your travel date handling logic here
        dispatcher.utter_message(text=f"Got it, you'd like to travel in {travel_season}.")
        return [SlotSet("travel_season", travel_season)]

class ActionCompleteBooking(Action):
    def name(self) -> Text:
        return "action_complete_booking"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot('location')
        travel_season = tracker.get_slot('travel_season')
        budget = tracker.get_slot('budget')

        if not location or not travel_season or not budget:
            dispatcher.utter_message(response="utter_ask_location")
            dispatcher.utter_message(response="utter_ask_dates")
            dispatcher.utter_message(response="utter_ask_budget")
            return []

        # Add your booking completion logic here
        dispatcher.utter_message(text=f"Awesome! I've booked your trip to {location} for {travel_season} within your budget of ${budget}.")
        return []

class ActionSuggestActivities(Action):
    def name(self) -> Text:
        return "action_suggest_activities"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot('location')
        if not location:
            dispatcher.utter_message(response="utter_ask_location")
            return []

        # Add your activity suggestion logic here
        dispatcher.utter_message(text=f"Here are some popular activities to do in {location}:")
        dispatcher.utter_message(text="- Visit the iconic landmarks\n- Explore the local food scene\n- Enjoy the natural attractions\n- Experience the vibrant culture")
        return []

class ActionGetTransportationInfo(Action):
    def name(self) -> Text:
        return "action_get_transportation_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot('location')
        if not location:
            dispatcher.utter_message(response="utter_ask_location")
            return []

        # Add your transportation information logic here
        dispatcher.utter_message(text=f"Here are some transportation options for getting around {location}:")
        dispatcher.utter_message(text="- Public transportation (buses, metro, trams)\n- Taxis and ride-sharing services\n- Rental cars\n- Walking and biking")
        return []

class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Sorry, I didn't understand that. Could you please rephrase your request?")
        return []