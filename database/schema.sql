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
	"created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	"updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY("city_id") REFERENCES "cities"("id") ON DELETE
	SET NULL
);
CREATE OR REPLACE FUNCTION update_updated_at_column() RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = now();
RETURN NEW;
END;
$$ language 'plpgsql';
CREATE TRIGGER update_users_updated_at BEFORE
UPDATE ON users FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
COMMIT;