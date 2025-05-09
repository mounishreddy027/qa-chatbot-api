# list_models.py
import google.generativeai as genai

genai.configure(api_key="AIzaSyCX2Hh4O6lohAoneQ5RpRUG3KsrzZC0cGc")

# List available models
models = genai.list_models()

# Print model names and their supported methods
for model in models:
    print(f"Model Name: {model.name}")
    print(f"Supported Methods: {model.supported_generation_methods}")
    print("---")
