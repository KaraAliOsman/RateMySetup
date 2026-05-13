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
