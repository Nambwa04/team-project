document.addEventListener('DOMContentLoaded', function () {
    console.log('Report JS loaded');

    const reportForm = document.getElementById('reportForm');
    if (reportForm) {
        reportForm.addEventListener('submit', function (e) {
            e.preventDefault(); // Prevent the default form submission

            Swal.fire({
                title: 'Submit Report?',
                text: 'This will notify responders about the emergency.',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Yes, submit report!',
                cancelButtonText: 'Cancel'
            }).then((result) => {
                if (result.isConfirmed) {
                    // Submit the form
                    reportForm.submit();
                }
            });
        });
    }
});
