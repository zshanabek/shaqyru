BEGIN TRANSACTION;
CREATE TABLE `users` (
	`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`name` TEXT NOT NULL,
	`age` INTEGER,
	`sex` INTEGER
);
INSERT INTO `users`
VALUES (1, 'mama', 12, 1);
CREATE TABLE `cities` (
	`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`name` TEXT NOT NULL,
	`name_kz` TEXT NOT NULL,
	`name_ru` TEXT NOT NULL
);
INSERT INTO `cities`
VALUES (1, 'Astana', 'Астана', 'Астана'),
	(2, 'Almaty', 'Алматы', 'Алматы'),
	(3, 'Shymkent', 'Шымкент', 'Шымкент');
COMMIT;