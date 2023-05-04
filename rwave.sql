DROP SOURCE wiki;
CREATE SOURCE IF NOT EXISTS wiki (
   timestamp TIMESTAMP,
   bot BOOLEAN,
   id bigint,
   user varchar,
   wiki varchar,
   server_name varchar,
   server_url varchar,
   title varchar,
   type varchar,
   meta STRUCT <
    domain varchar,
    stream varchar,
    topic varchar,
    uri varchar
   >
)
WITH (
   connector='kafka',
   topic='wiki-events',
   properties.bootstrap.server='kafka-wiki:9093',
   scan.startup.mode='earliest',
   scan.startup.timestamp_millis='140000000'
)
ROW FORMAT JSON;

CREATE MATERIALIZED VIEW wiki_view AS
SELECT _rw_kafka_timestamp, *
FROM wiki;

SELECT id, bot, "timestamp", window_start, window_end
FROM TUMBLE (wiki, "timestamp", INTERVAL '2 MINUTES');

SELECT window_start, window_end, count(*)
FROM TUMBLE (wiki, "timestamp", INTERVAL '1 MINUTES')
GROUP BY window_start, window_end
ORDER BY window_start;