FROM alpacamarkets/pylivetrader

# https://github.com/thunlp/OpenNE/issues/71
RUN pip install --upgrade numpy==1.16
