from python:3.9

RUN pip install --no-cache-dir pytz python-telegram-bot pyzmail36

COPY utils /opt/workdir/telegram-mail-bot/utils
COPY bot.py /opt/workdir/telegram-mail-bot/

WORKDIR /opt/workdir/telegram-mail-bot

ENV TELEGRAM_TOKEN=5815874262:AAHNNgR4YiT8rH5qsdQMA8SGoRnwSHBSCu4

CMD ["/bin/sh", "-c", "/usr/local/bin/python bot.py" ]