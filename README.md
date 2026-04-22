## Zameen_Registry

The Zameen Registry project is about an effort to solve the problem of land and property in Pakistan. See the thing is in Pakistan sometimes people sell the same plot of the land to two or three different people and sometimes the files are fake. So these kind of frauds are the main problem here.

# Important Stats:
 Now according to the official reports from PACRA (Pakistan Credit Rating Agency), the recorded real estate market value in Pakistan is worth more than PKR 3,700 Billion. And some experts even say if we count everything, it is worth around $400 Billion. So this covers a huge part of our country's money. But because there is so much fraud and fake paper work, many people are scared to invest in this sector and also many people get scammed in all of this. So this project is like an effort to build a kind of "solution" for this huge market so that the people can buy land without fear.

The main idea of this project is not just about saving data, rather it's about checking everything automatically. Like if a plot is already being sold then the system will "lock" it so that no one else can touch it. The project also checks like if the buyer has money and also if the person's finger-print (biometric) is real or not?

# Things to Learn:
See I already know how to make simple apps with one database. But now in order to improve I need to learn new things like:

1. Microservices:
 Instead of one big project, I am making 3 small projects that can work along each other.

2. Database Sharding:
 I am using 4 different databases for this project. Like one for Punjab land, one for Sindh land, etc. Though this is mainly required when the data becomes very big but still its a new thing to learn.

3. The Transaction Coordinator:
 This part is like if a user pays money but the land system fails, then the thing is the money should be automatically refunded.

4. Distributed Tracing:
This is also a new thing to learn because as in this Full Project has logic distributed in three parts, so this will help me see like how a request travels from Project 1 to Project 2 to Project 3.


# Key Features:
1. Real Time Locking:
 The thing is when you start buying a plot, then in order to avoid the fraud that plot in the database gets locked.

2. Shard Routing:
 This part is about knowing which database to use. Like if you look for the land in Lahore, then it goes to the Punjab database. If you look for the land in Karachi, then it goes to Sindh.

3. Biometric Check:
 This part is about the use of special service/mock biometric system in order to check if the user is real or not? 

4. Safe Money Transfer:
 This part is about "Escrow" logic which is offcourse used to hold the money. Means the seller will only get the money when the land is 100% transferred.

5. Circuit Breakers: If one part of my system (like the Identity service) is down, the whole system will not crash. It will just show a "Service Busy" message. This is how professional systems work.

6. Background Tasks:
This part is about using Celery feature of django which helps to automatically cancel the deals if buyer doesn't give the money within 24 hours.



## Tech Stack: 

# Core:
Django
DRF
PostgreSQL
Service Layer Use

# Async & Distributed Logic:
Redis
Celery
Celery Beat
Transaction Coordinator

# Security & Auth:
JWT 
Internal Service API Keys

# Advanced Django Features:
Database Routers
Custom Middlewares
Django Signals
Custom Permissions
Atomic Transactions