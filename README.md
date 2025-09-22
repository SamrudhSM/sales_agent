# sales_agent
building a complete e-commerce web application using Flask for the backend and a SQLite database. The frontend uses HTML with Tailwind CSS for styling.

Here's a summary of the key features:
Full User System: You have a complete user authentication system with signup, login, and session management to track who is using the site.
E-commerce Functionality: The site includes a product display page with search/filter, a shopping cart that users can add items to, and a checkout process.
Purchase History: When a user checks out, their cart items are moved to a purchases table, creating a permanent record of their shopping history .
Personalized AI Sales Bot: This is the core feature. You've integrated the Google Gemini API to create a smart sales assistant that:
Knows who the user is.

Can see the user's current cart and past purchases.
Uses this information to provide intelligent, personalized product recommendations to help the user and drive sales.
We've worked together to build this system from the ground up, including fixing bugs and refining the AI's prompts to make it a powerful tool.


AI-Powered E-Commerce Sales Agent
This project is a fully functional e-commerce web application built with Python and a SQLite database. Its standout feature is a personalized AI sales assistant powered by Google's Gemini API. The AI acts as a personal shopper, providing intelligent and context-aware product recommendations based on the user's live cart data and past purchase history.

Features
Full User Authentication: Secure user signup, login, and logout functionality with session management.

Dynamic Product Catalog: Browse a complete product catalog loaded from the database, with live search and category filtering.

Shopping Cart: Add items to a persistent shopping cart, view cart contents, and update quantities.


Checkout & Purchase History: A complete checkout process that saves cart items to a permanent purchase history for each user. 

Personalized AI Sales Assistant:

Context-Aware: The AI knows the user's name, current cart items, and past purchases.

Intelligent Recommendations: Provides smart suggestions for complementary products to enhance the shopping experience and drive sales.

Interactive Chat: A smooth chat interface in a popup modal that correctly formats AI responses (e.g., bold text).

Technology Stack
Backend: Python, Flask

Database: SQLite

Frontend: HTML, Tailwind CSS,  JavaScript

AI: Google Gemini API

Environment Management: python-dotenv
