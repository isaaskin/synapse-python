FROM python:3.9-slim

RUN pip3 install pipx && pipx install poetry && echo "export PATH=$PATH:$HOME/.local/bin" >> ~/.bashrc
