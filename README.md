# [ychat.dev](https://ychat.dev)

## Introduction

Welcome to the ychat.dev Django project! This is a simple chat application where users can create accounts, log in, and engage in real-time conversations. To get started, follow the installation and run guide below.

## Installation

Before running the project, ensure that you have Python and Django installed on your system. If not, you can download and install Python from [python.org](https://www.python.org/downloads/) and Django using pip:

```bash
pip install Django
```

1. **Clone the Repository:**

   Clone this repository to your local machine using Git:

   ```bash
   git clone https://github.com/CutyCat2000/ychat.dev.git
   ```

2. **Navigate to the Project Directory:**

   Change your current working directory to the project folder:

   ```bash
   cd ychat.dev
   ```

3. **Create a Virtual Environment (Optional but recommended):**

   It's a good practice to create a virtual environment for your project to isolate dependencies. You can create a virtual environment using `venv` (Python 3.3+):

   ```bash
   python -m venv venv
   ```

4. **Activate the Virtual Environment (Optional but recommended):**

   On Windows:

   ```bash
   venv\Scripts\activate
   ```

   On macOS and Linux:

   ```bash
   source venv/bin/activate
   ```

5. **Install Dependencies:**

   Install the project dependencies using pip:

   ```bash
   pip install -r requirements.txt
   ```

6. **Database Migration:**

   Run database migrations to set up the database schema:

   ```bash
   python manage.py migrate
   ```

7. **Create a Superuser:**

   To create an admin superuser account, run the following command and follow the prompts:

   ```bash
   python manage.py createsuperuser
   ```

8. **Run the Development Server:**

   Start the development server by running:

   ```bash
   python manage.py runserver
   ```

   The development server will be available at `http://127.0.0.1:8000/` by default.

## Usage

1. **Access the Admin Panel:**

   You can access the Django admin panel at `http://127.0.0.1:8000/admin/` and log in with the superuser credentials you created earlier. Here, you can manage users, chat rooms, and other application data.

2. **Access the Chat Application:**

   The chat application can be accessed at `http://127.0.0.1:8000/`. Users can register, log in, create chat rooms, and participate in real-time conversations.

## Customization

You can customize the project further by modifying the Django settings, adding new features, or changing the frontend templates. Refer to the Django documentation for more information on customization: [Django Documentation](https://docs.djangoproject.com/en/3.2/)

## Contributing

If you'd like to contribute to the project, feel free to submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the MPL License - see the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions or need further assistance, please contact [evilfiredragon53@gmail.com](evilfiredragon53@gmail.com).

Enjoy using ychat.dev!
![image](https://github.com/CutyCat2000/ychat.dev/assets/132785498/4d6731f6-ee24-493d-8c82-4734696302de)
