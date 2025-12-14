# CST1510_CW2_M01088086-Saifana
CST1510 Labwork from Week 06-12 (Coursework 2)
Student Name: [Saifana Kuradiela Maryam] 
Student ID: [M01088086]
Course: CST1510 -CW2 - Multi-Domain Intelligence Platform

# Week 6: GitHub Practice: Push and Pull
## Week 6 Project Description
Practicing uploading the CST1510_CW2_M01088086_Saifana repository, and utilising the push/pull feature on a linked GitHub account.

# Week 7-10: Dashboard Implementation (Pre-OOP)
## Week 7: Secure Authentication System
### Project Description
A command-line authentication system implementing secure password hashing
This system allows users to register accounts and log in with proper passwords and usernames
### Features
- Secure password hashing using bcrypt with automatic salt generation
- User registration with duplicate username prevention
- User login with password verification
- Input validation for usernames and passwords
- File-based user data persistence
### Technical Implementation
- Hashing Algorithm: bcrypt with automatic salting
- Data Storage: Plain text file (`users.txt`) with comma-separated values
- Password Security: One-way hashing, no plaintext storage
- Validation: Username (3-20 alphanumeric characters), Password (6-50 characters exlcuding space)

## Week 8: Data Pipline & CRUD (SQL)
### Project Description
Application formation of a dashboard with data formatted with pre-determined schemas in a database
The neat structure of the Application allows easy access to python packages and for debugging
### Features
- Adding, modifying, and deleting data (CRUD) from the intelligence_platform database
- Merging an connecting between tables and database
### Technical Implementation
- Migrated from file-based storage to a professional SQLite database (`intelligence_platform.db`)
- Created a complete database schema with 4 tables  
- Implemented secure authentication with bcrypt  
- Loaded CSV data efficiently using pandas  
- Built CRUD functions for all database operations  
- Secured your queries against SQL injection  
- Extracted insights using analytical SQL queries  

## Week 9: Streamlit Interface
### Project Description
The application of knowledge of the Streamlit interface and its features to create a functioning and aesthetic platform
Neat beautification of database visualizations and charts
### Features
- Viewing data visualizations for domains
- Implementing CRUD operation functionality
- Multi-page viewing of domains
### Technical Implementation
- Needs streamlit to be installed
- Run file using "streamlit run {filepath}"
- User login page > register > access to dashboard > utilize different features

## Week 10: ChatGPT OpenAI API Implementation
### Project Description
Final adjustments to Streamlit interface features with adding an AI Chat Bot
Each domain will have an AI Chat Bot with their respective specialty roles
### Features
- AI Chat Bot using ChatGPT's OpenAI API, model GPT-4o-mini 
- Able to chat with different specialists, adjust temperature, and clear/keep track of chat messages
### Technical Implementation
- .toml file in .streamlit folder has a placeholder API key, must be replaced with own API key to run AI
- Run file using "streamlit run {filepath}"
- User login / register page > dashboard access (if correct) > {domains:} > logout
    - **Domains:**
    - Cybersecurity: Analytics > CRUD Operations > AI Chat Bot
    - Data Science: Analytics > CRUD Operations > AI Chat Bot
    - IT Operations: Analytics > CRUD Operations > AI Chat Bot

# Week 11: Dashboard Implementation (OOP)
## Week 11 Project Description
Adjustment to overall project in the format of OOP for a cleaner, more polished program structure
Created models and classes for easier data package usages
### Features
- Similar website features to week 10
- Class models, for straight forward imports and cleaner code
- Features getters and setters within classes
### Technical Implementation
- .toml file in .streamlit folder has a placeholder API key, must be replaced with own API key to run AI
- Run file using "streamlit run {filepath}"
- User login / register page > dashboard access (if correct) > {domains:} > logout
    - **Domains:**
    - Cybersecurity: Analytics > CRUD Operations > AI Chat Bot
    - Data Science: Analytics > CRUD Operations > AI Chat Bot
    - IT Operations: Analytics > CRUD Operations > AI Chat Bot

# Instructions to Run App:
1. Check requirements.txt file to view any downloadable modules not included within default Python package
2. Add own API key to the secrets.toml file under the .streamlit folder under Week07-Week10_App or Week11_App
    - (TIP: File path should be like {projectroot}/.streamlit/secrets.toml)
3. Unzip app package and run from 1_Home.py file, or run from terminal "streamlit run {projectroot}/1_Home.py"
4. Will display Home page with authentication features, namely: Login/ Register
5. Register or login, after successful attempts > takes user to the first domain page "Cybersecurity"
6. Navigate on the page through the tabs: Analytics > Record Mangement > AI Chat Bot
- Analytics: Filters will adjust for all visualizations,  users may freely navigate between charts and dropdown menus
- Record Management: Users may freely navigate through CRUD operation buttons, and check record chart for updates
- AI Chat Bot: Users may chat freely with specialist AI Chat Bots
    - (TIP: If issues arise with the API key, check whether the secrets.toml file has the correct API key)
7. Navigate through each page: Cybersecurity > Data Science > IT Operations and repeat step 6 freely
8. Log out