import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
from dash import dcc, html, Input, Output, State
from dash.dependencies import Input, Output, State, ALL
from dash import MATCH
import plotly.express as px
import pandas as pd
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import numpy as np
import statsmodels.api as sm


# Define your custom colors based on the image
theme_colors = {
    "primary": "#5B7290",  # A blue-gray for card backgrounds
    "secondary": "#44B39D",  # Teal for accents
    "highlight": "#8CF085",  # Light green for metric values
    "background": "#1C1C2C",  # Dark background
    "text": "#FFFFFF",  # White text
    "accent": "#FFD700"
}

# Initialize the app with a custom color theme
#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)  # Change "DARKLY" to your preferred dark theme







app.title = "VA Department of Corrections - BI Dashboard"


# Load the cleaned dataset and convert 'Ordered.Date' to datetime
#cleaned_data = pd.read_csv('cleaned_prison_data.csv')

# Replace these lines:
# cleaned_data = pd.read_csv("local_path/cleaned_prison_data.csv")
# nigp_summary = pd.read_csv("local_path/nigp_summary.csv")

# With these lines:
cleaned_data = pd.read_csv("https://prison-dashboard-data.s3.us-east-1.amazonaws.com/cleaned_prison_data.csv")
nigp_summary = pd.read_csv("https://prison-dashboard-data.s3.us-east-1.amazonaws.com/nigp_summary.csv")


cleaned_data['Ordered.Date'] = pd.to_datetime(cleaned_data['Ordered.Date'])  # Ensure this column is datetime

# Load aggregated data
#nigp_summary = pd.read_csv("nigp_summary.csv")



#                id='date-range-picker',
#                id='region-dropdown',
#                id='order-status-dropdown',
#                id='procurement-transaction-desc-dropdown',
#                id='vendor-dropdown',

# Function to calculate metrics based on filtered dataset
def create_overview_metrics(filtered_data):
    # Define the formatting function for time values
    def format_time(value):
        if value < 1:
            hours = value * 24
            return f"{hours:.2f} hours"
        else:
            return f"{value:.2f} days"

    # Calculate metrics based on the filtered data
    total_expenditure = f"${filtered_data['Line.Total'].sum():,.2f}"
    total_orders = f"{filtered_data['BaseOrderNumber'].nunique()}"
    total_vendors = f"{filtered_data['Vendor.Name'].nunique()}"
    avg_order_lead_time = format_time(filtered_data['Order_Lead_Time'].mean())
    avg_processing_time = format_time(filtered_data['Processing_Time'].mean())

    # Define the metrics to display with updated values
    metrics = [
        {"title": "Total Expenditure", "value": total_expenditure, "icon": "fas fa-dollar-sign", "color": "linear-gradient(135deg, #b0b0b0, #8c8c8c)", "text_color": "#333333"},
        {"title": "Total Orders", "value": total_orders, "icon": "fas fa-box", "color": "linear-gradient(135deg, #60c6a8, #44b39d)", "text_color": "#333333"},
        {"title": "Number of Vendors", "value": total_vendors, "icon": "fas fa-industry", "color": "linear-gradient(135deg, #E8D6A7, #D3C2A3)", "text_color": "#333333"},
        {"title": "Average Order Lead Time", "value": avg_order_lead_time, "icon": "fas fa-clock", "color": "linear-gradient(135deg, #5b8cbe, #4a6fa1)", "text_color": "#333333"},
        {"title": "Average Processing Time", "value": avg_processing_time, "icon": "fas fa-stopwatch", "color": "linear-gradient(135deg, #a8d5ba, #91c6a5)", "text_color": "#333333"},
    ]

    # Create cards for each metric with uniform size
    cards = dbc.Row(
        [
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5(metric["title"], className="card-title", style={'font-weight': 'bold', 'color': metric["text_color"], 'margin-bottom': '10px', 'text-shadow': '1px 1px 2px rgba(0, 0, 0, 0.6)','font-size': '1.1em'}),
                        html.H2(metric["value"], className="card-text", style={'color': metric["text_color"], 'font-weight': 'bold', 'font-size': '1.5em', 'margin-top': '10', 'text-shadow': '1px 1px 2px rgba(0, 0, 0, 0.6)', 'text-shadow': '1px 1px 2px rgba(0, 0, 0, 0.6)'}),
                        html.I(className=metric["icon"], style={'font-size': '30px', 'color': metric["text_color"], 'margin-top': '10px'})
                    ]
                ),
                style={'background': metric["color"], 'border': 'none', 'margin': '10px', 'border-radius': '10px', 'padding': '15px', 'box-shadow': '0px 4px 8px rgba(0, 0, 0, 0.3)', 'height': '150px', 'width': '100%'},
                className="text-white text-center"
            ),
            #width=2.0  # Adjust width to keep all metrics in one row
            #width=4,  # Adjusted width for each metric card
            lg=2,  # Large screens get more narrow columns
            md=4,  # Medium screens get slightly wider columns
            sm=6,  # Small screens stack two columns per row
            xs=12  # Extra small screens stack one column per row
        ) for metric in metrics
    ],
            className="mb-4 gx-4 justify-content-center"  # gx-2 controls the gutter space between columns
)
    
    return dbc.Row(cards, className="mb-4 gx-4 justify-content-center")

import dash_bootstrap_components as dbc

# Function to create the filter with multi-selection enabled
def create_sidebar_filters(active_tab):
    region_options = [{'label': region, 'value': region} for region in cleaned_data['Virginia_Region'].unique()]
    status_options = [{'label': status, 'value': status} for status in cleaned_data['Order.Status'].unique()]
    desc_options = [{'label': desc, 'value': desc} for desc in cleaned_data['Procurement.Transaction.Desc'].unique()]
    vendor_options = [{'label': vendor, 'value': vendor} for vendor in cleaned_data['Vendor.Name'].unique()]

    if active_tab == "overview-tab":
        return html.Div([
            dcc.DatePickerRange(id='overview-date-range-picker', start_date=cleaned_data['Ordered.Date'].min(), end_date=cleaned_data['Ordered.Date'].max(),style={
            'backgroundColor': '#2b2b2b',
            'color': '#E8D6A7',
            'border': '1px solid #636EFA',  
            'borderRadius': '3px',         # Rounded corners
            'padding': '5px'
        }),
            dcc.Dropdown(id='overview-region-dropdown', options=region_options, placeholder="Select Region(s)", multi=True, 
        style={
            'backgroundColor': theme_colors["background"],
            #"backgroundColor": "#444444",  # Menu background color
            'color': '#636EFA',
            'border': '1px solid #636EFA',
            'borderRadius': '3px',
            'padding': '5px'
        }),
            dcc.Dropdown(id='overview-order-status-dropdown', options=status_options, placeholder="Select Order Status(es)", multi=True,
        style={
            'backgroundColor': theme_colors["background"],
            'color': '#636EFA',
            'border': '1px solid #636EFA',
            'borderRadius': '3px',
            'padding': '5px'
        }),
            dcc.Dropdown(id='overview-procurement-transaction-desc-dropdown', options=desc_options, placeholder="Select Procurement Transaction(s)", multi=True,
        style={
            'backgroundColor': theme_colors["background"],
            'color': '#636EFA',
            'border': '1px solid #636EFA',
            'borderRadius': '3px',
            'padding': '5px'
        }),
        ])
    elif active_tab == "spend-analysis-tab":
        return html.Div([
            dcc.DatePickerRange(id='spend-date-range-picker', start_date=cleaned_data['Ordered.Date'].min(), end_date=cleaned_data['Ordered.Date'].max()),style={
            'backgroundColor': '#2b2b2b',
            'color': '#E8D6A7',
            'border': '1px solid #636EFA',  
            'borderRadius': '3px',         # Rounded corners
            'padding': '5px'
        }),

            dcc.Dropdown(id='spend-region-dropdown', options=region_options, placeholder="Select Region(s)", multi=True), 
        style={
            'backgroundColor': theme_colors["background"],
            #"backgroundColor": "#444444",  # Menu background color
            'color': '#636EFA',
            'border': '1px solid #636EFA',
            'borderRadius': '3px',
            'padding': '5px'
        }),

            dcc.Dropdown(id='spend-vendor-dropdown', options=vendor_options, placeholder="Select Vendor(s)", multi=True), 
        style={
            'backgroundColor': theme_colors["background"],
            #"backgroundColor": "#444444",  # Menu background color
            'color': '#636EFA',
            'border': '1px solid #636EFA',
            'borderRadius': '3px',
            'padding': '5px'
        }),
        ])

    elif active_tab == "vendor-insights-tab":
        return html.Div([
            dcc.DatePickerRange(id='vendor-insights-date-range-picker', start_date=cleaned_data['Ordered.Date'].min(), end_date=cleaned_data['Ordered.Date'].max()),
            dcc.Dropdown(id='vendor-insights-vendor-dropdown', options=vendor_options, placeholder="Select Vendor(s)", multi=True),
        ])
    elif active_tab == "category-insights-tab":  # Add filters for Category Insights
        return html.Div([
            dcc.Dropdown(id='category-vendor-dropdown', options=vendor_options, placeholder="Select Vendor(s)", multi=True),
            dcc.Dropdown(id='category-procurement-dropdown', options=desc_options, placeholder="Select Procurement Transaction(s)", multi=True),
            dcc.DatePickerRange(id='category-date-range-picker', start_date=cleaned_data['Ordered.Date'].min(), end_date=cleaned_data['Ordered.Date'].max()),
        ])
    elif active_tab == "prediction-analysis-tab":
        return html.Div([
            dcc.Dropdown(
                id='prediction-vendor-dropdown',
                options=vendor_options,
                placeholder="Select Vendor(s)",
                multi=True
            ),
            dcc.Slider(
                id="forecast-horizon-slider",
                min=1,
                max=24,
                step=1,
                value=12,  # Default to 12 months
                marks={i: f"{i} months" for i in range(1, 25, 3)},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ])

    else:
        return html.Div("No filters available.")













@app.callback(
    Output("filters-container", "children"),
    Input("tabs", "active_tab"),
)
def update_filters(active_tab):
    return create_sidebar_filters(active_tab)











# Sample plot function for visual demonstration, now accepts data as an argument
def create_sample_plot(data):
    fig = px.line(data, x="Ordered.Date", y="Processing_Time", title="Processing Time Over Time")
    fig.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)",  # Transparent background
        paper_bgcolor=theme_colors["background"],
        font=dict(color=theme_colors["text"]),
        title_font=dict(size=20, color=theme_colors["text"], family="Roboto"),
    )
    return dcc.Graph(figure=fig)


