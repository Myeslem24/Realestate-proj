#!/usr/bin/env bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
CLOUDINARY_API_SECRET=EKhNF2vR2DBl7xA2gVg0JfxxFnM
