document.addEventListener('DOMContentLoaded', function() {
    console.log("SOS script loaded");
    
    const sosButton = document.getElementById('sosButton');
    const locationToggle = document.getElementById('locationToggle');
    
    if (sosButton) {
        console.log("SOS button found");
        
        // Add pulsing animation to make the button noticeable
        sosButton.classList.add('pulse-animation');
        
        // Stop pulsing when user interacts with the page
        document.addEventListener('click', function() {
            sosButton.classList.remove('pulse-animation');
        }, {once: true});
        
        sosButton.addEventListener('click', function(e) {
            console.log("SOS button clicked");
            e.preventDefault();
            
            // Show confirmation dialog
            Swal.fire({
                title: 'Send Emergency SOS Alert?',
                text: 'This will notify responders that you need immediate help.',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Yes, send SOS!',
                cancelButtonText: 'Cancel'
            }).then((result) => {
                if (result.isConfirmed) {
                    console.log("SOS confirmed");
                    sendSOSAlert();
                }
            });
        });
    } else {
        console.warn("SOS button not found!");
    }
    
    async function sendSOSAlert() {
        try {
            console.log("Preparing to send SOS alert");
            
            // Show loading state
            Swal.fire({
                title: 'Sending SOS Alert',
                text: 'Please wait...',
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });
            
            // Try to get current location for the emergency
            let locationData = null;
            try {
                console.log("Attempting to get location");
                if (navigator.geolocation) {
                    const position = await new Promise((resolve, reject) => {
                        navigator.geolocation.getCurrentPosition(resolve, reject, {
                            enableHighAccuracy: true,
                            timeout: 5000,
                            maximumAge: 0
                        });
                    });
                    
                    locationData = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    };
                    console.log("Location obtained:", locationData);
                } else {
                    console.log("Geolocation not available");
                }
            } catch (locErr) {
                console.warn("Error getting location:", locErr);
            }
            
            console.log("Sending SOS request to server");
            const response = await fetch('/victim/profile/sos', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    description: "Emergency SOS activated by victim",
                    location: locationData
                })
            });
            
            console.log("SOS response status:", response.status);
            
            // Check if response is JSON
            const contentType = response.headers.get("content-type");
            if (!contentType || !contentType.includes("application/json")) {
                throw new Error("Received non-JSON response. Please check your login status.");
            }
            
            const data = await response.json();
            console.log("SOS response data:", data);
            
            if (!response.ok) {
                throw new Error(data.error || "Failed to send SOS alert");
            }
            
            // Show success message
            Swal.fire({
                icon: 'success',
                title: 'SOS Alert Sent!',
                text: `Responders have been notified of your emergency. ${data.responders_notified} responder(s) alerted.`,
                confirmButtonColor: '#4CAF50'
            });
            
        } catch (error) {
            console.error("Error sending SOS alert:", error);
            
            Swal.fire({
                icon: 'error',
                title: 'Error Sending SOS',
                text: error.message || 'Failed to send emergency alert. Please try again or call emergency services directly.',
                confirmButtonColor: '#d33',
                showCancelButton: true,
                cancelButtonText: 'Try Again',
                confirmButtonText: 'OK'
            }).then((result) => {
                if (!result.isConfirmed) {
                    // Try again
                    sendSOSAlert();
                }
            });
        }
    }
    
    // Also handle retry logic for location permission errors
    if (locationToggle) {
        locationToggle.addEventListener('change', function() {
            if (this.checked) {
                // Request location permission
                navigator.geolocation.getCurrentPosition(
                    () => {
                        // Success - permission granted
                        console.log('Location permission granted');
                    },
                    (error) => {
                        // Error - permission denied or other error
                        console.error('Location error:', error);
                        
                        if (error.code === 1) { // PERMISSION_DENIED
                            // Show explanation and retry dialog
                            Swal.fire({
                                icon: 'warning',
                                title: 'Location Access Needed',
                                text: 'For your safety, please enable location sharing. This helps responders find you in emergencies.',
                                confirmButtonColor: '#4CAF50',
                                showCancelButton: true,
                                confirmButtonText: 'Try Again',
                                cancelButtonText: 'Not Now'
                            }).then((result) => {
                                if (result.isConfirmed) {
                                    // They want to try again
                                    this.checked = true;
                                    const event = new Event('change');
                                    this.dispatchEvent(event);
                                } else {
                                    // They declined
                                    this.checked = false;
                                }
                            });
                        } else {
                            // Other error
                            this.checked = false;
                            Swal.fire({
                                icon: 'error',
                                title: 'Location Error',
                                text: 'Could not access your location. Please check your device settings.',
                                confirmButtonColor: '#d33'
                            });
                        }
                    },
                    { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
                );
            }
        });
    }
});