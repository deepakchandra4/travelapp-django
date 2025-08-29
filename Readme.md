# Travel Booking Application

Simple Django app to view travel options, book tickets, and manage bookings.

## Setup

1. Create virtual environment and install dependencies

```bash
python -m venv .venv
.venv\\Scripts\\activate  # Windows PowerShell
pip install -r requirements.txt
```

2. Configure MySQL and apply migrations

```bash
REM Ensure MySQL is running and create DB (adjust user/password as needed)
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS travelapp_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

REM Run migrations
python manage.py migrate

REM Create admin user
python manage.py createsuperuser
```

3. Run server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Features

- Browse and filter travel options (type, source, destination, date)
- Book seats with validation and messages
- View current and past bookings; cancel to restore seats
- User registration, login/logout, and simple profile update

## Database: MySQL (default)

This project is configured to use MySQL out of the box via PyMySQL.

1) Install dependencies:

```bash
pip install -r requirements.txt
```

2) Ensure MySQL server is running and create the database:

```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS travelapp_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

3) Environment-specific overrides (optional): set user/password via env vars and in `travelapp/settings.py` if needed. Default user is `root` with empty password on `127.0.0.1:3306`.

## Deploy

- You can deploy on PythonAnywhere easily by uploading the project and configuring WSGI.
- Or deploy on any cloud that supports Django.

# 2. What each important file does (brief + why it matters)

* **manage.py**
  Small utility script. You run commands with it:

  * `python manage.py runserver`
  * `python manage.py makemigrations`
  * `python manage.py migrate`
  * `python manage.py createsuperuser`
  * `python manage.py test`

* **travelapp/settings.py**
  Core config:

  * `INSTALLED_APPS` — tells Django which apps to load (must include `'bookings'`).
  * `DATABASES` — which DB to use (SQLite default; you can switch to MySQL).
  * `DEBUG`, `ALLOWED_HOSTS`, `SECRET_KEY` — security & environment. Don’t expose SECRET\_KEY publicly.

* **travelapp/urls.py**
  Root URL router. It includes app routes: example:

  ```py
  path('', include('bookings.urls'))
  ```

* **travelapp/wsgi.py / asgi.py**
  Entry point for deploying (Gunicorn / uWSGI for production). Not used directly when running `runserver`, but crucial for deployment.

* **bookings/models.py**
  Your database models (tables). E.g.:

  * `TravelOption` (type, source, destination, departure\_datetime, price, available\_seats)
  * `Booking` (user FK, travel\_option FK, num\_seats, total\_price, booking\_date, status)
    Django uses these model classes to create DB tables via migrations.

* **bookings/admin.py**
  Registers models for the Django admin so you can manage TravelOption and Booking through `/admin/`. You can configure `list_display`, `list_filter`, `search_fields` here to make admin nicer.

* **bookings/views.py**
  Functions (or classes) that handle requests. Example flow:

  * `travel_list` queries TravelOption objects and renders template `travel_list.html`.
  * `create_booking` receives POST with seat count, validates, creates Booking, updates available seats.

* **bookings/forms.py**
  Django Forms for input validation (e.g., `BookingForm`). Good place to check `num_seats <= available_seats` and to show friendly error messages on the webpage.

* **bookings/urls.py**
  App-level routing. Example:

  ```py
  path('', views.travel_list, name='travel_list')
  path('travel/<int:pk>/', views.travel_detail, name='travel_detail')
  path('travel/<int:pk>/book/', views.create_booking, name='create_booking')
  ```

* **bookings/templates/**
  HTML files for display. Use template inheritance: `base.html` contains header/footer; other templates extend it:

  ```django
  {% extends 'base.html' %}
  {% block content %} ... {% endblock %}
  ```

* **bookings/static/**
  CSS, JS, images. During development Django serves them; in production run `collectstatic`.

* **migrations/**
  Auto-generated files that describe DB changes. They are created by `makemigrations` and applied by `migrate`. Commit migration files to source control.

# 3. Request lifecycle (how a page loads — the MVT flow)

1. **Browser** requests `http://127.0.0.1:8000/`.
2. **Django URL dispatcher** (project `urls.py`) checks URL patterns, finds app `bookings.urls`.
3. **App URLconf** (`bookings/urls.py`) maps the path (e.g., `''`) to a **view** function (`travel_list`).
4. **View** runs: it may query the database via the **Model** (`TravelOption.objects.filter(...)`), prepare a context dict and call `render(request, 'bookings/travel_list.html', context)`.

   * QuerySets are lazy — only evaluated when template iterates or length is checked.
5. **Template** renders HTML (using variables passed from view), and the HttpResponse is returned to the browser.

