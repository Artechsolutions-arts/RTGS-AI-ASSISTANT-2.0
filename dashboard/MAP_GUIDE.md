# Andhra Pradesh Interactive Map Guide

## Overview
The AP Government Dashboard features an **accurate, interactive SVG map** of Andhra Pradesh with all **26 districts** properly labeled, positioned, and color-coded based on activity levels.

---

## Map Features

### 1. **All 26 Districts Included**
The map accurately represents the current administrative structure of Andhra Pradesh (as of 2022 reorganization):

#### **North Coastal Andhra (Uttarandhra)**
1. **Srikakulam** - North-East Corner, Coastal
2. **Parvathipuram Manyam** - North Inland, Hilly/Tribal Area
3. **Vizianagaram** - Coastal
4. **Alluri Sitharama Raju** - Inland, Agency/Tribal Area
5. **Visakhapatnam** - Major Coastal City, IT Hub
6. **Anakapalli** - Coastal
7. **Kakinada** - Coastal Port City
8. **East Godavari** - Coastal, Rice Bowl
9. **Konaseema** - Delta, Coastal (Newest District)

#### **Central Coastal Andhra (Godavari Delta & Krishna Region)**
10. **West Godavari** - Delta Region, Aquaculture Hub
11. **Eluru** - Inland
12. **NTR** - Vijayawada, Capital Region
13. **Krishna** - Coastal, Agricultural Hub
14. **Palnadu** - Inland, Cotton Belt
15. **Guntur** - Major City, Chilli Capital
16. **Bapatla** - Coastal
17. **Prakasam** - Coastal, Ongole Bull

#### **South Coastal Andhra (Nellore Region)**
18. **Nellore** - Coastal, Major City, Rice
19. **Tirupati** - Inland, Pilgrimage City, Temple Town
20. **Chittoor** - Southern Border, Mango Belt
21. **Annamayya** - Southern Inland

#### **Rayalaseema Region (Inland West - Dry Zone)**
22. **YSR (Kadapa)** - Inland, Cement Hub
23. **Satya Sai** - Inland, Puttaparthi
24. **Anantapur** - Western Border, Largest District, Arid
25. **Kurnool** - North-West, Large District, Historical
26. **Nandyal** - North-West Inland

---

## Interactive Features

### **Color Coding by Activity Level**
Districts are automatically color-coded based on message activity:

