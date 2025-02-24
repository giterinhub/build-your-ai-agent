# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import traceback
import vertexai
import os
import logging

import vertexai.preview.generative_models as generative_models
from vertexai.preview.generative_models import (
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
)

import firebase_admin
from firebase_admin import credentials, firestore

from flask import Flask, request, jsonify, render_template

from common import config as configuration, function_calling, rag
from services.user import User as UserService

# Environment variables

PROJECT_ID = os.environ.get("PROJECT_ID", "<GCP_PROJECT_ID>")
REGION = os.environ.get("REGION", "<GCP_REGION>")
FAKE_USER_ID = "7608dc3f-d239-405c-a097-b152ab38a354"

SAFETY_SETTINGS = {
    generative_models.HarmCategory.HARM_CATEGORY_UNSPECIFIED: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
}

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

vertexai.init(project=PROJECT_ID, location=REGION)

config = configuration.Config.get_instance()
rag = rag.RAG(config)

def init_model():
    retail_tool = Tool(
        function_declarations=UserService.get_function_declarations(),        
    )

    model = GenerativeModel(
        config.get_property('general', 'gemini_version'),
        tools=[retail_tool],
        generation_config=GenerationConfig(temperature=1),
        system_instruction=[config.get_property('chatbot', 'llm_system_instruction') + config.get_property('chatbot', 'llm_response_type')]
    )

    return model

def init_rag_model(): 
    rag_retrieval_tool = Tool.from_retrieval(
        rag.get_rag_retrieval()
    )
    # Create a gemini-pro model instance
    model = GenerativeModel(
        model_name=config.get_property('general', 'gemini_version'), 
        tools=[rag_retrieval_tool]
    )

    return model


# Chat initialization per tenant (cleanup needed after timeout/logout)
def init_chat(model, user_id):
    if user_id in client_sessions and client_sessions[user_id] != None:
        logging.debug("Re-using existing session")
        return client_sessions[user_id]

    logging.debug("Creating new chat session for user %s", user_id)

    if user_id not in history_clients:
        history_clients[user_id] = []

    chat_client = model.start_chat(history=history_clients[user_id])

    client_sessions[user_id] = chat_client
    return client_sessions[user_id]

# Init models 
chat_model = init_model()
rag_model = init_rag_model()

cred = credentials.ApplicationDefault()  # Or use a service account key file
firebase_admin.initialize_app(cred)
db = firestore.client()

user_service = UserService(db, config, rag_model)

# Init our session handling variables
client_sessions = {}
history_clients = {}

app = Flask(
    __name__,
    instance_relative_config=True,
    template_folder="templates",
)

# Our main chat handler
@app.route("/chat", methods=["POST"])
def chat():
    chat = init_chat(chat_model, FAKE_USER_ID)

    prompt = Part.from_text(request.form.get("prompt"))
    response = chat.send_message(
        prompt,
        safety_settings=SAFETY_SETTINGS,
    )

    logging.info(response)

    history_clients[FAKE_USER_ID] = chat.history

    function_params = function_calling.extract_params(response)
    function_name = function_calling.extract_function(response)
    text_response = function_calling.extract_text(response)

    if function_name:
        try:
            # Injection of user_id (this should be done dynamically when proper auth is implemented)
            function_params['user_id'] = FAKE_USER_ID

            logging.info(function_params)
            logging.info("Calling  " + function_name)

            function_response, html_response = function_calling.call_function(user_service, function_name, function_params)

            response = chat.send_message(
                    Part.from_function_response(
                    name=function_name,
                    response={
                        "content": function_response,
                    },
                ),
                safety_settings=SAFETY_SETTINGS     
            )

            text_response = function_calling.extract_text(response) + html_response

        except TypeError as e:
            logging.error("%s, %s", traceback.format_exc(), e)
            text_response = config.get_property('chatbot', 'generic_error_message')

        except Exception as e:
            logging.error("%s, %s", traceback.format_exc(), e)
            text_response = config.get_property('chatbot', 'generic_error_message')

    if len(text_response) == 0:
        text_response = config.get_property('chatbot', 'generic_error_message')
        
    return function_calling.gemini_response_to_template_html(text_response)

@app.route("/", methods=["GET"])
def home():
    if os.environ.get("DEV_MODE") == "true":
        with open("templates/index.html", mode='r') as file: #
            data = file.read()

        return data
    
    return render_template("index.html")

@app.route("/version", methods=["GET"])
def version():
    return jsonify({
        "version": config.get_property('general', 'version')
        })

# Get character color
@app.route("/get_model", methods=["GET"])
def get_model():
    model = user_service.get_model(FAKE_USER_ID)

    if(model is not None) :
        response = jsonify(model.to_dict())
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    return 'Character was not found. Double-check the name and try again.', 404

@app.route("/reset", methods=["GET"])
def reset():
    for uid in client_sessions:
        client_sessions[uid] = None

    return jsonify({'status': 'ok'}), 200

if __name__ == "__main__":
    os.makedirs('uploads', exist_ok=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8888)))
