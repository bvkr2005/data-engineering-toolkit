-- Dedupe before MERGE (Databricks SQL). Test on a scratch schema, never on real tables.

-- 1) Setup: a target and a source that repeats key 1
CREATE OR REPLACE TABLE target (id INT, v STRING, updated_at DATE);
INSERT INTO target VALUES (1, 'start', DATE'2026-09-01'), (2, 'start', DATE'2026-09-01');

CREATE OR REPLACE TEMP VIEW updates AS
SELECT * FROM VALUES
  (1, 'old',  DATE'2026-10-01'),
  (1, 'new',  DATE'2026-10-05'),
  (2, 'only', DATE'2026-10-02')
AS t(id, v, updated_at);

-- 2) Without dedupe: expect an error, because two source rows match target id = 1
MERGE INTO target t
USING updates s
ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

-- 3) With dedupe: keep the latest row per key, then merge
MERGE INTO target t
USING (
  SELECT *
  FROM updates
  QUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC) = 1
) s
ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

SELECT * FROM target ORDER BY id;   -- expect: (1, new, 2026-10-05) and (2, only, 2026-10-02)