# 4. Important Django concepts (as a beginner)

* **ORM (Object Relational Mapper)**
  Work with DB using Python: `TravelOption.objects.create(...)`, `TravelOption.objects.filter(source='DEL')`. Avoid raw SQL unless needed.

* **Migrations**
  Source-controlled blueprint of DB changes. Workflow:

  ```
  python manage.py makemigrations
  python manage.py migrate
  ```

* **Admin**
  Built-in UI to manage models. Create superuser:

  ```
  python manage.py createsuperuser
  ```

  Visit `/admin/`.

* **Forms & Validation**
  Put validation logic in `forms.py` (or model `clean()` methods). Show errors in template with `{{ form.non_field_errors }}` and `{{ form.field.errors }}`.

* **Authentication**
  Django provides authentication: `django.contrib.auth`. Use decorators:

  ```py
  from django.contrib.auth.decorators import login_required
  @login_required
  def create_booking(...):
      ...
  ```

* **Transaction & Race conditions**
  For booking seats, use `transaction.atomic()` and `select_for_update()` to lock rows and avoid overselling seats.

* **Static & Media files**

  * Static: CSS/JS/images (`static/`), run `collectstatic` for production.
  * Media: user-uploaded files (not used here).

# 5. Common commands you’ll use

* Create virtualenv (Windows):

  ```
  python -m venv .venv
  .venv\Scripts\activate
  pip install -r requirements.txt
  ```
* Make & apply migrations:

  ```
  python manage.py makemigrations
  python manage.py migrate
  ```
* Run server:

  ```
  python manage.py runserver
  ```
* Shell to create objects quickly:

  ```
  python manage.py shell
  >>> from bookings.models import TravelOption
  >>> TravelOption.objects.create(type='Bus', source='Delhi', destination='Agra', departure_datetime='2025-09-01 08:00', price=500, available_seats=40)
  ```
* Create admin:

  ```
  python manage.py createsuperuser
  ```
* Reset admin password:

  ```
  python manage.py changepassword admin
  ```
* Run tests:

  ```
  python manage.py test
  ```

# 6. How to add seed data quickly

* **Admin UI:** easiest — go to `/admin/` and click *Add Travel option*.
* **Django shell** (fast):

  ```py
  python manage.py shell
  from bookings.models import TravelOption
  from django.utils import timezone
  TravelOption.objects.create(type='Flight', source='DEL', destination='BOM',
                              departure_datetime=timezone.now() + timedelta(days=2),
                              price=3000, available_seats=120)
  ```

# 7. Debugging tips (common errors & fixes)

* `no such table: bookings_traveloption` → You forgot `migrate`. Run `makemigrations` and `migrate`.
* `Model class ... isn't in INSTALLED_APPS` → add your app to `INSTALLED_APPS`.
* Template not found → check `TEMPLATES['DIRS']` and template path; use the `{% extends 'base.html' %}` correct path.
* Static file not loading in production → run `collectstatic` and configure server to serve `/static/`.
* Permissions / secret key issues on deploy → use environment variables (never commit SECRET\_KEY).

# 8. Security & production notes (brief)

* Set `DEBUG=False` in production.
* Set `ALLOWED_HOSTS` to your domain or host IP.
* Use a secure `SECRET_KEY` via environment variable.
* Configure HTTPS (TLS), use gunicorn + nginx or PythonAnywhere's config.
* Don’t use SQLite for heavy production; use MySQL or PostgreSQL.

# 9. Next learning steps (practical)

* Learn basic Django tutorial: models, templates, views.
* Build small features:

  * Add search by source/destination.
  * Add pagination (already in starter).
  * Add unit tests for booking flows.
* Learn Git: `git init`, `.gitignore` (exclude `.venv`, `db.sqlite3`), push to GitHub.
* Try deploying to PythonAnywhere (easier) or EC2 (more setup).

# 10. Quick checklist to keep going

* [ ] Make sure `bookings` is in `INSTALLED_APPS`.
* [ ] `python manage.py makemigrations` then `migrate`.
* [ ] `createsuperuser` → `/admin/` → add TravelOptions.
* [ ] Test booking flow on UI; try to overbook to see validation.
* [ ] Add unit tests in `bookings/tests.py`.
* [ ] Commit code and push to GitHub.

---

If you want, next I can:

* Walk you line-by-line through your actual `models.py`, `views.py`, and `templates/` (I can paste explanations for each function and block).
* Show you how to create a seed script (management command or fixture) to populate the DB with sample TravelOptions.
* Help create a `.gitignore` and GitHub README and push instructions.

Which of those would help most right now?
