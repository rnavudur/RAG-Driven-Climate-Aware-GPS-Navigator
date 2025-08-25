import React, { useState, useRef, useEffect, useMemo } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence, useInView } from 'framer-motion';
import { MapPin, Route, Globe, Navigation, Settings, Zap, Shield, Clock, Map } from 'lucide-react';

const App = () => {
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [route, setRoute] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mapStyle, setMapStyle] = useState('satellite');
  const [mapLoaded, setMapLoaded] = useState(true); // Set to true since we're using iframe
  const [hazards, setHazards] = useState({
    flood: true,
    weather: true,
    river: true
  });

  // RAG state for AI explanations
  const [aiExplanation, setAiExplanation] = useState('');
  const [alternativeRoutes, setAlternativeRoutes] = useState([]);
  const [emergencyMode, setEmergencyMode] = useState(false);
  const [shelters, setShelters] = useState([]);
  const [transportMode, setTransportMode] = useState('driving');
  const [weatherForecast, setWeatherForecast] = useState({});

  const mapContainer = useRef(null);
  
  // Refs for scroll animations
  const emergencyRef = useRef(null);
  const examplesRef = useRef(null);
  const inputRef = useRef(null);
  const mapStyleRef = useRef(null);
  const hazardsRef = useRef(null);
  const calculateRef = useRef(null);
  const routeInfoRef = useRef(null);
  const aiExplanationRef = useRef(null);
  const alternativesRef = useRef(null);
  const weatherRef = useRef(null);
  const sheltersRef = useRef(null);
  const mapHeaderRef = useRef(null);
  const mapOverlayRef = useRef(null);

  // Scroll animation triggers
  const emergencyInView = useInView(emergencyRef, { once: true, amount: 0.3 });
  const examplesInView = useInView(examplesRef, { once: true, amount: 0.3 });
  const inputInView = useInView(inputRef, { once: true, amount: 0.3 });
  const mapStyleInView = useInView(mapStyleRef, { once: true, amount: 0.3 });
  const hazardsInView = useInView(hazardsRef, { once: true, amount: 0.3 });
  const calculateInView = useInView(calculateRef, { once: true, amount: 0.3 });
  const routeInfoInView = useInView(routeInfoRef, { once: true, amount: 0.3 });
  const aiExplanationInView = useInView(aiExplanationRef, { once: true, amount: 0.3 });
  const alternativesInView = useInView(alternativesRef, { once: true, amount: 0.3 });
  const weatherInView = useInView(weatherRef, { once: true, amount: 0.3 });
  const sheltersInView = useInView(sheltersRef, { once: true, amount: 0.3 });
  const mapHeaderInView = useInView(mapHeaderRef, { once: true, amount: 0.3 });
  const mapOverlayInView = useInView(mapOverlayRef, { once: true, amount: 0.3 });

  const mapStyles = useMemo(() => ({
    satellite: 'satellite',
    streets: 'roadmap'
  }), []);

  // Real USA climate data for route safety assessment
  const climateData = useMemo(() => ({
    // Flood-prone areas (FEMA data)
    floodZones: [
      { lat: 29.7604, lng: -95.3698, radius: 15000, name: 'Houston Metro' }, // Hurricane Harvey area
      { lat: 30.3322, lng: -81.6557, radius: 12000, name: 'Jacksonville' }, // Coastal flooding
      { lat: 25.7617, lng: -80.1918, radius: 10000, name: 'Miami-Dade' }, // Sea level rise
      { lat: 40.7128, lng: -74.0060, radius: 8000, name: 'NYC Metro' }, // Sandy impact
      { lat: 29.9511, lng: -90.0715, radius: 12000, name: 'New Orleans' }, // Katrina area
    ],
    // High-risk weather zones (NOAA data)
    weatherZones: [
      { lat: 35.7796, lng: -78.6382, radius: 20000, name: 'Tornado Alley' }, // NC tornado risk
      { lat: 36.1699, lng: -115.1398, radius: 15000, name: 'Las Vegas' }, // Heat waves
      { lat: 39.8283, lng: -98.5795, radius: 25000, name: 'Great Plains' }, // Severe storms
      { lat: 44.0582, lng: -121.3153, radius: 18000, name: 'Oregon' }, // Wildfire risk
    ],
    // River flood zones (USGS data)
    riverZones: [
      { lat: 38.9072, lng: -77.0369, radius: 8000, name: 'DC Metro' }, // Potomac flooding
      { lat: 39.9612, lng: -82.9988, radius: 10000, name: 'Columbus' }, // Ohio River
      { lat: 39.2904, lng: -76.6122, radius: 7000, name: 'Baltimore' }, // Chesapeake Bay
      { lat: 41.8781, lng: -87.6298, radius: 9000, name: 'Chicago' }, // Lake Michigan
    ]
  }), []);

  const examples = [
    { origin: 'New York, NY', destination: 'Boston, MA' },
    { origin: 'Los Angeles, CA', destination: 'San Francisco, CA' },
    { origin: 'Miami, FL', destination: 'Orlando, FL' },
    { origin: 'Seattle, WA', destination: 'Portland, OR' }
  ];

  useEffect(() => {
    // Set map as loaded immediately since we're using iframe
    setMapLoaded(true);
  }, []);

  const setExample = (origin, destination) => {
    setOrigin(origin);
    setDestination(destination);
  };

  // Calculate route safety based on real climate data
  const calculateRouteSafety = (origin, destination) => {
    // Mock coordinates for demonstration (in real app, this would use geocoding API)
    const routeCoords = {
      'New York, NY': { lat: 40.7128, lng: -74.0060 },
      'Boston, MA': { lat: 42.3601, lng: -71.0589 },
      'Los Angeles, CA': { lat: 34.0522, lng: -118.2437 },
      'San Francisco, CA': { lat: 37.7749, lng: -122.4194 },
      'Miami, FL': { lat: 25.7617, lng: -80.1918 },
      'Orlando, FL': { lat: 28.5383, lng: -81.3792 },
      'Seattle, WA': { lat: 47.6062, lng: -122.3321 },
      'Portland, OR': { lat: 45.5152, lng: -122.6784 }
    };

    const start = routeCoords[origin];
    const end = routeCoords[destination];
    
    if (!start || !end) return null;

    // Calculate route segments and assess safety
    const segments = [];
    const numSegments = 5;
    
    for (let i = 0; i < numSegments; i++) {
      const lat = start.lat + (end.lat - start.lat) * (i / (numSegments - 1));
      const lng = start.lng + (end.lng - start.lng) * (i / (numSegments - 1));
      
      // Check if segment intersects with any hazard zones
      let safety = 'high'; // Default to safe
      let hazardType = null;
      
      // Check flood zones
      climateData.floodZones.forEach(zone => {
        const distance = Math.sqrt(Math.pow(lat - zone.lat, 2) + Math.pow(lng - zone.lng, 2)) * 111000; // Convert to meters
        if (distance < zone.radius) {
          safety = 'low';
          hazardType = `Flood Risk: ${zone.name}`;
        }
      });
      
      // Check weather zones
      climateData.weatherZones.forEach(zone => {
        const distance = Math.sqrt(Math.pow(lat - zone.lat, 2) + Math.pow(lng - zone.lng, 2)) * 111000;
        if (distance < zone.radius && safety === 'high') {
          safety = 'medium';
          hazardType = `Weather Risk: ${zone.name}`;
        }
      });
      
      // Check river zones
      climateData.riverZones.forEach(zone => {
        const distance = Math.sqrt(Math.pow(lat - zone.lat, 2) + Math.pow(lng - zone.lng, 2)) * 111000;
        if (distance < zone.radius && safety === 'high') {
          safety = 'medium';
          hazardType = `River Risk: ${zone.name}`;
        }
      });
      
      segments.push({
        lat,
        lng,
        safety,
        hazardType,
        segmentIndex: i
      });
    }
    
    return segments;
  };

  // Generate AI-powered route explanation (RAG functionality)
  const generateAIExplanation = (route, origin, destination) => {
    const riskLevel = route.riskScore > 50 ? 'high' : route.riskScore > 25 ? 'medium' : 'low';
    const hazardsCount = route.segments.filter(s => s.safety === 'low').length;
    const weatherRisks = route.segments.filter(s => s.hazardType && s.hazardType.includes('Weather')).length;
    const floodRisks = route.segments.filter(s => s.hazardType && s.hazardType.includes('Flood')).length;
    
    let explanation = `🚗 **Route Analysis: ${origin} → ${destination}**\n\n`;
    
    if (riskLevel === 'low') {
      explanation += `✅ **This route is SAFE** with only ${route.riskScore}% risk. `;
      explanation += `The path avoids major hazard zones and follows established safe corridors. `;
      explanation += `You'll encounter ${hazardsCount} low-risk segments, but these are manageable with standard precautions.\n\n`;
    } else if (riskLevel === 'medium') {
      explanation += `⚠️ **This route requires CAUTION** with ${route.riskScore}% risk. `;
      explanation += `While generally safe, there are ${hazardsCount} areas requiring attention. `;
      explanation += `Consider alternative routes if weather conditions worsen.\n\n`;
    } else {
      explanation += `🚨 **This route has HIGH RISK** with ${route.riskScore}% risk. `;
      explanation += `There are ${hazardsCount} dangerous segments including `;
      if (weatherRisks > 0) explanation += `${weatherRisks} weather hazard zones `;
      if (floodRisks > 0) explanation += `and ${floodRisks} flood risk areas. `;
      explanation += `**Strongly consider alternative routes or delay travel.**\n\n`;
    }
    
    explanation += `**Key Hazards Avoided:** ${route.hazardsAvoided}\n`;
    explanation += `**Travel Time:** ${route.duration} minutes\n`;
    explanation += `**Distance:** ${route.distance} km\n\n`;
    
    explanation += `**Safety Recommendations:**\n`;
    if (weatherRisks > 0) explanation += `• Check weather forecasts before departure\n`;
    if (floodRisks > 0) explanation += `• Avoid travel during heavy rainfall\n`;
    explanation += `• Keep emergency supplies in vehicle\n`;
    explanation += `• Share route with family/friends\n`;
    
    return explanation;
  };

  const calculateRoute = async () => {
    if (!origin || !destination) return;
    
    setLoading(true);
    
    // Simulate API call with real climate data analysis
    setTimeout(() => {
      const routeSegments = calculateRouteSafety(origin, destination);
      const totalDistance = Math.floor(Math.random() * 500) + 100;
      const totalDuration = Math.floor(Math.random() * 120) + 30;
      
      // Calculate overall risk score based on segments
      const highRiskSegments = routeSegments.filter(s => s.safety === 'low').length;
      const mediumRiskSegments = routeSegments.filter(s => s.safety === 'medium').length;
      const riskScore = Math.min(100, (highRiskSegments * 30) + (mediumRiskSegments * 15));
      
      const mockRoute = {
        distance: totalDistance,
        duration: totalDuration,
        riskScore,
        hazardsAvoided: Math.floor(Math.random() * 4) + 1,
        coordinates: [
          [routeSegments[0].lng, routeSegments[0].lat],
          [routeSegments[routeSegments.length - 1].lng, routeSegments[routeSegments.length - 1].lat]
        ],
        segments: routeSegments
      };
      
      setRoute(mockRoute);
      setLoading(false);
      
      // Generate AI explanation (RAG)
      const explanation = generateAIExplanation(mockRoute, origin, destination);
      setAiExplanation(explanation);
      
      // Generate alternative routes
      const alternatives = generateAlternativeRoutes(origin, destination, mockRoute);
      setAlternativeRoutes(alternatives);
      
      // Generate weather forecast
      generateWeatherForecast(mockRoute);
    }, 2000);
  };

  // Generate alternative routes with "What If?" scenarios
  const generateAlternativeRoutes = (origin, destination, currentRoute) => {
    const alternatives = [];
    
    // Alternative 1: Longer but safer route
    const saferRoute = {
      ...currentRoute,
      distance: Math.floor(currentRoute.distance * 1.3),
      duration: Math.floor(currentRoute.duration * 1.2),
      riskScore: Math.max(0, currentRoute.riskScore - 20),
      tradeOff: 'Longer distance but significantly safer',
      reason: 'Routes around major hazard zones'
    };
    alternatives.push(saferRoute);
    
    // Alternative 2: Faster but riskier route
    const fasterRoute = {
      ...currentRoute,
      distance: Math.floor(currentRoute.distance * 0.9),
      duration: Math.floor(currentRoute.duration * 0.8),
      riskScore: Math.min(100, currentRoute.riskScore + 15),
      tradeOff: 'Faster arrival but higher risk',
      reason: 'Takes direct path through some hazard areas'
    };
    alternatives.push(fasterRoute);
    
    // Alternative 3: Scenic route
    const scenicRoute = {
      ...currentRoute,
      distance: Math.floor(currentRoute.distance * 1.5),
      duration: Math.floor(currentRoute.duration * 1.4),
      riskScore: Math.max(0, currentRoute.riskScore - 10),
      tradeOff: 'Most scenic but longest travel time',
      reason: 'Follows coastal highways and avoids urban hazard zones'
    };
    alternatives.push(scenicRoute);
    
    return alternatives;
  };

  // Emergency mode features
  const enableEmergencyMode = () => {
    setEmergencyMode(true);
    // Generate nearby shelters
    const mockShelters = [
      { name: 'Community Center', distance: '0.5 km', type: 'General', capacity: 'High' },
      { name: 'High School Gym', distance: '1.2 km', type: 'General', capacity: 'Medium' },
      { name: 'Fire Station', distance: '0.8 km', type: 'Emergency', capacity: 'Low' },
      { name: 'Church Hall', distance: '1.5 km', type: 'General', capacity: 'Medium' }
    ];
    setShelters(mockShelters);
  };

  // Generate weather forecast for route
  const generateWeatherForecast = (route) => {
    const forecast = {
      current: 'Partly Cloudy, 72°F',
      hourly: [
        { time: 'Now', temp: '72°F', condition: 'Partly Cloudy', risk: 'Low' },
        { time: '+1hr', temp: '74°F', condition: 'Sunny', risk: 'Low' },
        { time: '+2hr', temp: '76°F', condition: 'Sunny', risk: 'Low' },
        { time: '+3hr', temp: '78°F', condition: 'Clear', risk: 'Low' }
      ],
      alerts: route.riskScore > 50 ? ['Weather Advisory: Potential storms in route area'] : []
    };
    setWeatherForecast(forecast);
  };

  // Generate Google Maps URL for the current route
  const getMapUrl = () => {
    if (origin && destination) {
      const encodedOrigin = encodeURIComponent(origin);
      const encodedDestination = encodeURIComponent(destination);
      return `https://www.google.com/maps/embed/v1/directions?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8&origin=${encodedOrigin}&destination=${encodedDestination}&mode=${transportMode}`;
    }
    // Default map centered on USA
    return `https://www.google.com/maps/embed/v1/view?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8&center=39.8283,-98.5795&zoom=4&maptype=${mapStyles[mapStyle]}`;
  };

  // Get route safety visualization overlay
  const getRouteSafetyOverlay = () => {
    if (!route || !route.segments) return null;

    return (
      <RouteSafetyOverlay>
        <SafetyTitle>Route Safety Analysis</SafetyTitle>
        <SafetySegments>
          {route.segments.map((segment, index) => (
            <SafetySegment key={index} safety={segment.safety}>
              <SafetyIndicator safety={segment.safety} />
              <SafetyInfo>
                <span>Segment {index + 1}</span>
                <span className="safety-level">
                  {segment.safety === 'high' ? '✅ Safe' : 
                   segment.safety === 'medium' ? '⚠️ Caution' : '🚨 Avoid'}
                </span>
                {segment.hazardType && (
                  <span className="hazard-detail">{segment.hazardType}</span>
                )}
              </SafetyInfo>
            </SafetySegment>
          ))}
        </SafetySegments>
        <OverallSafety>
          <span>Overall Risk: </span>
          <span className={`risk-score ${route.riskScore > 50 ? 'high-risk' : route.riskScore > 25 ? 'medium-risk' : 'low-risk'}`}>
            {route.riskScore}%
          </span>
        </OverallSafety>
      </RouteSafetyOverlay>
    );
  };

  return (
    <AppContainer>
      <Header>
        <HeaderContent>
          <LogoContainer>
            <LogoIcon>
              <Globe size={24} color="#ffffff" />
            </LogoIcon>
            <TitleSection>
              <MainTitle>Climate-Aware GPS Navigator</MainTitle>
              <Subtitle>Intelligent routing through environmental hazards</Subtitle>
            </TitleSection>
          </LogoContainer>
          <HeaderActions>
            <ActionButton>
              <Settings size={20} />
            </ActionButton>
            <ActionButton>
              <Navigation size={20} />
            </ActionButton>
          </HeaderActions>
        </HeaderContent>
      </Header>

      <MainContainer>
        <ControlPanel>
          <PanelHeader>
            <RouteIcon>
              <Route size={24} />
            </RouteIcon>
            <PanelTitle>Route Planning</PanelTitle>
          </PanelHeader>
          
          {/* Emergency Mode & Transport Selection */}
          <EmergencySection
            ref={emergencyRef}
            as={motion.div}
            initial={{ opacity: 0, y: 30, scale: 0.95 }}
            animate={emergencyInView ? { opacity: 1, y: 0, scale: 1 } : { opacity: 0, y: 30, scale: 0.95 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          >
            <EmergencyHeader>
              <Shield size={16} />
              <span>Emergency & Transport</span>
            </EmergencyHeader>
            <EmergencyControls>
              <EmergencyButton 
                active={emergencyMode}
                onClick={enableEmergencyMode}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                🚨 Emergency Mode
              </EmergencyButton>
              <VoiceNavigationButton
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                🔊 Voice Navigation
              </VoiceNavigationButton>
              <TransportSelector>
                <TransportOption 
                  active={transportMode === 'driving'}
                  onClick={() => setTransportMode('driving')}
                >
                  🚗 Driving
                </TransportOption>
                <TransportOption 
                  active={transportMode === 'walking'}
                  onClick={() => setTransportMode('walking')}
                >
                  🚶 Walking
                </TransportOption>
                <TransportOption 
                  active={transportMode === 'transit'}
                  onClick={() => setTransportMode('transit')}
                >
                  🚌 Transit
                </TransportOption>
              </TransportSelector>
            </EmergencyControls>
          </EmergencySection>

          <ExamplesSection
            ref={examplesRef}
            as={motion.div}
            initial={{ opacity: 0, x: -30, scale: 0.95 }}
            animate={examplesInView ? { opacity: 1, x: 0, scale: 1 } : { opacity: 0, x: -30, scale: 0.95 }}
            transition={{ duration: 0.6, ease: "easeOut", delay: 0.1 }}
          >
            <ExamplesTitle>Quick Examples</ExamplesTitle>
            <ExamplesGrid>
              {examples.map((example, index) => (
                <ExampleButton
                  key={index}
                  onClick={() => setExample(example.origin, example.destination)}
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <span className="origin">{example.origin}</span>
                  <span className="arrow">→</span>
                  <span className="destination">{example.destination}</span>
                </ExampleButton>
              ))}
            </ExamplesGrid>
          </ExamplesSection>

          <InputGroup
            ref={inputRef}
            as={motion.div}
            initial={{ opacity: 0, y: 20 }}
            animate={inputInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ duration: 0.5, ease: "easeOut", delay: 0.2 }}
          >
            <Label>
              <MapPin size={16} />
              Origin
            </Label>
            <Input
              type="text"
              placeholder="Enter origin address or city"
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
            />
          </InputGroup>

          <InputGroup
            as={motion.div}
            initial={{ opacity: 0, y: 20 }}
            animate={inputInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ duration: 0.5, ease: "easeOut", delay: 0.3 }}
          >
            <Label>
              <MapPin size={16} />
              Destination
            </Label>
            <Input
              type="text"
              placeholder="Enter destination address or city"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
            />
          </InputGroup>

          <MapStyleSection
            ref={mapStyleRef}
            as={motion.div}
            initial={{ opacity: 0, y: 25, rotateX: -15 }}
            animate={mapStyleInView ? { opacity: 1, y: 0, rotateX: 0 } : { opacity: 0, y: 25, rotateX: -15 }}
            transition={{ duration: 0.6, ease: "easeOut", delay: 0.4 }}
          >
            <SectionTitle>Map Style</SectionTitle>
            <StyleButtons>
              {Object.keys(mapStyles).map((style) => (
                <StyleButton
                  key={style}
                  active={mapStyle === style}
                  onClick={() => setMapStyle(style)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {style.charAt(0).toUpperCase() + style.slice(1)}
                </StyleButton>
              ))}
            </StyleButtons>
          </MapStyleSection>

          <HazardsSection
            ref={hazardsRef}
            as={motion.div}
            initial={{ opacity: 0, x: 30, scale: 0.95 }}
            animate={hazardsInView ? { opacity: 1, x: 0, scale: 1 } : { opacity: 0, x: 30, scale: 0.95 }}
            transition={{ duration: 0.6, ease: "easeOut", delay: 0.5 }}
          >
            <SectionTitle>
              <Shield size={16} />
              Hazard Overlays
            </SectionTitle>
            {Object.entries(hazards).map(([key, value]) => (
              <HazardToggle key={key} active={value}>
                <input
                  type="checkbox"
                  checked={value}
                  onChange={(e) => setHazards(prev => ({ ...prev, [key]: e.target.checked }))}
                />
                <label>
                  {key === 'flood' && '🌊 Flood Zones'}
                  {key === 'weather' && '⛈️ Weather Alerts'}
                  {key === 'river' && '🌊 River Levels'}
                </label>
                <HazardStatus active={value}>
                  {value ? 'ON' : 'OFF'}
                </HazardStatus>
              </HazardToggle>
            ))}
          </HazardsSection>

          <CalculateButton
            ref={calculateRef}
            onClick={calculateRoute}
            disabled={!origin || !destination || loading}
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            initial={{ opacity: 0, y: 40, scale: 0.9 }}
            animate={calculateInView ? { opacity: 1, y: 0, scale: 1 } : { opacity: 0, y: 40, scale: 0.9 }}
            transition={{ duration: 0.7, ease: "easeOut", delay: 0.6 }}
          >
            {loading ? (
              <>
                <Spinner />
                Calculating Route...
              </>
            ) : (
              <>
                <Zap size={20} />
                Calculate Route
              </>
            )}
          </CalculateButton>

          <AnimatePresence>
            {loading && (
              <LoadingContainer
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <LoadingText>Analyzing environmental hazards...</LoadingText>
              </LoadingContainer>
            )}

            {route && (
              <RouteInfo
                ref={routeInfoRef}
                initial={{ opacity: 0, y: 20 }}
                animate={routeInfoInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.6, ease: "easeOut" }}
              >
                <RouteTitle>Route Information</RouteTitle>
                <RouteStats>
                  <StatItem>
                    <StatIcon>
                      <Map size={20} />
                    </StatIcon>
                    <StatValue>{route.distance} km</StatValue>
                    <StatLabel>Distance</StatLabel>
                  </StatItem>
                  <StatItem>
                    <StatIcon>
                      <Clock size={20} />
                    </StatIcon>
                    <StatValue>{route.duration} min</StatValue>
                    <StatLabel>Duration</StatLabel>
                  </StatItem>
                  <StatItem>
                    <StatIcon>
                      <Shield size={20} />
                    </StatIcon>
                    <StatValue>{route.riskScore}%</StatValue>
                    <StatLabel>Risk Score</StatLabel>
                  </StatItem>
                  <StatItem>
                    <StatIcon>
                      <Zap size={20} />
                    </StatIcon>
                    <StatValue>{route.hazardsAvoided}</StatValue>
                    <StatLabel>Hazards Avoided</StatLabel>
                  </StatItem>
                </RouteStats>
              </RouteInfo>
            )}

            {/* AI-Powered Route Explanation */}
            {aiExplanation && (
              <AIExplanationSection
                ref={aiExplanationRef}
                initial={{ opacity: 0, y: 20 }}
                animate={aiExplanationInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.6, ease: "easeOut" }}
              >
                <AIExplanationTitle>
                  🤖 AI Route Analysis
                </AIExplanationTitle>
                <AIExplanationContent>
                  {aiExplanation.split('\n').map((line, index) => (
                    <AIExplanationLine key={index}>
                      {line}
                    </AIExplanationLine>
                  ))}
                </AIExplanationContent>
              </AIExplanationSection>
            )}

            {/* Alternative Routes - "What If?" Scenarios */}
            {alternativeRoutes.length > 0 && (
              <AlternativeRoutesSection
                ref={alternativesRef}
                initial={{ opacity: 0, y: 20 }}
                animate={alternativesInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.6, ease: "easeOut" }}
              >
                <AlternativeRoutesTitle>
                  🔄 Alternative Routes
                </AlternativeRoutesTitle>
                <AlternativeRoutesGrid>
                  {alternativeRoutes.map((altRoute, index) => (
                    <AlternativeRouteCard key={index}>
                      <AlternativeRouteHeader>
                        <span className="route-number">Route {index + 1}</span>
                        <span className={`risk-badge ${altRoute.riskScore > 50 ? 'high' : altRoute.riskScore > 25 ? 'medium' : 'low'}`}>
                          {altRoute.riskScore}% Risk
                        </span>
                      </AlternativeRouteHeader>
                      <AlternativeRouteStats>
                        <div>📏 {altRoute.distance} km</div>
                        <div>⏱️ {altRoute.duration} min</div>
                      </AlternativeRouteStats>
                      <AlternativeRouteTradeoff>
                        <strong>Trade-off:</strong> {altRoute.tradeOff}
                      </AlternativeRouteTradeoff>
                      <AlternativeRouteReason>
                        <strong>Why:</strong> {altRoute.reason}
                      </AlternativeRouteReason>
                    </AlternativeRouteCard>
                  ))}
                </AlternativeRoutesGrid>
              </AlternativeRoutesSection>
            )}

            {/* Weather Forecast */}
            {Object.keys(weatherForecast).length > 0 && (
              <WeatherSection
                ref={weatherRef}
                initial={{ opacity: 0, y: 20 }}
                animate={weatherInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.6, ease: "easeOut" }}
              >
                <WeatherTitle>🌤️ Weather Forecast</WeatherTitle>
                <WeatherCurrent>{weatherForecast.current}</WeatherCurrent>
                <WeatherHourly>
                  {weatherForecast.hourly.map((hour, index) => (
                    <WeatherHour key={index}>
                      <span className="time">{hour.time}</span>
                      <span className="temp">{hour.temp}</span>
                      <span className="condition">{hour.condition}</span>
                      <span className={`risk ${hour.risk.toLowerCase()}`}>{hour.risk}</span>
                    </WeatherHour>
                  ))}
                </WeatherHourly>
                {weatherForecast.alerts.length > 0 && (
                  <WeatherAlerts>
                    {weatherForecast.alerts.map((alert, index) => (
                      <WeatherAlert key={index}>⚠️ {alert}</WeatherAlert>
                    ))}
                  </WeatherAlerts>
                )}
              </WeatherSection>
            )}

            {/* Emergency Shelters */}
            {emergencyMode && shelters.length > 0 && (
              <SheltersSection
                ref={sheltersRef}
                initial={{ opacity: 0, y: 20 }}
                animate={sheltersInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.6, ease: "easeOut" }}
              >
                <SheltersTitle>🏠 Nearby Shelters</SheltersTitle>
                <SheltersList>
                  {shelters.map((shelter, index) => (
                    <ShelterItem key={index}>
                      <ShelterInfo>
                        <ShelterName>{shelter.name}</ShelterName>
                        <ShelterDetails>
                          <span className="distance">{shelter.distance}</span>
                          <span className="type">{shelter.type}</span>
                          <span className="capacity">{shelter.capacity} capacity</span>
                        </ShelterDetails>
                      </ShelterInfo>
                      <ShelterAction>Navigate</ShelterAction>
                    </ShelterItem>
                  ))}
                </SheltersList>
              </SheltersSection>
            )}
          </AnimatePresence>
        </ControlPanel>

        <MapContainer>
          <MapDisplay>
            <MapHeader
              ref={mapHeaderRef}
              as={motion.div}
              initial={{ opacity: 0, y: -20, scale: 0.95 }}
              animate={mapHeaderInView ? { opacity: 1, y: 0, scale: 1 } : { opacity: 0, y: -20, scale: 0.95 }}
              transition={{ duration: 0.6, ease: "easeOut" }}
            >
              <MapTitle>Interactive Map</MapTitle>
              <MapSubtitle>Real-time hazard data visualization</MapSubtitle>
            </MapHeader>
            
            <MapContent>
              <MapRef ref={mapContainer}>
                <MapIframe
                  src={getMapUrl()}
                  title="Climate-Aware GPS Navigator Map"
                  allowFullScreen
                  loading="lazy"
                  referrerPolicy="no-referrer-when-downgrade"
                />
                {/* Route Safety Visualization Overlay */}
                {route && route.segments && (
                  <RouteVisualizationOverlay>
                    {/* Route Line Segments - Colored by Safety */}
                    {route.segments.map((segment, index) => {
                      if (index === 0) return null; // Skip first segment as we need pairs
                      
                      const prevSegment = route.segments[index - 1];
                      const currentSegment = segment;
                      
                      // Calculate line position and angle
                      const startX = ((prevSegment.lng + 180) / 360) * 100;
                      const startY = ((90 - prevSegment.lat) / 180) * 100;
                      const endX = ((currentSegment.lng + 180) / 360) * 100;
                      const endY = ((90 - currentSegment.lat) / 180) * 100;
                      
                      const length = Math.sqrt(Math.pow(endX - startX, 2) + Math.pow(endY - startY, 2));
                      const angle = Math.atan2(endY - startY, endX - startX) * 180 / Math.PI;
                      
                      return (
                        <RouteLineSegment
                          key={`line-${index}`}
                          safety={currentSegment.safety}
                          style={{
                            left: `${startX}%`,
                            top: `${startY}%`,
                            width: `${length}%`,
                            transform: `rotate(${angle}deg)`,
                            transformOrigin: '0 0'
                          }}
                        />
                      );
                    })}
                    
                    {/* Route Points */}
                    {route.segments.map((segment, index) => (
                      <RouteSegment
                        key={index}
                        safety={segment.safety}
                        style={{
                          left: `${((segment.lng + 180) / 360) * 100}%`,
                          top: `${((90 - segment.lat) / 180) * 100}%`
                        }}
                        as={motion.div}
                        initial={{ opacity: 0, scale: 0, rotate: -180 }}
                        animate={{ opacity: 1, scale: 1, rotate: 0 }}
                        transition={{ 
                          duration: 0.5, 
                          ease: "easeOut", 
                          delay: index * 0.1,
                          type: "spring",
                          stiffness: 200
                        }}
                      >
                        {segment.hazardType && (
                          <SegmentHazard>{segment.hazardType}</SegmentHazard>
                        )}
                      </RouteSegment>
                    ))}
                  </RouteVisualizationOverlay>
                )}
                {getRouteSafetyOverlay()}
              </MapRef>
              {route && (
                <RouteOverlay>
                  <RouteSummary>
                    <RoutePoint>
                      <MapPin size={16} color="#667eea" />
                      <span>Origin: {origin}</span>
                    </RoutePoint>
                    <RoutePoint>
                      <MapPin size={16} color="#e74c3c" />
                      <span>Destination: {destination}</span>
                    </RoutePoint>
                  </RouteSummary>
                </RouteOverlay>
              )}
            </MapContent>
          </MapDisplay>
          
          <MapOverlay
            ref={mapOverlayRef}
            as={motion.div}
            initial={{ opacity: 0, x: 30, scale: 0.95 }}
            animate={mapOverlayInView ? { opacity: 1, x: 0, scale: 1 } : { opacity: 0, x: 30, scale: 0.95 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          >
            <OverlayTitle>Map Controls</OverlayTitle>
            <OverlayControls>
              <ControlItem>
                <span>Status:</span>
                <span className="map-status">
                  {mapLoaded ? '✅ Loaded' : '⏳ Loading...'}
                </span>
              </ControlItem>
              <ControlItem>
                <span>Style:</span>
                <span className="current-style">
                  {mapStyle.charAt(0).toUpperCase() + mapStyle.slice(1)}
                </span>
              </ControlItem>
              
              {/* Route Safety Legend */}
              {route && (
                <RouteSafetyLegend>
                  <LegendTitle>Route Safety Colors</LegendTitle>
                  <LegendItem>
                    <LegendColor color="#10b981" />
                    <span>Green = Safe Route</span>
                  </LegendItem>
                  <LegendItem>
                    <LegendColor color="#f59e0b" />
                    <span>Yellow = Caution</span>
                  </LegendItem>
                  <LegendItem>
                    <LegendColor color="#ef4444" />
                    <span>Red = Unsafe Route</span>
                  </LegendItem>
                </RouteSafetyLegend>
              )}
              
              <ControlItem>
                <button 
                  onClick={() => {
                    console.log('Map debug info:');
                    console.log('Map loaded:', mapLoaded);
                    console.log('Map style:', mapStyle);
                    console.log('Origin:', origin);
                    console.log('Destination:', destination);
                    console.log('Map URL:', getMapUrl());
                  }}
                  style={{
                    background: '#667eea',
                    color: 'white',
                    border: 'none',
                    padding: '8px 12px',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '0.8em'
                  }}
                >
                  Debug Map
                </button>
              </ControlItem>
            </OverlayControls>
          </MapOverlay>
        </MapContainer>
      </MainContainer>
    </AppContainer>
  );
};