""
def create_total_expenditure_plot(data):
    # Check if necessary columns exist
    if 'Ordered.Date' not in data.columns or 'Line.Total' not in data.columns:
        raise ValueError("The required columns 'Ordered.Date' and 'Line.Total' are missing from the data.")

    # Ensure 'Ordered.Date' is in datetime format
    data['Ordered.Date'] = pd.to_datetime(data['Ordered.Date'], errors='coerce')

    # Drop rows with invalid dates or line totals
    data = data.dropna(subset=['Ordered.Date', 'Line.Total'])

    # Group by 'Ordered.Date' and sum 'Line.Total'
    expenditure_data = (
        data.groupby(data['Ordered.Date'].dt.to_period("D"))['Line.Total']
        .sum()
        .reset_index()
    )
    expenditure_data['Ordered.Date'] = expenditure_data['Ordered.Date'].dt.to_timestamp()

    # Check if grouped data is empty
    if expenditure_data.empty:
        raise ValueError("No data available to plot after filtering and grouping.")

    # Create the line plot with Plotly Express
    fig = px.line(
        expenditure_data,
        x="Ordered.Date",
        y="Line.Total",
        title="Total Expenditure Over Time ($)",
        labels={"Ordered.Date": "Date", "Line.Total": "Total Expenditure"}
    )

    # Update the layout to match the theme
    fig.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)",  # Transparent background
        paper_bgcolor=theme_colors["background"],
        font=dict(color=theme_colors["text"]),
        title_font=dict(size=20, color=theme_colors["text"], family="Roboto")
    )

    return dcc.Graph(figure=fig)


""
def create_order_volume_plot(data):
    # Group by date and count unique BaseOrderNumber per day
    order_volume_data = data.groupby(data['Ordered.Date'].dt.to_period("D"))['BaseOrderNumber'].nunique().reset_index()
    order_volume_data['Ordered.Date'] = order_volume_data['Ordered.Date'].dt.to_timestamp()  # Convert to datetime for plotting
    order_volume_data.rename(columns={'BaseOrderNumber': 'Order Volume'}, inplace=True)

    # Create a line plot with Plotly Express
    fig = px.line(
        order_volume_data, 
        x="Ordered.Date", 
        y="Order Volume", 
        title="Order Volume Over Time",
        labels={"Ordered.Date": "Date", "Order Volume": "Number of Orders"}
    )

    # Update the layout to match the theme
    fig.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)",  # Transparent background
        paper_bgcolor=theme_colors["background"],
        font=dict(color=theme_colors["text"]),
        title_font=dict(size=20, color=theme_colors["text"], family="Roboto")
    )
    
    return dcc.Graph(figure=fig)

""
import plotly.graph_objects as go

def create_top_vendors_plot(data, top_n=5):
    # Group by vendor and sum expenditure
    vendor_expenditure = data.groupby('Vendor.Name')['Line.Total'].sum().reset_index()
    vendor_expenditure = vendor_expenditure.sort_values(by='Line.Total', ascending=False).head(top_n)
    
    # Define a color array for each bar
    colors = ["#44B39D", "#8CF085", "#5B7290", "#E8D6A7", "#A18CCB"]

    # Create a bar chart with go.Bar to control each bar's color
    fig = go.Figure(
        data=[
            go.Bar(
                x=vendor_expenditure['Line.Total'],
                y=vendor_expenditure['Vendor.Name'],
                orientation='h',  # Horizontal bars
                marker=dict(color=colors[:len(vendor_expenditure)])  # Apply color to each bar
            )
        ]
    )

    # Update layout to match the theme
    fig.update_layout(
        title=f"Top {top_n} Vendors by Expenditure",
        xaxis_title="Total Expenditure($)",
        yaxis_title="Vendor",
        plot_bgcolor="rgba(0, 0, 0, 0)",  # Transparent background
        paper_bgcolor=theme_colors["background"],
        font=dict(color=theme_colors["text"]),
        title_font=dict(size=20, color=theme_colors["text"], family="Roboto"),
    )
    
    return dcc.Graph(figure=fig)



""

def create_top_regions_plot(data, top_n=5):
    # Group by region and sum expenditure
    region_expenditure = data.groupby('Virginia_Region')['Line.Total'].sum().reset_index()
    region_expenditure = region_expenditure.sort_values(by='Line.Total', ascending=False).head(top_n)

    # Define the color palette for the pie chart
    colors = ["#44B39D", "#8CF085", "#5B7290", "#E8D6A7", "#A18CCB"]

    # Create a pie chart with Plotly Express
    fig = px.pie(
        region_expenditure, 
        values='Line.Total', 
        names='Virginia_Region', 
        title=f"Top {top_n} Regions by Expenditure",
        hole=0.3  # Makes it a donut chart; set to 0 for a full pie chart
    )

    # Apply custom colors to the pie chart
    fig.update_traces(marker=dict(colors=colors[:len(region_expenditure)]), textinfo='percent+label')

    # Update the layout to match the theme
    fig.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)",  # Transparent background
        paper_bgcolor=theme_colors["background"],
        font=dict(color=theme_colors["text"]),
        title_font=dict(size=20, color=theme_colors["text"], family="Roboto"),
    )
    
    return dcc.Graph(figure=fig)



""

def create_monthly_spend_trend(data):
    # Group by month and calculate total spend
    data['Ordered.Date'] = pd.to_datetime(data['Ordered.Date'])
    monthly_spend = data.resample('M', on='Ordered.Date').sum()['Line.Total'].reset_index()

    # Create the line plot
    fig = px.line(monthly_spend, x='Ordered.Date', y='Line.Total', title="Monthly Spend Trend")
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Total Spend",
        plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot background
        paper_bgcolor=theme_colors["background"],
        font=dict(color=theme_colors["text"]),
    )

    return dcc.Graph(figure=fig)



""

def create_spend_by_category_treemap(data):
    # Group by category and calculate total spend and order count
    category_spend = data.groupby('Procurement.Transaction.Desc').agg(
        Total_Spend=('Line.Total', 'sum'),
        Order_Count=('BaseOrderNumber', 'nunique')
    ).reset_index()
    category_spend = category_spend.sort_values(by='Total_Spend', ascending=False)
    
    # Define custom color mapping for categories
    color_mapping = {
        category: color for category, color in zip(
            category_spend['Procurement.Transaction.Desc'].unique(),
            [
                "#DDA0DD",  # Add your theme colors here
                "#8CF085",
                "#5B7290",
                "#E8D6A7",
                "#A18CCB",
                "#FFD700",
                "#44B39D",
                "#6A5ACD",
            ]
        )
    }
    
    # Create the treemap with customdata
    fig = px.treemap(
        category_spend,
        path=['Procurement.Transaction.Desc'],
        values='Total_Spend',
        title="Spend by Category",
        color='Procurement.Transaction.Desc',
        color_discrete_map=color_mapping,
        custom_data=['Procurement.Transaction.Desc', 'Total_Spend', 'Order_Count']  # Include more details
    )
    
    fig.update_traces(hovertemplate=("<b>%{label}</b><br>""Total Spend: %{value:,.2f}<br>""Order Count: %{customdata[2]}"))
    
    fig.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)",  # Transparent background
        paper_bgcolor=theme_colors["background"],
        font=dict(color=theme_colors["text"]),
        title_font=dict(size=16, color=theme_colors["accent"]))
    
    return dcc.Graph(id="category-treemap", figure=fig)


# Callback to handle click events and show details
@app.callback(
    Output('category-details', 'children'),  # A new container for dynamic details
    [Input('category-treemap', 'clickData')]  # Triggered by treemap clicks
)
def display_category_details(clickData):
    if clickData is None:
        return html.Div(
            "Click on a section to see more details.",
            style={"text-align": "center", "color": theme_colors["text"]}
        )
    
    # Extract details from clickData
    category = clickData['points'][0]['customdata'][0]
    total_spend = clickData['points'][0]['customdata'][1]
    order_count = clickData['points'][0]['customdata'][2]

    # Generate detailed view
    return dbc.Card(
        dbc.CardBody([
            html.H5(
                f"Details for Category: {category}",
                className="card-title",
                style={"color": theme_colors["text"]}
            ),
            html.P(
                f"Total Spend: ${total_spend:,.2f}",
                style={"color": theme_colors["text"]}
            ),
            html.P(
                f"Order Count: {order_count}",
                style={"color": theme_colors["text"]}
            ),
        ]),
        style={"background-color": theme_colors["background"], "border": f"1px solid {theme_colors['accent']}"}
    )





