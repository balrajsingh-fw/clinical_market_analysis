
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from django.shortcuts import render
from django.db.models import Sum
from collections import defaultdict
from datetime import datetime, timedelta
import pandas as pd
import folium
from folium.plugins import HeatMap
from sklearn.linear_model import LinearRegression
from .models import DrugSale

# Create your views here.
def home(request):
    return render(request, 'home.html')

def sales_analysis(request):
    # Get filters from request GET params
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    atc_code = request.GET.get('atc_code')
    frequency = request.GET.get('frequency')

    # Base queryset
    qs = DrugSale.objects.all()

    # Filter by date range if given
    if start_date:
        qs = qs.filter(datetime__gte=start_date)
    if end_date:
        qs = qs.filter(datetime__lte=end_date)

    # Filter by ATC code if given
    if atc_code:
        qs = qs.filter(atc_code=atc_code)

    # Filter by frequency if given
    if frequency:
        qs = qs.filter(frequency=frequency)

    # Determine truncation based on frequency (for grouping by date)
    if frequency == 'monthly':
        qs = qs.annotate(period=TruncMonth('datetime'))
    elif frequency == 'weekly':
        qs = qs.annotate(period=TruncWeek('datetime'))
    elif frequency == 'daily':
        qs = qs.annotate(period=TruncDay('datetime'))
    else:
        # Default to day if no frequency filter
        qs = qs.annotate(period=TruncDay('datetime'))

    # Aggregate total quantities grouped by period and ATC code
    data = (
        qs
        .values('period', 'atc_code', 'drug_name')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('period')
    )

    # Prepare data for charts

    # 1) Total sales over time (sum across all drugs for each period)
    total_sales_by_period = {}
    for row in data:
        key = row['period'].strftime('%Y-%m-%d')
        total_sales_by_period[key] = total_sales_by_period.get(key, 0) + row['total_quantity']

    # 2) Sales by ATC code (sum across all periods)
    total_sales_by_atc = {}
    for row in data:
        total_sales_by_atc[row['atc_code']] = total_sales_by_atc.get(row['atc_code'], 0) + row['total_quantity']

    # Send filter options for template
    atc_codes = DrugSale.objects.values_list('atc_code', flat=True).distinct()
    frequencies = DrugSale.objects.values_list('frequency', flat=True).distinct()

    context = {
        'data': list(data),
        'total_sales_by_period': total_sales_by_period,
        'total_sales_by_atc': total_sales_by_atc,
        'atc_codes': atc_codes,
        'frequencies': frequencies,
        'filters': {
            'start_date': start_date,
            'end_date': end_date,
            'atc_code': atc_code,
            'frequency': frequency,
        }
    }
    return render(request, 'sales_analysis.html', context)

