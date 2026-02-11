-- Migración para hacer nullable los campos historial_str y comentarios
ALTER TABLE competidor ALTER COLUMN historial_str DROP NOT NULL;
ALTER TABLE competidor ALTER COLUMN comentarios DROP NOT NULL;