""
def create_spend_by_shipping_city_map(data):
    # Filter for Virginia
    data_va = data[(data['Shipping.State'] == "VA") & data['Latitude'].notna() & data['Longitude'].notna()]

    # Group by city and calculate total spend
    city_spend = data_va.groupby(['Shipping.City', 'Latitude', 'Longitude'])['Line.Total'].sum().reset_index()

    # Create scatter map with coordinates
    fig = px.scatter_mapbox(
        city_spend,
        lat="Latitude",
        lon="Longitude",
        size="Line.Total",
        size_max=15,
        hover_name="Shipping.City",
        color="Line.Total",
        color_continuous_scale="Viridis",
        mapbox_style="carto-positron",
        title="Spend by Shipping City in Virginia",
        labels={'Line.Total': 'Total Spend'}
    )

    # Set custom height
    fig.update_layout(
        height=600,  # Adjust the height as desired
        paper_bgcolor=theme_colors["background"],
        font=dict(color=theme_colors["text"])
    )

    return dcc.Graph(figure=fig)



""
def create_spend_by_order_status_donut(data):
    # Group by Order Status and calculate total spend
    status_spend = data.groupby('Order.Status')['Line.Total'].sum().reset_index()
    
    # Define custom color sequence for Order Status
    color_sequence = ["#A18CCB", "#E8D6A7", "#44B39D", "#5B7290", "#8CF085"]
    
    # Create the donut chart
    fig = px.pie(
        status_spend,
        names='Order.Status',
        values='Line.Total',
        title="Spend by Order Status",
        hole=0.4,  # Creates the donut hole
        color='Order.Status',
        color_discrete_sequence=color_sequence,
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='%{label}: %{value:$,.2f} (<b>%{percent}</b>)'
    )
    
    fig.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor=theme_colors["background"],
        font=dict(color=theme_colors["text"]),
        title_font=dict(size=16, color=theme_colors["accent"]),
        showlegend=True,
    )
    
    return dcc.Graph(figure=fig)



""
# Step 1: Implement Summary Metrics Row (Row 1)
def create_summary_metrics_row(data):
    total_purchase = f"${data['Line.Total'].sum():,.2f}"
    quantity = data['BaseOrderNumber'].nunique()
    
    # Calculate max processing time with units
    max_processing_time_value = data['Processing_Time'].max()
    if max_processing_time_value < 1:
        max_processing_time = f"{max_processing_time_value * 24:.2f} hours"  # Convert to hours if less than a day
    else:
        max_processing_time = f"{max_processing_time_value:.2f} days"  # Show in days if 1 or more
    
    colors = ["#44B39D", "#5B7290", "#E8D6A7", "#A18CCB"]
    
    # Define metrics with color assignment
    metrics = [
        {"title": "Total Purchase", "value": total_purchase, "color": colors[0]},
        {"title": "Number of Orders", "value": quantity, "color": colors[1]},
        {"title": "Max Processing Time", "value": max_processing_time, "color": colors[2]}
    ]

    # Create cards for each standard metric with assigned background colors
    cards = [
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5(metric["title"], className="card-title", style={'font-weight': 'bold'}),
                        html.H2(metric["value"], className="card-text", style={'font-weight': 'bold', 'font-size': '1.5em'}),
                    ]
                ),
                style={'background': metric["color"], 'border': 'none', 'border-radius': '10px', 'padding': '15px'},
                className="text-white text-center"
            ),
            lg=3,  # Adjust width for each metric card
            md=6,
            sm=12
        ) for metric in metrics
    ]
    
    # Add the gauge card with a color from the theme
    gauge_card = dbc.Col(
        dbc.Card(
            dbc.CardBody(
                create_total_received_gauge(data)  # Gauge for Total Received
            ),
            style={
                'background': "#1C1C2C",  # Color for the gauge card from the theme
                'border': 'none', 
                'border-radius': '10px',
                'padding': '0px',
                'height': '150px',
                'width': '150px',
                'display': 'flex',
                'align-items': 'center',
                'justify-content': 'center'
            },
            className="text-white text-center"
        ),
        lg=3,
        md=6,
        sm=12
    )
    
    # Combine metrics with gauge card
    cards.append(gauge_card)
    
    return dbc.Row(cards, className="mb-4 justify-content-center")


def create_category_summary_metrics(metrics):
    # Define the cards using the correct metrics
    cards = [
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Total Spend", className="card-title", style={"color": "white"}),
                    html.H3(metrics["total_spend"], style={"color": "#44B39D"}),
                ]),
                style={"background-color": "#222222", "border": "1px solid #44B39D"},
            ),
            width=4,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Total Orders", className="card-title", style={"color": "white"}),
                    html.H3(f"{metrics['total_orders']:,}", style={"color": "#44B39D"}),
                ]),
                style={"background-color": "#222222", "border": "1px solid #44B39D"},
            ),
            width=4,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Top NIGP Category", className="card-title", style={"color": "white"}),
                    html.H3(metrics["top_category_detail"], style={"color": "#FFD700"}),
                ]),
                style={"background-color": "#222222", "border": "1px solid #FFD700"},
            ),
            width=4,
        ),
    ]
    return dbc.Row(cards, className="mb-4")



def update_summary_metrics(data):
    # Compute total spend
    total_spend = f"${data['Line.Total'].sum():,.2f}"

    # Count unique orders
    total_orders = data['BaseOrderNumber'].nunique()

    # Find top NIGP category
    top_category = data.groupby("NIGP.Description")["Line.Total"].sum().idxmax()
    top_category_spend = data.groupby("NIGP.Description")["Line.Total"].sum().max()
    top_category_detail = f"{top_category} (${top_category_spend:,.2f})"

    # Return as dictionary
    metrics = {
        "total_spend": total_spend,
        "total_orders": total_orders,
        "top_category_detail": top_category_detail,
    }
    return metrics





# Display "Total Received" as a Gauge Indicator Using Plotly’s Indicator Chart
import plotly.graph_objects as go

def create_total_received_gauge(data):
    total_received = data[data['Order.Status'] == 'Received']['BaseOrderNumber'].nunique()
    total_orders = data['BaseOrderNumber'].nunique()
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=total_received,
        title={'text': "Total Received", 'font': {'size': 12}},
        gauge={
            'axis': {'range': [0, total_orders], 'tickvals': [0, total_orders // 2, total_orders]},
            'bar': {'color': "#8CF085"},
            'steps': [
                {'range': [0, total_orders * 0.25], 'color': "#44B39D"},
                {'range': [total_orders * 0.25, total_orders * 0.75], 'color': "#5B7290"},
                {'range': [total_orders * 0.75, total_orders], 'color': "#A18CCB"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': total_received
            }
        },
        number={'suffix': f" / {total_orders}", 'font': {'size': 16}}
    ))

    fig.update_layout(
        width=150,  # Match the dimensions of the metric card
        height=170,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="#1C1C2C",
        font=dict(color="#FFFFFF")
    )

    return dcc.Graph(figure=fig, config={'displayModeBar': False})  # Hide extra controls





# Step 2: Implement Quantity Breakdown by Category (Row 2, Left)
# Step 2: Implement Quantity Breakdown by Category (Row 2, Left)
def create_quantity_breakdown_by_category(data):
    category_data = data.groupby('Procurement.Transaction.Desc')['Quantity.Ordered'].sum().reset_index()
    
    # Assign each category a color manually
    colors = {
        "Non-Tech Equipment": "#DDA0DD", 
        "Tech Equipment": "#8CF085",
        "Imported Goods": "#5B7290",
        "Non-Tech Services": "#E8D6A7",
        "Tech Services": "#A18CCB",
        "Professional Services": "#FFD700",
        "Non-Tech Supplies": "#44B39D",
        "Tech Supplies": "#6A5ACD",

    }




    fig = px.bar(
        category_data,
        x='Quantity.Ordered',
        y='Procurement.Transaction.Desc',
        orientation='h',
        title="Quantity Breakdown by Category",
        color='Procurement.Transaction.Desc',
        color_discrete_map=colors  # Map each category to a specific color
    )
    

    
    fig.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor=theme_colors["background"],
        font=dict(color=theme_colors["text"]),
        xaxis_title="Quantity",
        yaxis_title="Category"
    )
    return dcc.Graph(figure=fig)





# Step 3: Implement Order Quantity by Order Type (Row 2, Right)
def create_order_quantity_by_order_type(data):
    order_type_data = data['Order.Type'].value_counts().reset_index()
    order_type_data.columns = ['Order.Type', 'Count']
    fig = px.pie(
        order_type_data,
        names='Order.Type',
        values='Count',
        title="Order Quantity by Order Type",
        color_discrete_sequence=["#44B39D", "#8CF085"]
    )
    fig.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor=theme_colors["background"],
        font=dict(color=theme_colors["text"])
    )
    return dcc.Graph(figure=fig)






# Step 3: Implement Procurement Category Spend Distribution with Vendor Contribution
# Step: Implement Average Processing Time by Category (Row 2, Right)
def create_avg_processing_time_by_category(data):
    # Calculate the average processing time by procurement category
    avg_processing_time = data.groupby('Procurement.Transaction.Desc')['Processing_Time'].mean().reset_index()
    avg_processing_time.rename(columns={'Processing_Time': 'AvgProcessingTime'}, inplace=True)
    
    # Plot the average processing time by category
    fig = px.bar(
        avg_processing_time,
        x='AvgProcessingTime',
        y='Procurement.Transaction.Desc',
        orientation='h',
        title="Average Processing Time by Category",
        color_discrete_sequence=["#8CF085"]  # Set color as per theme
    )
    
    fig.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)",  # Transparent background
        paper_bgcolor=theme_colors["background"],
        font=dict(color=theme_colors["text"]),
        xaxis_title="Average Processing Time (days)",
        yaxis_title="Category",
        title_font=dict(size=20, color=theme_colors["text"], family="Roboto")
    )
    
    return dcc.Graph(figure=fig)




