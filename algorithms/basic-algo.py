from pylivetrader.api import order_target, symbol

def initialize(context):
    context.i = 0
    context.asset = symbol('AAPL')

def handle_data(context, data):
    short_mavg = data.history(context.asset, 'price', bar_count=15, frequency="1m").mean()
    long_mavg = data.history(context.asset, 'price', bar_count=8, frequency="1d").mean()

    if short_mavg > long_mavg:
        order_target(context.asset, 100)
    elif short_mavg < long_mavg:
        order_target(context.asset, 0)
