INSERT INTO wl_Counter (url, time) SELECT '/p/d4bc55f2/', 0 WHERE NOT EXISTS (SELECT 1 FROM wl_Counter WHERE url = '/p/d4bc55f2/');
INSERT INTO wl_Counter (url, time) SELECT '/p/e1ee5eca/', 0 WHERE NOT EXISTS (SELECT 1 FROM wl_Counter WHERE url = '/p/e1ee5eca/');

