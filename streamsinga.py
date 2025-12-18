import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Singapore Population Analysis",
    page_icon="👥",
    layout="wide"
)

# Title and description
st.title("🇸🇬 Singapore Population Analysis")
st.markdown("Interactive demographic data visualization (2000-2018)")

# File uploader
uploaded_file = st.file_uploader(
    "Upload Singapore_Residents.csv", 
    type=['csv'],
    help="Upload the CSV file containing Singapore population data"
)

if uploaded_file is not None:
    # Read the CSV file
    df = pd.read_csv(uploaded_file)
    
    st.success(f"✅ Data loaded successfully ({len(df)} rows)")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "📊 Total Population",
        "⚖️ Gender Ratios",
        "📈 Population Growth"
    ])
    
    # ==================== TAB 1: TOTAL POPULATION ====================
    with tab1:
        st.header("Total Population by Year")
        
        # Calculate total population by year
        total_population_df = df.groupby('Year')['Count'].sum().reset_index()
        total_population_df.columns = ['Year', 'Total_Population']
        
        # Create line chart
        fig1 = px.line(
            total_population_df,
            x='Year',
            y='Total_Population',
            title='Total Population Over Time',
            markers=True
        )
        fig1.update_traces(line_color='#4f46e5', line_width=3)
        fig1.update_layout(
            xaxis_title="Year",
            yaxis_title="Total Population",
            hovermode='x unified'
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Display table
        st.subheader("Population Data Table")
        total_population_df['Total_Population'] = total_population_df['Total_Population'].apply(
            lambda x: f"{x:,}"
        )
        st.dataframe(total_population_df, use_container_width=True)
    
    # ==================== TAB 2: GENDER RATIOS ====================
    with tab2:
        st.header("Female to Male Ratios (3-Year Intervals)")
        
        # Define years and groups
        years = [2000, 2003, 2006, 2009, 2012, 2015, 2018]
        groups = {
            'Total': ('Total Male Residents', 'Total Female Residents'),
            'Malays': ('Total Male Malays', 'Total Female Malays'),
            'Chinese': ('Total Male Chinese', 'Total Female Chinese'),
            'Indians': ('Total Male Indians', 'Total Female Indians'),
            'Others': ('Other Ethnic Groups (Males)', 'Other Ethnic Groups (Females)')
        }
        
        # Calculate ratios
        ratio_data = []
        for year in years:
            row_data = {'Year': year}
            for group_name, (male_label, female_label) in groups.items():
                male_count = df[(df['Year'] == year) & (df['Residents'] == male_label)]['Count'].values
                female_count = df[(df['Year'] == year) & (df['Residents'] == female_label)]['Count'].values
                
                if len(male_count) > 0 and len(female_count) > 0:
                    ratio = female_count[0] / male_count[0]
                    row_data[group_name] = round(ratio, 4)
            
            ratio_data.append(row_data)
        
        ratio_df = pd.DataFrame(ratio_data)
        
        # Create line chart
        fig2 = go.Figure()
        colors = {
            'Total': '#4f46e5',
            'Malays': '#10b981',
            'Chinese': '#f59e0b',
            'Indians': '#ef4444',
            'Others': '#8b5cf6'
        }
        
        for group in ['Total', 'Malays', 'Chinese', 'Indians', 'Others']:
            fig2.add_trace(go.Scatter(
                x=ratio_df['Year'],
                y=ratio_df[group],
                mode='lines+markers',
                name=group,
                line=dict(color=colors[group], width=2),
                marker=dict(size=8)
            ))
        
        fig2.update_layout(
            title='Female to Male Ratios by Ethnic Group',
            xaxis_title='Year',
            yaxis_title='Female/Male Ratio',
            hovermode='x unified',
            yaxis=dict(range=[0.9, 1.2])
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Display detailed table
        st.subheader("Detailed Gender Ratio Data")
        
        # Format the output nicely
        for year in years:
            st.markdown(f"### **{year}**")
            year_data = ratio_df[ratio_df['Year'] == year]
            
            cols = st.columns(5)
            for idx, group in enumerate(['Total', 'Malays', 'Chinese', 'Indians', 'Others']):
                with cols[idx]:
                    male_label, female_label = groups[group]
                    male = df[(df['Year'] == year) & (df['Residents'] == male_label)]['Count'].values[0]
                    female = df[(df['Year'] == year) & (df['Residents'] == female_label)]['Count'].values[0]
                    ratio = year_data[group].values[0]
                    
                    st.metric(
                        label=group,
                        value=f"{ratio:.4f}",
                        delta=f"M: {male:,} | F: {female:,}",
                        delta_color="off"
                    )
            st.divider()
    
    # ==================== TAB 3: POPULATION GROWTH ====================
    with tab3:
        st.header("Population Growth Analysis")
        
        # Filter for total residents only
        pop = df[df['Residents'] == 'Total Residents'].sort_values('Year').copy()
        
        # Calculate growth percentages
        pop['Growth_YoY'] = pop['Count'].pct_change() * 100
        pop['Running_Total'] = ((pop['Count'] - pop['Count'].iloc[0]) / pop['Count'].iloc[0]) * 100
        
        # Create dual-axis chart
        fig3 = go.Figure()
        
        fig3.add_trace(go.Bar(
            x=pop['Year'],
            y=pop['Growth_YoY'],
            name='Year-over-Year Growth %',
            marker_color='#4f46e5',
            yaxis='y'
        ))
        
        fig3.add_trace(go.Scatter(
            x=pop['Year'],
            y=pop['Running_Total'],
            name='Total Growth from 2000 %',
            mode='lines+markers',
            line=dict(color='#10b981', width=3),
            marker=dict(size=8),
            yaxis='y2'
        ))
        
        fig3.update_layout(
            title='Population Growth Metrics',
            xaxis_title='Year',
            yaxis=dict(
                title='Year-over-Year Growth %',
                titlefont=dict(color='#4f46e5'),
                tickfont=dict(color='#4f46e5')
            ),
            yaxis2=dict(
                title='Total Growth from 2000 %',
                titlefont=dict(color='#10b981'),
                tickfont=dict(color='#10b981'),
                overlaying='y',
                side='right'
            ),
            hovermode='x unified',
            legend=dict(x=0.01, y=0.99)
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        
        # Display detailed table
        st.subheader("Detailed Growth Data")
        
        growth_table = pop[['Year', 'Count', 'Growth_YoY', 'Running_Total']].copy()
        growth_table.columns = ['Year', 'Population', 'YoY Growth %', 'Total Growth %']
        growth_table['Population'] = growth_table['Population'].apply(lambda x: f"{x:,}")
        growth_table['YoY Growth %'] = growth_table['YoY Growth %'].apply(
            lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A"
        )
        growth_table['Total Growth %'] = growth_table['Total Growth %'].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(growth_table, use_container_width=True)
        
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Starting Population (2000)",
                f"{pop.iloc[0]['Count']:,.0f}"
            )
        
        with col2:
            st.metric(
                "Ending Population (2018)",
                f"{pop.iloc[-1]['Count']:,.0f}"
            )
        
        with col3:
            avg_growth = pop['Growth_YoY'].mean()
            st.metric(
                "Average YoY Growth",
                f"{avg_growth:.2f}%"
            )
        
        with col4:
            total_growth = pop['Running_Total'].iloc[-1]
            st.metric(
                "Total Growth (2000-2018)",
                f"{total_growth:.2f}%"
            )

else:
    st.info("👆 Please upload a CSV file to begin the analysis")
    
    # Show example of expected CSV format
    st.markdown("### Expected CSV Format:")
    st.code("""Year,Residents,Count
2000,Total Residents,3273363
2000,Total Male Residents,1634667
2000,Total Female Residents,1638696
...""", language="csv")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Singapore Residents Population Data (2000-2018)"
    "</div>",
    unsafe_allow_html=True
)
