BEGIN TRANSACTION;
drop table if exists "users";
drop table if exists "cities";
CREATE TABLE "cities" (
	"id" serial PRIMARY KEY,
	"name" VARCHAR (25) NOT NULL,
	"name_kz" VARCHAR (25) NOT NULL,
	"name_ru" VARCHAR (25) NOT NULL
);
INSERT INTO "cities" ("id", "name", "name_kz", "name_ru")
VALUES (1, 'Almaty', 'Алматы', 'Алматы'),
	(2, 'Astana', 'Астана', 'Астана'),
	(3, 'Shymkent', 'Шымкент', 'Шымкент');
CREATE TABLE "users" (
	"id" serial PRIMARY KEY,
	"name" VARCHAR (255),
	"city_id" INTEGER,
	"phone_number" VARCHAR (12),
	"language" VARCHAR (2),
	"telegram_id" VARCHAR (10),
	"telegram_username" VARCHAR(50),
	"decision" BOOLEAN,
	FOREIGN KEY("city_id") REFERENCES "cities"("id") ON DELETE
	SET NULL
);
COMMIT;