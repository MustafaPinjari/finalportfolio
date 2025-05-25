function submitContactForm(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    fetch('{% url "contact" %}', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('successModal').classList.remove('hidden');
            form.reset();
        }
    });
}

function closeModal() {
    document.getElementById('successModal').classList.add('hidden');
}