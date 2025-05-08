// Main JavaScript file for Khatma App

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Handle notification marking as read
    var notificationLinks = document.querySelectorAll('.notification-item a');
    notificationLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            var notificationId = this.dataset.notificationId;
            if (notificationId) {
                fetch('/notifications/' + notificationId + '/mark-read/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    }
                });
            }
        });
    });

    // Handle Khatma part completion toggle
    var partToggleButtons = document.querySelectorAll('.part-toggle');
    partToggleButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            var khatmaId = this.dataset.khatmaId;
            var partId = this.dataset.partId;
            var isCompleted = this.dataset.isCompleted === 'true';
            
            fetch('/khatma/api/khatma/' + khatmaId + '/part/' + partId + '/status/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: 'is_completed=' + (!isCompleted)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Update button state
                    this.dataset.isCompleted = data.is_completed;
                    
                    // Update button text and class
                    if (data.is_completed) {
                        this.innerHTML = '<i class="fas fa-check-circle"></i> تم الإكمال';
                        this.classList.remove('btn-outline-primary');
                        this.classList.add('btn-success');
                    } else {
                        this.innerHTML = '<i class="fas fa-circle"></i> تحديد كمكتمل';
                        this.classList.remove('btn-success');
                        this.classList.add('btn-outline-primary');
                    }
                    
                    // Update part item class
                    var partItem = document.querySelector('.part-item[data-part-id="' + partId + '"]');
                    if (partItem) {
                        if (data.is_completed) {
                            partItem.classList.add('completed');
                        } else {
                            partItem.classList.remove('completed');
                        }
                    }
                    
                    // Update progress bar
                    updateKhatmaProgress(khatmaId);
                }
            });
        });
    });

    // Function to update Khatma progress
    function updateKhatmaProgress(khatmaId) {
        fetch('/khatma/api/khatma/' + khatmaId + '/progress/')
        .then(response => response.json())
        .then(data => {
            var progressBar = document.querySelector('#khatma-progress-bar');
            if (progressBar) {
                progressBar.style.width = data.progress_percentage + '%';
                progressBar.setAttribute('aria-valuenow', data.progress_percentage);
                document.querySelector('#completed-parts').textContent = data.completed_parts;
                document.querySelector('#total-parts').textContent = data.total_parts;
            }
            
            // If Khatma is completed, show completion message
            if (data.is_completed && !document.querySelector('#khatma-completed-alert')) {
                var alertDiv = document.createElement('div');
                alertDiv.id = 'khatma-completed-alert';
                alertDiv.className = 'alert alert-success';
                alertDiv.innerHTML = '<i class="fas fa-check-circle"></i> تم إكمال الختمة بنجاح!';
                document.querySelector('.khatma-progress-container').appendChild(alertDiv);
            }
        });
    }

    // Handle Quran audio player
    var audioPlayer = document.querySelector('#quran-audio-player');
    if (audioPlayer) {
        var playButtons = document.querySelectorAll('.play-ayah');
        playButtons.forEach(function(button) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                var audioSrc = this.dataset.audioSrc;
                audioPlayer.src = audioSrc;
                audioPlayer.play();
                
                // Update active ayah
                document.querySelectorAll('.ayah').forEach(function(ayah) {
                    ayah.classList.remove('active-ayah');
                });
                this.closest('.ayah').classList.add('active-ayah');
            });
        });
    }

    // Handle Quran reading position tracking
    var ayahElements = document.querySelectorAll('.ayah');
    ayahElements.forEach(function(ayah) {
        ayah.addEventListener('click', function(e) {
            if (e.target.tagName !== 'A' && e.target.tagName !== 'BUTTON') {
                var surahId = this.dataset.surahId;
                var ayahNumber = this.dataset.ayahNumber;
                
                // Send AJAX request to update last read position
                fetch('/quran/update-last-read/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: 'surah_id=' + surahId + '&ayah_number=' + ayahNumber
                });
            }
        });
    });

    // Helper function to get CSRF token from cookies
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
