pip install -r requirements.txt

python manage.py migrate

python manage.py runserver


O SINO

Instalación y ejecución
cd RateMySetup-main
python -m venv venv
Activar entorno

Git Bash:

source venv/Scripts/activate

PowerShell:

.\venv\Scripts\Activate.ps1
Instalar dependencias
pip install -r requirements.txt

o

python -m pip install -r requirements.txt
Base de datos
python manage.py makemigrations
python manage.py migrate
Ejecutar
python manage.py runserver

python manage.py createsuperuser
