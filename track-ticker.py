import pylivetrader.api as algo


def enter_play(context, data):
    s = context.ticker

    if not data.can_trade(s):
        return

    fast_sma = data.history(s, 'price', context.fast_sma_days, '1d').mean()
    slow_sma = data.history(s, 'price', context.slow_sma_days, '1d').mean()
    
    context.target_percentage = context.exit_percentage if fast_sma < slow_sma else context.enter_percentage

    order_target_percent(s, context.target_percentage)


def initialize(context):
    # TODO: Try gradient descent on these parameters
    context.exit_percentage = 0.1
    context.enter_percentage = 1.0
    context.fast_sma_days = 2
    context.slow_sma_days = 15
    
    context.trade_at_minute = 30
    
    context.ticker = symbol('QQQ')

    algo.schedule_function(
        enter_play,
        algo.date_rules.every_day(),
        algo.time_rules.market_open(minutes=context.trade_at_minute),
    )

#     algo.schedule_function(
#         record_vars,
#         algo.date_rules.every_day(),
#         algo.time_rules.market_close(),
#     )


# def record_vars(context, data):
#     price = data.current(context.ticker, 'price')
#     if 'start_price' not in context:
#         log.info('First price {}'.format(price))
#         context['start_price'] = price

#     current_return = context.portfolio.portfolio_value / context.portfolio.starting_cash
#     price_return = price / context['start_price']
    
#     record(
#         RELATIVE_RETURN=((current_return / price_return) - 1.0),
#         # TARGET_PERCENTAGE=context.target_percentage,
#     )
    
#     if "previous_target_percentage" not in context:
#         context.previous_target_percentage = context.target_percentage
    
#     if context.previous_target_percentage != context.target_percentage:
#         log.info("target_percentage changed to {}".format(context.target_percentage))
#     context.previous_target_percentage = context.target_percentage
