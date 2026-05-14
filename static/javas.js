document.addEventListener('DOMContentLoaded', function () {
    // Check if the button exists
    const extractTextButton = document.getElementById('extract-text-button');
    if (extractTextButton) {
        // Log the button to confirm it exists
        console.log('Button found:', extractTextButton);

        // Automatically click the button
        extractTextButton.click();
    } else {
        console.log('Button not found!');
    }

    // File preview logic
    const fileInput = document.getElementById('file');
    const previewImg = document.getElementById('preview-img');
    const previewSection = document.getElementById('image-preview');
    const extractedTextArea = document.getElementById('extracted-text');
    const reviewSection = document.getElementById('review-section');
    const downloadButton = document.getElementById('download-button');
    const fileTypeSelector = document.getElementById('file-type');

    // Show Preview Button Logic
    document.getElementById('preview-button').addEventListener('click', function () {
        if (fileInput.files.length === 0) {
            alert('Please select an image file first.');
            return;
        }
        const reader = new FileReader();
        reader.onload = function (e) {
            previewImg.src = e.target.result;
            previewSection.classList.remove('hidden');
        };
        reader.readAsDataURL(fileInput.files[0]);
    });

    // Extract Text Button Logic
    extractTextButton.addEventListener('click', function () {
        if (fileInput.files.length === 0) {
            alert('Please upload a file first.');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        fetch('/process', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(`Error: ${data.error}`);
            } else {
                extractedTextArea.value = data.text;  // Populate the extracted text
                reviewSection.classList.remove('hidden');  // Show review
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while extracting text.');
        });
    });

    // Download Button Logic
    document.getElementById('download-button').addEventListener('click', function () {
        const correctedText = document.getElementById('extracted-text').value;
        const fileType = document.getElementById('file-type').value;
    
        fetch('/finalize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ correctedText, fileType }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.downloadUrl) {
                console.log(`Download URL: ${data.downloadUrl}`);
                window.location.href = data.downloadUrl;  // Trigger file download
            } else {
                alert(data.error || 'An error occurred.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to generate the output file.');
        });
    });
    
});