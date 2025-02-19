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
import models.ticket
from json2html import Json2Html
from vertexai.generative_models import FunctionDeclaration
from vertexai.preview.vision_models import ImageGenerationModel
from common.db import getcursor, commit
from common.function_calling import extract_text

class User:
    def __init__(self, connection_pool, config_service, rag_model):
        self.connection_pool = connection_pool
        self.config_service = config_service
        self.rag_model = rag_model

    @staticmethod
    def get_function_declarations():
        fc_get_user_tickets = FunctionDeclaration(
            name="fc_get_user_tickets",
            description="Get the support tickets that the user",
            parameters={
                "type": "object",
                "properties": {},            
            }
        )

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
                about super secret Digital Natives team at Google.''',
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

        return [
            fc_get_user_tickets,
            fc_generate_profile_picture,
            fc_rag_retrieval
        ]

    def fc_rag_retrieval(self, user_id, question_passthrough):
        response = self.rag_model.generate_content(question_passthrough)
        return extract_text(response)

    def fc_get_user_tickets(self, user_id):
        try:
            with getcursor(self.connection_pool) as cur:
                cur.execute('''SELECT ticket_id, ticket_type, user_id, message, created_at 
                            FROM user_tickets 
                            WHERE user_id = %s''', [user_id])

            results = cur.fetchall()

            tickets = []
            for i in range(len(results)):
                tickets.append(models.ticket.Ticket.from_dict(results[i]))

            # Format the data for json2html
            formatted_data = [
                {
                    "Ticket Type": ticket.ticket_type,
                    "Message": ticket.message,
                    "Date": ticket.created_at
                }
                for ticket in tickets
            ]

            j2h = Json2Html()
            html_table = j2h.convert(json=formatted_data)

            html_table.__str__

            return html_table

        except Exception as e:
            logging.error("%s, %s", traceback.format_exc(), e)
            return 'Reply that we failed to fetch their tickets. Ask them to try again later'
        
    def fc_generate_profile_picture(self, user_id, description):
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
            with getcursor(self.connection_pool) as cur:
                cur.execute(
                    "UPDATE users SET avatar = %s WHERE user_id = %s; COMMIT;",
                    (cdn_url, user_id),
                )

                commit(self.connection_pool)
                logging.info('Updated user profile picture to %s', cdn_url)
        except Exception as e:
            logging.info("%s, %s", traceback.format_exc(), e)
            return 'Reply that we failed to generate a new profile picture. Ask them to try again later'

        return '''Reply "There you go." and output this raw HTML: 
            `<div>
                <img style="width: 50%; border-radius: 10px;" src="''' + cdn_url + '''">
            </div>`'''
        
