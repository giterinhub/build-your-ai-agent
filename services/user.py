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
import random
import logging
import base64
import requests
import time
import os
import urllib.request
import shutil
from firebase_admin import credentials, firestore
from json2html import Json2Html
from google.cloud.firestore_v1.base_query import FieldFilter
from vertexai.generative_models import FunctionDeclaration
from vertexai.preview.vision_models import ImageGenerationModel
from common.function_calling import extract_text
from models import model, user

class User:
    def __init__(self, db, config_service, rag_model):
        """
        Initializes the User service.

        Args:
            db: Firestore client instance.
            config_service: Service to get configuration values.
            rag_model: The RAG model instance.
        """
        self.db = db
        self.config_service = config_service
        self.rag_model = rag_model

    @staticmethod
    def get_function_declarations():
        
        fc_show_my_avatar = FunctionDeclaration(
            name="fc_show_my_avatar",
            description="Show user's current avatar.",
            parameters={
                "type": "object",
                "properties": {},            
            }
        )

        fc_show_my_model = FunctionDeclaration(
            name="fc_show_my_model",
            description="Show user's model / character on the screen.",
            parameters={
                "type": "object",
                "properties": {},            
            }
        )

        fc_generate_avatar = FunctionDeclaration(
            name="fc_generate_avatar",
            description='''Create new avatar or avatar.  
                Inject the description into the function that is being called.''',
            parameters={
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Description of the picture or avatar"},
                },
                "required": [
                    "description",
                ]
            }
        )

        fc_save_model_color = FunctionDeclaration(
            name="fc_save_model_color",
            description="Save new color when user requests to update his game model. Input is a color in hex format",
            parameters={
                "type": "object",
                "properties": {
                    "color": {"type": "string", "description": "Hex color"},
                },
                "required": [
                    "color"
                ]
            }
        )

        fc_rag_retrieval = FunctionDeclaration(
            name="fc_rag_retrieval",
            description='''Function to be invoked when the prompt is 
                about a super secret game called Cloud Meow.''',
            parameters={
                "type": "object",
                "properties": {
                    "question_passthrough": {"type": "string", "description": "The whole user's prompt in the context of this message"}
                },
                "required": [
                    "question_passthrough",
                ]            
            }
        )

        fc_create_3d_model_from_avatar = FunctionDeclaration(
            name="fc_create_3d_model_from_avatar",
            description="Create a 3D model/character based on the user's current avatar image",
            parameters={
                "type": "object",
                "properties": {},
            }
        )

        ### rest of function declarations

        return [
            fc_rag_retrieval,
            fc_generate_avatar,
            fc_save_model_color,
            fc_show_my_model,
            fc_show_my_avatar,
            fc_create_3d_model_from_avatar  # Add the new function to the list
        ]        

    def fc_show_my_model(self, user_id):
        logging.info(f"Showing user's ({user_id}) character")
        return '''Reply something like "there you go"''', '''<script>$("#modelWindow").show();</script>'''

    def fc_show_my_avatar(self, user_id):
        logging.info(f"Showing user's ({user_id}) avatar")
        return '''Reply something like "There you go."''', '''
            <div>
                <br>
                <img class="avatar" src="/static/avatars/%s.png?rand=%s">
            </div>''' % (user_id, str(random.randint(0, 1000000)))

    def get_model(self, user_id):
        """
        Retrieves the color of a character from Firestore.

        Args:
            user_id: The ID of the user.

        Returns:
            A dictionary containing the character's color information, or None if not found.
        """
        try:
            # Get the models collection reference
            models_ref = self.db.collection("models")

            # Query for the model with the given user_id
            query = models_ref.where("user_id", "==", user_id)
            results = query.get()

            if not results:
                logging.warning(f"No character found for '{user_id}'.")
                return None

            # In our current setup, there should only be one matching model
            # model_doc = results[0]
            # model_data = model_doc.to_dict()
            
            return model.Model.from_dict(results[0].to_dict())

            # we return the full object since it is now already a dict
            # return model_data

        except Exception as e:
            logging.error("%s, %s", traceback.format_exc(), e)
            return None

    def fc_generate_avatar(self, user_id, description):
        try:
            model = ImageGenerationModel.from_pretrained(self.config_service.get_property("general", "imagen_version"))

            instruction = self.config_service.get_property("chatbot", "diffusion_generation_instruction")

            images = model.generate_images(
                prompt=instruction % description,
                number_of_images=4,
                language="en",
                seed=100,
                add_watermark=False,
                aspect_ratio="1:1",
                safety_filter_level="block_some",
                person_generation="allow_adult",
            )

            output_file = "static/avatars/" + str(user_id) + ".png"
            images[0].save(location=output_file, include_generation_parameters=False)        

            cdn_url = '/' + output_file
        except Exception as e:
            logging.info("%s, %s", traceback.format_exc(), e)
            return 'Reply that we failed to generate a new avatar. Ask them to try again later'

        try:
            # Update Firestore "users" collection
            user_ref = self.db.collection("users").where(filter=FieldFilter("user_id", "==", user_id))
            user_ref.get()[0].reference.update({"avatar": cdn_url})
            logging.info('Updated user avatar to %s', cdn_url)
        except Exception as e:
            logging.info("%s, %s", traceback.format_exc(), e)
            return 'Reply that we failed to generate a new avatar. Ask them to try again later'

        return '''Reply that the avatar was successfully created.''', '''
            <div>
                <br>
                <img class="avatar" src="%s?rand=%s">
            </div>''' % (cdn_url, str(random.randint(0, 1000000)))

    def fc_save_model_color(self, user_id, color):
        try:
            # Get the models collection reference
            models_ref = self.db.collection("models")

            # Query for the model with the given user_id
            query = models_ref.where(filter=FieldFilter("user_id", "==", user_id))
            results = query.get()

            if not results:
                return f"Reply that no character for user '{user_id}' was found."

            # Update the color of the first matching document
            for doc in results:
                doc.reference.update({"color": color, "original_material": False})
                logging.info(f"Updated color to '{color}' for '{user_id}'\'s model.")
                break

            return '''Reply that their character color has been updated''', '''<script>window.reloadCurrentModel();</script>'''
        
        except Exception as e:
            logging.error("%s, %s", traceback.format_exc(), e)
            return 'Reply that we failed to update their character settings.'

    def fc_rag_retrieval(self, user_id, question_passthrough):
        response = self.rag_model.generate_content(question_passthrough)
        return extract_text(response), ''

    def fc_create_3d_model_from_avatar(self, user_id):
        """
        Creates a 3D model from the user's avatar using an external API.
        
        Args:
            user_id: The ID of the user.
            
        Returns:
            A tuple containing a message to the user and HTML to display.
        """
        try:
            # Path to the user's avatar
            avatar_path = f"static/avatars/{user_id}.png"
            
            # Check if avatar exists
            if not os.path.exists(avatar_path):
                return "Reply that no avatar was found for this user. Suggest creating an avatar first.", ""
            
            # Read the avatar image and encode it in base64
            with open(avatar_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Send request to the API to create 3D model
            api_endpoint = "https://genai3d.nikolaidan.demo.altostrat.com/upload"
            payload = {"image": encoded_image}
            
            logging.info(f"Sending avatar for user {user_id} to 3D model API")
            response = requests.post(api_endpoint, json=payload)
            
            if response.status_code != 200:
                logging.error(f"API returned error: {response.status_code, response.text}")
                return "Reply that there was an error creating the 3D model. Ask them to try again later.", ""
            
            # Get job ID from response
            job_data = response.json()
            job_id = job_data.get("job_id")
            
            if not job_id:
                logging.error(f"No job ID returned from API: {job_data}")
                return "Reply that there was an error processing the avatar. Ask them to try again later.", ""
            
            # Poll for job completion
            check_url = f"https://genai3d.nikolaidan.demo.altostrat.com/check_job/{job_id}"
            max_attempts = 60  # Maximum attempts (10 minutes at 10-second intervals)
            attempt = 0
            
            while attempt < max_attempts:
                logging.info(f"Checking job status for job {job_id}, attempt {attempt+1}")
                status_response = requests.get(check_url)
                
                if status_response.status_code != 200:
                    logging.error(f"Error checking job status: {status_response.status_code, status_response.text}")
                    return "Reply that there was an error checking the status of your 3D model. Ask them to try again later.", ""
                
                status_data = status_response.json()
                
                if status_data.get("status") == "finished":
                    # Job is complete, download the model file
                    model_url = status_data.get("filename")
                    if not model_url:
                        logging.error(f"No model URL in finished job: {status_data}")
                        return "Reply that there was an error retrieving the 3D model. Ask them to try again later.", ""
                    
                    # Create directory if it doesn't exist
                    os.makedirs("static/models", exist_ok=True)
                    
                    # Download the model file
                    model_filename = f"{job_id}.glb"
                    model_path = f"static/models/{model_filename}"
                    
                    try:
                        logging.info(f"Downloading 3D model from {model_url} to {model_path}")
                        urllib.request.urlretrieve(model_url, model_path)
                    except Exception as e:
                        logging.error(f"Error downloading model file: {str(e)}")
                        return "Reply that there was an error downloading your 3D model. Ask them to try again later.", ""
                    
                    # Update Firestore with the new model
                    try:
                        models_ref = self.db.collection("models")
                        query = models_ref.where(filter=FieldFilter("user_id", "==", user_id))
                        results = query.get()
                        
                        if not results:
                            logging.warning(f"No model record found for user {user_id} to update")
                            return f"Reply that we created a 3D model, but couldn't find your character record to update.", ""
                        
                        for doc in results:
                            doc.reference.update({"model": model_filename})
                            logging.info(f"Updated model for {user_id} to {model_filename}")
                            break
                        
                        # Return success message and reload the model
                        return '''Reply that the 3D model was successfully created from their avatar.''', '''<script>window.reloadCurrentModel();</script>'''
                    
                    except Exception as e:
                        logging.error(f"Error updating model in Firestore: {str(e)}")
                        return "Reply that the 3D model was created but there was an error updating your character. Ask them to try again later.", ""
                
                elif status_data.get("status") == "queued" or status_data.get("status") == "processing":
                    # Job is still in progress, wait and check again
                    time.sleep(10)  # Wait 10 seconds before checking again
                    attempt += 1
                else:
                    # Unknown status
                    logging.error(f"Unknown job status: {status_data}")
                    return "Reply that there was an unexpected status while creating your 3D model. Ask them to try again later.", ""
            
            # If we get here, we've exceeded max attempts
            return "Reply that the 3D model is taking too long to generate. Suggest they try again later.", ""
            
        except Exception as e:
            logging.error(f"Error in fc_create_3d_model_from_avatar: {str(e)}")
            logging.error(traceback.format_exc())
            return "Reply that there was an error creating the 3D model from your avatar. Ask them to try again later.", ""