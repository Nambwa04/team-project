document.addEventListener('DOMContentLoaded', function () {
    console.log('Responder Profile JS loaded');

    // Function to fetch messages
    function fetchMessages() {
        $.ajax({
            url: "{{ url_for('responderProfile.get_messages') }}",
            method: "GET",
            success: function (data) {
                const messageList = $('#responderMessageList');
                messageList.empty();
                data.messages.forEach(message => {
                    const messageItem = `
                        <div class="responder-message-item">
                            <p><strong>${message.username}:</strong> ${message.message}</p>
                            <div class="message-time">${message.timestamp}</div>
                        </div>`;
                    messageList.append(messageItem);
                });
            }
        });
    }

    // Poll every 5 seconds
    setInterval(fetchMessages, 5000);

    // Send message
    $('#responderMessageForm').on('submit', function (e) {
        e.preventDefault();
        const messageInput = $('#responderMessageInput');
        const message = messageInput.val();
        $.ajax({
            url: "{{ url_for('responderProfile.send_message') }}",
            method: "POST",
            data: { message: message },
            success: function () {
                messageInput.val('');
                fetchMessages();
            }
        });
    });

    fetchMessages(); // Initial fetch
});