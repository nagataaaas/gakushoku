import uvicorn

from config import HOST, PORT

if __name__ == '__main__':
    uvicorn.run(app='main:app', reload=True, host=HOST, port=PORT, workers=2)