- 🔴 **Red (#F44336)** - High Activity (e.g., Visakhapatnam, NTR, Guntur, Krishna)
- 🟠 **Orange (#FF9800)** - Medium Activity (most districts)
- 🟢 **Green (#4CAF50)** - Low Activity (e.g., Parvathipuram Manyam, Satya Sai)

### **Hover Tooltips**
When you hover over any district, a detailed tooltip appears showing:
- District Name
- Total Messages
- High Priority Messages
- Medium Priority Messages
- Low Priority Messages
- Departments Involved

### **Click Interactions**
Clicking on a district displays a detailed alert with comprehensive statistics (can be customized to open a modal or navigate to a detailed view).

### **Visual Enhancements**
- **Drop Shadow Effects** - Districts have subtle shadows for depth
- **Hover Effects** - Districts slightly enlarge and change stroke on hover
- **Smooth Transitions** - All interactions are animated smoothly
- **Region Labels** - Background labels for Uttarandhra, Godavari Delta, and Rayalaseema
- **Coastal Indicator** - Dashed line showing the Bay of Bengal coastline

---

## Technical Details

### **SVG Specifications**
- **ViewBox**: `0 0 1200 1400` (larger canvas for better detail)
- **Stroke Width**: 2.5px (enhanced visibility)
- **Font Size**: 13px for district labels (11px for smaller districts)
- **Font Weight**: 700 (bold, clear labels)
- **Text Shadow**: Multi-layer shadows for maximum readability

### **Geographic Accuracy**
The map is designed to reflect:
- Actual relative positions of districts
- Approximate size relationships
- Coastal vs. inland positioning
- Regional groupings (Uttarandhra, Godavari Delta, Rayalaseema)

### **Responsive Design**
The map automatically scales to fit the container while maintaining aspect ratio:
```css
.map-container svg {
    max-width: 100%;
    max-height: 100%;
    height: auto;
}
```

---

## Data Integration

### **Mock Data Structure**
Each district has associated data:
```javascript
{
    messages: 45,
    departments: ['Health', 'Infrastructure', 'Electricity'],
    priority: { high: 3, medium: 12, low: 30 },
    activity: 'high'
}
```

### **API Integration Points**
Replace mock data with live data from:
```
GET /webhook/districts-stats
```

Expected response format:
```json
{
    "Visakhapatnam": {
        "messages": 45,
        "departments": ["Health", "Infrastructure", "Electricity"],
        "priority": {
            "high": 3,
            "medium": 12,
            "low": 30
        },
        "activity": "high"
    },
    ...
}
```

---

## Customization Options

### **Change Color Scheme**
Edit the color assignments in `ap-map.js`:
```javascript
if (districtInfo.activity === 'high') {
    path.style.fill = '#F44336'; // Change to your color
}
```

### **Modify Tooltip Content**
Update the tooltip HTML in `showDistrictTooltip()` function:
```javascript
tooltipContent.innerHTML = `
    <div><strong>Messages:</strong> ${districtInfo.messages}</div>
    // Add more fields here
`;
```

### **Add Click Actions**
Customize `handleDistrictClick()` to:
- Open a modal with detailed district view
- Navigate to a district-specific page
- Filter messages by district
- Show district-specific analytics

---

## Browser Compatibility

### **Fully Supported**
- ✅ Chrome 90+
- ✅ Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+

### **SVG Features Used**
- Path elements with complex shapes
- Text elements with shadows
- CSS filters (drop-shadow)
- CSS transitions
- Event listeners on SVG elements

---

## Performance Considerations

### **Optimizations**
- SVG is embedded inline (no external file loading)
- Event listeners attached once on initialization
- Tooltip reused (not recreated on each hover)
- Smooth transitions without heavy animations

### **Memory Usage**
- Lightweight SVG markup (~15KB)
- Minimal JavaScript overhead
- No external dependencies

---

## Future Enhancements

### **Potential Features**
1. **Zoom & Pan** - Allow users to zoom into specific regions
2. **District Boundaries** - More accurate GeoJSON-based boundaries
3. **Heat Map Mode** - Gradient colors based on message density
4. **Time-based Animation** - Show activity changes over time
5. **Multi-layer View** - Toggle between different data visualizations
6. **Export Functionality** - Download map as PNG/SVG
7. **Accessibility** - Keyboard navigation and screen reader support

### **Data Enhancements**
1. Real-time updates via WebSocket
2. Historical data comparison
3. Predictive analytics overlay
4. Integration with GIS systems

---

## Troubleshooting

### **Map Not Displaying**
- Check browser console for errors
- Verify `apMapContainer` element exists in HTML
- Ensure `ap-map.js` is loaded after DOM is ready

### **Tooltips Not Showing**
- Verify `districtTooltip` element exists in HTML
- Check CSS z-index values
- Ensure tooltip is not hidden by overflow

### **Colors Not Updating**
- Check `DISTRICT_DATA` object has correct activity levels
- Verify color assignment logic in `initializeMap()`
- Inspect element styles in browser DevTools

### **Click Events Not Working**
- Check browser console for JavaScript errors
- Verify event listeners are attached
- Ensure `handleDistrictClick()` function is defined

---

## Credits

**Map Design**: Based on official Andhra Pradesh administrative boundaries (2022)  
**Technology**: SVG, Vanilla JavaScript, CSS3  
**Color Palette**: Government-grade professional colors  

---

## Contact & Support

For issues, enhancements, or questions about the map:
- Review the main `README.md` for overall dashboard documentation
- Check `ap-map.js` for implementation details
- Inspect browser DevTools for runtime debugging

---

**Last Updated**: 2024  
**Version**: 2.0 (Enhanced Geographic Accuracy)
