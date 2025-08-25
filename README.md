# Climate-Aware GPS Navigator

A modern, intelligent GPS navigation system that routes users through environmental hazards using real-time climate data and advanced risk assessment algorithms.

## Features

- **Hazard-Aware Routing**: Avoids flood zones, weather warnings, and other environmental risks
- **Real-Time Data**: Integrates with NWS, NOAA, USGS, and FEMA APIs
- **Interactive 3D Maps**: Beautiful, responsive mapping with multiple style options
- **Risk Assessment**: Comprehensive hazard evaluation and scoring
- **Modern UI**: Professional, animated interface with smooth interactions
- **Responsive Design**: Works seamlessly on desktop and mobile devices


### Prerequisites

- Node.js 16+ and npm
- Python 3.8+ (for backend)
- Git

### Frontend Setup (React)

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm start
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

The React app will automatically reload when you make changes to the code.

### Backend Setup (FastAPI)

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements-minimal.txt
   ```

3. **Set environment variables:**
   ```bash
   cp env_demo.txt .env
   ```

4. **Run the backend:**
   ```bash
   python -m app.main_simple
   ```

The API will be available at `http://localhost:8000`

## Architecture

### Frontend (React)
- **React 18** with modern hooks and functional components
- **Styled Components** for maintainable CSS-in-JS
- **Framer Motion** for smooth animations
- **Leaflet** for interactive mapping
- **Lucide React** for beautiful icons

### Backend (FastAPI)
- **FastAPI** for high-performance API development
- **Pydantic** for data validation
- **Async/await** for non-blocking operations
- **CORS** enabled for frontend integration

### Data Sources
- **NWS API**: Weather alerts and warnings
- **NOAA NWPS**: Water prediction services
- **USGS**: Water services and river data
- **FEMA NFHL**: Flood hazard data
- **OpenStreetMap**: Base mapping and routing

## 🔧 Development

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run test suite
- `npm run eject` - Eject from Create React App

### Project Structure

```
├── public/                 # Static assets
├── src/                   # React source code
│   ├── App.js            # Main application component
│   └── index.js          # Application entry point
├── app/                   # Backend Python code
│   ├── main_simple.py    # FastAPI application
│   └── core/             # Configuration and utilities
├── package.json           # Frontend dependencies
├── requirements-minimal.txt # Backend dependencies
└── README.md             # This file
```

## Current Status

- ✅ **Frontend**: Complete React application with modern UI
- ✅ **Backend**: Basic FastAPI structure with mock endpoints
- ✅ **Mapping**: Interactive Leaflet integration
- ✅ **Styling**: Professional design with animations
- 🔄 **Data Integration**: Mock data (ready for real APIs)
- 🔄 **Routing Engine**: Basic structure (ready for pgRouting)
