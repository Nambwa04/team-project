document.addEventListener('DOMContentLoaded', function() {
    console.log('Report JS loaded');

    const reportForm = document.getElementById('reportForm');
    reportForm.addEventListener('submit', function(e) {
        console.log("Submitting report...");
    });
});