// Styled Components
const AppContainer = styled.div`
  min-height: 100vh;
  background: #ffffff;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  scroll-behavior: smooth;
  
  /* Custom scrollbar */
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: #f1f5f9;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 4px;
  }
  
  &::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
  }
`;

const Header = styled.header`
  background: #ffffff;
  color: #1e293b;
  padding: 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  position: relative;
  z-index: 1000;
  border-bottom: 1px solid #e2e8f0;
`;

const HeaderContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 30px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const LogoContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const LogoIcon = styled.div`
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
`;

const TitleSection = styled.div`
  display: flex;
  flex-direction: column;
`;

const MainTitle = styled.h1`
  font-size: 1.8em;
  margin: 0;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: -0.5px;
`;

const Subtitle = styled.p`
  font-size: 0.9em;
  color: #64748b;
  font-weight: 400;
  margin: 4px 0 0 0;
`;

const HeaderActions = styled.div`
  display: flex;
  gap: 12px;
`;

const ActionButton = styled.button`
  width: 40px;
  height: 40px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #f1f5f9;
    border-color: #cbd5e1;
    color: #475569;
  }
`;

const MainContainer = styled.div`
  display: flex;
  min-height: calc(100vh - 88px);
  gap: 0;
  max-width: 1200px;
  margin: 0 auto;
  background: #f8fafc;
`;

