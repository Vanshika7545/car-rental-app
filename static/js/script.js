// JavaScript for Car Rental System

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Brand filter functionality for user dashboard
    const brandFilter = document.getElementById('brandFilter');
    if (brandFilter) {
        brandFilter.addEventListener('change', function() {
            const selectedBrand = this.value;
            const carCards = document.querySelectorAll('.car-card');
            
            carCards.forEach(card => {
                if (selectedBrand === 'all' || card.dataset.brand === selectedBrand) {
                    card.closest('.car-column').style.display = 'block';
                } else {
                    card.closest('.car-column').style.display = 'none';
                }
            });
        });
    }

    // Rental date validation
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    const pricePerDayElement = document.getElementById('price_per_day');
    const totalPriceElement = document.getElementById('total_price');
    
    if (startDateInput && endDateInput && pricePerDayElement && totalPriceElement) {
        const pricePerDay = parseFloat(pricePerDayElement.dataset.price);
        
        function updateTotalPrice() {
            const startDate = new Date(startDateInput.value);
            const endDate = new Date(endDateInput.value);
            
            if (startDate && endDate && !isNaN(startDate) && !isNaN(endDate)) {
                // Calculate the difference in days
                const timeDiff = endDate - startDate;
                const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24)) + 1; // +1 to include the start day
                
                if (daysDiff > 0) {
                    const totalPrice = daysDiff * pricePerDay;
                    totalPriceElement.textContent = `$${totalPrice.toFixed(2)}`;
                } else {
                    totalPriceElement.textContent = 'Invalid date range';
                }
            }
        }
        
        startDateInput.addEventListener('change', updateTotalPrice);
        endDateInput.addEventListener('change', updateTotalPrice);
    }

    // Confirmation dialogs for delete actions
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Car rental cancellation confirmation
    const cancelRentalButtons = document.querySelectorAll('.cancel-rental-btn');
    cancelRentalButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to cancel this rental?')) {
                e.preventDefault();
            }
        });
    });
});
