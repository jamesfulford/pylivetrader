from zipline.pipeline import Pipeline
from pipeline_live.data.alpaca.factors import SimpleMovingAverage
from pipeline_live.data.alpaca.pricing import USEquityPricing

from pylivetrader.api import *
from pylivetrader.algorithm import date_rules, time_rules

import logbook

log = logbook.Logger('algo')


def initialize(context):
    log.info('initialize')
    ma = SimpleMovingAverage(inputs=[USEquityPricing.close], window_length=15)

    pipe = Pipeline(
        columns={
            'crossing_line': ma
        },
        screen=(USEquityPricing.volume.latest > 1000000)
    )
    attach_pipeline(pipe, name="ma_pipeline")

    context.N = 70
    context.RISE_ABOVE = 1.0
    context.FALL_BELOW = context.RISE_ABOVE
    context.MIN_CASH_FOR_ENTERING = 200
       
    # Schedule times to enter trades
    schedule_function(enter_handler, date_rules.every_day(), time_rules.market_open(minutes=40))
    schedule_function(enter_handler, date_rules.every_day(), time_rules.market_close(minutes=40))
    
    for minutes in range(5, 5 * 91, 5):
        schedule_function(exit_handler, date_rules.every_day(), time_rules.market_open(minutes=5))

def before_trading_start(context, data):
    log.info('before_trading_start')
    pipeline_results_today = pipeline_output('ma_pipeline')
    context.pipeline_results_today = pipeline_results_today

#
# Helpers
#

def is_invested(ticker, context, _data):
    return ticker in context.portfolio.positions or ticker in get_open_orders()

def has_open_order(ticker):
    return ticker in get_open_orders()

def active_trades(context):
    return context.portfolio.positions.keys()

#
# Handlers
#

def exit_handler(context, data):
    log.info('exit_handler')
    pipeline_results_today = context.pipeline_results_today
    
    active_sid_tuples = list(filter(lambda s: data.can_trade(s[0]), pipeline_results_today.itertuples()))

    exits = list(filter(lambda s: is_invested(s[0], context, data) and not has_open_order(s[0]) and (data.current(s[0], 'price') / s.crossing_line) < context.FALL_BELOW, active_sid_tuples))

    for exit in exits:
        s = exit[0]
        order_target_value(s, 0)


def enter_handler(context, data):
    log.info('exit_handler')
    pipeline_results_today = context.pipeline_results_today

    current_active_trades = active_trades(context)
    currently_in = len(current_active_trades)
    shots = context.N - currently_in
    
    active_sid_tuples = list(filter(lambda s: data.can_trade(s[0]), pipeline_results_today.itertuples()))

    if shots <= 0 or context.portfolio.cash < context.MIN_CASH_FOR_ENTERING:
        log.info('DAY: In {}, Have {} shots left'.format(currently_in, shots))
        return
    
    enters = list(filter(lambda s: (not is_invested(s[0], context, data)) and (data.current(s[0], 'price') / s.crossing_line) > context.RISE_ABOVE, active_sid_tuples))
    opportunities = len(enters)
    
    target_stake = context.portfolio.cash / shots
    
    log.info('DAY: In {}, Taking {} (of {}) shots at ${} apiece'.format(currently_in, shots, opportunities, target_stake))

    # Enter new opportunities
    for enter in sorted(enters, key=lambda s: (data.current(s[0], 'price') / s.crossing_line))[:shots]:
        s = enter[0]
        order_target_value(s, target_stake)
