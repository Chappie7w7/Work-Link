from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))


#from app import create_app

#app = create_app()

#if __name__ == '__main__':
    #app.run(debug=True)
