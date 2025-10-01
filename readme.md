# INDECScraping

Este proyecto utiliza el scraping web para obtener el informe actual sobre el índice de precios al consumidor (IPC) publicado por el INDEC, (instituto nacional de estadistica y censos de la república Argentina) y expone esa información en una API.

## Requisitos

- Python 3.12 o superior
- fastapi
- uvicorn
- playwright
- redis
- Entorno linux (por limitaciones de uvicorn en windows)

## Uso

El servidor está disponible en el puerto 8000.
AL acceder a localhost:8000/ipc el servidor devuelve  el siguiente json:
```
{
    "fecha": "fecha de la última actualización del      informe",
    "informe": "Texto del informe actual",
    "siguiente": "fecha de la próxima actualización"
}
```

