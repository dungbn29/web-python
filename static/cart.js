document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.quantity-btn').forEach(button => {
      button.addEventListener('click', async function() {
        const action = this.classList.contains('plus') ? 'increase' : 'decrease';
        const productName = this.dataset.name;
        const quantityElement = this.parentElement.querySelector('.quantity');
        const priceElement = this.closest('.cart-item').querySelector('.cart-price');
        
        const originalContent = this.innerHTML;
        
        // Hiệu ứng loading
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        this.disabled = true;
        
        try {
          const response = await fetch('/update_cart', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              name: productName,
              action: action
            })
          });
          
          const data = await response.json();
          
          if (data.success) {
            quantityElement.textContent = data.newQuantity;
            priceElement.textContent = `${data.newPrice} VND`;
            
            if (document.querySelector('.cart-total')) {
              document.querySelector('.cart-total').innerHTML = 
                `<strong>Tổng tiền: ${data.newTotal} VND</strong>`;
            }
          } else {
            showToast(data.message || 'Có lỗi xảy ra');
          }
        } catch (error) {
          showToast('Lỗi kết nối đến server');
          console.error('Error:', error);
        } finally {
          this.innerHTML = originalContent;
          this.disabled = false;
        }
      });
    });
    
    function showToast(message) {
      const toast = document.createElement('div');
      toast.className = 'toast-notification';
      toast.textContent = message;
      document.body.appendChild(toast);
      
      setTimeout(() => {
        toast.classList.add('show');
        setTimeout(() => {
          toast.classList.remove('show');
          setTimeout(() => {
            document.body.removeChild(toast);
          }, 300);
        }, 3000);
      }, 100);
    }
  });
  