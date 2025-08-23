# flights-api
REST API built with FastAPI to search flight journeys with up to two flight events. It retrieves data from an external API and returns valid journeys filtered by date, origin, destination, and constraints like max 24h duration and 4h layover. Async, fast, and integration-ready.

docker build -t fligth-image .
sudo docker run -d -p 8000:8000 --name flight-container fligth-image