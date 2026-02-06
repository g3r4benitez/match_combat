module.exports = {
  apps : [{
    name: "match-combat",
    script: "./main.py",
    cwd: "/root/projects/match_combat/app/", // PM2 saltará aquí antes de ejecutar el script
    interpreter: "/root/projects/match_combat/.venv/bin/python"
  }]
}