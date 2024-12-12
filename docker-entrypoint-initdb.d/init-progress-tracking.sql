-- init-progress-tracking.sql
-- init-progress-tracking.sql
CREATE SEQUENCE IF NOT EXISTS progress_tracking_id_seq;

ALTER TABLE progress_tracking ALTER COLUMN id SET DEFAULT nextval('progress_tracking_id_seq');

ALTER SEQUENCE progress_tracking_id_seq OWNED BY progress_tracking.id;