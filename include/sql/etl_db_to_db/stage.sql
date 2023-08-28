truncate table stage.{{ params.source_table }}

;COPY INTO stage.{{ params.source_table }}
FROM @postgre_ext_stage/{{ params.source_table }}.csv
FILE_FORMAT = (TYPE = CSV FIELD_DELIMITER = ',');