# Step: Implement Procurement Category Spend Distribution (Row 3, Left)
def create_procurement_category_spend_distribution(data):
    # Step 1: Calculate total purchases by each vendor in each category, considering filtering
    vendor_category_total = data.groupby(['Vendor.Name', 'Procurement.Transaction.Desc'])['Line.Total'].sum().reset_index()
    vendor_category_total.rename(columns={'Line.Total': 'VendorTotalPurchasesByCategory'}, inplace=True)
    
    # Step 2: Calculate total purchases for each category across all vendors using the full (unfiltered) dataset
    full_category_total = cleaned_data.groupby('Procurement.Transaction.Desc')['Line.Total'].sum().reset_index()
    full_category_total.rename(columns={'Line.Total': 'TotalPurchasesByCategoryAllVendors'}, inplace=True)
    
    # Step 3: Merge the filtered vendor totals with the full category totals
    vendor_category_total = vendor_category_total.merge(full_category_total, on='Procurement.Transaction.Desc', how='left')
    
    # Step 4: Calculate the percentage contribution
    vendor_category_total['VendorPercentageContribution'] = (
        vendor_category_total['VendorTotalPurchasesByCategory'] / vendor_category_total['TotalPurchasesByCategoryAllVendors']
    ) * 100  # Multiply by 100 to get percentage

    # Assign each category a color manually
    colors = {
        "Non-Tech Equipment": "#DDA0DD", 
        "Tech Equipment": "#8CF085",
        "Imported Goods": "#5B7290",
        "Non-Tech Services": "#E8D6A7",
        "Tech Services": "#A18CCB",
        "Professional Services": "#FFD700",
        "Non-Tech Supplies": "#44B39D",
        "Tech Supplies": "#6A5ACD",

    }  

    
    # Step 5: Create the plot
    fig = px.treemap(
        vendor_category_total,
        path=['Procurement.Transaction.Desc', 'Vendor.Name'],  # Hierarchy: Category -> Vendor
        values='VendorPercentageContribution',
        color='Procurement.Transaction.Desc',
        title="Procurement Category Spend Distribution: Vendor vs. All Vendors",
        color_discrete_sequence=["#44B39D", "#8CF085", "#5B7290", "#E8D6A7", "#A18CCB", "#FFD700", "#FF7F50", "#6A5ACD"]
    )
    
    fig.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor=theme_colors["background"],
        font=dict(color=theme_colors["text"]),
        title_font=dict(size=20, color=theme_colors["text"], family="Roboto")
    )
    
    return dcc.Graph(figure=fig)




# Step 6: Implement Purchases Over Time (Row 4)
def create_purchases_over_time(data):
    # Step 1: Generate a complete monthly date range for the analysis period
    data['Ordered.Date'] = pd.to_datetime(data['Ordered.Date'])
    date_range = pd.date_range(start=data['Ordered.Date'].min(), end=data['Ordered.Date'].max(), freq='M')
    
    # Step 2: Aggregate purchases by month and ensure all months are present
    monthly_purchases = data.groupby(data['Ordered.Date'].dt.to_period("M"))['Line.Total'].sum().reindex(date_range.to_period("M"), fill_value=0).reset_index()
    monthly_purchases.columns = ['Ordered.Date', 'Line.Total']
    monthly_purchases['Ordered.Date'] = monthly_purchases['Ordered.Date'].dt.to_timestamp()
    
    # Step 3: Calculate the percentage change, handling cases where the previous month has zero purchases
    monthly_purchases['Pct_Change'] = monthly_purchases['Line.Total'].pct_change().replace([float('inf'), -float('inf')], None) * 100  # Convert to percentage

    # Step 4: Determine which entries are legitimately "New" increases from zero
    monthly_purchases['Pct_Change_Label'] = monthly_purchases.apply(
        lambda row: "New" if row['Line.Total'] > 0 and row['Pct_Change'] is None else
                    f"{min(abs(row['Pct_Change']), 999.99):.2f}%" if not pd.isna(row['Pct_Change']) else "",
        axis=1
    )

    # Step 5: Determine symbols and colors based on increase or decrease
    monthly_purchases['Symbol'] = np.where(monthly_purchases['Pct_Change'] > 0, '▲', '▼')
    monthly_purchases['Color'] = np.where(monthly_purchases['Pct_Change'] > 0, "#8CF085", "#FF7F50")  # Teal for increase, coral for decrease
    
    # Step 6: Create the bar plot with annotations
    fig = px.bar(
        monthly_purchases,
        x='Ordered.Date',
        y='Line.Total',
        title="Purchases Over Time",
        labels={'Ordered.Date': 'Date', 'Line.Total': 'Total Purchases'},
        color_discrete_sequence=["#5B7290"]  # Using theme color for bars
    )
    
    # Step 7: Add annotations for percentage change with symbols and colors
    for i, row in monthly_purchases.iterrows():
        if row['Pct_Change_Label']:  # Only add annotation if there's a meaningful label
            fig.add_annotation(
                x=row['Ordered.Date'],
                y=row['Line.Total'],
                text=f"{row['Symbol']} {row['Pct_Change_Label']}",
                showarrow=False,
                yshift=10,  # Shift label slightly above the bar
                font=dict(size=12, color=row['Color'])  # Use teal for increase, coral for decrease
            )
    
    # Step 8: Update layout to match theme colors
    fig.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor=theme_colors["background"],
        font=dict(color=theme_colors["text"]),
        xaxis_title="Date",
        yaxis_title="Total Purchases",
        title_font=dict(size=20, color=theme_colors["text"], family="Roboto")
    )
    
    return dcc.Graph(figure=fig)





""
# Placeholder data for predictions
# Function to generate forecast data
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_percentage_error
import itertools

# Function to optimize ARIMA parameters for initial exploration
def optimize_arima(train_data):
    p = d = q = range(0, 3)
    pdq_combinations = list(itertools.product(p, d, q))
    
    best_aic = float("inf")
    best_pdq = None
    for pdq in pdq_combinations:
        try:
            model = ARIMA(train_data, order=pdq)
            model_fit = model.fit()
            if model_fit.aic < best_aic:
                best_aic = model_fit.aic
                best_pdq = pdq
        except:
            continue
    return best_pdq


""
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_percentage_error
import numpy as np

from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_percentage_error
import numpy as np

def rolling_cross_validation(data, forecast_length=3, seasonal_order=(1, 1, 1, 12), num_folds=5):
    """
    Performs rolling cross-validation for time series data with SARIMA model.
    
    Parameters:
    - data (pd.Series): The time series data.
    - forecast_length (int): Number of steps to forecast in each fold.
    - seasonal_order (tuple): Seasonal order parameters for SARIMA.
    - num_folds (int): Number of cross-validation folds.
    
    Returns:
    - avg_mape (float): Average MAPE across folds.
    - mape_scores (list): List of MAPE scores for each fold.
    """
    fold_size = len(data) // (num_folds + 1)
    mape_scores = []

    for fold in range(num_folds):
        # Define the training and test sets for this fold
        train_data = data[:fold_size * (fold + 1)]
        test_data = data[fold_size * (fold + 1): fold_size * (fold + 1) + forecast_length]

        # Apply SARIMA model to the training data
        model = SARIMAX(train_data, order=(1, 1, 1), seasonal_order=seasonal_order)
        try:
            results = model.fit(disp=False)
            forecast_log = results.forecast(steps=len(test_data))
            forecast = np.expm1(forecast_log)  # Reverse log transformation if used

            # Calculate MAPE for this fold
            actual = np.expm1(test_data)  # Reverse log transformation on test data if used
            mape = mean_absolute_percentage_error(actual, forecast)
            mape_scores.append(mape)
        except Exception as e:
            print(f"Error in fold {fold + 1}: {e}")
            continue

    # Calculate the average MAPE across all folds
    avg_mape = np.mean(mape_scores) if mape_scores else None
    return avg_mape, mape_scores



""
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.statespace.sarimax import SARIMAX
# Generate forecast data using SARIMA with optimized parameters
from pmdarima import auto_arima
from sklearn.metrics import mean_absolute_percentage_error
import numpy as np
import pandas as pd

from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_percentage_error
import numpy as np
import pandas as pd

from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_percentage_error


from sklearn.metrics import mean_absolute_percentage_error
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_absolute_percentage_error
import numpy as np
import pandas as pd

def generate_forecast_ets(data, forecast_length, seasonal_period=12, num_folds=5):
    try:
        # Aggregate data to monthly totals
        monthly_data = data.groupby(data['Ordered.Date'].dt.to_period("M"))['Line.Total'].sum()
        monthly_data.index = monthly_data.index.to_timestamp()

        # Log transformation to stabilize variance
        log_monthly_data = np.log1p(monthly_data)

        # Split into training and test sets
        split_point = int(len(log_monthly_data) * 0.8)
        train_data, test_data = log_monthly_data[:split_point], log_monthly_data[split_point:]

        # Apply Exponential Smoothing on the training data
        ets_model = ExponentialSmoothing(train_data, seasonal='mul', seasonal_periods=seasonal_period)
        ets_fit = ets_model.fit()

        # Forecast on the test data to evaluate accuracy
        test_forecast_log = ets_fit.forecast(steps=len(test_data))
        test_forecast = np.expm1(test_forecast_log)  # Reverse log transformation
        mape = mean_absolute_percentage_error(np.expm1(test_data), test_forecast)  # MAPE calculation for test data

        # Forecast future values beyond the test set
        future_forecast_log = ets_fit.forecast(steps=forecast_length)
        future_forecast = np.expm1(future_forecast_log)  # Reverse log transformation
        future_dates = pd.date_range(start=monthly_data.index[-1], periods=forecast_length + 1, freq='M')[1:]
        forecast_df = pd.DataFrame({'Date': future_dates, 'Forecast': future_forecast})

        print(f"ETS Model Accuracy (MAPE on test set): {mape:.2f}%")
        return forecast_df, mape

    except Exception as e:
        print(f"ETS Forecast Error: {e}")
        # Return empty forecast and None for MAPE if an error occurs
        return pd.DataFrame(columns=['Date', 'Forecast']), None



