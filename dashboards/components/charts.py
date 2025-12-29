"""
Chart components for Dash dashboard.
Reusable Plotly chart configurations.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Color palette (color-blind accessible)
COLORS = {
    'primary': '#ff3621',
    'bg': '#0f0f1a',
    'card': '#1e1e35',
    'text': '#ffffff',
    'text_secondary': '#a0a0b8',
    'border': 'rgba(255, 255, 255, 0.08)',
    'risk_low': '#2e9e5e',
    'risk_medium': '#e6a23c',
    'risk_high': '#e64545',
    'trend_improving': '#2e9e5e',
    'trend_stable': '#6b6b84',
    'trend_degrading': '#e64545',
}

# Common layout settings
COMMON_LAYOUT = {
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'font': {
        'family': 'Inter, sans-serif',
        'color': COLORS['text']
    },
    'margin': {'l': 40, 'r': 40, 't': 40, 'b': 40},
    'autosize': False,
}


def create_risk_distribution_pie(high, medium, low):
    """
    Create a pie chart showing risk distribution.
    """
    fig = go.Figure(data=[go.Pie(
        labels=['High Risk', 'Medium Risk', 'Low Risk'],
        values=[high, medium, low],
        marker=dict(colors=[
            COLORS['risk_high'],
            COLORS['risk_medium'],
            COLORS['risk_low']
        ]),
        hole=0.6,
        textinfo='label+value',
        textposition='outside',
        textfont=dict(size=12, color=COLORS['text']),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
    )])
    
    fig.update_layout(
        **COMMON_LAYOUT,
        height=350,
        showlegend=False,
        annotations=[{
            'text': f'{high + medium + low}',
            'x': 0.5, 'y': 0.5,
            'font': {'size': 36, 'color': COLORS['text'], 'family': 'Inter, sans-serif'},
            'showarrow': False
        }, {
            'text': 'Total',
            'x': 0.5, 'y': 0.4,
            'font': {'size': 14, 'color': COLORS['text_secondary'], 'family': 'Inter, sans-serif'},
            'showarrow': False
        }]
    )
    
    return fig


def create_risk_trend_line(dates, scores, levels):
    """
    Create a line chart showing risk score trends over time.
    """
    # Create color mapping based on risk level
    level_colors = {
        'Low': COLORS['risk_low'],
        'Medium': COLORS['risk_medium'],
        'High': COLORS['risk_high']
    }
    
    colors = [level_colors.get(level, COLORS['text']) for level in levels]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=scores,
        mode='lines+markers',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(
            size=10,
            color=colors,
            line=dict(width=2, color=COLORS['text'])
        ),
        hovertemplate="<b>Date:</b> %{x}<br><b>Score:</b> %{y:.1f}<extra></extra>"
    ))
    
    # Add threshold lines
    fig.add_hline(y=35, line_dash="dash", line_color=COLORS['risk_low'], opacity=0.5,
                  annotation_text="Low/Medium", annotation_position="right")
    fig.add_hline(y=65, line_dash="dash", line_color=COLORS['risk_medium'], opacity=0.5,
                  annotation_text="Medium/High", annotation_position="right")
    
    fig.update_layout(
        **COMMON_LAYOUT,
        height=350,
        xaxis=dict(
            title='Date',
            showgrid=True,
            gridcolor=COLORS['border'],
            tickfont=dict(color=COLORS['text_secondary'])
        ),
        yaxis=dict(
            title='Risk Score',
            range=[0, 100],
            showgrid=True,
            gridcolor=COLORS['border'],
            tickfont=dict(color=COLORS['text_secondary'])
        ),
        hovermode='x unified'
    )
    
    return fig


def create_signal_heatmap(engagements, factors, values):
    """
    Create a heatmap showing contributing factors by engagement.
    """
    fig = go.Figure(data=go.Heatmap(
        z=values,
        x=factors,
        y=engagements,
        colorscale=[
            [0, COLORS['risk_low']],
            [0.5, COLORS['risk_medium']],
            [1, COLORS['risk_high']]
        ],
        hovertemplate="<b>%{y}</b><br>%{x}: %{z:.1f}<extra></extra>"
    ))
    
    fig.update_layout(
        **COMMON_LAYOUT,
        xaxis=dict(tickfont=dict(color=COLORS['text_secondary'])),
        yaxis=dict(tickfont=dict(color=COLORS['text_secondary']))
    )
    
    return fig


def create_industry_bar(industries, counts):
    """
    Create a horizontal bar chart showing engagements by industry.
    """
    fig = go.Figure(data=[go.Bar(
        y=industries,
        x=counts,
        orientation='h',
        marker=dict(
            color=COLORS['primary'],
            line=dict(width=0)
        ),
        hovertemplate="<b>%{y}</b><br>Engagements: %{x}<extra></extra>"
    )])
    
    fig.update_layout(
        **COMMON_LAYOUT,
        height=300,
        xaxis=dict(
            title='Number of Engagements',
            showgrid=True,
            gridcolor=COLORS['border'],
            tickfont=dict(color=COLORS['text_secondary'])
        ),
        yaxis=dict(
            tickfont=dict(color=COLORS['text_secondary'])
        )
    )
    
    return fig


def create_signal_timeline(dates, success_counts, failure_counts):
    """
    Create a stacked bar chart showing job success/failure over time.
    """
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=dates,
        y=success_counts,
        name='Successful Jobs',
        marker_color=COLORS['risk_low'],
        hovertemplate="<b>%{x}</b><br>Successful: %{y}<extra></extra>"
    ))
    
    fig.add_trace(go.Bar(
        x=dates,
        y=failure_counts,
        name='Failed Jobs',
        marker_color=COLORS['risk_high'],
        hovertemplate="<b>%{x}</b><br>Failed: %{y}<extra></extra>"
    ))
    
    fig.update_layout(
        **COMMON_LAYOUT,
        barmode='stack',
        xaxis=dict(
            title='Date',
            showgrid=False,
            tickfont=dict(color=COLORS['text_secondary'])
        ),
        yaxis=dict(
            title='Job Count',
            showgrid=True,
            gridcolor=COLORS['border'],
            tickfont=dict(color=COLORS['text_secondary'])
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(color=COLORS['text_secondary'])
        )
    )
    
    return fig


def create_gauge_chart(value, title, thresholds=(35, 65)):
    """
    Create a gauge chart for risk score display.
    """
    if value <= thresholds[0]:
        color = COLORS['risk_low']
    elif value <= thresholds[1]:
        color = COLORS['risk_medium']
    else:
        color = COLORS['risk_high']
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 16, 'color': COLORS['text']}},
        number={'font': {'size': 32, 'color': COLORS['text']}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': COLORS['text_secondary']},
            'bar': {'color': color},
            'bgcolor': COLORS['card'],
            'borderwidth': 0,
            'steps': [
                {'range': [0, 35], 'color': 'rgba(46, 158, 94, 0.2)'},
                {'range': [35, 65], 'color': 'rgba(230, 162, 60, 0.2)'},
                {'range': [65, 100], 'color': 'rgba(230, 69, 69, 0.2)'}
            ],
            'threshold': {
                'line': {'color': COLORS['text'], 'width': 2},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        **COMMON_LAYOUT,
        height=250
    )
    
    return fig