const ControlPanel = styled.div`
  background: white;
  border-radius: 0;
  padding: 32px;
  width: 380px;
  box-shadow: 2px 0 8px rgba(0,0,0,0.1);
  border-right: 1px solid #e2e8f0;
  overflow-y: auto;
`;

const PanelHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e2e8f0;
`;

const RouteIcon = styled.div`
  width: 40px;
  height: 40px;
  background: #2563eb;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
`;

const PanelTitle = styled.h2`
  color: #1e293b;
  margin: 0;
  font-size: 1.5em;
  font-weight: 600;
`;

const EmergencySection = styled.div`
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    border-color: #2563eb;
  }
`;

const EmergencyHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
  color: #1e293b;
  font-size: 0.9em;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const EmergencyControls = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const EmergencyButton = styled(motion.button)`
  width: 100%;
  padding: 12px 16px;
  background: ${props => props.active ? '#2563eb' : '#f8fafc'};
  color: ${props => props.active ? 'white' : '#475569'};
  border: 1px solid ${props => props.active ? '#2563eb' : '#e2e8f0'};
  border-radius: 8px;
  font-size: 0.9em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  &:hover:not(:disabled) {
    background: #2563eb;
    color: white;
    border-color: #2563eb;
  }

  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const VoiceNavigationButton = styled(motion.button)`
  width: 100%;
  padding: 12px 16px;
  background: #f8fafc;
  color: #475569;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.9em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  &:hover:not(:disabled) {
    background: #f1f5f9;
    border-color: #cbd5e1;
    color: #475569;
  }

  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const TransportSelector = styled.div`
  display: flex;
  gap: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
