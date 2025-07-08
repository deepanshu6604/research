import os
os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "0"  # Disable gRPC fork warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Suppress TensorFlow logs

from pymongo import MongoClient

 # Load environment variables from .env


import google.generativeai as genai

# Gemini API Configuration
GENAI_API_KEY = "AIzaSyCPJOknpdRBaBJpy-sEcUTdOXdpEE2ztLI"
GENAI_MODEL_NAME = "gemini-2.0-flash"
GENAI_MAX_TOKENS = 5000  # Maximum tokens for response generation
GENAI_TEMPERATURE = 0.5 #

OPENAI_MODEL_NAME = "gpt-4o-mini"  # or "gpt-3.5-turbo"
OPENAI_MAX_TOKENS = 500
OPENAI_TEMPERATURE = 0.7
OPENAI_API_KEY = "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"

# ---- DATABASE SETTINGS ----
MONGO_URI = "mongodb://localhost:27017"
# MONGO_DB_NAME = "chatbot_memory"
# MONGO_STM_COLLECTION = "stm"  # Short-Term Memory
# MONGO_LTM_COLLECTION = "ltm"  # Long-Term Memory
# MONGO_FACTUAL_COLLECTION = "factual_memory"


#MONGO_URI="mongodb+srv://ayushjariwala:ayush123@chatbotcluster.yglqbir.mongodb.net/?retryWrites=true&w=majority&appName=chatbotcluster"
MONGO_DB_NAME = "chatbot_memory"
MONGO_STM_COLLECTION = "stm"
MONGO_LTM_COLLECTION = "ltm"
MONGO_FACTUAL_COLLECTION = "factual_memory"

SQLITE_DB_PATH = "feedback.db"

# ---- MEMORY MANAGEMENT SETTINGS ----
STM_MAX_ENTRIES = 10  # Defines how many recent interactions STM will store before flushing to LTM
LTM_RETENTION_POLICY = "infinite"  # Options: 'infinite' / 'time-based'
FACTUAL_MEMORY_UPDATE = True  # If True, allows factual updates dynamically

# ---- RESPONSE GENERATION SETTINGS ----
ENABLE_RESPONSE_REFINEMENT = True  # If True, enables advanced response tuning
ENABLE_PERSONALITY_DEFINITION = False  # Reserved for future chatbot personality improvements

# ---- LOGGING SETTINGS ----
LOGGING_LEVEL = "DEBUG"  # Options: 'DEBUG', 'INFO', 'WARNING', 'ERROR'

# ---- FUNCTION TO SET UP GOOGLE GENERATIVE AI ----
def configure_genai():
    genai.configure(api_key=GENAI_API_KEY)

# Call function to configure Generative AI
configure_genai()
