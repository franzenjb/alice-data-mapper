# ALICE Data Interactive Mapper

A powerful interactive visualization tool for exploring ALICE (Asset Limited, Income Constrained, Employed) data across the United States.

## Features

- **Interactive Map**: Visual representation of ALICE data across 32 states
- **Dynamic Filtering**: Switch between viewing Poverty Rate, ALICE Rate, or Combined Rate
- **State Rankings**: Sortable list of states by various metrics
- **Detailed State Information**: Click any state for comprehensive statistics
- **Data Visualizations**: 
  - Bar chart showing top 10 states by financial hardship
  - Scatter plot showing correlation between poverty and ALICE rates
- **Responsive Design**: Works on desktop and mobile devices

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript
- **Visualization Libraries**:
  - Leaflet.js for interactive mapping
  - Chart.js for data charts
  - D3.js for advanced data manipulation
- **Data Collection**: 
  - Playwright for web scraping
  - Axios for HTTP requests

## Data Source

Data is sourced from the United For ALICE website (https://www.unitedforalice.org), which provides comprehensive research on households that are Asset Limited, Income Constrained, and Employed.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/[your-username]/alice-data-mapper.git
cd alice-data-mapper
```

2. Install dependencies:
```bash
npm install
```

3. Run the data scraper (optional - data is pre-included):
```bash
node enhanced-scraper.js
```

4. Open `index.html` in your browser or serve with a local server:
```bash
npx http-server -p 8080
```

## Understanding ALICE

ALICE represents households that earn above the federal poverty level but struggle to afford basic household necessities. The combined ALICE and poverty rate shows the true percentage of households facing financial hardship in each state.

## Key Metrics

- **Poverty Rate**: Percentage of households below the federal poverty line
- **ALICE Rate**: Percentage of households above poverty but below the ALICE threshold
- **Combined Rate**: Total percentage of households struggling financially

## States Covered

The tool includes data for 32 states with active ALICE research programs:
Alabama, Arkansas, Colorado, Connecticut, Delaware, Florida, Georgia, Hawaii, Idaho, Illinois, Indiana, Iowa, Kansas, Louisiana, Maine, Maryland, Michigan, Minnesota, Mississippi, New Jersey, New Mexico, New York, North Carolina, Ohio, Oregon, Pennsylvania, South Carolina, Tennessee, Texas, Virginia, Washington, and West Virginia.

## License

MIT License

## Acknowledgments

- United For ALICE for providing the research and data
- OpenStreetMap contributors for map tiles
- All open-source library maintainers