def generate_forecast_sarima(data, forecast_length, seasonal_order=(1, 1, 1, 12), num_folds=5):
    print("Entering generate_forecast_sarima...")  # Debug start

    try:
        # Aggregate data to monthly totals
        monthly_data = data.groupby(data['Ordered.Date'].dt.to_period("M"))['Line.Total'].sum()
        monthly_data.index = monthly_data.index.to_timestamp()
        print(f"Monthly Data Shape: {monthly_data.shape}")
        print(f"Monthly Data Preview:\n{monthly_data.head()}")
    except Exception as e:
        print(f"Error aggregating data for SARIMA: {e}")
        return pd.DataFrame(columns=['Date', 'Forecast']), None

    # Ensure sufficient data
    if len(monthly_data) < seasonal_order[-1] * 2:
        print("Insufficient data for SARIMA.")
        return pd.DataFrame(columns=['Date', 'Forecast']), None

    # Log transformation to stabilize variance
    try:
        log_monthly_data = np.log1p(monthly_data)
        print("Log transformation applied successfully.")
    except Exception as e:
        print(f"Error applying log transformation: {e}")
        return pd.DataFrame(columns=['Date', 'Forecast']), None

    # Debug splitting into training and test sets
    try:
        split_point = int(len(log_monthly_data) * 0.8)
        train_data, test_data = log_monthly_data[:split_point], log_monthly_data[split_point:]
        print(f"Training Data Shape: {train_data.shape}, Test Data Shape: {test_data.shape}")
    except Exception as e:
        print(f"Error splitting data: {e}")
        return pd.DataFrame(columns=['Date', 'Forecast']), None

    # Debug model fitting and forecasting
    try:
        sarima_model = SARIMAX(train_data, order=(1, 1, 1), seasonal_order=seasonal_order)
        sarima_fit = sarima_model.fit(disp=False)
        print("SARIMA model fitted successfully.")
    except Exception as e:
        print(f"Error fitting SARIMA model: {e}")
        return pd.DataFrame(columns=['Date', 'Forecast']), None

    try:
        # Forecast on the test data to evaluate accuracy
        test_forecast_log = sarima_fit.forecast(steps=len(test_data))
        test_forecast = np.expm1(test_forecast_log)  # Reverse log transformation
        mape = mean_absolute_percentage_error(np.expm1(test_data), test_forecast)  # MAPE calculation for test data

        # Forecast future values beyond the test set
        future_forecast_log = sarima_fit.forecast(steps=forecast_length)
        future_forecast = np.expm1(future_forecast_log)  # Reverse log transformation
        future_dates = pd.date_range(start=monthly_data.index[-1], periods=forecast_length + 1, freq='M')[1:]
        forecast_df = pd.DataFrame({'Date': future_dates, 'Forecast': future_forecast})

        print(f"SARIMA Model Accuracy (MAPE on test set): {mape:.2f}%")
        return forecast_df, mape

    except Exception as e:
        print(f"Error during forecasting: {e}")
        return pd.DataFrame(columns=['Date', 'Forecast']), None










# Function to create layout for Prediction Analysis

def create_prediction_analysis_content(data, forecast_length):
    print("Entering create_prediction_analysis_content...")  # Debugging
    print(f"Input Data Shape: {data.shape}")
    print(f"Forecast Length: {forecast_length}")

    # Ensure Ordered.Date is in datetime format
    data['Ordered.Date'] = pd.to_datetime(data['Ordered.Date'], errors='coerce')
    print("Converted Ordered.Date to datetime.")

    # Aggregate the historical data
    try:
        historical_data = data.groupby(data['Ordered.Date'].dt.to_period("M"))['Line.Total'].sum().reset_index()
        historical_data['Ordered.Date'] = historical_data['Ordered.Date'].dt.to_timestamp()
        print(f"Aggregated Historical Data:\n{historical_data.head()}")
    except Exception as e:
        print(f"Error during aggregation: {e}")
        raise

    # Initialize variables for forecasts and MAPE
    forecast_df_ets, mape_ets, ets_error_message = None, None, None
    forecast_df_sarima, mape_sarima, sarima_error_message = None, None, None

    # Try generating ETS forecast
    try:
        forecast_df_ets, mape_ets = generate_forecast_ets(data, forecast_length)
    except ValueError as e:
        ets_error_message = f"ETS Forecast Error: {e}"
        print(ets_error_message)

    # Try generating SARIMA forecast
    try:
        forecast_df_sarima, mape_sarima = generate_forecast_sarima(data, forecast_length)
    except ValueError as e:
        sarima_error_message = f"SARIMA Forecast Error: {e}"
        print(sarima_error_message)


    # Create the figure with available forecasts
    traces = [
        go.Scatter(
            x=historical_data['Ordered.Date'],
            y=historical_data['Line.Total'],
            mode='lines+markers',
            name='Historical Data',
            line=dict(color="blue")
        )
    ]

    if forecast_df_ets is not None and not forecast_df_ets.empty:
        traces.append(
            go.Scatter(
                x=forecast_df_ets['Date'],
                y=forecast_df_ets['Forecast'],
                mode='lines+markers',
                name='ETS Forecast',
                line=dict(color="lightgreen", dash="dash")
            )
        )
    if forecast_df_sarima is not None and not forecast_df_sarima.empty:
        traces.append(
            go.Scatter(
                x=forecast_df_sarima['Date'],
                y=forecast_df_sarima['Forecast'],
                mode='lines+markers',
                name='SARIMA Forecast',
                line=dict(color="lightcoral", dash="dot")
            )
        )



    fig = go.Figure(traces)
    fig.update_layout(
        title="Forecast vs. Historical Data",
        xaxis_title="Date",
        yaxis_title="Line Total",
        paper_bgcolor=theme_colors["background"],  # Matches the background of your web app
        plot_bgcolor="rgba(0, 0, 0, 0)",          # Transparent plot background
        font=dict(color="white"),                 # Font color for text
        xaxis=dict(
            gridcolor="gray",                     # Gridline color
            tickfont=dict(color="white")          # Tick color
        ),
        yaxis=dict(
            gridcolor="gray",
            tickfont=dict(color="white")
        ),
        legend=dict(
            font=dict(color="white"),             # Legend text color
            bgcolor="rgba(0, 0, 0, 0)",           # Transparent legend background
            bordercolor="gray"                    # Legend border color
        )
    )


    print("Forecast DF ETS:", forecast_df_ets is not None)
    print("Forecast DF SARIMA:", forecast_df_sarima is not None)
    print("ETS Error Message:", ets_error_message)
    print("SARIMA Error Message:", sarima_error_message)

    # Handle cases where no valid forecasts were generated
    if forecast_df_ets is None or forecast_df_sarima is None or forecast_df_ets.empty and forecast_df_sarima.empty:
        user_message = html.Div([
            html.H4("No valid forecasts generated", style={"color": "red", "text-align": "center"}),
            html.P("Reasons:", style={"text-align": "center"}),
            html.Ul([
                html.Li(ets_error_message if ets_error_message else "ETS model failed due to insufficient data."),
                html.Li(sarima_error_message if sarima_error_message else "SARIMA model failed due to insufficient data."),
            ], style={"color": "gray", "text-align": "center"}),
            html.P("Possible Causes:", style={"text-align": "center", "margin-top": "10px"}),
            html.Ul([
                html.Li("Data is too short (less than 24 months for ETS or 12 months for SARIMA)."),
                html.Li("No clear seasonal pattern in the data."),
                html.Li("Contains zero or negative values, which are incompatible with ETS."),
                html.Li("Missing critical data points."),
            ], style={"color": "gray", "text-align": "center"}),
        ])
        return html.Div([
            dcc.Graph(id='forecast-plot', figure=fig),
            user_message
        ])

    # Build the summary for valid forecasts
    summary_parts = []
    if forecast_df_ets is not None and mape_ets is not None:
        summary_parts.append(f"ETS Model Accuracy (MAPE): {mape_ets:.2f}%")
    if forecast_df_sarima is not None and mape_sarima is not None:
        summary_parts.append(f"SARIMA Model Accuracy (MAPE): {mape_sarima:.2f}%")

    forecast_summary = " | ".join(summary_parts) if summary_parts else None

    # Return the figure and summary if forecasts exist
    components = [dcc.Graph(id='forecast-plot', figure=fig)]
    if forecast_summary:
        components.append(
            html.Div(
                forecast_summary,
                style={"color": "lightgrey", "text-align": "center", "margin-top": "10px"}
            )
        )

    return html.Div(components)





# Create Plots
def create_top_categories_by_spend(nigp_summary):
    fig = px.bar(
        nigp_summary.nlargest(10, "Total_Spend"),
        x="NIGP.Description",
        y="Total_Spend",
        title="Top Categories by Spend",
        labels={"NIGP.Description": "Category", "Total_Spend": "Total Spend"},
        text="Total_Spend",
        template="plotly_dark"
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        clickmode="event+select",  # Enables click interaction
        plot_bgcolor="#121212",  # Match the dashboard's background
        paper_bgcolor="#121212",
        font=dict(color="white"),
        yaxis=dict(tickformat=".2s"),
        title_font=dict(size=20, color="#44B39D")
    )
    fig.update_traces(texttemplate="%{text:.2s}")
    return dcc.Graph(id="top-categories-by-spend", figure=fig)





