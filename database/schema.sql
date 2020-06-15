BEGIN TRANSACTION;
drop table if exists "users";
drop table if exists "cities";
CREATE TABLE "cities" (
	"id" serial PRIMARY KEY,
	"name" VARCHAR (25) NOT NULL,
	"name_kz" VARCHAR (25) NOT NULL,
	"name_ru" VARCHAR (25) NOT NULL
);
INSERT INTO "cities" ("id", "name", "name_ru", "name_kz")
VALUES (1, 'Almaty', 'Алматы', 'Алматы'),
	(2, 'Astana', 'Астана', 'Астана'),
	(3, 'Shymkent', 'Шымкент', 'Шымкент'),
	(4, 'Almaty', 'Актобе', 'Ақтөбе'),
	(5, 'Astana', 'Тараз', 'Тараз'),
	(6, 'Shymkent', 'Павлодар', 'Павлодар'),
	(7, 'Almaty', 'Актобе', 'Ақтөбе'),
	(8, 'Astana', 'Караганда', 'Қарағанды'),
	(9, 'Shymkent', 'Усть-Каменогорск', 'Өскемен'),
	(10, 'Almaty', 'Семей', 'Семей'),
	(11, 'Astana', 'Атырау', 'Атырау'),
	(12, 'Shymkent', 'Костанай', 'Костанай'),
	(13, 'Shymkent', 'Кызылорда', 'Қызылорда'),
	(14, 'Almaty', 'Уральск', 'Орал'),
	(15, 'Astana', 'Петропавловск', 'Петропавл'),
	(16, 'Shymkent', 'Талдыкорган', 'Талдықорған'),
	(17, 'Shymkent', 'Кокшетау', 'Көкшетау'),
	(18, 'Almaty', 'Туркестан', 'Түркістан');
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