# Social Media Analysis for Depression Detection

This project collects, processes, and analyzes social media data (Facebook and Twitter) to detect signs of depression. It includes a web scraping system, a processing and analysis API, and a MongoDB database for data storage.

## Table of Contents

- [Features](#features)
- [Project Architecture](#project-architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Data Scraping](#data-scraping)
  - [API Endpoints](#api-endpoints)
- [Docker Deployment](#docker-deployment)
- [Data Structure](#data-structure)
- [Examples](#examples)


## Features

### Data Collection
- **Web Scraping**
  - Facebook posts collection by hashtag
  - Twitter tweets collection by keyword
  - Raw data storage in MongoDB

### Data Processing
- Text cleaning and normalization
- Stopwords and emoji removal
- Natural language processing

### Analysis
- **Sentiment Analysis**
  - Classification into three categories:
    - `POSITIVE`: Content expressing positive emotions
    - `NEGATIVE`: Content expressing negative emotions
    - `NEUTRAL`: Neutral or undetermined content
  - Model: `cardiffnlp/twitter-roberta-base-sentiment-latest`
  - Specifically trained for social media sentiment analysis

- **Theme Detection**
  - Mental health disorder classification:
    - `Depression`: Depressive disorders
    - `Anxiety`: Anxiety disorders
    - `Bipolar Disorder`: Bipolar disorders
    - `Schizophrenia`: Schizophrenia
    - `Eating Disorder`: Eating disorders
    - `Substance Abuse`: Substance-related disorders
  - Zero-shot classification using `facebook/bart-large-mnli`
  - No specific training required for new categories

### API Endpoints
- Data transformation endpoints
- Analysis and prediction endpoints
- Status monitoring

## Project Architecture

```
.
├── api_nett/                  # API source code
│   ├── __init__.py
│   ├── functions.py          # Utility functions and database operations
│   ├── main.py               # API endpoints
│   └── ml.py                 # Machine learning models
├── scrap_twitter.py          # Twitter scraping script
├── scrape_facebook.py        # Facebook scraping script
├── charger_mongo.py          # MongoDB data loader
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile                # Docker configuration
├── requirements.txt          # Python dependencies
└── .env                      # Environment variables
```

## Prerequisites

- Python 3.8+
- MongoDB 4.4+
- Docker and Docker Compose
- Google Chrome browser
- ChromeDriver

## Installation

1. Clone the repository:
   ```bash
   git clone [REPOSITORY_URL]
   cd test_dep
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # OR
   .\venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download NLTK resources:
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

## Configuration

Create a `.env` file in the project root with the following variables:

```env
# MongoDB
MONGODB_URI=mongodb://root:root@localhost:27017/?authSource=admin
MONGODB_DB=depression_social_media
```

## Usage

### Data Scraping

#### Facebook
```bash
python scrape_facebook.py
```

#### Twitter
```bash
python scrap_twitter.py
```

### API Endpoints

Start the API server:
```bash
uvicorn api_nett.main:app --reload
```

#### Available Endpoints:

1. **Transform Facebook Posts**
   ```bash
   curl -X POST "http://localhost:8000/transform_facebook"
   ```

2. **Analyze Facebook Posts**
   ```bash
   curl -X POST "http://localhost:8000/predict_facebook"
   ```

3. **Transform Tweets**
   ```bash
   curl -X POST "http://localhost:8000/transform_twitter"
   ```

4. **Analyze Tweets**
   ```bash
   curl -X POST "http://localhost:8000/predict_twitter"
   ```

## Docker Deployment

1. Build the containers:
   ```bash
   docker-compose build
   ```

2. Start the services:
   ```bash
   docker-compose up -d
   ```

3. Stop the services:
   ```bash
   docker-compose down
   ```

## Data Structure

### MongoDB Collections
- `post_brut_facebook`: Raw Facebook posts
- `post_brut_twitter`: Raw Twitter tweets
- `post_transformed_facebook`: Processed Facebook posts
- `post_predicted_facebook`: Analyzed Facebook posts
- `post_transformed_twitter`: Processed tweets
- `post_predicted_twitter`: Analyzed tweets

## Examples

### Complete Analysis Pipeline

1. Scrape Facebook data:
   ```bash
   python scrape_facebook.py
   ```

2. Transform the data:
   ```bash
   curl -X POST "http://localhost:8000/transform_facebook"
   ```

3. Run sentiment and theme analysis:
   ```bash
   curl -X POST "http://localhost:8000/predict_facebook"
   ```

4. View results in MongoDB:
   ```javascript
   use depression_social_media
   db.post_predicted_facebook.find().pretty()
   ```

## Troubleshooting

### Scraping Issues
- Check your internet connection
- Verify Chrome and ChromeDriver versions match
- Ensure you're not being rate-limited

### MongoDB Connection Issues
- Verify MongoDB is running
- Check credentials in `.env`
- Ensure port 27017 is accessible

### API Issues
- Check if all dependencies are installed
- Review Docker logs if using containers
- Verify port 8000 is available




