document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const locationToggle = document.getElementById('locationToggle');
    const locationStatus = document.getElementById('locationStatus');
    const lastUpdatedTime = document.getElementById('lastUpdatedTime');
    const sosButton = document.getElementById('sosButton');
    const locationIndicator = document.getElementById('locationIndicator');
    
    // State
    let locationWatchId = null;
    
    // Initialize location toggle if it exists
    if (locationToggle) {
        // Check if geolocation is supported
        if (!navigator.geolocation) {
            locationToggle.disabled = true;
            locationStatus.textContent = 'Geolocation not supported by your browser';
            locationToggle.parentElement.classList.add('disabled');
            return;
        }
        
        // Set initial state based on saved preference
        const locationEnabled = localStorage.getItem('locationSharingEnabled') === 'true';
        locationToggle.checked = locationEnabled;
        updateLocationStatus(locationEnabled);
        
        if (locationEnabled) {
            startLocationSharing();
        }
        
        // Handle location toggle change
        locationToggle.addEventListener('change', function() {
            const isEnabled = locationToggle.checked;
            localStorage.setItem('locationSharingEnabled', isEnabled);
            
            if (isEnabled) {
                startLocationSharing();
            } else {
                stopLocationSharing();
            }
            
            updateLocationStatus(isEnabled);
        });
    }
    
    // Initialize SOS button if it exists
    if (sosButton) {
        sosButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Confirm before sending SOS
            if (confirm('Are you sure you want to send an emergency SOS alert? This will alert all available responders.')) {
                sendSOSAlert();
            }
        });
    }
    
    // Helper functions
    function updateLocationStatus(isEnabled) {
        if (locationStatus) {
            locationStatus.textContent = isEnabled ? 'Active' : 'Disabled';
            locationStatus.className = isEnabled ? 'status-active' : 'status-inactive';
        }
        
        if (locationIndicator) {
            locationIndicator.className = isEnabled ? 'location-indicator active' : 'location-indicator inactive';
        }
    }
    
    function startLocationSharing() {
        // Clear any existing watch
        if (locationWatchId !== null) {
            stopLocationSharing();
        }
        
        // Start watching position
        locationWatchId = navigator.geolocation.watchPosition(
            handlePositionSuccess,
            handlePositionError,
            { 
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    }
    
    function stopLocationSharing() {
        if (locationWatchId !== null) {
            navigator.geolocation.clearWatch(locationWatchId);
            locationWatchId = null;
        }
    }
    
    function handlePositionSuccess(position) {
        const latitude = position.coords.latitude;
        const longitude = position.coords.longitude;
        
        // Update last updated time
        if (lastUpdatedTime) {
            const now = new Date();
            lastUpdatedTime.textContent = `Last Updated: ${now.toLocaleTimeString()}`;
        }
        
        // Send location to server
        sendLocationToServer(latitude, longitude);
    }
    
    function handlePositionError(error) {
        console.error('Error getting location:', error);
        
        let errorMessage = 'Unknown error occurred while getting your location';
        
        switch(error.code) {
            case error.PERMISSION_DENIED:
                errorMessage = 'Location permission denied. Please enable location access for safety features.';
                break;
            case error.POSITION_UNAVAILABLE:
                errorMessage = 'Location information is unavailable. Please check your device settings.';
                break;
            case error.TIMEOUT:
                errorMessage = 'Location request timed out. Please try again.';
                break;
        }
        
        showNotification(errorMessage, 'error');
        
        // Turn off toggle if there's an error
        if (locationToggle && locationToggle.checked) {
            locationToggle.checked = false;
            localStorage.setItem('locationSharingEnabled', false);
            updateLocationStatus(false);
        }
    }
    
    async function sendLocationToServer(latitude, longitude) {
        try {
            const response = await fetch('/victim/profile/update-location', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ latitude, longitude })
            });
            
            if (!response.ok) {
                throw new Error('Failed to update location');
            }
            
            // Optional: show success indicator briefly
            if (locationIndicator) {
                locationIndicator.classList.add('pulse');
                setTimeout(() => {
                    locationIndicator.classList.remove('pulse');
                }, 1000);
            }
            
        } catch (error) {
            console.error('Error sending location to server:', error);
            showNotification('Failed to update your location. Please try again.', 'warning');
        }
    }
    
    async function sendSOSAlert() {
        try {
            // Show loading state
            const originalText = sosButton.textContent;
            sosButton.textContent = 'Sending...';
            sosButton.disabled = true;
            
            const response = await fetch('/victim/profile/sos', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            // Reset button state
            sosButton.disabled = false;
            sosButton.textContent = originalText;
            
            if (!response.ok) {
                throw new Error('Failed to send SOS alert');
            }
            
            const result = await response.json();
            
            // Show success message
            showNotification('Emergency alert sent successfully. Help is on the way.', 'success');
            
            // Automatically enable location sharing if not already enabled
            if (locationToggle && !locationToggle.checked) {
                locationToggle.checked = true;
                localStorage.setItem('locationSharingEnabled', true);
                startLocationSharing();
                updateLocationStatus(true);
            }
            
        } catch (error) {
            console.error('Error sending SOS alert:', error);
            showNotification('Failed to send emergency alert. Please try again.', 'error');
            
            // Reset button state if not already done
            if (sosButton.disabled) {
                sosButton.disabled = false;
                sosButton.textContent = 'SOS EMERGENCY';
            }
        }
    }
    
    function showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // Append to body
        document.body.appendChild(notification);
        
        // Show notification
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 5000);
    }
});