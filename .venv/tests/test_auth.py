import pytest
from app import create_app
from extensions import db


def test_register_successful():
    app = create_app()
    test_email = "test@example.com"
    test_password = "123456"
    test_first_name = "Alex"
    test_last_name = "Sultanov"
    dictionary = {
        "email": test_email,
        "password": test_password,
        "first_name": test_first_name,
        "last_name": test_last_name
    }
    with app.app_context():
        db.create_all()
    client = app.test_client()
    response = client.post('/auth/register',json = dictionary)
    assert response.status_code == 201
    
def test_register_duplicates():
    app = create_app()
    test_email = "test@example.com"
    test_password = "123456"
    test_first_name = "Alex"
    test_last_name = "Sultanov"
    dictionary = {
        "email": test_email,
        "password": test_password,
        "first_name": test_first_name,
        "last_name": test_last_name
    }
    client = app.test_client()
    response = client.post('/auth/register',json= dictionary)
    assert response.status_code == 409
    

    



    
    


