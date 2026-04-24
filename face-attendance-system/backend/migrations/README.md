Use Flask-Migrate to generate migrations:

```bash
flask db init
flask db migrate -m "init schema"
flask db upgrade
```
