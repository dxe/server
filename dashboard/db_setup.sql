CREATE TABLE community (
  id INT PRIMARY KEY
);

CREATE TABLE event (
  id INT PRIMARY KEY,
  name TEXT,
  start_time TIMESTAMP WITH TIME ZONE,
  community_id INT REFERENCES community(id)
);

CREATE TABLE attendee (
  id INT PRIMARY KEY,
  event_id INT REFERENCES event(id),
  rsvp_status TEXT
);
