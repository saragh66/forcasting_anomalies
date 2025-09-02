
# **RH-Predict: Human Resources Intelligence & Forecasting Engine**

**An end-to-end Business Intelligence and Machine Learning solution engineered to convert raw time-tracking data into strategic, predictive insights. This project was developed within the Data & AI department at Orange Morocco, showcasing a production-ready approach to proactive human resources management.**

---

## Executive Summary: From Reactive Reporting to Predictive Strategy

The core vision of RH-Predict is to architect an analytical nervous system for HR operations. The platform moves beyond historical reporting to address critical business questions: How do we automate the entire data lifecycle, from ingestion to strategic insight? How do we empower field managers with secure, relevant, and real-time data? Crucially, how do we transition from a reactive management model to a **predictive framework** that anticipates future workforce trends?

This platform is the answer.

## Core Architecture & Key Capabilities

RH-Predict is built on an enterprise-grade, containerized architecture designed for performance, scalability, and a frictionless user experience.

-   ### **High-Throughput Asynchronous ETL Pipeline**
    Large-scale CSV data ingestion is handled in the background by a distributed task queue powered by **Celery & Redis**. This non-blocking architecture ensures the user interface remains responsive and fluid, regardless of the data volume being processed.

-   ### **Multi-Layered Analytical Dashboards**
    Dynamic, interactive data visualizations built with **Chart.js** provide insights across all organizational levels. The system allows for drilling down from a global, company-wide overview to granular performance metrics for a specific department or individual.

-   ### **Temporal Forecasting Engine**
    At the heart of the platform lies a machine learning model leveraging **Facebook's Prophet** library. It performs time-series analysis to accurately forecast future anomaly trends, enabling the organization to shift from asking "What happened?" to "**What will happen?**"

-   ### **Zero-Trust Secure Manager Portal**
    A dedicated, authenticated portal where managers access data exclusively pertaining to their own teams. Security and data segregation are enforced at the database query level, guaranteeing strict confidentiality and need-to-know access.

-   ### **On-the-Fly PDF Report Generation**
    Any filtered data view can be instantly exported into a professional, presentation-ready **PDF** report, rendered server-side with **WeasyPrint**.

-   ### **Containerized & Portable Infrastructure**
    The entire application stack—including the Django backend, Celery workers, Redis message broker, and MySQL database—is containerized with **Docker** and orchestrated via Docker Compose. This ensures perfect environmental parity, one-command deployment, and seamless portability across systems.

---

## Technology Stack

The platform is engineered using a modern, robust, and scalable technology stack selected for enterprise reliability.

| Domain | Technology | Rationale & Strategic Role |
| :--- | :--- | :--- |
| **Application Core (Backend)** | **Django** & **Django REST Framework** | A secure, battle-tested Python framework for building complex, data-driven applications. |
| **User Experience (Frontend)** | **HTML5, CSS3, JavaScript** & **Bootstrap** | For creating clean, responsive, and intuitive user interfaces. |
| **Asynchronous Engine**| **Celery** & **Redis** | The industry standard for distributed task processing and high-performance message brokering in the Python ecosystem. |
| **Data Persistence** | **MySQL** | A proven, reliable relational database management system capable of handling millions of records. |
| **AI & Data Science** | **Pandas** & **Prophet (by Meta)** | For best-in-class data manipulation and state-of-the-art time-series forecasting. |
| **Infrastructure** | **Docker** & **Docker Compose** | Infrastructure-as-Code for reproducible, isolated, and scalable deployments. |

---

## Quick Start Guide: Deployment in a Single Command

### Prerequisites
-   Docker
-   Docker Compose

### Instructions

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/saragh66/forcasting_anomalies.git
    cd forcasting_anomalies
    ```

2.  **Configure the Environment:**
    Create a `.env` file from the provided template and populate it with your credentials.
    ```bash
    # Create the .env file
    cp env.example .env
    # Now, edit the .env file with your specific secrets
    ```

3.  **Launch the System:**
    This command builds the container images and orchestrates the launch of the entire service ecosystem.
    ```bash
    docker-compose up --build
    ```

4.  **Access the Platform:**
    Navigate to `http://127.0.0.1:8000` in your web browser.

5.  **(First Time Only) Seed the Database:**
    Open a **new terminal** to execute database initialization commands.
    -   **Create a Superuser:**
        ```bash
        docker-compose exec web python manage.py createsuperuser
        ```
    -   **Populate with Initial Data:** *(It is recommended to place seeding logic into a custom management command for production environments)*
        ```bash
        docker-compose exec web python manage.py shell < scripts/populate_db.py
        ```

---

## Author & Contact

**Sara ELGHAYATI** - Data Scientist

-   **Project developed at:** Orange Morocco, Data & AI Department
- 
-   **GitHub:** [github.com/saragh66](https://github.com/saragh66)
-   **Professional Inquiries:** [saraelghayati726@gmail.com](mailto:saraelghayati726@gmail.com)