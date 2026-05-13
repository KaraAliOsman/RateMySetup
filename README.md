# RateMySetup

## PowerShell
```powershell
cd RateMySetup-main
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Git Bash
```bash
cd RateMySetup-main
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```



```
.\venv\Scripts\Activate.ps1
python manage.py runserver
```












como ultimo

```
O en Git Bash:
python -m venv venv
source venv/Scripts/activate
Instala las dependencias:
pip install -r requirements.txt
Ejecuta las migraciones:
python manage.py migrate
Inicia el servidor:
python manage.py runserver
```
