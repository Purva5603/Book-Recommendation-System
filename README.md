#  Book Recommendation System

A web-based **Book Recommendation System** developed using **Flask** and **PyCharm**. Users can enter a book name and get similar books as recommendations, displayed with cover images and author names.

---

##  Features

-  Enter a book name to get top recommendations  
-  Displays book cover, title, and author  
-  Flash messages for invalid input  
-  Simple login/logout authentication  
-  Clean UI using Bootstrap



##  Tech Stack

- **Python**, **Flask**, **HTML/CSS (Bootstrap)**, **Jinja2**
- **Pandas**, **NumPy**, **Pickle**
- Developed in **PyCharm**

---

##  Flask Usage

- Routes: `/` (Home), `/recommend` (Recommendation)
- Handles form submissions (POST requests)
- Renders templates with Jinja2 (`recommend.html`)
- Displays flash messages and manages user login/logout

---

##  Template: recommend.html

- Contains the input form for book name  
- Uses Bootstrap cards to display recommended books  
- Shows flash messages like "Book not found"  
- Dynamically displays content using Jinja2

---
