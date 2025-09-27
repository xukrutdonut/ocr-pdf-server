#!/bin/bash

# Script de despliegue para OCR-PDF Server
echo "🚀 Iniciando despliegue de OCR-PDF Server..."

# Navegar al directorio del proyecto
cd /home/arkantu/ocr-pdf-server

# Actualizar desde git (si es necesario)
echo "📡 Actualizando código..."
git pull 2>/dev/null || echo "⚠️  No hay repositorio git o no se pudo actualizar"

# Activar entorno virtual e instalar/actualizar dependencias
echo "📦 Actualizando dependencias..."
source venv/bin/activate
pip install -r requirements.txt --quiet

# Reiniciar el servidor con PM2
echo "🔄 Reiniciando servidor..."
pm2 reload ocr-pdf-server 2>/dev/null || pm2 start ecosystem.config.js

# Mostrar estado
echo "✅ Despliegue completado. Estado del servidor:"
pm2 status ocr-pdf-server

# Verificar que el servidor responda
echo "🔍 Verificando servidor..."
sleep 3

if curl -s http://localhost:8000/health | jq -e '.status == "healthy"' > /dev/null 2>&1; then
    echo "✅ Servidor saludable y funcionando en puerto 8000"
    echo "🌐 Recuerda configurar el proxy reverso para apuntar a localhost:8000"
else
    echo "❌ Error: El servidor no responde correctamente"
    echo "📋 Revisar logs con: pm2 logs ocr-pdf-server"
fi

echo "🎉 Script de despliegue terminado"