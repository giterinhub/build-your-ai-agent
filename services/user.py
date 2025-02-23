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
from google.cloud.firestore_v1.base_query import FieldFilter
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

        fc_revert_model_color = FunctionDeclaration(
            name="fc_revert_model_color",
            description="Revert the color/material of user's model on their request.",
            parameters={
                "type": "object"
            }
        )        

        fc_show_my_model = FunctionDeclaration(
            name="fc_show_my_model",
            description="Show user's model on the screen.",
            parameters={
                "type": "object",
                "properties": {},            
            }
        )

        return [
            fc_generate_avatar,
            fc_rag_retrieval,
            fc_save_model_color,
            fc_revert_model_color,
            fc_show_my_model
        ]
    
    def fc_save_model_color(self, user_id, color):
        """
        Saves the model's color to Firestore.

        Args:
            user_id: The ID of the user.
            color: The hex color to save.

        Returns:
            A string response for the user.
        """
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

    def fc_revert_model_color(self, user_id):
        """
        Revert's the model's color.

        Args:
            user_id: The ID of the user.

        Returns:
            A string response for the user.
        """
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
                doc.reference.update({"original_material": True})
                logging.info(f"Reverted to original materials for '{user_id}'\'s model.")
                break

            return '''Reply that their character colors have been reverted''', '''<script>window.reloadCurrentModel();</script>'''
        
        except Exception as e:
            logging.error("%s, %s", traceback.format_exc(), e)
            return 'Reply that we failed to update their character settings.'

    def fc_generate_avatar(self, user_id, description):
        """
        Generates a avatar using the image generation model and saves it to Firestore.

        Args:
            user_id: The ID of the user.
            description: The description of the desired image.

        Returns:
            A string response for the user, including the image HTML if successful.
        """
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

        return '''Reply something like "There you go."''', '''
            <div>
                <img style="width: 50%; border-radius: 10px;" src="''' + cdn_url + '?rand=' + str(random.randint(0, 1000000)) + '''">
            </div>'''

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

    def fc_show_my_model(self, user_id):
        logging.info(f"Showing user's ({user_id}) Character")
        return '''Reply something like "there you go"''', '''<script>$("#modelWindow").show();</script>'''

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
            model_doc = results[0]
            model_data = model_doc.to_dict()
            
            # we return the full object since it is now already a dict
            return model_data

        except Exception as e:
            logging.error("%s, %s", traceback.format_exc(), e)
            return None