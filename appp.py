from flask import Flask, request, render_template_string, jsonify
import requests
import os

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🌍 Worldwide File Link Generator</title>
    <style>
        body { font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px; }
        .upload-area { border: 3px dashed #007bff; padding: 40px; text-align: center; cursor: pointer; }
        .upload-area.dragover { background: #e3f2fd; }
        input[type=file] { display: none; }
        button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; }
        .result { margin-top: 20px; padding: 15px; background: #d4edda; border-radius: 5px; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>🚀 File to Worldwide Link Generator</h1>
    <p>Upload JPG, PNG, PDF, DOCX, PPTX, XLSX (Max 100MB)</p>
    
    <div class="upload-area" onclick="document.getElementById('file').click()">
        <p>📁 Click or drag file here</p>
        <p><small>Supports all formats</small></p>
        <input type="file" id="file" multiple>
    </div>
    
    <div id="result"></div>

    <script>
        const uploadArea = document.querySelector('.upload-area');
        const fileInput = document.getElementById('file');
        
        // Drag & drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            fileInput.files = e.dataTransfer.files;
            uploadFiles();
        });
        
        fileInput.addEventListener('change', uploadFiles);
        
        async function uploadFiles() {
            const files = fileInput.files;
            if (!files.length) return;
            
            const formData = new FormData();
            formData.append('file', files[0]);
            
            document.getElementById('result').innerHTML = 
                '<p>📤 Uploading... Please wait</p>';
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('result').innerHTML = 
                        `<div class="result">
                            <h3>✅ Success!</h3>
                            <p><strong>File:</strong> ${data.filename}</p>
                            <p><strong>🌍 Worldwide Link:</strong></p>
                            <a href="${data.link}" target="_blank">${data.link}</a>
                            <br><button onclick="navigator.clipboard.writeText('${data.link}')">📋 Copy Link</button>
                        </div>`;
                } else {
                    document.getElementById('result').innerHTML = 
                        `<div class="error">${data.error}</div>`;
                }
            } catch (error) {
                document.getElementById('result').innerHTML = 
                    `<div class="error">Upload failed: ${error}</div>`;
            }
        }
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    try:
        # Upload to anonfiles (or any service)
        files = {'file': (file.filename, file.read())}
        response = requests.post('https://api.anonfiles.com/upload', files=files)
        data = response.json()
        
        if data['status']:
            link = data['data']['file']['url']['full']
            return jsonify({
                'success': True, 
                'link': link, 
                'filename': file.filename
            })
        else:
            return jsonify({'success': False, 'error': 'Upload failed'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
