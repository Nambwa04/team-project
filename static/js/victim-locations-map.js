document.addEventListener('DOMContentLoaded', function() {
    // Initialize map if the container exists
    const mapContainer = document.getElementById('victimLocationsMap');
    
    if (!mapContainer) return;
    
    // Initialize the map
    const map = L.map(mapContainer).setView([0, 0], 2); // Default view of the world
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    // Create marker clusters for better performance with many markers
    const markers = L.markerClusterGroup();
    
    // Load victim locations
    loadVictimLocations();
    
    // Refresh locations every 30 seconds
    setInterval(loadVictimLocations, 30000);
    
    // Function to load victim locations from server
    async function loadVictimLocations() {
        try {
            const response = await fetch('/admin/victim-locations');
            
            if (!response.ok) {
                throw new Error('Failed to load victim locations');
            }
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Unknown error');
            }
            
            // Clear existing markers
            markers.clearLayers();
            
            // Add new markers for each victim
            const victimMarkers = [];
            
            data.locations.forEach(victim => {
                if (victim.location && victim.location.latitude && victim.location.longitude) {
                    const marker = L.marker([victim.location.latitude, victim.location.longitude]);
                    
                    const lastUpdated = new Date(victim.location.timestamp).toLocaleString();
                    
                    marker.bindPopup(`
                        <strong>${victim.username}</strong><br>
                        Last Updated: ${lastUpdated}<br>
                        <button class="contact-victim-btn" data-victim-id="${victim._id}">Contact</button>
                    `);
                    
                    markers.addLayer(marker);
                    victimMarkers.push(marker);
                }
            });
            
            // Add markers to map
            map.addLayer(markers);
            
            // Auto-zoom to fit all markers if there are any
            if (victimMarkers.length > 0) {
                const group = L.featureGroup(victimMarkers);
                map.fitBounds(group.getBounds(), { padding: [50, 50] });
            }
            
            // Add event listeners to contact buttons
            setTimeout(() => {
                document.querySelectorAll('.contact-victim-btn').forEach(button => {
                    button.addEventListener('click', function() {
                        const victimId = this.getAttribute('data-victim-id');
                        window.location.href = `/admin/message/${victimId}`;
                    });
                });
            }, 100);
            
        } catch (error) {
            console.error('Error loading victim locations:', error);
            showNotification('Failed to load victim locations', 'error');
        }
    }
    
    // Function to show notifications
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `map-notification ${type}`;
        notification.textContent = message;
        
        mapContainer.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }
});