import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import threading
import customtkinter as ctk
import tkinter as tk  # Import tkinter for standard GUI components
from calculation import extract_calculation, calculate  # Importing from the new calculation module
from browser_manager import close_browser  # Importing the close_browser function
from assistant_logic import speak, takeCommand  # Importing assistant logic functions
from weather_manager import get_weather  # Importing the weather manager
import pyjokes  # Importing the pyjokes module for jokes
from news_manager import get_news, country_code_mapping  # Importing the news manager and country code mapping
from PIL import ImageGrab  # Importing ImageGrab for taking screenshots
import time  # Importing time to generate unique filenames
import os  # Import os to use for opening the calculator
import socket  # Import socket to get the IP address
import openai  # Import OpenAI for ChatGPT functionality

# Initialize text-to-speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# Set your OpenAI API key
openai.api_key = "#"  # Replace with your actual OpenAI API key

class AssistantWindow:
    def __init__(self):
        self.window = None
        self.loading_label = None  # Initialize loading_label
        self.setup_window()

    def setup_window(self):
        self.window = ctk.CTk()
        self.window.title("Nova AI Assistant")
        self.window.geometry("600x700")
        self.window.resizable(True, True)  # Allow resizing
        self.window.minsize(400, 500)  # Set minimum size
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main frame with a soothing background color
        self.main_frame = ctk.CTkFrame(self.window, fg_color="#1E1E1E")  # Darker background for better eye comfort
        self.main_frame.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Create title label with a new font and color
        self.title_label = ctk.CTkLabel(self.main_frame, text="Nova AI Assistant", font=("Helvetica", 24, "bold"), text_color="#00BFFF")  # Softer blue color
        self.title_label.pack(pady=10)

        # Create loading label
        self.loading_label = ctk.CTkLabel(self.main_frame, text="", font=("Helvetica", 12), text_color="#FFFFFF")
        self.loading_label.pack(pady=10)

        # Create chat display area with custom styling
        self.text_area = ctk.CTkTextbox(self.main_frame, 
                                          width=600, 
                                          height=400,
                                          font=("Arial", 12),
                                          corner_radius=10,
                                          fg_color="#F0F0F0",  # Light gray background for text area
                                          text_color="#000000")  # Black text for contrast
        self.text_area.pack(padx=10, pady=10, fill='both', expand=True)

        # Create input box for manual input
        self.input_var = tk.StringVar()
        self.input_entry = ctk.CTkEntry(self.main_frame, textvariable=self.input_var, width=400, corner_radius=10, fg_color="#FFFFFF", text_color="#000000")  # White background for input
        self.input_entry.pack(pady=10)

        # Create button to submit manual input
        self.submit_button = ctk.CTkButton(self.main_frame, text="Submit", command=self.submit_input, corner_radius=10, fg_color="#4CAF50", text_color="#FFFFFF")  # Green button
        self.submit_button.pack(pady=10)

        # Create button to trigger voice input
        self.voice_button = ctk.CTkButton(self.main_frame, text="Speak", command=self.start_voice_input, corner_radius=10, fg_color="#2196F3", text_color="#FFFFFF")  # Blue button
        self.voice_button.pack(pady=10)

        # Create status label with a different color
        self.status_label = ctk.CTkLabel(self.main_frame, 
                                           text="Nova is ready...",
                                           font=("Helvetica", 14),
                                           text_color="#4CAF50")
        self.status_label.pack(pady=10)

    def submit_input(self):
        """Process the input from the entry box."""
        query = self.input_var.get()
        self.input_var.set("")  # Clear the input box
        process_query(query)  # Process the query

    def start_voice_input(self):
        """Start listening for voice input."""
        query = takeCommand()  # Get input from the microphone
        process_query(query)  # Process the query

    def show(self):
        """Show the assistant window"""
        if not self.window:
            self.setup_window()
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()

    def hide(self):
        """Hide the assistant window"""
        if self.window:
            self.window.withdraw()

    def update_text(self, message, sender="Nova"):
        if not self.window:
            return
        tag = "assistant" if sender == "Nova" else "user"
        self.text_area.tag_config("assistant", foreground="#00BFFF")  # Softer blue for assistant
        self.text_area.tag_config("user", foreground="#4CAF50")  # Green for user
        
        self.text_area.insert("end", f"\n{sender}: ", tag)
        self.text_area.insert("end", f"{message}\n")
        self.text_area.see("end")
        
    def start(self):
        if self.window:
            self.window.mainloop()

    def show_functionalities(self):
        functionalities = (
            "Here are some things I can do for you:\n"
            "1. Search Wikipedia            8. Tell the current time\n"
            "2. Open YouTube                9. Take a screenshot\n"
            "3. Play a video on YouTube     10. Close YouTube\n"
            "4. Get the latest news         11. Close Google\n"
            "5. Provide weather information  12. Exit the assistant\n"
            "6. Tell a joke                 13. Sleep mode\n"
            "7. Perform calculations         14. Open google calculator\n"
       
        )
        self.update_text(functionalities)

