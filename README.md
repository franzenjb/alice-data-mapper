# ALICE Data Mapper

An interactive data visualization tool for exploring ALICE (Asset Limited, Income Constrained, Employed) demographic data across the United States. Built for the American Red Cross to support disaster response and community outreach efforts.

## Live Demo

🌐 **[View Live Application](https://franzenjb.github.io/alice-data-mapper/)**

## Features

- 📊 **Interactive Choropleth Map**: Visualize ALICE data across 3,000+ U.S. counties
- 🔍 **Smart Search**: Filter by state and county with automatic zoom
- 📈 **Historical Trends**: Analyze data from 2010-2023
- 💾 **Export Capability**: Download data as CSV for further analysis
- 🎨 **Red Cross Branding**: Official American Red Cross theme and colors
- 🔓 **No Authentication Required**: Public access using OpenStreetMap tiles

## Data Source

The application displays ALICE data from the United Way's ALICE project, which provides comprehensive poverty and financial hardship metrics at the county and sub-county level across all U.S. states.

### Key Metrics
- **ALICE Rate**: Percentage of households above poverty but below basic cost of living
- **Poverty Rate**: Percentage of households below federal poverty line
- **Combined Rate**: Total percentage of households struggling financially

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/franzenjb/alice-data-mapper.git
cd alice-data-mapper
```

2. Serve the application locally:
```bash
npm run serve
```
Or with Python:
```bash
python3 -m http.server 8000
```

3. Open in browser:
```
http://localhost:8000
```

## Technology Stack

- **Mapping**: Leaflet.js with OpenStreetMap tiles
- **Data Visualization**: Chart.js for trend analysis
- **Styling**: Custom CSS with Red Cross branding
- **Data Format**: JSON database with 79,964 geographic records

## Browser Compatibility

Works on all modern browsers including:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## License

MIT License - See LICENSE file for details

## Support

For questions or issues, please open a GitHub issue in this repository.