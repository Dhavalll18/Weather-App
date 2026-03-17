# Weather Web App (Django + OpenWeather + OpenAI)

Production-ready weather web application with:

- City search
- Current weather (temperature, humidity, wind, condition)
- 5-day forecast
- AI-generated natural-language weather summary
- Responsive UI with loading spinner and robust error handling

## Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, JavaScript (vanilla)
- **APIs:** OpenWeather API + OpenAI API

## Project Structure

```text
Weather-App/
├── manage.py
├── requirements.txt
├── .env.example
├── weather_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── weather/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── services.py
    ├── tests.py
    ├── urls.py
    ├── views.py
    ├── migrations/
    │   └── __init__.py
    ├── templates/weather/
    │   └── index.html
    └── static/weather/
        ├── app.js
        └── styles.css
```

## API Endpoint

- `GET /get-weather/?city=<city_name>`

### Success Response

```json
{
  "city": "London",
  "country": "GB",
  "current": {
    "temperature": 15.2,
    "humidity": 67,
    "wind_speed": 4.1,
    "condition": "Clouds",
    "description": "broken clouds"
  },
  "forecast": [
    {
      "date": "2026-03-17",
      "temp_min": 8.1,
      "temp_max": 16.9,
      "condition": "Rain"
    }
  ],
  "ai_summary": "Expect a cool, cloudy day..."
}
```

### Error Response

```json
{
  "error": "City not found. Please try a different city."
}
```

## Setup & Run Instructions

1. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Then export variables from `.env` in your shell or configure them in your runtime environment.
4. **Apply migrations**
   ```bash
   python manage.py migrate
   ```
5. **Run development server**
   ```bash
   python manage.py runserver
   ```
6. Open: `http://127.0.0.1:8000/`

## Environment Variables

- `OPENWEATHER_API_KEY` (**required**) for weather data.
- `OPENAI_API_KEY` (optional but recommended) for AI weather summary.
- `OPENAI_MODEL` (optional, default: `gpt-4o-mini`).
- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS` for Django settings.

## Notes

- If `OPENAI_API_KEY` is unavailable, the app gracefully falls back to a deterministic local summary.
- Frontend uses `fetch()` to consume `/get-weather/` and displays errors without page reload.
- UI includes a loading spinner and responsive layout for mobile and desktop.
