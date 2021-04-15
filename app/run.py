import sys

import uvicorn

sys.path.append('./')

from app.config import HOST, PORT


if __name__ == '__main__':
    uvicorn.run(app='api:app', reload=True, host=HOST, port=PORT, workers=2)
