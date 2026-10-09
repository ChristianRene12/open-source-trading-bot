# Open Source Trading Bot

A Python-based trading research project featuring a moving-average crossover backtester, risk management utilities, automated tests, and CSV trade exports.

The project is designed to explore trading strategies, evaluate historical price data, and demonstrate software engineering practices such as testing, input validation, and continuous integration.

## Features

- **Moving-average strategy:** Generates trades using fast and slow simple moving average crossovers.
- **Backtesting:** Evaluates a strategy against historical closing prices.
- **Trading costs:** Supports simplified estimates for spread, commission, and slippage.
- **Performance statistics:** Calculates total return, win rate, profit factor, and maximum drawdown.
- **Risk management:** Includes position sizing and risk/reward calculations.
- **CSV export:** Exports completed trades for further analysis.
- **Automated testing:** Runs unit tests using GitHub Actions.

## Project Structure

```text
open-source-trading-bot/
├── backtest.py
├── risk_management.py
├── test_backtest.py
├── test_risk_management.py
├── sample_prices.csv
├── .github/
│   └── workflows/
│       └── tests.yml
├── LICENSE
└── README.md
```

## Requirements

- Python 3.12 or later
- No third-party Python packages are required for the core functionality.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/ChristianRene12/open-source-trading-bot.git
cd open-source-trading-bot
```

### 2. Run the backtest

Use the included sample price data:

```bash
python backtest.py sample_prices.csv
```

The CSV file must contain a column named `close` with positive closing prices.

### 3. Configure the strategy

You can customize the fast and slow moving-average periods:

```bash
python backtest.py sample_prices.csv --fast 5 --slow 20
```

The fast period must be smaller than the slow period.

### 4. Include estimated trading costs

```bash
python backtest.py sample_prices.csv --fast 5 --slow 20 --spread-pct 0.1 --commission-pct 0.05 --slippage-pct 0.02
```

These cost parameters are simplified percentage estimates, not a complete broker execution model.

### 5. Export completed trades

```bash
python backtest.py sample_prices.csv --export-csv trades.csv
```

The resulting CSV contains entry price, exit price, and trade return percentage.

You can combine CSV export with custom strategy parameters and cost estimates.

## Risk Management

The `risk_management.py` module provides utilities for calculating position size based on account equity, risk percentage, and stop-loss distance. It also supports risk/reward calculations for long and short positions.

These calculations are intended to help evaluate risk before placing a trade. They do not guarantee that actual losses will remain within the estimated risk amount.

## Performance Metrics

The backtester reports:

| Metric | Description |
|---|---|
| Completed trades | Number of closed trades |
| Win rate | Percentage of trades with positive returns |
| Total return | Compounded return across completed trades |
| Maximum drawdown | Largest observed decline from a previous equity peak |
| Profit factor | Sum of positive trade returns divided by the absolute sum of negative trade returns |

Performance metrics depend on the strategy, input data, and cost assumptions. Maximum drawdown is an estimate based on the backtest's equity-tracking implementation.

## Running Tests

Run the complete test suite with:

```bash
python -m unittest discover -v
```

The repository also uses GitHub Actions to run the tests automatically when changes are pushed.

## Limitations

This project is intended for educational and research purposes.

- The sample price data is for demonstration, not evidence of profitability.
- Simplified trading costs may differ from real broker fees and execution.
- Historical backtest results do not predict future performance.
- Position sizing and financing costs are not integrated into the backtest's portfolio returns.
- The strategy does not account for all real-world execution constraints.
- Results should be independently validated using realistic data before drawing conclusions.

## Contributing

Contributions, bug reports, and suggestions are welcome. Please include tests when introducing new functionality or fixing bugs.

## Disclaimer

This software is provided for educational and research purposes only. It is not financial advice, and it does not guarantee profits. Trading financial instruments involves risk, including the potential loss of capital.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