def create_top_categories_by_quantity(nigp_summary):
    fig = px.bar(
        nigp_summary.nlargest(10, "Total_Quantity_Ordered"),
        x="NIGP.Description",
        y="Total_Quantity_Ordered",
        title="Top Categories by Quantity Ordered",
        labels={"NIGP.Description": "Category", "Total_Quantity_Ordered": "Quantity Ordered"},
        text="Total_Quantity_Ordered",
        template="plotly_dark"
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor="#121212",
        paper_bgcolor="#121212",
        font=dict(color="white"),
        yaxis=dict(tickformat=".2s"),
        title_font=dict(size=20, color="#44B39D")
    )
    fig.update_traces(texttemplate="%{text:.2s}")
    return dcc.Graph(id="top-categories-by-quantity", figure=fig)



def create_category_distribution_bar(nigp_summary):
    # Define your theme colors

    theme_colors = [
        "#DDA0DD", 
        "#8CF085",
        "#5B7290",
        "#E8D6A7",
        "#A18CCB",
        "#FFD700",
        "#44B39D",
        "#6A5ACD",
        "#F8B195",  # Added Coral
        "#00CED1"   # Added Dark Turquoise
    ]
    
    # Sort and select the top 10 categories
    sorted_data = nigp_summary.sort_values("Order_Count", ascending=False).head(10).copy()
    
    # Add a new column for colors
    sorted_data["Color"] = theme_colors[:len(sorted_data)]  # Assign colors to bars
    
    # Create the bar chart
    fig = px.bar(
        sorted_data,
        x="Order_Count",
        y="NIGP.Description",
        title="Category Distribution by Orders",
        labels={"Order_Count": "Order Count", "NIGP.Description": "Category"},
        text="Order_Count",
        orientation="h",
        color="Color",  # Use the 'Color' column for individual bar colors
        color_discrete_map="identity",  # Ensure exact colors are used
        template="plotly_dark"
    )
    
    # Update layout
    fig.update_layout(
        plot_bgcolor="#121212",  # Dark background for the plot
        paper_bgcolor="#121212",  # Dark background for the paper
        font=dict(color="white"),  # White font color
        yaxis=dict(tickformat=".2s"),  # Format y-axis ticks
        title_font=dict(size=20, color="#44B39D")  # Title styling
    )
    
    # Format text labels on the bars
    fig.update_traces(texttemplate="%{text:.2s}")
    
    return dcc.Graph(id="category-distribution-bar", figure=fig)





def create_cumulative_spend_chart(filtered_data):
    try:
        # Validate required columns
        required_columns = ['Ordered.Date', 'Line.Total', 'NIGP.Description']
        missing_columns = [col for col in required_columns if col not in filtered_data.columns]
        
        if missing_columns:
            return html.Div(
                f"Cumulative Spend Chart: Missing columns {', '.join(missing_columns)}.",
                style={"text-align": "center", "color": "red"}
            )

        # Ensure data is not empty
        if filtered_data.empty:
            return html.Div(
                "Cumulative Spend Chart: No data available.",
                style={"text-align": "center", "color": "red"}
            )

        # Prepare data for cumulative spend calculation
        filtered_data = filtered_data.sort_values(by='Ordered.Date')
        filtered_data['Cumulative_Spend'] = (
            filtered_data.groupby('NIGP.Description')['Line.Total'].cumsum()
        )


        # Create cumulative spend chart
        fig = px.line(
            filtered_data,
            x="Ordered.Date",
            y="Cumulative_Spend",
            color="NIGP.Description",  # Differentiate categories
            title="Cumulative Spend Over Time",
            labels={"Ordered.Date": "Date", "Cumulative_Spend": "Cumulative Spend"},
            line_shape="spline"  # Optional for smoother curves
        )
        fig.update_layout(
            plot_bgcolor="#333333",  # Match dark theme
            paper_bgcolor="#333333",
            font_color="#FFFFFF",
            title_font_size=20
        )
        return dcc.Graph(figure=fig)
    
    except Exception:
        return html.Div(
            "An unexpected error occurred while creating the Cumulative Spend chart.",
            style={"color": "red", "text-align": "center"}
        )



""
def render_category_insights_tab(filtered_data, metrics, nigp_summary):
    # Check if filtered_data is empty
    if filtered_data.empty:
        return html.Div(
            "No data available to display for the selected filters.",
            style={"text-align": "center", "color": "red", "padding": "20px"}
        )

    return dbc.Container(
        [
            # Section Heading: Summary Metrics
            dbc.Row(
                dbc.Col(
                    html.H4("", style={"color": "#1DB954", "margin-bottom": "10px"})
                )
            ),

            # Render category-specific summary metrics
            create_category_summary_metrics(metrics),

            # Section Heading: Visualizations
            dbc.Row(
                dbc.Col(
                    html.H4("", style={"color": "#1DB954", "margin-bottom": "10px"})
                )
            ),

            # Visualization Section: Cumulative Spend Chart
            dbc.Row(
                [
                    dbc.Col(create_cumulative_spend_chart(filtered_data), width=12),
                ],
                className="mb-4",
            ),

            # Visualization Section: Top Categories and Category Distribution
            dbc.Row(
                [
                    dbc.Col(create_top_categories_by_spend(nigp_summary), width=6),
                    dbc.Col(create_top_categories_by_quantity(nigp_summary), width=6),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(create_category_distribution_bar(nigp_summary), width=12),
                ],
                className="mb-4",
            ),

            # Drill-Through Section
            html.Div(
                id="vendor-breakdown",
                style={"margin-top": "20px"},
            ),
        ],
        fluid=True,
        style={"background-color": "#121212", "padding": "20px"},
    )






""


def create_vendor_breakdown(filtered_data):
    try:
        fig = px.bar(
            filtered_data.groupby("Vendor.Name")
            .agg(Total_Spend=("Line.Total", "sum"))
            .reset_index(),
            x="Vendor.Name",
            y="Total_Spend",
            title="Vendor Breakdown for Selected Category",
            labels={"Vendor.Name": "Vendor", "Total_Spend": "Total Spend"},
            text="Total_Spend",
            template="plotly_dark"
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            plot_bgcolor="#121212",  # Match the dark background
            paper_bgcolor="#121212",
            font=dict(color="white"),
            yaxis=dict(tickformat=".2s"),
            title_font=dict(size=20, color="#44B39D"),
            legend=dict(font=dict(color="white"))
        )
        fig.update_traces(texttemplate="%{text:.2s}")
        return dcc.Graph(id="vendor-breakdown-chart", figure=fig)
    except Exception as e:
        return html.Div(
            f"Error creating vendor breakdown chart: {e}",
            style={"color": "red", "text-align": "center"}
        )






app.layout = dbc.Container(
    fluid=True,
    style={
        'backgroundColor': theme_colors["background"],
        'minHeight': '100vh',
        'padding': '10px 20px',
    },
    children=[
        # Header Section
        dbc.Row(
            dbc.Col(
                html.H1("Virginia Department of Corrections - Insights Dashboard",
                        className="text-center",
                        style={
                            #'color': theme_colors["text"],
                            'color': '#8c8c8c',         # Light green header
                            'font-family': 'Roboto, sans-serif',
                            'font-weight': '700',
                            'font-size': '2.5em',
                            'margin-top': '10px',
                            #'font-weight': 'bold',
                            'margin-bottom': '10px',
                            'text-shadow': '2px 2px 4px rgba(0, 0, 0, 0.7)'  # Soft shadow
                        }),
                width=12
            )
        ),
        # Filter Section
        dbc.Row(
            dbc.Col(
                html.Div(id="filters-container"),  # Dynamic filters container
                width={"size": 10, "offset": 1},
                style={'margin-bottom': '15px'}
            )
        ),
        # Tabs Section
        dbc.Row(
            dbc.Col(
                dbc.Tabs(
                    [
                        dbc.Tab(label="Overview", tab_id="overview-tab", className="custom-tab",
                                tab_style={
                                    'backgroundColor': 'linear-gradient(135deg, #5b8cbe, #4a6fa1)',  # Blue gradient
                                    'color': '#E8D6A7',
                                    'padding': '10px',
                                    'borderRadius': '5px',
                                    'fontWeight': 'bold',
                                    'border': '2px solid #44b39d'},
                                active_label_style={
                                    'backgroundColor': '#FFD700',  # Highlight active tab in gold
                                    'color': '#333333',
                                    'fontWeight': 'bold',
                                    'border': '2px solid #FFD700',
                                    'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.3)',
                                    'borderRadius': '5px'}
                                ),
                        dbc.Tab(label="Spend Analysis", tab_id="spend-analysis-tab", className="custom-tab",
                                tab_style={
                                    'backgroundColor': 'linear-gradient(135deg, #60c6a8, #44b39d)',  # Green gradient
                                    'color': '#E8D6A7',
                                    'padding': '10px',
                                    'borderRadius': '5px',  # Rounded corners
                                    'fontWeight': 'bold',
                                    'border': '2px solid #44b39d'},
                                active_label_style={
                                    'backgroundColor': '#8CF085',  # Soft green for active
                                    'fontWeight': 'bold',
                                    'border': '2px solid #FFD700',
                                    'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.3)',
                                    'borderRadius': '5px'}
                                ),
                        dbc.Tab(label="Vendor Insights", tab_id="vendor-insights-tab", className="custom-tab",
                                tab_style={
                                    'backgroundColor': 'linear-gradient(135deg, #a18ccb, #5b7290)',  # Purple gradient
                                    'color': '#E8D6A7',
                                    'padding': '10px',
                                    'borderRadius': '5px',
                                    'fontWeight': 'bold',
                                    'border': '2px solid #44b39d'},
                                active_label_style={
                                    'backgroundColor': '#DDA0DD',  # Soft purple for active
                                    'color': '#333333',
                                    'fontWeight': 'bold',
                                    'border': '2px solid #FFD700',
                                    'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.3)',
                                    'borderRadius': '5px'}
                                ),
                        dbc.Tab(label="Category Insights", tab_id="category-insights-tab", className="custom-tab",
                                tab_style={
                                    'backgroundColor': 'linear-gradient(135deg, #E8D6A7, #D3C2A3)',  # Beige gradient
                                    'color': '#E8D6A7',
                                    'padding': '10px',
                                    'borderRadius': '5px',
                                    'fontWeight': 'bold',
                                    'border': '2px solid #44b39d'},
                                active_label_style={
                                    'backgroundColor': '#FFD700',  # Gold for active
                                    'color': '#333333',
                                    'fontWeight': 'bold',
                                    'border': '2px solid #FFD700',
                                    'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.3)',
                                    'borderRadius': '5px'}
                                ),
                        dbc.Tab(label="Prediction Analysis", tab_id="prediction-analysis-tab", className="custom-tab",
                                tab_style={
                                    'backgroundColor': 'linear-gradient(135deg, #a8d5ba, #91c6a5)',  # Light green gradient
                                    'color': '#E8D6A7',
                                    'padding': '10px',
                                    'borderRadius': '5px',
                                    'fontWeight': 'bold',
                                    'border': '2px solid #44b39d'},
                                active_label_style={
                                    'backgroundColor': '#44B39D',  # Highlight active in darker green
                                    'color': '#333333',
                                    'fontWeight': 'bold',
                                    'border': '2px solid #FFD700',
                                    'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.3)',
                                    'borderRadius': '5px'}
                                ),
                    ],
                    id="tabs",
                    active_tab="overview-tab",
                    className="custom-tabs justify-content-center"
                ),
                width=12,
                style={'margin': '10px 0','margin-bottom': '10px', 'borderBottom': '1px solid #333333'}
            )
        ),
        # Tab Content Containers
        html.Div(id="overview-content", style={"display": "none"}),
        html.Div(id="spend-analysis-content", style={"display": "none"}),
        html.Div(id="vendor-insights-content", style={"display": "none"}),
        html.Div(
            id="category-insights-content",
            style={"display": "none"},
            children=[
                dbc.Container([
                    dbc.Row([
                        dbc.Col(create_top_categories_by_spend(nigp_summary), width=6, style={"margin-bottom": "20px"}),  # Add margin
                        dbc.Col(create_top_categories_by_quantity(nigp_summary), width=6),
                    ], className="mb-4"),
                    dbc.Row([
                        dbc.Col(create_category_distribution_bar(nigp_summary), width=12),
                    ]),
                    html.Div(
                        id="vendor-breakdown",
                        style={"margin-top": "20px"}  # Add spacing for the drill-through section
                    ),
                ])
            ]
        ),


        html.Div(id="prediction-analysis-content", style={"display": "none"}),
    ]
)










