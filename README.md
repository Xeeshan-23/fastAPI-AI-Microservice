# fastAPI-AI-Microservice# FastAPI Task Management Microservice 

A high-performance, asynchronous REST API built with **Python 3.12**, **FastAPI**, and **SQLModel**.

## Tech Stack
- **Framework:** FastAPI
- **Database:** SQLite (SQLModel/SQLAlchemy)
- **Validation:** Pydantic
- **Server:** Uvicorn

## Features
- **CRUD Operations:** Create, Read, Update, and Delete tasks efficiently.
- **Automatic Docs:** Interactive Swagger UI integration.
- **Data Validation:** Prevents invalid data entry using Pydantic models.

## How to Run locally:

1. **Clone the repo**
   ```bash
   git clone [https://github.com/Xeeshan-23/fastAPI-AI-Microservice.git](https://github.com/Xeeshan-23/fastAPI-AI-Microservice.git)
2. **Install Dependencies:**
   pip install -r requirements.txt
3. **Run the server:**
   uvicorn main:app --reload
4. **Access the API Open:** 
   https://www.google.com/search?q=http://127.0.0.1:8000/docs