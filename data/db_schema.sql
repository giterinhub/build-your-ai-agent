-- Copyright 2024 Google LLC
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
--      https://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.

CREATE TYPE TicketType AS ENUM ('general', 'support');

CREATE TABLE users (
  user_id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  email VARCHAR(255),
  password VARCHAR(64),
  avatar TEXT
);

INSERT INTO users (user_id, name, email, password, is_active, is_validated) VALUES
(1,	'Test User 1',	'test-user-1@domain.tld',	encode(sha256('password'), 'hex'),	't',	't');

CREATE TABLE user_tickets (
  ticket_id SERIAL PRIMARY KEY,
  ticket_type TicketType,
  user_id SERIAL,
  message TEXT,
  created_at DATE
);

INSERT INTO user_tickets (ticket_id, ticket_type, user_id, message, created_at) VALUES
(1,	'general', 1, 'Just wanted to ask you about any cool upcoming events at Google Cloud. Thank you!',	CURRENT_DATE);

CREATE TABLE character_personalization (
  character_id SERIAL PRIMARY KEY,
  user_id SERIAL REFERENCES users(user_id),
  color VARCHAR(16),
  character_name VARCHAR(2048)
);

INSERT INTO character_personalization (character_id, user_id, color, character_name) VALUES
(1,	1,	'#CCCCCC', 'Bugdroid');
