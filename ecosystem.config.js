module.exports = {
    apps : [{
      name: "match-combat",
      // Apuntamos al binario de uvicorn en el venv
      script: "./.venv/bin/uvicorn",
      // Pasamos los argumentos como un array
      args: "app.main:app --port 9009",
      // Opcional: forzamos el intérprete del venv
      interpreter: "./.venv/bin/python",
      instances: 1,
      autorestart: true,
      watch: false
    }]
  }