from nicegui import ui


def setup_static_content():
    """Setup static content and routes"""

    # Add custom CSS for better styling
    ui.add_head_html("""
    <style>
        /* Custom animations and transitions */
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Enhanced hover effects */
        .hover-lift:hover {
            transform: translateY(-2px);
            transition: transform 0.2s ease;
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8;
        }
        
        /* Risk level indicators */
        .risk-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .risk-green { background-color: #10b981; }
        .risk-yellow { background-color: #f59e0b; }
        .risk-red { background-color: #ef4444; }
        
        /* Body map styling */
        .body-map-container {
            position: relative;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 15px;
            padding: 20px;
        }
        
        /* Loading animation */
        .loading-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Glass morphism effect */
        .glass-card {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        
        /* Assessment status badges */
        .status-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .status-completed {
            background-color: #d1fae5;
            color: #065f46;
        }
        
        .status-in-progress {
            background-color: #fef3c7;
            color: #92400e;
        }
        
        /* Responsive design helpers */
        @media (max-width: 768px) {
            .mobile-stack {
                flex-direction: column !important;
            }
            
            .mobile-full {
                width: 100% !important;
            }
            
            .mobile-hide {
                display: none !important;
            }
        }
        
        /* Enhanced button styles */
        .btn-gradient {
            background: linear-gradient(45deg, #3b82f6 0%, #8b5cf6 100%);
            border: none;
            color: white;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .btn-gradient:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        }
        
        /* Assessment progress indicator */
        .progress-step {
            display: flex;
            align-items: center;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 8px;
            transition: all 0.3s ease;
        }
        
        .progress-step.active {
            background-color: #dbeafe;
            border-left: 4px solid #3b82f6;
        }
        
        .progress-step.completed {
            background-color: #d1fae5;
            border-left: 4px solid #10b981;
        }
        
        /* Form enhancements */
        .form-section {
            background: #fafafa;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            border: 1px solid #e5e7eb;
        }
        
        /* Data visualization */
        .metric-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transform: translateY(-2px);
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            line-height: 1;
            margin: 8px 0;
        }
        
        .metric-label {
            color: #6b7280;
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* Interactive elements */
        .clickable-area {
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .clickable-area:hover {
            opacity: 0.8;
            transform: scale(1.02);
        }
        
        /* Notification enhancements */
        .notification-success {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }
        
        .notification-warning {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        }
        
        .notification-error {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        }
    </style>
    """)

    # Serve placeholder images
    @ui.page("/static/images/camera_placeholder.png")
    def camera_placeholder():
        # In a real implementation, this would serve an actual image file
        # For now, we'll return a simple response
        ui.label("Camera Placeholder").classes("text-center p-8 bg-gray-200 rounded")

    @ui.page("/static/images/camera_active.png")
    def camera_active():
        # In a real implementation, this would serve an actual image file
        ui.label("Camera Active").classes("text-center p-8 bg-green-200 rounded")

    # Add JavaScript utilities
    ui.add_head_html("""
    <script>
        // Utility functions for enhanced UI interactions
        window.ErgonomicAssessment = {
            // Smooth scroll to element
            scrollToElement: function(selector) {
                const element = document.querySelector(selector);
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth' });
                }
            },
            
            // Add pulse animation to element
            pulseElement: function(selector) {
                const element = document.querySelector(selector);
                if (element) {
                    element.classList.add('animate-pulse');
                    setTimeout(() => {
                        element.classList.remove('animate-pulse');
                    }, 2000);
                }
            },
            
            // Show loading state
            showLoading: function(containerId) {
                const container = document.getElementById(containerId);
                if (container) {
                    container.innerHTML = '<div class="loading-spinner"></div>';
                }
            },
            
            // Format number with proper decimals
            formatScore: function(score, decimals = 1) {
                return parseFloat(score).toFixed(decimals);
            },
            
            // Get risk color based on level
            getRiskColor: function(level) {
                switch(level.toLowerCase()) {
                    case 'green': return '#10b981';
                    case 'yellow': return '#f59e0b';
                    case 'red': return '#ef4444';
                    default: return '#6b7280';
                }
            },
            
            // Local storage helpers
            saveData: function(key, data) {
                try {
                    localStorage.setItem(key, JSON.stringify(data));
                } catch (e) {
                    console.warn('Could not save to localStorage:', e);
                }
            },
            
            loadData: function(key) {
                try {
                    const data = localStorage.getItem(key);
                    return data ? JSON.parse(data) : null;
                } catch (e) {
                    console.warn('Could not load from localStorage:', e);
                    return null;
                }
            }
        };
        
        // Initialize tooltips and other UI enhancements when DOM is ready
        document.addEventListener('DOMContentLoaded', function() {
            // Add smooth transitions to all cards
            const cards = document.querySelectorAll('.q-card');
            cards.forEach(card => {
                card.style.transition = 'all 0.3s ease';
            });
            
            // Add keyboard navigation support
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    // Close any open dialogs or modals
                    const dialogs = document.querySelectorAll('.q-dialog');
                    dialogs.forEach(dialog => {
                        if (dialog.style.display !== 'none') {
                            // Trigger close event
                            const closeBtn = dialog.querySelector('[role="button"][aria-label*="close"]');
                            if (closeBtn) closeBtn.click();
                        }
                    });
                }
            });
        });
    </script>
    """)


def create():
    """Create static content module"""
    setup_static_content()
