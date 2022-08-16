# Quick Start

```bash
# Add your DATABASE URI in app.py

# Install virtualenv
pip install virtualenv
# activate it 
source env/scripts/activate
# and then install requirements in it


# Server on localhost:5000
python app.py or flask shell
```

# DB commands shell
```bash
export FLASK_APP=app.py (Bash) or set FLASK_APP=app.py (cmd)
flask shell (Bash) or python (cmd)
>>> from app import db
>>> db.create_all()
>>> exit()
```
