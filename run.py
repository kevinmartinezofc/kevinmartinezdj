from app import create_app

app = create_app()

if __name__ == "__main__":
    # Nur fuer lokale Entwicklung. Produktiv wird Gunicorn verwendet:
    #   gunicorn -w 4 -b 0.0.0.0:8000 run:app
    app.run(debug=True, host="0.0.0.0", port=5000)