### Adding Debugging Print Statements

from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.dependencies import Input, Output, State, MATCH

from dash import callback_context
from dash.exceptions import PreventUpdate
from dash import no_update

@app.callback(
    Output("overview-content", "children"),
    [
        Input("overview-date-range-picker", "start_date"),
        Input("overview-date-range-picker", "end_date"),
        Input("overview-region-dropdown", "value"),
        Input("overview-order-status-dropdown", "value"),
        Input("overview-procurement-transaction-desc-dropdown", "value"),
    ],
)
def render_overview_tab(start_date, end_date, region, status, procurement_desc):
    # Filter the data based on the selected filters
    filtered_data = cleaned_data.copy()
    if start_date and end_date:
        filtered_data = filtered_data[
            (filtered_data['Ordered.Date'] >= pd.to_datetime(start_date)) &
            (filtered_data['Ordered.Date'] <= pd.to_datetime(end_date))
        ]
    if region:
        filtered_data = filtered_data[filtered_data['Virginia_Region'].isin(region)]
    if status:
        filtered_data = filtered_data[filtered_data['Order.Status'].isin(status)]
    if procurement_desc:
        filtered_data = filtered_data[filtered_data['Procurement.Transaction.Desc'].isin(procurement_desc)]

    # Handle empty data case
    if filtered_data.empty:
        return html.Div("No data available for the selected filters.", style={"color": "red", "text-align": "center"})

    # Return the metrics and plots
    return html.Div([
        dbc.Row(
            dbc.Col(
                create_overview_metrics(filtered_data),
                width={"size": 10, "offset": 1},  # Center metrics with offset
                className="justify-content-center"
            ),
            className="mb-4"
        ),
        create_total_expenditure_plot(filtered_data),  # Total Expenditure plot
        create_order_volume_plot(filtered_data),       # Order Volume plot
        create_top_vendors_plot(filtered_data),        # Top Vendors by Expenditure plot
        create_top_regions_plot(filtered_data)         # Top Regions by Expenditure plot
    ])






@app.callback(
    Output("spend-analysis-content", "children"),
    [
        Input("spend-date-range-picker", "start_date"),
        Input("spend-date-range-picker", "end_date"),
        Input("spend-region-dropdown", "value"),
        Input("spend-vendor-dropdown", "value"),
    ],
)
def render_spend_analysis_tab(start_date, end_date, region, vendor):
    # Filter the data based on the selected filters
    filtered_data = cleaned_data.copy()
    if start_date and end_date:
        filtered_data = filtered_data[
            (filtered_data['Ordered.Date'] >= pd.to_datetime(start_date)) &
            (filtered_data['Ordered.Date'] <= pd.to_datetime(end_date))
        ]
    if region:
        filtered_data = filtered_data[filtered_data['Virginia_Region'].isin(region)]
    if vendor:
        filtered_data = filtered_data[filtered_data['Vendor.Name'].isin(vendor)]

    # Handle empty data case
    if filtered_data.empty:
        return html.Div("No data available for the selected filters.", style={"color": "red", "text-align": "center"})

    # Return the plots organized by layout
    return html.Div([
        # Header Section: Filters and Summary Cards
        html.Div(
            [
                # Filters section can be placed here if needed
                html.Div("Filters and Summary Cards", style={"font-weight": "bold", "text-align": "center"})
            ],
            style={"margin-bottom": "20px"}
        ),

        # Key Visualizations Section
        html.Div(
            [
                create_monthly_spend_trend(filtered_data),  # Monthly Spend Trend plot
            ],
            style={"margin-bottom": "20px"}
        ),

        html.Div(
            [
                # Side-by-side Treemap and Donut Chart
                html.Div(
                    create_spend_by_category_treemap(filtered_data),
                    style={"width": "48%", "display": "inline-block"}
                ),
                html.Div(
                    create_spend_by_order_status_donut(filtered_data),
                    style={"width": "48%", "display": "inline-block", "margin-left": "2%"}
                ),
            ],
            style={"margin-bottom": "20px"}
        ),

        # Category Details Section
        html.Div(
            id='category-details',
            style={"margin-top": "20px", "text-align": "center", "color": "blue"}
        ),

        # Detailed Analysis Section
        html.Div(
            [
                create_spend_by_shipping_city_map(filtered_data),  # Spend by Shipping City map
            ]
        )
    ])





@app.callback(
    Output("vendor-insights-content", "children"),
    [
        Input("vendor-insights-date-range-picker", "start_date"),
        Input("vendor-insights-date-range-picker", "end_date"),
        Input("vendor-insights-vendor-dropdown", "value"),
    ],
)
def render_vendor_insights_tab(start_date, end_date, vendor):
    # Filter the data based on the selected filters
    filtered_data = cleaned_data.copy()
    if start_date and end_date:
        filtered_data = filtered_data[
            (filtered_data['Ordered.Date'] >= pd.to_datetime(start_date)) &
            (filtered_data['Ordered.Date'] <= pd.to_datetime(end_date))
        ]
    if vendor:
        filtered_data = filtered_data[filtered_data['Vendor.Name'].isin(vendor)]

    # Handle empty data case
    if filtered_data.empty:
        return html.Div("No data available for the selected filters.", style={"color": "red", "text-align": "center"})

    # Return the styled content
    return html.Div([
        create_summary_metrics_row(filtered_data),  # Use the summary function which calculates quantity
        dbc.Row([
            dbc.Col(create_quantity_breakdown_by_category(filtered_data), width=6),
            dbc.Col(create_order_quantity_by_order_type(filtered_data), width=6),
        ]),
        dbc.Row([
            dbc.Col(create_procurement_category_spend_distribution(filtered_data), width=6),
            dbc.Col(create_avg_processing_time_by_category(filtered_data), width=6),
        ]),
        create_purchases_over_time(filtered_data)
    ])



@app.callback(
    Output("vendor-breakdown", "children"),
    Input("top-categories-by-spend", "clickData")
)
def update_vendor_breakdown(click_data):
    print(f"Raw clickData: {click_data}")  # Log raw clickData for inspection

    if click_data is None or "points" not in click_data:
        return html.Div("Click a category to see vendor details.", style={"text-align": "center", "color": "gray"})

    try:
        selected_category = click_data["points"][0]["x"]
        print(f"Selected category: {selected_category}")
        filtered_data = cleaned_data[cleaned_data["NIGP.Description"] == selected_category]

        if filtered_data.empty:
            return html.Div("No vendor data available for the selected category.", style={"text-align": "center", "color": "red"})

        return create_vendor_breakdown(filtered_data)
    except Exception as e:
        print(f"Error processing clickData: {e}")
        return html.Div("An error occurred while processing your selection.", style={"color": "red"})



