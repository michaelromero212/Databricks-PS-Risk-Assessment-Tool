"""
Risk Dashboard Layout for Dash application.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


def create_metric_card(title, value, subtitle=None, color=None):
    """Create a metric card component."""
    return html.Div([
        html.Div(title, style={
            'fontSize': '0.875rem',
            'color': '#a0a0b8',
            'marginBottom': '0.5rem'
        }),
        html.Div(str(value), style={
            'fontSize': '2rem',
            'fontWeight': '700',
            'color': color or '#ffffff'
        }),
        html.Div(subtitle, style={
            'fontSize': '0.75rem',
            'color': '#6b6b84',
            'marginTop': '0.25rem'
        }) if subtitle else None
    ], style={
        'background': '#1e1e35',
        'border': '1px solid rgba(255, 255, 255, 0.08)',
        'borderRadius': '12px',
        'padding': '1.25rem',
        'minWidth': '180px'
    })


def create_dashboard_layout():
    """Create the main dashboard layout."""
    return html.Div([
        # Header
        html.Header([
            html.Div([
                html.Div([
                    html.Div('PS', style={
                        'width': '40px',
                        'height': '40px',
                        'background': 'linear-gradient(135deg, #ff3621, #cc2a1a)',
                        'borderRadius': '8px',
                        'display': 'flex',
                        'alignItems': 'center',
                        'justifyContent': 'center',
                        'fontWeight': '700',
                        'color': 'white',
                        'fontSize': '1.125rem'
                    }),
                    html.Div([
                        html.Div('Risk Assessment Dashboard', style={
                            'fontSize': '1.25rem',
                            'fontWeight': '600',
                            'color': '#ffffff'
                        }),
                        html.Div('Databricks Professional Services', style={
                            'fontSize': '0.875rem',
                            'color': '#6b6b84'
                        })
                    ], style={'marginLeft': '0.75rem'})
                ], style={'display': 'flex', 'alignItems': 'center'}),
                
                html.Div([
                    html.A('React App', href='http://localhost:3000', target='_blank',
                           style={
                               'padding': '0.5rem 1rem',
                               'background': '#252542',
                               'borderRadius': '8px',
                               'color': '#a0a0b8',
                               'textDecoration': 'none',
                               'fontSize': '0.875rem',
                               'fontWeight': '500'
                           })
                ])
            ], style={
                'maxWidth': '1400px',
                'margin': '0 auto',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'space-between'
            })
        ], style={
            'background': '#1a1a2e',
            'borderBottom': '1px solid rgba(255, 255, 255, 0.08)',
            'padding': '1rem 1.5rem',
            'position': 'sticky',
            'top': 0,
            'zIndex': 100
        }),
        
        # Main Content
        html.Main([
            # Page Title
            html.Div([
                html.H1('Analytics Dashboard', style={
                    'fontSize': '1.875rem',
                    'fontWeight': '700',
                    'color': '#ffffff',
                    'marginBottom': '0.5rem'
                }),
                html.P('Real-time insights into engagement risk and platform activity', style={
                    'color': '#a0a0b8',
                    'marginBottom': 0
                })
            ], style={'marginBottom': '1.5rem'}),
            
            # Metrics Row
            html.Div(id='metrics-row', style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(auto-fit, minmax(180px, 1fr))',
                'gap': '1rem',
                'marginBottom': '1.5rem'
            }),
            
            # Charts Row 1
            html.Div([
                # Risk Distribution
                html.Div([
                    html.H3('Risk Distribution', style={
                        'fontSize': '1rem',
                        'fontWeight': '600',
                        'color': '#ffffff',
                        'marginBottom': '1rem'
                    }),
                    dcc.Graph(id='risk-distribution-chart', config={'displayModeBar': False})
                ], style={
                    'background': '#1e1e35',
                    'border': '1px solid rgba(255, 255, 255, 0.08)',
                    'borderRadius': '12px',
                    'padding': '1.25rem'
                }),
                
                # Industry Breakdown
                html.Div([
                    html.H3('Engagements by Industry', style={
                        'fontSize': '1rem',
                        'fontWeight': '600',
                        'color': '#ffffff',
                        'marginBottom': '1rem'
                    }),
                    dcc.Graph(id='industry-chart', config={'displayModeBar': False})
                ], style={
                    'background': '#1e1e35',
                    'border': '1px solid rgba(255, 255, 255, 0.08)',
                    'borderRadius': '12px',
                    'padding': '1.25rem'
                })
            ], id='charts-row-1', style={
                'display': 'grid',
                'gridTemplateColumns': '1fr',
                'gap': '1.5rem',
                'marginBottom': '1.5rem'
            }),
            
            # Charts Row 2 - Full Width
            html.Div([
                html.H3('Average Risk Score Trend', style={
                    'fontSize': '1rem',
                    'fontWeight': '600',
                    'color': '#ffffff',
                    'marginBottom': '1rem'
                }),
                dcc.Graph(id='trend-chart', config={'displayModeBar': False})
            ], style={
                'background': '#1e1e35',
                'border': '1px solid rgba(255, 255, 255, 0.08)',
                'borderRadius': '12px',
                'padding': '1.25rem',
                'marginBottom': '1.5rem'
            }),
            
            # Engagement Table
            html.Div([
                html.H3('All Engagements', style={
                    'fontSize': '1rem',
                    'fontWeight': '600',
                    'color': '#ffffff',
                    'marginBottom': '1rem'
                }),
                html.Div(id='engagement-table')
            ], style={
                'background': '#1e1e35',
                'border': '1px solid rgba(255, 255, 255, 0.08)',
                'borderRadius': '12px',
                'padding': '1.25rem',
                'marginBottom': '1.5rem'
            }),
            
            # AI Model Status Panel
            html.Div([
                html.Div([
                    html.Div('🤖', style={
                        'width': '32px',
                        'height': '32px',
                        'background': 'linear-gradient(135deg, #5b8def, #a855f7)',
                        'borderRadius': '8px',
                        'display': 'flex',
                        'alignItems': 'center',
                        'justifyContent': 'center',
                        'fontSize': '1rem'
                    }),
                    html.Div('AI Model Status', style={
                        'fontSize': '1rem',
                        'fontWeight': '600',
                        'color': '#ffffff',
                        'marginLeft': '0.75rem'
                    }),
                    html.Div(id='ai-status-indicator', style={'marginLeft': 'auto'})
                ], style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'marginBottom': '1rem'
                }),
                html.Div(id='ai-metadata', style={
                    'display': 'grid',
                    'gridTemplateColumns': 'repeat(auto-fit, minmax(150px, 1fr))',
                    'gap': '1rem',
                    'paddingTop': '1rem',
                    'borderTop': '1px solid rgba(255, 255, 255, 0.08)'
                })
            ], style={
                'background': 'linear-gradient(135deg, #252542, #1a1a2e)',
                'border': '1px solid rgba(255, 255, 255, 0.08)',
                'borderRadius': '12px',
                'padding': '1.25rem'
            })
            
        ], style={
            'padding': '1rem',
            'maxWidth': '1400px',
            'margin': '0 auto'
        }),
        
        # Interval for auto-refresh (every 30 seconds)
        dcc.Interval(id='refresh-interval', interval=30*1000, n_intervals=0)
        
    ], style={
        'minHeight': '100vh',
        'background': '#0f0f1a',
        'fontFamily': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
    })
