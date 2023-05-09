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


SELECT window_start, window_end, count(*) AS edits, 
       count(DISTINCT user) AS users, 
       count(DISTINCT (meta).domain) AS domains
FROM TUMBLE (wiki, "timestamp", INTERVAL '1 MINUTES')
WHERE timestamp > CURRENT_TIMESTAMP AT TIME ZONE 'UTC' - INTERVAL '10 minutes'
GROUP BY window_start, window_end
ORDER BY window_start;


set timezone TO 'Europe/London';

CREATE MATERIALIZED VIEW wiki_10mins AS 
SELECT window_start, window_end, count(*) AS edits, 
       count(DISTINCT user) AS users, 
       count(DISTINCT (meta).domain) AS domains
FROM TUMBLE (wiki, "timestamp", INTERVAL '1 MINUTES')
WHERE timestamp > (now() - INTERVAL '10 minutes')
GROUP BY window_start, window_end;

CREATE MATERIALIZED VIEW wiki_10mins2 AS 
SELECT window_start, window_end, count(*) AS edits, 
       count(DISTINCT user) AS users, 
       count(DISTINCT (meta).domain) AS domains
FROM TUMBLE (wiki, "timestamp", INTERVAL '1 MINUTES')
WHERE timestamp > (now() AT TIME ZONE 'UTC' - INTERVAL '10 minutes')
GROUP BY window_start, window_end;

SELECT window_start, window_end, count(*) AS edits, 
       count(DISTINCT user) AS users, 
       count(DISTINCT (meta).domain) AS domains
FROM TUMBLE (wiki, "timestamp", INTERVAL '1 MINUTES')
WHERE timestamp > CURRENT_TIMESTAMP AT TIME ZONE 'UTC' - INTERVAL '2 minutes'
GROUP BY window_start, window_end
ORDER BY window_start;