@app.callback(
    Output("category-insights-content", "children"),
    [
        Input("category-vendor-dropdown", "value"),
        Input("category-procurement-dropdown", "value"),
        Input("category-date-range-picker", "start_date"),
        Input("category-date-range-picker", "end_date"),
    ]
)
def update_category_insights_tab(selected_vendors, selected_category, start_date, end_date):
    # Create a copy of the cleaned dataset
    filtered_data = cleaned_data.copy()

    # Apply Vendor Filter
    if selected_vendors:
        filtered_data = filtered_data[filtered_data["Vendor.Name"].isin(selected_vendors)]

    # Apply Procurement Category Filter
    if selected_category:
        if isinstance(selected_category, list):  # Multi-select dropdown
            filtered_data = filtered_data[filtered_data["Procurement.Transaction.Desc"].isin(selected_category)]
        else:  # Single-selection dropdown
            filtered_data = filtered_data[filtered_data["Procurement.Transaction.Desc"] == selected_category]

    # Apply Date Range Filter
    if start_date and end_date:
        filtered_data = filtered_data[
            (filtered_data["Ordered.Date"] >= pd.to_datetime(start_date)) &
            (filtered_data["Ordered.Date"] <= pd.to_datetime(end_date))
        ]



    # If no data is left after filtering
    if filtered_data.empty:
        return html.Div("No data available for the selected filters.", style={"text-align": "center", "color": "red"})


    # Compute metrics and summary
    metrics = update_summary_metrics(filtered_data)
    nigp_summary = filtered_data.groupby("NIGP.Description").agg(
        Total_Spend=("Line.Total", "sum"),
        Total_Quantity_Ordered=("Quantity.Ordered", "sum"),
        Order_Count=("BaseOrderNumber", "nunique")
    ).reset_index()

    # Pass both metrics and nigp_summary to the render function
    return render_category_insights_tab(filtered_data, metrics, nigp_summary)
    



    
@app.callback(
    Output("prediction-analysis-content", "children"),
    [Input("prediction-vendor-dropdown", "value"),
     Input("forecast-horizon-slider", "value")]
)
def render_prediction_analysis_tab(vendor, forecast_length):
    print("Entering render_prediction_analysis_tab...")  # Debug start

    # Default forecast length if None
    if not forecast_length:
        forecast_length = 12  # Default to 12 months
    print(f"Forecast Length Selected: {forecast_length}")

    # Filter the data based on the selected vendor
    filtered_data = cleaned_data.copy()

    if vendor:
        print(f"Vendors selected: {vendor}")
        try:
            filtered_data = filtered_data[filtered_data['Vendor.Name'].isin(vendor)]
            print(f"Filtered Data Shape After Vendor Selection: {filtered_data.shape}")
        except Exception as e:
            print(f"Error during vendor filtering: {e}")
            return html.Div("Error filtering data for selected vendor.", style={"color": "red", "text-align": "center"})

    # Handle empty data case
    if filtered_data.empty:
        print("Filtered data is empty after applying vendor filter.")
        return html.Div("No data available for the selected filters.", style={"color": "red", "text-align": "center"})

    # Generate prediction content
    try:
        print("Filtered data is not empty. Proceeding to create content.")
        prediction_content = create_prediction_analysis_content(filtered_data, forecast_length)
    except ValueError as e:
        print(f"ValueError during content creation: {e}")
        return html.Div(
            f"Error generating prediction: {e}",
            style={"color": "red", "text-align": "center", "margin-top": "20px"}
        )
    except Exception as e:
        print(f"Unexpected error during content creation: {e}")
        return html.Div(
            "An unexpected error occurred while generating the prediction.",
            style={"color": "red", "text-align": "center", "margin-top": "20px"}
        )

    print("Prediction content successfully created.")
    print("Rendered Content:", prediction_content)

    return prediction_content









@app.callback(
    [
        Output("overview-content", "style"),
        Output("spend-analysis-content", "style"),
        Output("vendor-insights-content", "style"),
        Output("category-insights-content", "style"),  # Change to "style"
        Output("prediction-analysis-content", "style"),
    ],
    Input("tabs", "active_tab"),
)
def toggle_tab_visibility(active_tab):
    # Default style for all tabs (hidden)
    hidden_style = {"display": "none"}
    visible_style = {"display": "block"}

    # Return visibility styles for all tabs
    return (
        visible_style if active_tab == "overview-tab" else hidden_style,
        visible_style if active_tab == "spend-analysis-tab" else hidden_style,
        visible_style if active_tab == "vendor-insights-tab" else hidden_style,
        visible_style if active_tab == "category-insights-tab" else hidden_style,
        visible_style if active_tab == "prediction-analysis-tab" else hidden_style,
    )









# Separate callback for updating the forecast plot and summary metrics based on forecast settings


@app.callback(
    [Output("forecast-plot", "figure"),
     Output("forecast-summary", "children")],
    [Input("forecast-length", "value")],
    [State("tab-content", "children")]
)
def update_forecast(forecast_length, tab_content):
    global cleaned_data  # Ensure to use the main dataset


    print("Entering update_forecast...")  # Debug start
    # Validate forecast_length
    if not forecast_length:
        forecast_length = 12  # Default to 12 months if none provided
        print(f"No forecast length provided. Defaulting to {forecast_length} months.")

    # Debug the main dataset
    print(f"Cleaned Data Shape: {cleaned_data.shape}")
    print(f"Cleaned Data Columns: {cleaned_data.columns}")


    # Filter the data if needed
    data = cleaned_data.copy()


    # Debug the data after copying
    print(f"DataFrame Shape after copying cleaned_data: {data.shape}")
    print(f"DataFrame Head after copying cleaned_data:\n{data.head()}")
    
    # Ensure Ordered.Date is in datetime format
    try:
        data['Ordered.Date'] = pd.to_datetime(data['Ordered.Date'], errors='coerce')
        print("Ordered.Date successfully converted to datetime.")
    except Exception as e:
        print(f"Error converting Ordered.Date: {e}")

    # Check if data is non-empty before proceeding
    if data.empty:
        print("Cleaned data is empty after processing.")
        return (
            go.Figure(),  # Return an empty figure
            "No data available for forecasting."
        )

    # Add debugging before generating forecasts
    print("Data looks good. Proceeding to generate forecasts...")

    # Debug forecast_length and filtered data
    print(f"Forecast Length: {forecast_length}")
    print(f"Filtered Data Shape: {data.shape}")
    print(f"Filtered Data Preview:\n{data.head()}")
    
    # Try generating ETS and SARIMA forecasts
    forecast_df_ets, mape_ets = None, None
    try:
        forecast_df_ets, mape_ets = generate_forecast_ets(data, forecast_length=forecast_length)
        print(f"ETS Forecast Data:\n{forecast_df_ets.head()}")
        print(f"ETS MAPE: {mape_ets}")
    except Exception as e:
        print(f"ETS Forecast Error: {e}")

    forecast_df_sarima, mape_sarima = None, None
    try:
        forecast_df_sarima, mape_sarima = generate_forecast_sarima(data, forecast_length=forecast_length)
        print(f"SARIMA Forecast Data:\n{forecast_df_sarima.head()}")
        print(f"SARIMA MAPE: {mape_sarima}")
    except Exception as e:
        print(f"SARIMA Forecast Error: {e}")

    # Prepare historical data for plotting
    # Debug historical data creation
    try:
        historical_data = data.groupby(data['Ordered.Date'].dt.to_period("M"))['Line.Total'].sum().reset_index()
        historical_data['Ordered.Date'] = historical_data['Ordered.Date'].dt.to_timestamp()
        print("Historical data created successfully.")
        print(f"Historical Data Preview:\n{historical_data.head()}")
    except Exception as e:
        print(f"Error creating historical data: {e}")

    # Initialize traces
    traces = [
        go.Scatter(
            x=historical_data['Ordered.Date'],
            y=historical_data['Line.Total'],
            mode='lines+markers',
            name='Historical Data',
            line=dict(color="lightblue")
        )
    ]

    # Add ETS forecast trace if forecast_df_ets is non-empty
    if forecast_df_ets is not None and not forecast_df_ets.empty:
        traces.append(
            go.Scatter(
                x=forecast_df_ets['Date'],
                y=forecast_df_ets['Forecast'],
                mode='lines+markers',
                name='ETS Forecast',
                line=dict(color="lightgreen", dash="dash")
            )
        )

    # Add SARIMA forecast trace if forecast_df_sarima is non-empty
    if forecast_df_sarima is not None and not forecast_df_sarima.empty:
        traces.append(
            go.Scatter(
                x=forecast_df_sarima['Date'],
                y=forecast_df_sarima['Forecast'],
                mode='lines+markers',
                name='SARIMA Forecast',
                line=dict(color="lightcoral", dash="dot")
            )
        )

    # Build the figure
    fig = go.Figure(traces)
    fig.update_layout(title="Forecast vs. Historical Data", xaxis_title="Date", yaxis_title="Line Total")

    # Build the forecast summary
    forecast_summary_parts = []
    if mape_ets is not None:
        forecast_summary_parts.append(f"ETS Model Accuracy (MAPE): {mape_ets:.2f}%")
    if mape_sarima is not None:
        forecast_summary_parts.append(f"SARIMA Model Accuracy (MAPE): {mape_sarima:.2f}%")
    forecast_summary = " | ".join(forecast_summary_parts) if forecast_summary_parts else "Forecasting models failed due to insufficient data."

    return fig, forecast_summary




def evaluate_sarima_model_with_cv(data):
    # Define SARIMA model parameters
    p, d, q = 1, 1, 1
    seasonal_order = (1, 1, 1, 12)  # Adjust seasonal order if needed

    # Set forecast length (e.g., 1 month for each fold)
    forecast_length = 1  # Monthly prediction

    # Perform rolling cross-validation
    avg_mape, mape_scores = rolling_cross_validation(data, forecast_length, p, d, q, seasonal_order)

    print(f"Average MAPE across folds: {avg_mape * 100:.2f}%")
    print(f"MAPE scores for each fold: {[round(m * 100, 2) for m in mape_scores]}")
    return avg_mape




import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))  # Default to 8050 if PORT is not set
    app.run_server(host="0.0.0.0", port=port, debug=False)




                                                                                                                                                                                              