# Create global instance
assistant_window = None

def chat_with_gpt(user_input):
    """Function to interact with ChatGPT."""
    print(f"User Input: {user_input}")  # Debugging output
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can use "gpt-4" if you have access
            messages=[
                {"role": "user", "content": user_input}
            ]
        )
        print(f"ChatGPT Response: {response}")  # Debugging output
        return response['choices'][0]['message']['content']
    except openai.error.AuthenticationError:
        return "Authentication failed. Please check your API key."
    except openai.error.InvalidRequestError as e:
        return f"Invalid request: {e.user_message}"
    except openai.error.RateLimitError:
        return "Rate limit exceeded. Please try again later."
    except Exception as e:
        print(f"Error communicating with OpenAI: {e}")  # Debugging output
        return "Sorry, I couldn't get a response from ChatGPT."

def process_query(query):
    """Process the query from either voice or keyboard input."""
    global gui_active
    if query == "None":
        return

    # Show loading indicator
    assistant_window.loading_label.configure(text="Processing...")

    if not gui_active and ('start' in query or 'open' in query or 'wake up' in query or 'nova' in query):
        gui_active = True
        assistant_window.show()
        speak("Hello! I'm Nova, How can I help you?")
        assistant_window.show_functionalities()  # Show functionalities
        return

    if gui_active:
        # Check if the user wants to interact with ChatGPT
        if 'chat gpt' in query or 'chat with gpt' in query:
            user_input = query.replace("chat gpt", "").replace("chat with gpt", "").strip()
            if user_input:
                gpt_response = chat_with_gpt(user_input)
                assistant_window.update_text(f"ChatGPT: {gpt_response}")
                speak(gpt_response)
            else:
                speak("Please provide a question or topic to discuss with ChatGPT.")
                assistant_window.update_text("Please provide a question or topic to discuss with ChatGPT.")
        
        # Check for news command
        if 'news' in query:
            speak("Which country do you want news from? ")
            country_name = takeCommand()  # Get country name from user
            if country_name == "None":  # If voice input is not given, check for typed input
                country_name = query  # Use the typed input instead
            country_code = country_code_mapping.get(country_name.lower())  # Get country code from mapping
            if country_code:  # Ensure country code is found
                api_key = "b95b7c85a8ce4b5bae8b43944dd3b0aa"  # Replace with your News API key
                news_articles = get_news(api_key, country_code)  # Fetch news by country
                if news_articles:
                    news_summary = "\n".join(news_articles)
                    speak(f"Here are the latest news headlines from {country_name}:")
                    assistant_window.update_text(f"Latest News from {country_name}:\n{news_summary}")
                else:
                    speak("Sorry, I couldn't fetch the news at the moment. Please check your API key or try again later.")
            else:
                speak("I didn't recognize that country name. Please try again.")
        
       # Check for related news command
        elif 'related news about' in query:
            topic = query.replace("related news about", "").strip()  # Extract the topic from the query
            api_key = "b95b7c85a8ce4b5bae8b43944dd3b0aa"  # Replace with your News API key
            news_articles = get_news(api_key, None, topic)  # Fetch related news
            if news_articles:
                news_summary = "\n".join(news_articles)
                speak(f"Here are the latest news headlines related to {topic}:")
                assistant_window.update_text(f"Latest News about {topic}:\n{news_summary}")
            else:
                speak("Sorry, I couldn't fetch the related news at the moment. Please check your API key or try again later.")
        
        # Check for Google search command
        elif 'search for' in query or 'on google' in query:
            search_query = query.replace("search for", "").replace("on google", "").strip()  # Extract the search term
            if search_query:
                search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"  # Construct the search URL
                webbrowser.open(search_url)  # Open the search URL in the default web browser
                speak(f"Opening Google for {search_query}.")
                assistant_window.update_text(f"Opening Google for {search_query}.")
            else:
                speak("Please specify what you want to search for on Google.")
        
        # Check for calculator command
        elif 'calculator' in query or 'open calculator' in query:
            if os.name == 'nt':  # For Windows
                os.system('calc')  # Open Windows Calculator
            elif os.name == 'posix':  # For macOS
                os.system('open -a Calculator')  # Open macOS Calculator
            else:
                speak("Sorry, I cannot open the calculator on this operating system.")
            speak("Opening calculator.")
            assistant_window.update_text("Opening calculator.")
        
        # Check for YouTube play command
        if 'play' in query and 'youtube' in query:
            # Extract the video title from the query
            video_title = query.replace("play", "").replace("youtube", "").strip()
            if video_title:
                # Construct the YouTube search URL
                search_url = f"https://www.youtube.com/results?search_query={video_title.replace(' ', '+')}"
                webbrowser.open(search_url)  # Open the search URL in the default web browser
                speak(f"Playing {video_title} on YouTube.")
                assistant_window.update_text(f"Playing {video_title} on YouTube.")
            else:
                speak("Please specify what you want to play on YouTube.")
                assistant_window.update_text("Please specify what you want to play on YouTube.")
        
        # Check if the query contains the word 'wikipedia'
        if 'wikipedia' in query or 'about' in query:
            # Inform the user that a Wikipedia search is starting
            speak('Searching Wikipedia...')
            # Remove the word 'wikipedia' from the query to get the actual search term
            query = query.replace("wikipedia", "")
            # Fetch a summary from Wikipedia based on the modified query
            results = wikipedia.summary(query, sentences=2)
            # Inform the user that the results are coming from Wikipedia
            speak("According to Wikipedia")
            # Update the assistant window with the fetched results
            assistant_window.update_text(f"Result: {results}")
            # Speak out the results to the user
            speak(results)

            
        
        # Weather functionality
        elif 'weather' in query:
            speak("Which city?")
            city = takeCommand()  # Get city name from user
            if city != "None":
                api_key = "29671cdf7262218be46f54a04aea3b20"  # Replace with your OpenWeatherMap API key
                weather_info = get_weather(city, api_key)
                if weather_info:
                    temp, humidity, description = weather_info
                    temp = f"{temp:.2f}"  # Format temperature to show 2 decimal places
                    speak(f"The temperature is {temp} degrees Celsius, humidity is {humidity} percent, and the weather is {description}.")
                    assistant_window.update_text(f"Weather in {city}: {temp}°C, {humidity}%, {description}")
                else:
                    speak("Sorry, I couldn't find the weather for that city.")
        if 'open youtube' in query:
            webbrowser.open("youtube.com")
        elif 'open google' in query:
            webbrowser.open("google.com")
        elif 'close youtube' in query:
            if close_browser('youtube'):
                speak("Closed YouTube")
            else:
                speak("YouTube is not open or I couldn't close it")
        elif 'close google' in query:
            if close_browser('google'):
                speak("Closed Google")
            else:
                speak("Google is not open or I couldn't close it")
        elif any(word in query for word in ['calculate', 'compute', 'what is']):
            calc_text = extract_calculation(query)
            result = calculate(calc_text)
            speak(result)
            assistant_window.update_text(f"Calculation: {calc_text}\n{result}")
        elif 'time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"The time is {strTime}")
            assistant_window.update_text(f"Time is : {strTime}\n")
        elif 'joke' in query:
            speak(pyjokes.get_joke())
            assistant_window.update_text(pyjokes.get_joke())
        elif 'exit' in query:
            speak("Thanks for using me. Have a good day!")
            assistant_window.window.quit()
            return
        elif 'sleep' in query or 'goodbye' in query:
            speak("Going to sleep mode. Say 'start' when you need me!")
            assistant_window.hide()
            gui_active = False
            return
        # Check for screenshot command
        if 'screenshot' in query:
            timestamp = time.strftime("%Y%m%d_%H%M%S")  # Create a timestamp
            filename = f"screenshot_{timestamp}.png"  # Generate a unique filename
            screenshot = ImageGrab.grab()  # Capture the current screen
            screenshot.save(filename)  # Save the screenshot with the unique filename
            speak(f"Screenshot taken Successfully")
            assistant_window.update_text(f"Screenshot taken and saved as {filename}.")

        # Check for IP address command
        elif 'ip address' in query or 'my ip' in query:
            ip_address = socket.gethostbyname(socket.gethostname())  # Get the IP address
            speak(f"Your IP address is {ip_address}.")
            assistant_window.update_text(f"Your IP address is: {ip_address}")

        # Check for day command
        elif 'day' in query or 'what day is it' in query:
            today = datetime.datetime.now().strftime("%A")  # Get the current day
            speak(f"Today is {today}.")
            assistant_window.update_text(f"Today is: {today}")

    # After processing, hide the loading indicator
    assistant_window.loading_label.configure(text="") 

def assistant_loop():
    global gui_active
    gui_active = False
    while True:
        # Wait for the user to wake up the assistant
        query = takeCommand()  # Get input from the microphone
        process_query(query)  # Process the query

def main():
    global assistant_window
    assistant_window = AssistantWindow()
    assistant_window.hide()  # Hide window initially
    
    print("Say 'start' or 'open' to start the GUI assistant...")
    
    # Start the assistant logic in a separate thread
    threading.Thread(target=assistant_loop, daemon=True).start()
    
    # Run the GUI main loop in the main thread
    assistant_window.start()

if __name__ == "__main__":
    main() 