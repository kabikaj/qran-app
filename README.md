# qran-app

Web app for qran package [https://github.com/kabikaj/qran]

Visit it on render: https://qran-app.onrender.com

## Install locally (development)

```bash
pip install -r requirements.txt

uvicorn main:app --reload
```

## Install with docker

```bash
# build app
docker build -t qran-app .

# save image:
docker save -o qran-app.tar qran-app

# load and run:

docker load -i qran-app.tar
docker run -p 8000:8000 qran-app
```

## Author

Alicia González Martínez
