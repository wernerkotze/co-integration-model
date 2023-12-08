import matplotlib.pyplot as plt
import seaborn as sns


def CorrelationMatrix(train_data, results_dir):
    _, ax = plt.subplots(figsize=(20, 16))
    sns.heatmap(train_data.pct_change().corr(method='pearson'), ax=ax, cmap='coolwarm', annot=True, fmt=".2f")
    ax.set_title('Assets Correlation Matrix')
    plt.savefig(results_dir + '/CorrelationMatrix', dpi=500)
    plt.close('all')


def CointegrationPValues(pvalues, train_data, results_dir):
    _, ax = plt.subplots(figsize=(20, 14))
    sns.heatmap(pvalues, xticklabels=train_data.columns, yticklabels=train_data.columns, cmap='RdYlGn_r',
                annot=True, fmt=".2f", mask=(pvalues >= 0.99))
    ax.set_title('Assets Cointegration Matrix P-Values')
    plt.tight_layout()
    plt.savefig(results_dir + '/CointegrationPValues', dpi=500)
    plt.close('all')

def Prices(asset1, asset2, data, test_dir):
    fig = plt.figure(figsize=(20, 14))
    bx1 = fig.add_subplot(111)
    bx2 = bx1.twinx()

    bx1.plot(data[asset1], c='blue', label=asset1)
    bx2.plot(data[asset2], c='orange', label=asset2)
    bx1.set_ylabel(asset1)
    bx2.set_ylabel(asset2, rotation=270)

    lines, labels = bx1.get_legend_handles_labels()
    lines2, labels2 = bx2.get_legend_handles_labels()
    bx2.legend(lines + lines2, labels + labels2, loc=0)

    plt.title(f"Prices for {asset1} and {asset2}")
    plt.xlabel('Date')
    plt.grid(True)
    plt.savefig(test_dir + '/PriceChart', dpi=500)
    plt.close('all')
    return


def OLSRegression(text, test_dir):
    _, ax = plt.subplots(figsize=(20, 14))
    plt.text(0.01, 0.05, text, {'fontsize': 16}, fontproperties='monospace')
    plt.axis('off')
    plt.tight_layout()
    plt.subplots_adjust(left=0.2, right=0.8, top=0.7, bottom=0.1)
    plt.savefig(test_dir + '/OLSRegressionResults', dpi=500)
    plt.close('all')
    plt.axis('on')


def Spread(spread, test_dir):
    ax = spread.plot(figsize=(20, 12), title="Pair Spread")
    ax.set_ylabel("Spread")
    ax.grid(True)
    plt.savefig(test_dir + '/Spread', dpi=500)
    plt.close('all')


def Signals(asset1, asset2, signals, test_dir):
    fig = plt.figure(figsize=(20, 12))
    bx = fig.add_subplot(111)
    bx2 = bx.twinx()
    # Visualize assets
    bx.plot(signals[asset1], c='#4abdac', label=asset1)
    bx.plot(signals[asset1][signals['positions1'] == 1], lw=0, marker='^',
                 markersize=8, c='green', alpha=0.7, label=asset1 + " LONG")
    bx.plot(signals[asset1][signals['positions1'] == -1], lw=0, marker='v',
                 markersize=8, c='red', alpha=0.7, label=asset1 + " SHORT")

    bx2.plot(signals[asset2], c='#907163', label=asset2)
    bx2.plot(signals[asset2][signals['positions2'] == 1], lw=0, marker='^',
                  markersize=8, c='blue', alpha=0.7, label=asset2 + " LONG")
    bx2.plot(signals[asset2][signals['positions2'] == -1], lw=0, marker='v',
                  markersize=8, c='orange', alpha=0.7, label=asset2 + " SHORT")

    lines, labels = bx.get_legend_handles_labels()
    lines2, labels2 = bx2.get_legend_handles_labels()
    bx2.legend(lines + lines2, labels + labels2, loc=0)

    # change names and parameters
    bx.set_ylabel(asset1)
    bx2.set_ylabel(asset2, rotation=270)
    bx.yaxis.labelpad = 15
    bx2.yaxis.labelpad = 15
    bx.set_xlabel('Date')
    bx.xaxis.labelpad = 15

    plt.title('Trading Signals')
    plt.xlabel('Date')
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(test_dir + '/Backtest', dpi=500)
    plt.close('all')


def PortfolioPerformance(portfolio, test_dir, profit_stats):
    fig = plt.figure(figsize=(20, 14), )
    ax = fig.add_subplot(111)
    ax2 = ax.twinx()

    l1, = ax.plot(portfolio['total asset'], c='g')
    l2, = ax2.plot(portfolio['z'], c='black', alpha=0.3)

    b = ax2.fill_between(portfolio.index, portfolio['z upper limit'], portfolio['z lower limit'],
                         alpha=0.2, color='#ffb48f')

    ax.set_ylabel('Portfolio Value')
    ax2.set_ylabel('Z Statistics', rotation=270)
    ax.yaxis.labelpad = 15
    ax2.yaxis.labelpad = 15
    ax.set_xlabel('Date')
    ax.xaxis.labelpad = 15
    plt.title(f'Portfolio Performance PNL - {profit_stats}')
    plt.legend([l2, b, l1], ['Z Statistics',
                             'Z Statistics +-1 Sigma',
                             'Total Portfolio Value'], loc='upper left')
    plt.savefig(test_dir + '/PortfolioPerformance', dpi=500)
    plt.close('all')