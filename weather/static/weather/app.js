const form = document.getElementById('weather-form');
const cityInput = document.getElementById('city-input');
const spinner = document.getElementById('spinner');
const errorMessage = document.getElementById('error-message');
const weatherResult = document.getElementById('weather-result');
const locationEl = document.getElementById('location');
const tempEl = document.getElementById('temp');
const humidityEl = document.getElementById('humidity');
const windEl = document.getElementById('wind');
const conditionEl = document.getElementById('condition');
const aiSummaryEl = document.getElementById('ai-summary-text');
const forecastGrid = document.getElementById('forecast-grid');

function setLoading(loading) {
  spinner.classList.toggle('hidden', !loading);
}

function setError(message = '') {
  const hasError = Boolean(message);
  errorMessage.textContent = message;
  errorMessage.classList.toggle('hidden', !hasError);
}

function renderForecast(forecast) {
  forecastGrid.innerHTML = '';
  forecast.forEach((day) => {
    const node = document.createElement('article');
    node.className = 'forecast-item';
    node.innerHTML = `
      <h4>${day.date}</h4>
      <p>${day.condition}</p>
      <p>${day.temp_min}°C - ${day.temp_max}°C</p>
    `;
    forecastGrid.appendChild(node);
  });
}

function renderWeather(payload) {
  locationEl.textContent = `${payload.city}, ${payload.country}`;
  tempEl.textContent = `${payload.current.temperature} °C`;
  humidityEl.textContent = `${payload.current.humidity}%`;
  windEl.textContent = `${payload.current.wind_speed} m/s`;
  conditionEl.textContent = payload.current.condition;
  aiSummaryEl.textContent = payload.ai_summary;
  renderForecast(payload.forecast);
  weatherResult.classList.remove('hidden');
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const city = cityInput.value.trim();
  if (!city) {
    setError('Please enter a city name.');
    return;
  }

  setLoading(true);
  setError('');
  weatherResult.classList.add('hidden');

  try {
    const response = await fetch(`/get-weather/?city=${encodeURIComponent(city)}`);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Failed to fetch weather data.');
    }

    renderWeather(data);
  } catch (error) {
    setError(error.message || 'Something went wrong.');
  } finally {
    setLoading(false);
  }
});
