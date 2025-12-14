# CST1510_CW2_M01088086-Saifana
CST1510 Labwork from Week 06-12 (Coursework 2)
Student Name: [Saifana Kuradiela Maryam] 
Student ID: [M01088086]
Course: CST1510 - CW2 - Multi-Domain Intelligence Platform

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
- User login / register page > dashboard access (if correct) > {Domains:} > logout
    **Domains:**
    - Cybersecurity: Analytics > CRUD Operations > AI Chat Bot
    - Data Science: Analytics > CRUD Operations > AI Chat Bot
    - IT Operations: Analytics > CRUD Operations > AI Chat Bot