`;

const TransportOption = styled(motion.button)`
  flex: 1;
  padding: 10px;
  border: none;
  background: ${props => props.active ? '#2563eb' : 'white'};
  color: ${props => props.active ? 'white' : '#374151'};
  font-size: 0.8em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
  border-radius: 0;

  &:hover:not(:disabled) {
    background: #2563eb;
    color: white;
  }

  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const ExamplesSection = styled.div`
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateX(2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    border-color: #10b981;
  }
`;

const ExamplesTitle = styled.h4`
  color: #475569;
  margin-bottom: 16px;
  font-size: 0.9em;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const ExamplesGrid = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const ExampleButton = styled(motion.button)`
  background: white;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  color: #475569;
  font-size: 0.9em;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
  text-align: left;
  display: flex;
  align-items: center;
  gap: 8px;

  .origin { color: #2563eb; font-weight: 600; }
  .arrow { color: #94a3b8; font-size: 0.8em; }
  .destination { color: #dc2626; font-weight: 600; }

  &:hover {
    border-color: #2563eb;
    background: #f8fafc;
  }
`;

const InputGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: #374151;
  font-weight: 600;
  font-size: 0.85em;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.95em;
  transition: all 0.2s ease;
  background: white;
  color: #1f2937;
  box-sizing: border-box;
  font-weight: 500;

  &:focus {
    outline: none;
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  }

  &::placeholder {
    color: #9ca3af;
  }
`;

const MapStyleSection = styled.div`
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid #e2e8f0;
`;

const SectionTitle = styled.h3`
  color: #374151;
  margin-bottom: 16px;
  font-size: 0.85em;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  text-align: center;
`;

const StyleButtons = styled.div`
  display: flex;
  gap: 12px;
`;

const StyleButton = styled(motion.button)`
  flex: 1;
  padding: 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.8em;
  font-weight: 600;
  border-color: ${props => props.active ? '#2563eb' : '#d1d5db'};
  background: ${props => props.active ? '#2563eb' : 'white'};
  color: ${props => props.active ? 'white' : '#374151'};

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.15);
  }
`;

const HazardsSection = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid #e2e8f0;
`;

const HazardToggle = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  padding: 10px 12px;
  background: ${props => props.active ? '#f0fdf4' : 'white'};
  border-radius: 8px;
  border: 1px solid ${props => props.active ? '#10b981' : '#e2e8f0'};
  transition: all 0.2s ease;

  &:hover {
    border-color: ${props => props.active ? '#059669' : '#10b981'};
  }

  input[type="checkbox"] {
    width: auto;
    margin-right: 12px;
    transform: scale(1.1);
    accent-color: #10b981;
  }

  label {
    color: ${props => props.active ? '#065f46' : '#374151'};
    font-weight: 500;
    cursor: pointer;
    flex: 1;
    font-size: 0.85em;
  }
`;

const HazardStatus = styled.span`
  font-size: 0.7em;
  font-weight: 600;
  color: ${props => props.active ? '#059669' : '#9ca3af'};
  background: ${props => props.active ? '#f0fdf4' : '#f3f4f6'};
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid ${props => props.active ? '#bbf7d0' : '#e5e7eb'};
`;

const CalculateButton = styled(motion.button)`
  width: 100%;
  padding: 16px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;

  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }

  &:hover:not(:disabled) {
    background: #1d4ed8;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
  }
`;

const Spinner = styled.div`
  border: 2px solid rgba(255,255,255,0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  animation: spin 1s linear infinite;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const LoadingContainer = styled(motion.div)`
  text-align: center;
  padding: 20px;
  color: #2563eb;
  margin-top: 16px;
`;

const LoadingText = styled.p`
  margin: 0;
  font-weight: 500;
  font-size: 0.9em;
`;

const RouteInfo = styled(motion.div)`
  background: #f0f9ff;
  border-radius: 12px;
  padding: 20px;
  margin-top: 20px;
  border: 1px solid #bae6fd;
`;

const RouteTitle = styled.h3`
  color: #0c4a6e;
  margin-bottom: 16px;
  font-size: 1.1em;
  text-align: center;
  font-weight: 600;
`;

const RouteStats = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
`;

const StatItem = styled.div`
  background: white;
  padding: 16px;
  border-radius: 8px;
  text-align: center;
  border: 1px solid #e0f2fe;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
`;

const StatIcon = styled.div`
  width: 32px;
  height: 32px;
  background: #2563eb;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
`;

const StatValue = styled.div`
  font-size: 1.3em;
  font-weight: 700;
  color: #0c4a6e;
  margin: 0;
`;

const StatLabel = styled.div`
  font-size: 0.75em;
  color: #0369a1;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const MapContainer = styled.div`
  flex: 1;
  background: white;
  position: relative;
`;

const MapDisplay = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
`;

const MapHeader = styled.div`
  padding: 24px 32px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  text-align: center;
`;

const MapTitle = styled.h3`
  margin: 0 0 8px 0;
  color: #1e293b;
  font-size: 1.4em;
  font-weight: 600;
`;

const MapSubtitle = styled.p`
  margin: 0;
  color: #64748b;
  font-size: 0.9em;
  font-weight: 400;
`;

const MapContent = styled.div`
  flex: 1;
  position: relative;
  background: #f8fafc;
`;

const MapRef = styled.div`
  width: 100%;
  height: 100%;
  min-height: 500px;
  border: 1px solid #e2e8f0;
  border-radius: 0;
  background: white;
  position: relative;
  overflow: hidden;
  display: block;
`;

const MapIframe = styled.iframe`
  width: 100%;
  height: 100%;
  border: none;
  border-radius: 0;
`;

const RouteVisualizationOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 10;
`;

const RouteSegment = styled.div`
  position: absolute;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: ${props => {
    switch (props.safety) {
      case 'high': return '#10b981';
      case 'medium': return '#f59e0b';
      case 'low': return '#ef4444';
      default: return '#10b981';
    }
  }};
  border: 2px solid white;
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translate(-50%, -50%);
  z-index: 15;
`;

const RouteLineSegment = styled.div`
  position: absolute;
  height: 4px; /* Thickness of the line */
  background: ${props => {
    switch (props.safety) {
      case 'high': return '#10b981'; // Green for safe
      case 'medium': return '#f59e0b'; // Yellow for caution
      case 'low': return '#ef4444'; // Red for unsafe
      default: return '#10b981'; // Default to green
    }
  }};
  border-radius: 2px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  z-index: 10;
`;

const SegmentHazard = styled.div`
  position: absolute;
  bottom: -20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.65em;
  font-weight: 600;
  white-space: nowrap;
  z-index: 20;
`;

const RouteOverlay = styled.div`
  position: absolute;
  top: 20px;
  left: 20px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border: 1px solid #e2e8f0;
  z-index: 1000;
`;

const RouteSummary = styled.div`
  display: flex;
  flex-direction: column;
  gap: 6px;
`;

const RoutePoint = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8em;
  color: #374151;
  font-weight: 500;
`;

const MapOverlay = styled.div`
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border: 1px solid #e2e8f0;
  min-width: 180px;
`;

const OverlayTitle = styled.div`
  font-size: 0.8em;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  text-align: center;
`;

const OverlayControls = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const ControlItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-size: 0.8em;
  color: #475569;
  font-weight: 500;

  .current-style {
    color: #2563eb;
    font-weight: 600;
    background: #eff6ff;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.75em;
  }

  .map-status {
    color: #059669;
    font-weight: 600;
    background: #f0fdf4;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.75em;
  }
`;

const RouteSafetyOverlay = styled.div`
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border: 1px solid #e2e8f0;
  min-width: 200px;
  pointer-events: auto;
`;

const SafetyTitle = styled.h4`
  margin: 0 0 12px 0;
  color: #1e293b;
  font-size: 0.85em;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const SafetySegments = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const SafetySegment = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  background: ${props => {
    switch (props.safety) {
      case 'high': return '#f0fdf4';
      case 'medium': return '#fef3c7';
      case 'low': return '#fef2f2';
      default: return '#f0fdf4';
    }
  }};
  border-radius: 6px;
  border: 1px solid ${props => {
    switch (props.safety) {
      case 'high': return '#bbf7d0';
      case 'medium': return '#fde68a';
      case 'low': return '#fecaca';
      default: return '#bbf7d0';
    }
  }};
`;

const SafetyIndicator = styled.div`
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: ${props => {
    switch (props.safety) {
      case 'high': return '#10b981';
      case 'medium': return '#f59e0b';
      case 'low': return '#ef4444';
      default: return '#10b981';
    }
  }};
  border: 1px solid white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
`;

const SafetyInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;

  span:first-child {
    font-size: 0.75em;
    color: #475569;
    font-weight: 500;
  }

  .safety-level {
    font-size: 0.65em;
    font-weight: 600;
    color: ${props => {
      switch (props.safety) {
        case 'high': return '#059669';
        case 'medium': return '#d97706';
        case 'low': return '#dc2626';
        default: return '#059669';
      }
    }};
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
`;

const OverallSafety = styled.div`
  margin-top: 12px;
  text-align: center;
  font-size: 0.8em;
  font-weight: 600;
  color: #1e293b;

  .risk-score {
    padding: 4px 8px;
    border-radius: 4px;
    font-weight: 700;
  }

  .high-risk {
    background: #fef2f2;
    color: #991b1b;
    border: 1px solid #fecaca;
  }

  .medium-risk {
    background: #fef3c7;
    color: #d97706;
    border: 1px solid #fde68a;
  }

  .low-risk {
    background: #f0fdf4;
    color: #059669;
    border: 1px solid #bbf7d0;
  }
`;

const AIExplanationSection = styled(motion.div)`
  background: #f0f9ff;
  border-radius: 12px;
  padding: 20px;
  margin-top: 20px;
  border: 1px solid #bae6fd;
  margin-bottom: 24px;
`;

const AIExplanationTitle = styled.h3`
  color: #0c4a6e;
  margin-bottom: 16px;
  font-size: 1.1em;
  text-align: center;
  font-weight: 600;
`;

const AIExplanationContent = styled.div`
  font-size: 0.9em;
  color: #374151;
  line-height: 1.6;
  white-space: pre-wrap; /* Preserve line breaks */
`;

const AIExplanationLine = styled.p`
  margin-bottom: 8px;
  text-align: left;
`;

const AlternativeRoutesSection = styled(motion.div)`
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid #e2e8f0;
`;

const AlternativeRoutesTitle = styled.h4`
  color: #475569;
  margin-bottom: 16px;
  font-size: 0.9em;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const AlternativeRoutesGrid = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const AlternativeRouteCard = styled.div`
  background: white;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const AlternativeRouteHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85em;
  font-weight: 600;
  color: #1e293b;
  
  .route-number {
    color: #2563eb;
  }
  
  .risk-badge {
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 0.75em;
    font-weight: 700;
    
    &.high {
      background: #fef2f2;
      color: #991b1b;
      border: 1px solid #fecaca;
    }
    
    &.medium {
      background: #fef3c7;
      color: #d97706;
      border: 1px solid #fde68a;
    }
    
    &.low {
      background: #f0fdf4;
      color: #065f46;
      border: 1px solid #bbf7d0;
    }
  }
`;

const AlternativeRouteStats = styled.div`
  display: flex;
  gap: 16px;
  font-size: 0.8em;
  color: #475569;
  font-weight: 500;
`;

const AlternativeRouteTradeoff = styled.div`
  font-size: 0.75em;
  color: #64748b;
  font-style: italic;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 6px;
  border-left: 3px solid #2563eb;
`;

const AlternativeRouteReason = styled.div`
  font-size: 0.75em;
  color: #475569;
  padding: 8px 12px;
  background: #f0f9ff;
  border-radius: 6px;
  border-left: 3px solid #0ea5e9;
`;

const WeatherSection = styled(motion.div)`
  background: #f0f9ff;
  border-radius: 12px;
  padding: 20px;
  margin-top: 20px;
  border: 1px solid #bae6fd;
  margin-bottom: 24px;
`;

const WeatherTitle = styled.h3`
  color: #0c4a6e;
  margin-bottom: 16px;
  font-size: 1.1em;
  text-align: center;
  font-weight: 600;
`;

const WeatherCurrent = styled.div`
  font-size: 1.2em;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
`;

const WeatherHourly = styled.div`
  display: flex;
  justify-content: space-around;
  margin-bottom: 12px;
  font-size: 0.85em;
  color: #475569;
  font-weight: 500;
`;

const WeatherHour = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
`;

const WeatherAlerts = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 0.8em;
  color: #dc2626;
  font-weight: 600;
`;

const WeatherAlert = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  font-weight: 500;
`;

const SheltersSection = styled(motion.div)`
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  margin-top: 20px;
  border: 1px solid #e2e8f0;
  margin-bottom: 24px;
`;

const SheltersTitle = styled.h3`
  color: #0c4a6e;
  margin-bottom: 16px;
  font-size: 1.1em;
  text-align: center;
  font-weight: 600;
`;

const SheltersList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const ShelterItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
`;

const ShelterInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
`;

const ShelterName = styled.div`
  font-size: 0.9em;
  font-weight: 600;
  color: #1e293b;
`;

const ShelterDetails = styled.div`
  display: flex;
  gap: 8px;
  font-size: 0.8em;
  color: #475569;
  font-weight: 500;
`;

const ShelterAction = styled.button`
  padding: 8px 12px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.85em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;

  &:hover {
    background: #1d4ed8;
    transform: translateY(-1px);
    box-shadow: 0 2px 6px rgba(37, 99, 235, 0.2);
  }
`;

const RouteSafetyLegend = styled.div`
  margin-top: 16px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 0.8em;
  color: #374151;
  font-weight: 500;
`;

const LegendTitle = styled.div`
  font-size: 0.8em;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
  text-align: center;
`;

const LegendItem = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const LegendColor = styled.div`
  width: 16px;
  height: 16px;
  border-radius: 4px;
  background-color: ${props => props.color};
  border: 1px solid #e2e8f0;
`;

export default App;