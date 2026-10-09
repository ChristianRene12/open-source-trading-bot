# open-source-trading-bot
Open-source algorithmic trading toolkit for forex and gold (XAUUSD), featuring backtesting, trade analysis, position sizing, and risk management.
# Open Source Trading Bot

An open-source Python toolkit for researching and backtesting trading strategies in forex and gold markets, including XAUUSD and USDJPY.

## Project goals

The goal is to help independent traders evaluate trading strategies, understand performance, and apply consistent risk management before risking real capital.

## Current features

- Simple moving-average crossover backtesting
- Historical closing-price CSV input
- Win rate and total return calculations
- Maximum drawdown tracking
- Configurable fast and slow moving-average periods

## Planned features

- Position sizing based on account equity and risk percentage
- Stop-loss and take-profit simulation
- Spread, commission, and slippage modelling
- Detailed trade journal and performance reports
- Support for historical XAUUSD and USDJPY data
- Unit tests and improved error handling

## Getting started

The backtesting engine uses Python's standard library.

Run a backtest with a CSV file containing a `close` column:

```bash
python backtest.py historical_prices.csv
```

Customise the moving-average periods:

```bash
python backtest.py historical_prices.csv --fast 10 --slow 30
```

## Important limitations

This project is experimental and intended for research and educational purposes. Backtest results do not guarantee future performance. The current implementation does not account for transaction costs, spread, slippage, or live-market execution.

Always validate strategies using realistic assumptions before considering live trading.

## Contributing

Contributions, bug reports, testing, and suggestions are welcome. Please document changes and include tests where possible.

## License

MIT License. See the `LICENSE` file for details.
## Running a Backtest

The project includes synthetic example prices in `sample_prices.csv`.

Run the moving-average crossover backtest:

```bash
python backtest.py sample_prices.csv
```

Customize the moving-average periods:

```bash
python backtest.py sample_prices.csv --fast 3 --slow 8
```

Include estimated trading costs and export completed trades:

```bash
python backtest.py sample_prices.csv --fast 3 --slow 8 --spread-pct 0.1 --commission-pct 0.05 --slippage-pct 0.02 --export-csv trades.csv
```

The trade log will be saved to `trades.csv` in the current working directory.

**Note:** The sample prices are synthetic, not real market data. Backtest results are for research and educational purposes and do not predict future performance.

