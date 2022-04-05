-- based on https://www.postgresql.org/docs/current/plpgsql-trigger.html

CREATE TABLE hosts(
    host_id UUID,
    url VARCHAR(255) NOT NULL,
    created TIMESTAMP,
    PRIMARY KEY(host_id),
    UNIQUE (url)
);

CREATE TABLE records(
    record_id UUID NOT NULL,
    host_id UUID NOT NULL,
    url VARCHAR(255) NOT NULL,
    response_time REAL NOT NULL,
    status_code INTEGER NOT NULL,
    last_check TIMESTAMP,
    content_search_pattern VARCHAR (255),
    content_search_success BOOLEAN,
    PRIMARY KEY(record_id),
    CONSTRAINT fk_host
        FOREIGN KEY(host_id)
        REFERENCES hosts(host_id)
);


CREATE OR REPLACE FUNCTION turl_update_meta() RETURNS trigger AS $turl_update_meta$
    BEGIN
        INSERT INTO hosts ( "host_id", "url", "created")
        VALUES(NEW.host_id, NEW.url, current_timestamp)
        ON CONFLICT DO NOTHING;

        RETURN NEW;
    END;
$turl_update_meta$ LANGUAGE plpgsql;

CREATE TRIGGER turl_update_meta BEFORE INSERT OR UPDATE ON records
    FOR EACH ROW EXECUTE FUNCTION turl_update_meta();
