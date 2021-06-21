#!/bin/bash
gunicorn wsgi:server --bind 0.0.0.0:80