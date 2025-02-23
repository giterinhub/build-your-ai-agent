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
from firebase_admin import credentials, firestore
from json2html import Json2Html
from vertexai.generative_models import FunctionDeclaration
from vertexai.preview.vision_models import ImageGenerationModel
from common.function_calling import extract_text

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
        fc_generate_profile_picture = FunctionDeclaration(
            name="fc_generate_profile_picture",
            description='''Create new profile picture or avatar.  
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

        fc_save_model_color = FunctionDeclaration(
            name="fc_save_model_color",
            description="Save model's color when user requests to update his game model by name. Input is a color in hex format",
            parameters={
                "type": "object",
                "properties": {
                    "model_name": {"type": "string", "description": "The name of the game model user wants to change color of"},
                    "color": {"type": "string", "description": "Hex color"},
                },
                "required": [
                    "model_name",
                    "color"
                ]
            }
        )        

        return [
            fc_generate_profile_picture,
            fc_rag_retrieval,
            fc_save_model_color
        ]
    
    def fc_save_model_color(self, user_id, model_name, color):
        """
        Saves the model's color to Firestore.

        Args:
            user_id: The ID of the user.
            model_name: The name of the game model.
            color: The hex color to save.

        Returns:
            A string response for the user.
        """
        try:
            # Get the models collection reference
            models_ref = self.db.collection("models")

            # Query for the model with the given name
            query = models_ref.where("name", "==", model_name)
            results = query.get()

            if not results:
                return f"Reply that no character with name '{model_name}' was found."

            # Update the color of the first matching document
            for doc in results:
                doc.reference.update({"color": color})
                logging.info(f"Updated model '{model_name}' color to '{color}' for user '{user_id}'.")
                break

            return "Reply that their character colors have been saved and add this raw HTML in the end: <script>window.reloadCurrentModel();</script>"
        
        except Exception as e:
            logging.error("%s, %s", traceback.format_exc(), e)
            return 'Reply that we failed to update their character settings.'


    def fc_rag_retrieval(self, user_id, question_passthrough):
        """
        Retrieves information using RAG model.

        Args:
            user_id: The ID of the user.
            question_passthrough: The user's prompt.

        Returns:
            The RAG model's response as a string.
        """
        response = self.rag_model.generate_content(question_passthrough)
        return extract_text(response)
        
    def fc_generate_profile_picture(self, user_id, description):
        """
        Generates a profile picture using the image generation model and saves it to Firestore.

        Args:
            user_id: The ID of the user.
            description: The description of the desired image.

        Returns:
            A string response for the user, including the image HTML if successful.
        """
        try:
            model = ImageGenerationModel.from_pretrained(self.config_service.get_property("general", "imagen_version"))

            images = model.generate_images(
                prompt=description,
                number_of_images=4,
                language="en",
                seed=100,
                add_watermark=False,
                aspect_ratio="1:1",
                safety_filter_level="block_some",
                person_generation="allow_adult",
            )

            output_file = "static/avatars/tmp-" + str(user_id) + "-" + str(random.randint(0, 10000)) + ".png"
            images[0].save(location=output_file, include_generation_parameters=False)        

            cdn_url = '/' + output_file
        except Exception as e:
            logging.info("%s, %s", traceback.format_exc(), e)
            return 'Reply that we failed to generate a new profile picture. Ask them to try again later'


        try:
            # Update Firestore "users" collection
            user_ref = self.db.collection("users").document(str(user_id))
            user_ref.update({"avatar": cdn_url})
            logging.info('Updated user profile picture to %s', cdn_url)
        except Exception as e:
            logging.info("%s, %s", traceback.format_exc(), e)
            return 'Reply that we failed to generate a new profile picture. Ask them to try again later'

        return '''Reply "There you go." and output this raw HTML: 
            `<div>
                <img style="width: 50%; border-radius: 10px;" src="''' + cdn_url + '''">
            </div>`'''
        
    def get_model(self, user_id, model_name):
        """
        Retrieves the color of a character from Firestore.

        Args:
            user_id: The ID of the user.
            model_name: The name of the character.

        Returns:
            A dictionary containing the character's color information, or None if not found.
        """
        try:
            # Get the models collection reference
            models_ref = self.db.collection("models")

            # Query for the model with the given name
            query = models_ref.where("name", "==", model_name)
            results = query.get()

            if not results:
                logging.warning(f"No character found with name '{model_name}'.")
                return None

            # In our current setup, there should only be one matching model
            model_doc = results[0]
            model_data = model_doc.to_dict()
            
            # we return the full object since it is now already a dict
            return model_data

        except Exception as e:
            logging.error("%s, %s", traceback.format_exc(), e)
            return None