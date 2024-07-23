# MalSense

MalSense is a tool designed to detect malicious texts such as phishing and scams through text and images. Utilizing OpenAI's GPT-4 and URLScan.io, MalSense helps identify suspicious content and provides insights into its potential risks.

## Features

- **Text Analysis**: Detects suspicious content in provided text.
- **Image Analysis**: Processes and analyzes images for suspicious content.
- **URL Extraction and Scanning**: Extracts URLs from text and scans them using URLScan.io API.
- **Suspicion Scoring**: Provides a suspicion score and highlights points of suspicion.

## Requirements

- Python 3.7+
- Streamlit
- OpenAI
- Requests
- PIL (Pillow)

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/your-username/malsense.git
    cd malsense
    ```

2. Create a virtual environment:

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:

    ```sh
    pip install -r requirements.txt
    ```

4. Set up the necessary API keys in Streamlit secrets. Create a `.streamlit/secrets.toml` file and add your OpenAI and URLScan API keys:

    ```toml
    [general]
    OPENAI_API_KEY = "your_openai_api_key"
    URLSCAN_API_KEY = "your_urlscan_api_key"
    ```

## Usage

To run the application:

```sh
streamlit run app.py
