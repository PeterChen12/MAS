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

# Function to extract information using GPT-4
def extract_information_from_text(user_message):
    prompt = (
        "Extract the following information from the user's message if available: "
        "1. Vehicle's year, 2. Vehicle's make, 3. Vehicle's model, "
        "4. First name, 5. Last name, 6. Email address, 7. Phone number. "
        "If any of this information is missing, return the missing items as 'Not provided'. "
        "Here is the message: " + user_message
    )
    
    conversation = [
        {"role": "system", "content": "You are an AI assistant."},
        {"role": "user", "content": prompt}
    ]
    response = chat_with_gpt4(conversation)
    
    # Parse the response into a dictionary
    lines = response.strip().split('\n')
    info_dict = {}
    for line in lines:
        if ": " in line:
            key, value = line.split(": ", 1)
            info_dict[key.strip()] = value.strip()
    
    # Ensure all required keys are present, if not, set to 'Not provided'
    required_keys = ["Vehicle's year", "Vehicle's make", "Vehicle's model", "First name", "Last name", "Email address", "Phone number"]
    for key in required_keys:
        if key not in info_dict:
            info_dict[key] = 'Not provided'
    
    return info_dict

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
    
    # Extract the user response to get necessary details
    extracted_info = extract_information_from_text(user_message)
    print("Extracted information:", extracted_info)  # Debugging print

    # Check if all necessary details are provided
    if all(key in extracted_info and extracted_info[key] != 'Not provided' for key in ["Vehicle's year", "Vehicle's make", "Vehicle's model", "First name", "Last name", "Email address", "Phone number"]):
        save_to_csv(extracted_info)
    else:
        print("Missing some required information.")
    
    return jsonify({'message': bot_response})

# Save the parsed data to a CSV file
def save_to_csv(details):
    file_exists = os.path.isfile('appointments.csv')
    with open('appointments.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Vehicle Year", "Vehicle Make", "Vehicle Model", "Reason for Visit", "First Name", "Last Name", "Email", "Phone Number"])
        
        # Debugging print to verify data being written to CSV
        print("Writing data to CSV:", details)
        
        writer.writerow([
            details.get("Vehicle's year", "Not provided"),
            details.get("Vehicle's make", "Not provided"),
            details.get("Vehicle's model", "Not provided"),
            "Oil change",  # Assuming reason for visit is oil change based on the interaction
            details.get("First name", "Not provided"),
            details.get("Last name", "Not provided"),
            details.get("Email address", "Not provided"),
            details.get("Phone number", "Not provided")
        ])

if __name__ == '__main__':
    app.run(debug=True)
