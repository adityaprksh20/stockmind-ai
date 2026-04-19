import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


def get_chart_data(ticker, period="1y"):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    if hist.empty:
        return None
    return hist


def build_main_chart(ticker, period="1y", show_bollinger=True, show_sma=True, show_volume=True, jyotish_events=None):
    hist = get_chart_data(ticker, period)
    if hist is None:
        return None

    close = hist["Close"]
    high = hist["High"]
    low = hist["Low"]
    open_p = hist["Open"]
    volume = hist["Volume"]
    dates = hist.index

    sma_20 = close.rolling(20).mean()
    sma_50 = close.rolling(50).mean()
    sma_200 = close.rolling(200).mean()

    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema_12 - ema_26
    macd_signal = macd_line.ewm(span=9, adjust=False).mean()
    macd_hist = macd_line - macd_signal

    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss.replace(0, float("nan"))
    rsi = 100 - (100 / (1 + rs))

    bb_mid = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    bb_upper = bb_mid + 2 * bb_std
    bb_lower = bb_mid - 2 * bb_std

    row_heights = [0.5, 0.15, 0.15, 0.2]
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights,
        subplot_titles=("Price", "Volume", "RSI", "MACD"),
    )

    fig.add_trace(
        go.Candlestick(
            x=dates, open=open_p, high=high, low=low, close=close,
            name="Price",
            increasing_line_color="#26a69a",
            decreasing_line_color="#ef5350",
            increasing_fillcolor="#26a69a",
            decreasing_fillcolor="#ef5350",
        ),
        row=1, col=1,
    )

    if show_sma:
        fig.add_trace(go.Scatter(x=dates, y=sma_20, name="SMA 20", line=dict(color="#ffa726", width=1.2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=dates, y=sma_50, name="SMA 50", line=dict(color="#42a5f5", width=1.2)), row=1, col=1)
        if len(close) >= 200:
            fig.add_trace(go.Scatter(x=dates, y=sma_200, name="SMA 200", line=dict(color="#ab47bc", width=1.2)), row=1, col=1)

    if show_bollinger:
        fig.add_trace(go.Scatter(x=dates, y=bb_upper, name="BB Upper", line=dict(color="rgba(150,150,150,0.4)", width=1, dash="dot")), row=1, col=1)
        fig.add_trace(go.Scatter(x=dates, y=bb_lower, name="BB Lower", line=dict(color="rgba(150,150,150,0.4)", width=1, dash="dot"), fill="tonexty", fillcolor="rgba(150,150,150,0.05)"), row=1, col=1)

    if jyotish_events:
        for evt in jyotish_events:
            evt_date = evt.get("date")
            evt_label = evt.get("label", "")
            evt_color = evt.get("color", "yellow")
            if evt_date:
                fig.add_vline(x=evt_date, line_dash="dash", line_color=evt_color, line_width=1, row=1, col=1)
                fig.add_annotation(
                    x=evt_date, y=1.02, yref="paper",
                    text=evt_label, showarrow=False,
                    font=dict(size=9, color=evt_color),
                    row=1, col=1,
                )

    colors = ["#26a69a" if c >= o else "#ef5350" for c, o in zip(close, open_p)]
    if show_volume:
        fig.add_trace(
            go.Bar(x=dates, y=volume, name="Volume", marker_color=colors, opacity=0.7),
            row=2, col=1,
        )

    fig.add_trace(go.Scatter(x=dates, y=rsi, name="RSI", line=dict(color="#ab47bc", width=1.5)), row=3, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="#ef5350", line_width=0.8, row=3, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="#26a69a", line_width=0.8, row=3, col=1)
    fig.add_hrect(y0=30, y1=70, fillcolor="rgba(150,150,150,0.05)", line_width=0, row=3, col=1)

    macd_colors = ["#26a69a" if v >= 0 else "#ef5350" for v in macd_hist]
    fig.add_trace(go.Bar(x=dates, y=macd_hist, name="MACD Hist", marker_color=macd_colors, opacity=0.7), row=4, col=1)
    fig.add_trace(go.Scatter(x=dates, y=macd_line, name="MACD", line=dict(color="#42a5f5", width=1.2)), row=4, col=1)
    fig.add_trace(go.Scatter(x=dates, y=macd_signal, name="Signal", line=dict(color="#ffa726", width=1.2)), row=4, col=1)
    fig.add_hline(y=0, line_dash="dot", line_color="rgba(150,150,150,0.5)", line_width=0.5, row=4, col=1)

    fig.update_layout(
        height=800,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", size=11),
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(size=10),
        ),
        margin=dict(l=50, r=20, t=40, b=20),
        xaxis_rangeslider_visible=False,
    )

    for i in range(1, 5):
        fig.update_xaxes(
            gridcolor="rgba(150,150,150,0.1)",
            showgrid=True,
            row=i, col=1,
        )
        fig.update_yaxes(
            gridcolor="rgba(150,150,150,0.1)",
            showgrid=True,
            row=i, col=1,
        )

    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Vol", row=2, col=1)
    fig.update_yaxes(title_text="RSI", range=[0, 100], row=3, col=1)
    fig.update_yaxes(title_text="MACD", row=4, col=1)

    return fig


def build_returns_chart(ticker, period="1y"):
    hist = get_chart_data(ticker, period)
    if hist is None:
        return None

    close = hist["Close"]
    returns = (close / close.iloc[0] - 1) * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist.index, y=returns,
        fill="tozeroy",
        fillcolor="rgba(38,166,154,0.15)",
        line=dict(color="#26a69a", width=2),
        name="Return %",
    ))
    fig.add_hline(y=0, line_dash="dot", line_color="rgba(150,150,150,0.5)")

    fig.update_layout(
        height=300,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", size=11),
        margin=dict(l=50, r=20, t=20, b=20),
        yaxis_title="Return %",
        showlegend=False,
    )
    fig.update_xaxes(gridcolor="rgba(150,150,150,0.1)")
    fig.update_yaxes(gridcolor="rgba(150,150,150,0.1)")

    return fig
