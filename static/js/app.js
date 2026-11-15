/**
 * IIIT Allahabad - Cyber Security IT-30001
 * Front-end interactive utility scripts for live exploit demonstration
 */

document.addEventListener('DOMContentLoaded', () => {
    // Enable payload chip quick fill
    const chips = document.querySelectorAll('.payload-chip');
    chips.forEach(chip => {
        chip.addEventListener('click', (e) => {
            const payload = chip.getAttribute('data-payload');
            const targetId = chip.getAttribute('data-target');
            if (targetId && payload) {
                const targetInput = document.getElementById(targetId);
                if (targetInput) {
                    targetInput.value = payload;
                    targetInput.focus();
                    
                    // Flash effect on input
                    targetInput.style.transition = 'background-color 0.3s';
                    const origBg = targetInput.style.backgroundColor;
                    targetInput.style.backgroundColor = 'rgba(0, 229, 255, 0.2)';
                    setTimeout(() => {
                        targetInput.style.backgroundColor = origBg;
                    }, 400);
                }
            }
        });
    });

    // Auto-dismiss alerts after 8 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.6s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 600);
        }, 8000);
    });
});

function copyToClipboard(text, btnElement) {
    navigator.clipboard.writeText(text).then(() => {
        const originalText = btnElement.innerText;
        btnElement.innerText = "Copied!";
        btnElement.classList.add('btn-success');
        setTimeout(() => {
            btnElement.innerText = originalText;
            btnElement.classList.remove('btn-success');
        }, 1500);
    }).catch(err => {
        console.error('Failed to copy payload: ', err);
    });
}
