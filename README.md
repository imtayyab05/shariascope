# ShariaScope

AI-powered Shariah compliance screening for listed companies.

## Setup Instructions

1. **Install Requirements:**
   Make sure you have Python installed. Then, run the following command to install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables:**
   Copy the provided `.env` placeholder or edit the existing `.env` file to include your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

3. **Run the Application:**
   Start the Flask application by running:
   ```bash
   flask run
   ```
   Alternatively, run:
   ```bash
   python app.py
   ```
   The application will be accessible at `http://127.0.0.1:5000/`.
