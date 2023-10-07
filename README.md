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

6. **Configurate your chatapp**

   Go to [config.py](config.py) and set ALL of the variables to your desired value. `- All are required.`

7. **Sync your database**

   Just use the command ``python manage.py migrate``

9. **Run the Development Server:**

   Start the development server by running:

   ```bash
   python manage.py runserver
   ```

   The development server will be available at `http://127.0.0.1:8000/` by default.

## Usage

1. **Access the Admin Panel:**

   You can access the Django admin panel at `http://127.0.0.1:8000/admin` and log in with the first account registered. Here, you can manage users, chat rooms, and other application data.

2. **Access the Chat Application:**

   The chat application can be accessed at `http://127.0.0.1:8000`. Users can register, log in, create chat rooms, and participate in real-time conversations.

## Customization

You can customize the project further by modifying the Django settings, adding new features, or changing the frontend templates. Refer to the Django documentation for more information on customization: [Django Documentation](https://docs.djangoproject.com/en/3.2/)

## Contributing

If you'd like to contribute to the project, feel free to submit pull requests or open issues on the GitHub repository.

## New Releases

To update your app without loosing data, keep the [db.sqlite3](db.sqlite3) file the same as you have, just replace all other files with the new ones. Then run ``python manage.py migrate`` to apply the changes to the database.

## License

This project is licensed under the MPL License - see the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions or need further assistance, please contact [on Discord (https://discord.gg/SB9gbN265N)](https://discord.gg/SB9gbN265N).

Enjoy using ychat.dev!
![image](https://github.com/CutyCat2000/ychat.dev/assets/132785498/4d6731f6-ee24-493d-8c82-4734696302de)
![image](https://github.com/CutyCat2000/ychat.dev/assets/132785498/2bcce2c9-2706-465d-876e-846c6ca14834)