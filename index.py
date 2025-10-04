from app import app

# Vercel expects the WSGI application to be called 'application'
application = app

if __name__ == "__main__":
    application.run()
