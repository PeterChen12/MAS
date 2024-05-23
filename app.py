# app.py
import os
import openai
import csv
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Use the API key with OpenAI
openai.api_key = api_key

app = Flask(__name__)

# Function to handle the interaction with GPT-4
def chat_with_gpt4(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return response['choices'][0]['message']['content']

# Initialize the conversation
conversation = [
    {"role": "system", "content": "You are a customer service representative for HongQi Automotive repair shop. Your task is to get the customer's car information (year, make, model, reason for the visit) and the customer's personal information (first name, last name, email, phone number) and make an appointment for any time between 9am to 4pm."}
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    conversation.append({"role": "user", "content": user_message})
    bot_response = chat_with_gpt4(conversation)
    conversation.append({"role": "assistant", "content": bot_response})
    
    # Extract and save data if user provides all necessary details
    if "First Name" in user_message and "Last Name" in user_message and "Email" in user_message and "Phone Number" in user_message:
        parsed_data = parse_user_input(user_message)
        save_to_csv(parsed_data)
    
    return jsonify({'message': bot_response})

# Parse the user input (assuming the format is known)
def parse_user_input(user_input):
    lines = user_input.strip().split("\n")
    car_year = lines[0].split(": ")[1]
    car_make = lines[1].split(": ")[1]
    car_model = lines[2].split(": ")[1]
    reason = lines[3].split(": ")[1]
    first_name = lines[5].split(": ")[1]
    last_name = lines[6].split(": ")[1]
    email = lines[7].split(": ")[1]
    phone_number = lines[8].split(": ")[1]
    return [car_year, car_make, car_model, reason, first_name, last_name, email, phone_number]

# Save the parsed data to a CSV file
def save_to_csv(data):
    file_exists = os.path.isfile('appointments.csv')
    with open('appointments.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Year", "Make", "Model", "Reason for the visit", "First Name", "Last Name", "Email", "Phone Number"])
        writer.writerow(data)

if __name__ == '__main__':
    app.run(debug=True)
