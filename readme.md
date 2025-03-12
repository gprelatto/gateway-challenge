# Faucet API
## Challenge solved by Gonzalo Prelatto

This is a simple Django REST API application that provides a faucet service for sending Sepolia ETH to specified wallet addresses. The application includes endpoints for funding wallets and retrieving transaction statistics.

## Features

- **POST /faucet/fund**: Sends 0.0001 Sepolia ETH from a pre-configured wallet to the specified wallet address.
- **GET /faucet/stats**: Returns statistics for the number of successful and failed transactions in the last 24 hours.
- **Swagger Documentation**: Interactive API documentation available at `/swagger/`.

## Requirements

- Docker
- Docker Compose

## Setup

1. **Clone the repository:**

   ```sh
   git clone https://github.com/yourusername/gateway-challenge.git
   cd gateway-challenge
   ```

2. **Create a .env file (already provided):**

   ```sh
   # Django settings
   DEBUG=1
   SECRET_KEY=your_secret_key
   ALLOWED_HOSTS=*

   # Web3 settings
   WEB3_PROVIDER_URI=https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID
   FAUCET_PRIVATE_KEY=YOUR_PRIVATE_KEY
   FAUCET_ADDRESS=YOUR_WALLET_ADDRESS
   WEB3_CHAIN_ID=11155111 #using sepolia
   ```

3. Build and run the Docker containers:
    ```sh
    docker-compose up --build
    ```

4. Apply the database migrations (optional, sqlite db is provided for fast testing):
    ```sh
    docker-compose exec web python manage.py migrate
    ```

## Tests
The API is provided with basic unit tests that covers:

- test_fund_wallet_success: should succeed if valid wallet address is provided
- test_fund_wallet_invalid_address: should fail if invalid wallet address is provided
- test_fund_wallet_rate_limit: should fail if rate limit is exceeded
- test_faucet_stats: should return correct statistics

Run them with:
 ```sh
 docker-compose exec web python manage.py test
 ```
## Usage

1. Access Swagger to play with the endpoints
Open your web browser and navigate to http://localhost:8000/swagger/ to view the Swagger documentation and interact with the API.

2. Endpoints:
- POST /api/faucet/fund: Send Sepolia ETH to a specified wallet address.
    - Body
    ```json
        {
            "wallet_to": "0x0000000000000000000000000000000000000000"
        }
    ```
- GET /api/faucet/stats: Retrieve transaction statistics for the last 24 hours.


## Potential improvements:
- Split the service into microservices to correctly handle transaction flow. Consider the following:
    - TX Creation Service
    - TX Signature Service
    - TX Scanner Service
- Implement Service-Based database (cloud maybe), like Postgress or Mysql
- Implement Kafka for event-driven communication between services to ensure TX statuses remain up to date.
- Implement a wallet vault to prevent running out of funds (or using a wallet API like Fireblocks).
- Improve transaction processing to avoid nonce duplication (critical).
- Consider using a RabbitMQ sequential queue as a potential fix for nonce duplication issues.
- Improve test coverage to ensure comprehensive validation and reliability of the codebase.
- Apply orchestration using Kubernetes to enhance stability, scalability, and efficient management of services.
