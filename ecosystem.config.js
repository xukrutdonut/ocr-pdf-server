module.exports = {
  apps: [{
    name: 'ocr-pdf-server',
    cwd: '/home/arkantu/ocr-pdf-server',
    script: 'start_server.sh',
    interpreter: 'bash',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    },
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log',
    log_file: './logs/pm2.log',
    time: true
  }]
}