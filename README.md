# FastAPI Address Book Application

This is a simple address book application built using FastAPI, SQLite, and SQLAlchemy. Users can create, update, and delete addresses. Additionally, users can retrieve addresses within a given distance from a specified location.

## Requirements

- Python 3.9
- Install Python 3.9 and create a virtual environment using the command:
  ```bash
  python -m venv venv
  ```

## Installation

1. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux:
     ```bash
     source venv/bin/activate
     ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

To run the application, use the following command:
```bash
uvicorn main:app --reload
```

After running the command, you can access the FastAPI Swagger documentation by visiting [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## API Endpoints

- `POST /addresses/`: Create a new address.
- `PUT /addresses/{address_id}`: Update an existing address.
- `DELETE /addresses/{address_id}`: Delete an existing address.
- `GET /addresses/distance/`: Retrieve addresses within a given distance from a specified location.

## Notes

- The application uses SQLite as the database backend.
- Ensure that the virtual environment is activated before running the application.
- Make sure to replace `{address_id}` with the actual ID of the address when using the update and delete endpoints.

