// PM2 configuration for Match Combat (Debian 13 production).
//
// The application listens on 127.0.0.1:9009. nginx is the only process that
// exposes the API to the LAN, at https://SERVER_IP/api.
//
// Application secrets and database settings live in the project-root .env
// file, read by app/core/config.py. Do not hardcode them here.
//
// Start in production:
//   pm2 start ecosystem.config.js --env production

module.exports = {
  apps: [
    {
      name: "match-combat",

      // Required so app/core/config.py finds the project-root .env file.
      cwd: __dirname,

      // Run uvicorn through the virtualenv interpreter.
      script: "./.venv/bin/python",
      args: "-m uvicorn app.main:app --host 127.0.0.1 --port 9009 --proxy-headers --forwarded-allow-ips=127.0.0.1",
      interpreter: "none",

      instances: 1,
      exec_mode: "fork",
      autorestart: true,
      watch: false,

      max_memory_restart: "512M",
      restart_delay: 3000,
      exp_backoff_restart_delay: 100,
      kill_timeout: 10000,

      time: true,
      merge_logs: true,
      error_file: "./logs/pm2-error.log",
      out_file: "./logs/pm2-out.log",

      env: {
        NODE_ENV: "production",
      },
      env_production: {
        NODE_ENV: "production",
      },
    },
  ],
};
