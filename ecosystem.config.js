module.exports = {
    apps : [{
      name: "match-combat",
      // Apuntamos al binario de uvicorn en el venv
      script: "./.venv/bin/uvicorn",
      // Pasamos los argumentos como un array
      args: "app.main:app --host 0.0.0.0 --port 9009",
      // Opcional: forzamos el intérprete del venv
      interpreter: "./.venv/bin/python",
      instances: 1,
      autorestart: true,
      watch: false,
      env_production: {
        NODE_ENV: "production",
        DB_URL: "postgresql+psycopg2://match_user:match_password@localhost:5432/match_db",
        JWT_SECRET_KEY: "dev-secret-key-change-in-production",
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES: 30,
        JWT_REFRESH_TOKEN_EXPIRE_DAYS: 7,
        ADMIN_USERNAME: "admin",
        ADMIN_PASSWORD: "changeme123",
        ADMIN_EMAIL: "admin@matchcombat.local",
        NOMBRE_EVENTO: "ASCENSO - 14 DE JUNIO 2026"
      }
    }]
  }