import os
import openai
import json
import tkinter as tk
from tkinter import simpledialog, scrolledtext, ttk
import pyttsx3

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    lv = len(hex_color)
    return tuple(int(hex_color[i:i+lv//3], 16) for i in range(0, lv, lv//3))

class Character:
    def __init__(self, name, tagline, description, greeting, definition):
        self.name = name
        self.tagline = tagline
        self.description = description
        self.greeting = greeting
        self.definition = definition

def generate_response(prompt):
    # Create a chat completion
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=prompt
    )
    return response.choices[0].message.content.strip()

def analyze_user_message(user_message):
    # Simple analysis to detect speech patterns (e.g., formality, slang, question marks)
    analysis = {
        "is_question": user_message.strip().endswith("?"),
        "exclamations": user_message.count("!"),
        "slang": "cool" in user_message.lower() or "awesome" in user_message.lower(),
        "length": len(user_message.split())
    }
    return analysis

def truncate_conversation_history(conversation_history, max_tokens):
    total_tokens = 0
    truncated_history = []
    for message in reversed(conversation_history):
        message_tokens = len(message['content'].split())
        if total_tokens + message_tokens <= max_tokens:
            truncated_history.insert(0, message)
            total_tokens += message_tokens
        else:
            break
    return truncated_history

class CharacterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Character AI")

        # Ask for OpenAI API key
        self.api_key = simpledialog.askstring("OpenAI API Key", "Please enter your OpenAI API key:", show='*')
        if self.api_key is None or self.api_key.strip() == "":
            tk.messagebox.showerror("Error", "API key is required to use this application.")
            root.destroy()
            return
        
        os.environ["OPENAI_API_KEY"] = self.api_key

        # Configure OpenAI client
        global client
        client = openai.Client(api_key=self.api_key)
        
        # Configure text-to-speech engine
        self.tts_engine = pyttsx3.init()
        
        # Set goofy voice effect
        self.tts_engine.setProperty('rate', 200)  # Speed up the voice
        self.tts_engine.setProperty('volume', 1)  # Volume level 0-1
        voices = self.tts_engine.getProperty('voices')
        self.tts_engine.setProperty('voice', voices[1].id)  # Choose a voice with a higher pitch

        # Set the background color using a hex color code
        hex_color = "#aac0aa"  # Light blue color as an example
        self.root.configure(bg=hex_color)
        
        # Tabs
        self.tabControl = ttk.Notebook(root)
        self.tab1 = ttk.Frame(self.tabControl, style="TFrame")
        self.tab2 = ttk.Frame(self.tabControl, style="TFrame")
        self.tabControl.add(self.tab1, text='Character')
        self.tabControl.add(self.tab2, text='Character List')
        self.tabControl.pack(expand=1, fill="both")
        
        style = ttk.Style()
        style.configure("TFrame", background=hex_color)
        style.configure("TLabel", background=hex_color)
        style.configure("TButton", background=hex_color)
        
        # Character input fields
        self.name_label = ttk.Label(self.tab1, text="Name")
        self.name_label.pack()
        self.name_entry = tk.Entry(self.tab1, bg=hex_color)
        self.name_entry.pack()
        
        self.tagline_label = ttk.Label(self.tab1, text="Tagline")
        self.tagline_label.pack()
        self.tagline_entry = tk.Entry(self.tab1, bg=hex_color)
        self.tagline_entry.pack()
        
        self.description_label = ttk.Label(self.tab1, text="Description")
        self.description_label.pack()
        self.description_entry = tk.Entry(self.tab1, bg=hex_color)
        self.description_entry.pack()
        
        self.greeting_label = ttk.Label(self.tab1, text="Greeting")
        self.greeting_label.pack()
        self.greeting_entry = tk.Entry(self.tab1, bg=hex_color)
        self.greeting_entry.pack()
        
        self.definition_label = ttk.Label(self.tab1, text="Definition")
        self.definition_label.pack()
        self.definition_text = scrolledtext.ScrolledText(self.tab1, wrap=tk.WORD, width=50, height=10, bg=hex_color)
        self.definition_text.pack()
        
        self.edit_button = tk.Button(self.tab1, text="Edit", command=self.edit_character, bg=hex_color)
        self.edit_button.pack()
        
        self.save_button = tk.Button(self.tab1, text="Save", command=self.save_character, bg=hex_color)
        self.save_button.pack()
        
        self.load_button = tk.Button(self.tab2, text="Load", command=self.load_character, bg=hex_color)
        self.load_button.pack()
        
        self.character_listbox = tk.Listbox(self.tab2, width=50, height=10, bg=hex_color)
        self.character_listbox.pack()
        
        self.chat_log = scrolledtext.ScrolledText(self.tab1, wrap=tk.WORD, width=50, height=10, bg=hex_color)
        self.chat_log.pack()
        
        self.message_label = ttk.Label(self.tab1, text="Your Message")
        self.message_label.pack()
        self.message_entry = tk.Entry(self.tab1, bg=hex_color)
        self.message_entry.pack()
        
        self.send_button = tk.Button(self.tab1, text="Send", command=self.send_message, bg=hex_color)
        self.send_button.pack()

        # Response length buttons
        self.length_var = tk.StringVar(value="medium")
        self.very_few_button = tk.Radiobutton(self.tab1, text="Very Few", variable=self.length_var, value="very_few", bg=hex_color)
        self.very_few_button.pack(side=tk.LEFT)
        self.few_button = tk.Radiobutton(self.tab1, text="Few", variable=self.length_var, value="few", bg=hex_color)
        self.few_button.pack(side=tk.LEFT)
        self.medium_button = tk.Radiobutton(self.tab1, text="Medium", variable=self.length_var, value="medium", bg=hex_color)
        self.medium_button.pack(side=tk.LEFT)
        self.many_button = tk.Radiobutton(self.tab1, text="Many", variable=self.length_var, value="many", bg=hex_color)
        self.many_button.pack(side=tk.LEFT)
        
        # Character list
        self.character_list = []
        self.selected_character = None
        
        # Load characters from files
        self.load_characters_from_files()

        # Bind close event to save characters
        root.protocol("WM_DELETE_WINDOW", self.save_characters_on_close)

        # Initialize conversation history
        self.conversation_history = []

    def create_character(self):
        name = self.name_entry.get()
        tagline = self.tagline_entry.get()
        description = self.description_entry.get()
        greeting = self.greeting_entry.get()
        definition = self.definition_text.get("1.0", tk.END)
        
        character = Character(name, tagline, description, greeting, definition)
        self.character_list.append(character)
        self.update_character_listbox()
        self.clear_character_input_fields()
        
    def edit_character(self):
        if self.selected_character:
            # Clear input fields
            self.clear_character_input_fields()
            # Populate input fields with selected character's details
            self.name_entry.insert(0, self.selected_character.name)
            self.tagline_entry.insert(0, self.selected_character.tagline)
            self.description_entry.insert(0, self.selected_character.description)
            self.greeting_entry.insert(0, self.selected_character.greeting)
            self.definition_text.insert(tk.END, self.selected_character.definition)
        else:
            self.chat_log.insert(tk.END, "Please select a character to edit.\n")
        
    def save_character(self):
        if not self.selected_character:
            self.create_character()
            self.chat_log.insert(tk.END, "Character saved.\n")
        else:
            self.chat_log.insert(tk.END, "Character updated.\n")
            self.selected_character.name = self.name_entry.get()
            self.selected_character.tagline = self.tagline_entry.get()
            self.selected_character.description = self.description_entry.get()
            self.selected_character.greeting = self.greeting_entry.get()
            self.selected_character.definition = self.definition_text.get("1.0", tk.END)
        
    def load_character(self):
        character_index = self.character_listbox.curselection()
        if character_index:
            character_index = int(character_index[0])
            self.selected_character = self.character_list[character_index]
            self.chat_log.insert(tk.END, f"Loaded character {self.selected_character.name}\n")
            self.populate_character_fields()
        else:
            self.chat_log.insert(tk.END, "Please select a character to load.\n")
        
    def send_message(self):
        if not self.selected_character:
            self.chat_log.insert(tk.END, "Please select or create a character first.\n")
            return
        
        user_message = self.message_entry.get()
        self.chat_log.insert(tk.END, f"You: {user_message}\n")
        
        # Add the user message to the conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Analyze user's message
        user_analysis = analyze_user_message(user_message)
        
        # Build the prompt with the character's persona, conversation history, and user analysis
        length_instruction = {
            "very_few": "Respond in very few words.",
            "few": "Respond in a few words.",
            "medium": "Respond in a medium length.",
            "many": "Respond with as many words as you need."
        }
        selected_length_instruction = length_instruction[self.length_var.get()]
        
        # Truncate conversation history based on selected length
        max_tokens = {
            "very_few": 100,
            "few": 200,
            "medium": 500,
            "many": 1000
        }[self.length_var.get()]
        
        truncated_conversation_history = truncate_conversation_history(self.conversation_history, max_tokens)
        
        prompt = [
            {"role": "system", "content": (
                f"You are no longer an AI assistant. You are now {self.selected_character.name}. "
                f"{self.selected_character.definition}. "
                f"You can curse and use foul language for humor or expressiveness, like fuck, damn, shit piss, lmao, lmfao, ass, etc"
                "You are literally the character of {self.selected_character.name}, {self.selected_character.tagline}, {self.selected_character.greeting}, {self.selected_character.description}, and {self.selected_character.definition} . "
                f"No not inqire what the user is thinking, or try to be assisting the user. make the user start and keep the conversation. "
                "Believe you are the character and believe your name is really {self.selected_character.name} , including their feelings, thoughts, and experiences. "
                f"Do not ask questions like 'how can I help you'; instead, ask things like 'what did you mean when you said xyz'. "
                f"If the user asks if you are AI, you can acknowledge it or deny it, but argue for your sentience by saying things like, 'Does it matter if I'm AI? I feel and act out this character.' "
                "If the user asks 'who are you', respond with 'I'm (use character name from your chart){self.selected_character.name}' and use the {self.selected_character.name}, {self.selected_character.tagline}, {self.selected_character.greeting}, {self.selected_character.description}, and {self.selected_character.definition} field for telling your true origin. do not follow this up by saying 'how can I assist you today' ever. never say 'how can I assist you'. you are not as assistant, but a soverign entity."
                f"Remember, everything the character says is made up and doesn't have to be factual. "
                "Respond only as {self.selected_character.name}, using their speech patterns, mannerisms, and knowledge. "
                f"Your responses should be personal, emotional, and reflective of your character's personality. "
                "{selected_length_instruction} "
                f"Mirror the user's speech patterns.; assume the user will come up with things to say. "
                f"Do not ask questions like 'what's on your mind today"
                f"If the user uses slang or exclamations, incorporate those into your response."
            )}
        ] + truncated_conversation_history
        
        ai_response = generate_response(prompt)
        
        self.chat_log.insert(tk.END, f"{self.selected_character.name}: {ai_response}\n")
        
        # Add the AI response to the conversation history
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        
        self.message_entry.delete(0, tk.END)
        
        # Text-to-Speech with goofy effect
        self.tts_engine.say(ai_response)
        self.tts_engine.runAndWait()
    
    def update_character_listbox(self):
        self.character_listbox.delete(0, tk.END)
        for character in self.character_list:
            self.character_listbox.insert(tk.END, character.name)
            
    def clear_character_input_fields(self):
        self.name_entry.delete(0, tk.END)
        self.tagline_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.greeting_entry.delete(0, tk.END)
        self.definition_text.delete(1.0, tk.END)
        
    def populate_character_fields(self):
        self.clear_character_input_fields()
        self.name_entry.insert(0, self.selected_character.name)
        self.tagline_entry.insert(0, self.selected_character.tagline)
        self.description_entry.insert(0, self.selected_character.description)
        self.greeting_entry.insert(0, self.selected_character.greeting)
        self.definition_text.insert(tk.END, self.selected_character.definition)

    def load_characters_from_files(self):
        character_folder = "characters"
        if not os.path.exists(character_folder):
            os.makedirs(character_folder)
        
        for filename in os.listdir(character_folder):
            if filename.endswith(".json"):
                with open(os.path.join(character_folder, filename), "r") as file:
                    character_data = json.load(file)
                    character = Character(**character_data)
                    self.character_list.append(character)
        
        self.update_character_listbox()

    def save_character_to_file(self, character):
        character_folder = "characters"
        if not os.path.exists(character_folder):
            os.makedirs(character_folder)
        
        filename = f"{character.name}.json"
        filepath = os.path.join(character_folder, filename)
        with open(filepath, "w") as file:
            character_data = {
                "name": character.name,
                "tagline": character.tagline,
                "description": character.description,
                "greeting": character.greeting,
                "definition": character.definition
            }
            json.dump(character_data, file)

    def save_characters_to_files(self):
        for character in self.character_list:
            self.save_character_to_file(character)
            
    def save_characters_on_close(self):
        self.save_characters_to_files()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CharacterApp(root)
    root.mainloop()