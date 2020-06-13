BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "users" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	"name" TEXT,
	"city_id" INTEGER,
	"phone_number" TEXT,
	"language" TEXT,
	"decision" INTEGER,
	FOREIGN KEY("city_id") REFERENCES "cities"("id") ON DELETE
	SET NULL
);
CREATE TABLE IF NOT EXISTS "cities" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	"name" TEXT NOT NULL,
	"name_kz" NUMERIC NOT NULL,
	"name_ru" TEXT NOT NULL
);
INSERT INTO "users" (
		"id",
		"name",
		"city_id",
		"phone_number",
		"language",
		"decision"
	)
VALUES (4, 'Kola', 2, '+77785547554', 'ru', 1),
	(5, 'dfdfdf', 2, '+77078419016', 'ru', 1);
INSERT INTO "cities" ("id", "name", "name_kz", "name_ru")
VALUES (1, 'Almaty', 'Алматы', 'Алматы'),
	(2, 'Astana', 'Астана', 'Астана'),
	(3, 'Shymkent', 'Шымкент', 'Шымкент');
COMMIT;