def drug_analysis(request):
    selected_drug = request.GET.get('drug_name')
    forecast_flag = request.GET.get('forecast') == 'true'
    forecast_for = request.GET.get('forecast_for', 'tomorrow')
    forecast_for_display = forecast_for.replace('_', ' ').title()

    # Get all distinct drug names for dropdown
    distinct_drugs = DrugSale.objects.values_list('drug_name', flat=True).distinct().order_by('drug_name')

    if not selected_drug:
        return render(request, 'drug_select.html', {'distinct_drugs': distinct_drugs})

    # Monthly sales aggregation
    monthly_sales = (
        DrugSale.objects
        .filter(drug_name=selected_drug)
        .annotate(month=TruncMonth('datetime'))
        .values('month')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('month')
    )

    avg_monthly_sales = (
        sum(m['total_quantity'] for m in monthly_sales) / len(monthly_sales)
        if monthly_sales else 0
    )

    # Top 5 months by year
    monthly_by_year = defaultdict(list)
    for entry in monthly_sales:
        year = entry['month'].year
        monthly_by_year[year].append(entry)

    top_months_by_year = {
        year: sorted(entries, key=lambda x: x['total_quantity'], reverse=True)[:5]
        for year, entries in monthly_by_year.items()
    }

    # Seasonal trend analysis
    season_map = {
        12: 'Winter', 1: 'Winter', 2: 'Winter',
        3: 'Spring', 4: 'Spring', 5: 'Spring',
        6: 'Summer', 7: 'Summer', 8: 'Summer',
        9: 'Fall', 10: 'Fall', 11: 'Fall',
    }

    seasonal_sales = {}
    for record in monthly_sales:
        season = season_map[record['month'].month]
        seasonal_sales[season] = seasonal_sales.get(season, 0) + record['total_quantity']

    season_order = ['Winter', 'Spring', 'Summer', 'Fall']
    seasonal_sales_sorted = [(s, seasonal_sales.get(s, 0)) for s in season_order]
    season_names = [s[0] for s in seasonal_sales_sorted]
    season_values = [s[1] for s in seasonal_sales_sorted]

    # Get sales data for maps and forecasting
    sales_data = list(DrugSale.objects.filter(
        drug_name=selected_drug
    ).values('datetime', 'quantity', 'latitude', 'longitude', 'city'))

    sales_data = [s for s in sales_data if s['latitude'] and s['longitude'] and s['quantity'] > 0]

    # Prepare base heatmap
    heat_data = [[s['latitude'], s['longitude'], s['quantity']] for s in sales_data]
    map_center = [20.0, 100.0]
    m = folium.Map(location=map_center, zoom_start=4, tiles='CartoDB positron')

    if heat_data:
        HeatMap(heat_data, radius=12, blur=15, max_zoom=6, min_opacity=0.4).add_to(m)

        # Group by city + lat + lon and sum quantities
        city_grouped_data = defaultdict(lambda: {'quantity': 0, 'latitude': None, 'longitude': None})

        for s in sales_data:
            key = (s['city'], s['latitude'], s['longitude'])
            city_grouped_data[key]['quantity'] += s['quantity']
            city_grouped_data[key]['latitude'] = s['latitude']
            city_grouped_data[key]['longitude'] = s['longitude']

        # Add single marker per city with total quantity
        for (city, lat, lon), data in city_grouped_data.items():
            folium.CircleMarker(
                location=[lat, lon],
                radius=8,
                color=None,
                fill=True,
                fill_color='#00000000',
                fill_opacity=0.0,
                tooltip=f"{city or 'Unknown City'} — {data['quantity']} units"
            ).add_to(m)

    map_html = m._repr_html_()

    # Forecast Map Section
    forecast_map_html = None
    if forecast_flag and sales_data:
        df = pd.DataFrame(sales_data)
        df = df.dropna(subset=['datetime', 'quantity', 'latitude', 'longitude'])

        if not df.empty:
            df['timestamp'] = df['datetime'].map(datetime.timestamp)
            df['lat_lon'] = list(zip(df['latitude'], df['longitude']))

            today = datetime.today()
            forecast_days = {
                'tomorrow': 1,
                'next_week': 7,
                'next_month': 30,
                'next_year': 365
            }.get(forecast_for, 1)

            future_dates = [today + timedelta(days=i) for i in range(1, forecast_days + 1)]
            future_timestamps = [datetime.timestamp(d) for d in future_dates]

            # Filter out coordinate groups with insufficient data
            valid_groups = df.groupby('lat_lon').filter(lambda x: len(x) >= 3)

            if not valid_groups.empty:
                def forecast_group(group):
                    X = group[['timestamp']]
                    y = group['quantity']
                    model = LinearRegression().fit(X, y)
                    preds = model.predict([[ts] for ts in future_timestamps])
                    total_forecast = sum(max(p, 0) for p in preds)
                    return pd.Series({
                        'latitude': group['latitude'].iloc[0],
                        'longitude': group['longitude'].iloc[0],
                        'forecast': total_forecast
                    })

                forecast_df = valid_groups.groupby('lat_lon').apply(forecast_group).reset_index(drop=True)
                forecast_results = forecast_df[['latitude', 'longitude', 'forecast']].values.tolist()
            else:
                forecast_results = []

            # Build forecast map
            f_m = folium.Map(location=map_center, zoom_start=4, tiles='CartoDB positron')
            if forecast_results:
                HeatMap(forecast_results, radius=12, blur=15, max_zoom=6, min_opacity=0.4).add_to(f_m)

                city_lookup = {}
                for s in sales_data:
                    key = (round(s['latitude'], 5), round(s['longitude'], 5))
                    if key not in city_lookup and s['city']:
                        city_lookup[key] = s['city']

                for _, row in forecast_df.iterrows():
                    lat = round(row['latitude'], 5)
                    lon = round(row['longitude'], 5)
                    forecast_val = row['forecast']
                    city = city_lookup.get((lat, lon), 'Unknown City')

                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=8,
                        color=None,
                        fill=True,
                        fill_color='#00000000',
                        fill_opacity=0.0,
                        tooltip=f"{city} — Forecast: {int(forecast_val)} units"
                    ).add_to(f_m)

                forecast_map_html = f_m._repr_html_()
            else:
                forecast_map_html = "<p>No forecast data available for this filter.</p>"

    # Final context
    context = {
        'distinct_drugs': distinct_drugs,
        'selected_drug': selected_drug,
        'avg_monthly_sales': avg_monthly_sales,
        'top_months_by_year': top_months_by_year,
        'season_names': season_names,
        'season_values': season_values,
        'map': map_html,
        'forecast_map': forecast_map_html,
        'forecast_for_display': forecast_for_display if forecast_flag else None,
    }

    return render(request, 'drug_analysis.html', context)

