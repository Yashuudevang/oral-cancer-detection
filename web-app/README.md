# Web Application Project

This project is a simple web application built using Flask that includes user registration and login functionality. 

## Project Structure

```
web-app
├── src
│   ├── app.py                # Main application file
│   ├── templates             # HTML templates
│   │   ├── base.html         # Base template
│   │   ├── login.html        # Login page template
│   │   └── register.html     # Registration page template
│   ├── static                # Static files
│   │   ├── css               # CSS files
│   │   │   └── styles.css    # Styles for the application
│   │   └── js                # JavaScript files
│   │       └── scripts.js     # Scripts for interactivity
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd web-app
   ```

2. **Create a virtual environment**:
   ```
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. **Install the required dependencies**:
   ```
   pip install -r requirements.txt
   ```

5. **Run the application**:
   ```
   python src/app.py
   ```

6. **Access the application**:
   Open your web browser and go to `http://127.0.0.1:5000`.

## Usage

- Navigate to the registration page to create a new account.
- After registration, you can log in using your credentials on the login page.

## License

This project is licensed under the MIT License.