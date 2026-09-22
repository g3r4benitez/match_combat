-- Migración para añadir las columnas de evento y area a las tablas existentes
ALTER TABLE modalidad ADD COLUMN evento_id INTEGER;
ALTER TABLE competidor ADD COLUMN evento_id INTEGER;
ALTER TABLE match ADD COLUMN evento_id INTEGER;
ALTER TABLE match ADD COLUMN area_id INTEGER;
ALTER TABLE entrada ADD COLUMN evento_id INTEGER;
