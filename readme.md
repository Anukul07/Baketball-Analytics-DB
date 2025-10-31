## NBA playoff teams' players analysis (2024-25)

This project is an end-to-end ETL (Extract, Transform, Load) pipeline demonstration that uses web scraping with BeautifulSoup and PostgreSQL to perform advanced analytical tasks. The core goal is to identify the top offensive and defensive contributors on every qualified team for the 2024-25 NBA playoffs and also visualize their differentials, showcasing skills in relational database design, JOINs, CTEs, and Window Functions for in-depth comparative analysis.

---

### The ETL process

1. Extract - The project begins with the Extraction phase, where Python is used alongside the requests library to fetch the raw HTML data, including player game logs, from the target website. To bypass advanced server bot detection , the specialized library curl_cffi is utilized, which ensures the requests appear to originate from a standard web browser. The primary Output of this phase is the raw HTML code of the webpages.
2. Transform - In the Transformation phase, the raw HTML is structured and cleaned. The StatsScraper class, built using Object-Oriented Programming (OOP) principles, has BeautifulSoup library to parse the raw HTML. This process extracts specific per-game statistics (Points, Assists, Steals, Blocks, Rebounds), calculates custom player scores, and prepares the data to fit the relational schema. The resulting Output is a collection of clean, structured Python dictionaries.
3. Load - Finally, the Load phase takes the clean, structured data and permanently inserts it into the analytical database. The connection is managed by psycopg2, the Python adapter for PostgreSQL. The loading script handles necessary steps like checking for and avoiding duplicate entries and linking records across tables : teams, players,regular_season_stats and playoff_stats using foreign keys. The final output populates this table, making it ready for analysis.

---

### Key analytical findings

The core analysis uses custom-weighted scores to measure offensive and defensive contributions.

The final visualization plots every team's top player by their Offensive score (Y-axis) and Defensive score (X-axis). This reveals clear player categories across the entire league.

- Two-Way Stars: Players landing in the top-right quadrant (e.g., Nikola Jokić, Giannis Antetokounmpo) who are their team's best on both ends.
- Offensive Specialists: Players in the top-left (e.g., Jalen Brunson) who excel offensively but are below average defensively for this elite group.
- Defensive Specialists: Players in the bottom-right (e.g., Rudy Gobert, Anthony Davis) who anchor their team's defense.
<img width="1339" height="1184" alt="image" src="https://github.com/user-attachments/assets/b0438c05-793a-4257-94c9-9ffd0aa1a978" />


Also, to find the top offensive player and defensive player from each team, CTEs and Window functions (Rank() OVER (Partition BY...)) were used. CTEs were used in numerous scenarios too.
<img width="1197" height="884" alt="image" src="https://github.com/user-attachments/assets/32f37bc6-14c5-4333-9744-6018c2ea8d87" />
<img width="1197" height="884" alt="image" src="https://github.com/user-attachments/assets/aca8999a-3ebc-49fc-a8dd-699be83dda3c" />

More findings or charts are at visualizations folder

---

### Technology or tools stack

- Database: PostgreSQL
- Programming language: Python
- Libraries: psycopg2, requests, curl_cffi, BeautifulSoup4, pandas, seaborn
- Code structure : Modular, Object-oriented (for scraping file)
- Analysis: Intermediate SQL (JOINs, CTEs, Window Functions)

---

### Setup and execution

1. Prerequisites

   - PostgreSQL server installed and running locally.
   - .env setup: DB_HOST= ...
     DB_PORT= ...
     DB_NAME= ...
     DB_USER= ...
     DB_PASSWORD= ...

2. Environment setup
   git clone https://github.com/Anukul07/Baketball-Analytics-DB.git
   cd Basketball-Analytics-DB
   conda env create -f environment.yml
   conda activate basketball-analytics

3. Run the ETL pipeline
   python src/main.py

4. Final analysis
   Navigate to notebooks/analysis.ipynb to run the final SQL queries and generate the charts.

---
