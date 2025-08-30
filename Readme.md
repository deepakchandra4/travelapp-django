

`markdown
# Travel Booking Application

A Django-based travel booking web application.

## Local Setup

1. Clone the repository:  
   
   git clone https://github.com/deepakchandra4/travelapp-django
   cd travelapp-django
`

2. Create and activate a virtual environment:

   
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   

3. Install dependencies:

   
   pip install -r requirements.txt
   

4. Run database migrations:

   
   python manage.py makemigrations
   python manage.py migrate
   

5. Create a superuser (optional):

   
   python manage.py createsuperuser
   

6. Start the development server:

   
   python manage.py runserver
   

7. Access the app: Open `http://127.0.0.1:8000/` in your browser.

8. Run tests (optional):

   
   python manage.py test
   
   This will run 21 test cases covering:
   - Model creation and validation
   - View functionality and authentication
   - Booking system and seat management
   - User registration and profile updates
   - Search and filtering features



