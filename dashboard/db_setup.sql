CREATE TABLE community (
  id BIGINT PRIMARY KEY
);

CREATE TABLE event (
  id BIGINT PRIMARY KEY,
  name TEXT,
  start_time TIMESTAMP WITH TIME ZONE,
  community_id BIGINT REFERENCES community(id)
);

CREATE TABLE attendance (
  id TEXT,
  event_id BIGINT REFERENCES event(id),
  rsvp_status TEXT,
  PRIMARY KEY(id, event_id)
);
